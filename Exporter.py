import os
import bpy
from bpy.types import Operator, Panel, UIList

from .helpers import Action_List_Helper
from . import exportFunctions

from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty, IntProperty


export_dir = ""

# Custom Property Group to store action references
class ElRigActionItem(bpy.types.PropertyGroup):
    action: PointerProperty(name="Action", type=bpy.types.Action)  # type: ignore

class ExportProperties(bpy.types.PropertyGroup):
    SetFileName: StringProperty(
        name="File Name",
        description="Set the file name for the exported FBX. The name will be appended with _V# automatically",
        default="",
        maxlen=1024,
        subtype='FILE_NAME'
    ) # type: ignore
    export_filepath: StringProperty(
        name="Export Filepath",
        description="Filepath to export the FBX to",
        default="",
        maxlen=1024,
        subtype='FILE_PATH'
    ) # type: ignore
    

class BoolProperties(bpy.types.PropertyGroup):
    clear_nla_tracks: BoolProperty(
    name="Clear NLA tracks",
    description="Clear NLA tracks after export. If neither is selected, the NLA tracks will be kept.",
    default=True
) # type: ignore

clear_all_nla_tracks: BoolProperty(
    name="Clear all NLA tracks",
    description="Clear all NLA tracks after export. If neither is selected, the NLA tracks will be kept.",
    default=False
) # type: ignore 
overwrite_file: BoolProperty(
    name="Overwrite File",
    description="Overwrite the file if it already exists",
    default=False
) # type: ignore
export_mesh: BoolProperty(
    name="Export with Mesh",
    description="Export the mesh of the selected object",
    default=True
) # type: ignore


class VIEW_3D_UI_Elements(Panel):
    bl_label = "Export UI"
    bl_idname = "OBJECT_PT_ui_elements"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ElRig'
    
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        export_tool = scene.export_props
        #clear_nla_tracks = scene.clear_nla_tracks

        if obj is not None:
            
            layout = self.layout
            row  = layout.row()
            row.template_list("ACTION__UI_UL_actions", "", obj, "action_list", obj, "elrig_active_action_index") 
                        
            col = row.column(align=True)            
            col.operator("elrig.move_action_up", icon='TRIA_UP', text="")            
            col.operator("elrig.move_action_down", icon='TRIA_DOWN', text="") 

            col.separator()
            col.separator()
            col.separator()
            col.operator("elrig.create_action",icon="PLUS", text="")
            col.operator("elrig.duplicate_action", icon="DUPLICATE", text="")
            
            row = layout.row()
            row.operator("elrig.add_action", text="Add Current Action")
        else:
            box = layout.box()
            box.label(text="No object selected")    
        
        global export_dir
        folder_directory = export_dir
        export_dir = scene.export_props.export_filepath
        

        
        
        layout.label(text="Export Directory: " + folder_directory)
        layout.separator()
        layout.operator("elrig.set_file_path", text="Set File Path")
        layout.separator()
        layout.prop(export_tool, "SetFileName")
        layout.prop(scene, "overwrite_file")
        layout.separator()

        layout.separator()
        
        layout.prop(scene, "export_mesh")
        layout.separator()
        layout.operator("elrig.export_rig", text="Export Rig")
        layout.separator()
        layout.label(text="Export Cleanup Options:")
        layout.prop(scene, "clear_nla_tracks")
        layout.prop(scene, "clear_all_nla_tracks")
        layout.separator()


# UIList
class ACTION__UI_UL_actions(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.action:
                layout.prop(item.action, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="No Action", icon='ERROR')
            
            # Find the index of the item
            index = -1
            for i, list_item in enumerate(data.action_list):
                if list_item == item:
                    index = i
                    break
            
            row = layout.row()
            op = layout.operator("elrig.remove_action", text="", icon='X')
            op.index = index
            
            # Icon for set active action button
            is_active = context.object.animation_data and context.object.animation_data.action == item.action
            icon = 'CHECKMARK' if is_active else 'BLANK1'
            op = row.operator("elrig.set_active_action", text="", icon=icon) 
            op.action_name = item.action.name if item.action else ""

            # Icon for Filtered actions
            # Add the star icon for "starred" actions
            row = layout.row(align=True)  # Align the star icon with other operators
            is_starred = item.action.is_starred if item.action else False
            star_icon = 'SOLO_ON' if is_starred else 'SOLO_OFF'
            op = row.operator("elrig.filter_actions", text="", icon=star_icon)
            op.action_name = item.action.name if item.action else ""           
        
        

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            if item.action:
                layout.label(text="", icon_value=icon)
            else:
                layout.label(text="No Action", icon='ERROR')
    
class FilterActionsOperator(Operator):
    bl_idname = "elrig.filter_actions"
    bl_label = "Toggle Star Action"
    bl_description = "Star or unstar the action"

    action_name: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        obj = bpy.context.object
        if obj and self.action_name:
            action = bpy.data.actions.get(self.action_name)           

            if action:
                action.is_starred = not action.is_starred  # Toggle the starred status    
                
                
            return {'FINISHED'}

class CreateActionOperator(Operator):
    bl_idname = "elrig.create_action"
    bl_label = "Create Action"
    bl_description = "Create a new action for the object"

    def execute(self, context):
        obj = context.object
        action = bpy.data.actions.new(name="Action")
        obj.animation_data_create()
        obj.animation_data.action = action
        AddAction(self, context)
        self.report({'INFO'}, "Created new action.")
        return {'FINISHED'}
    
class DuplicateActionOperator(Operator):
    bl_idname = "elrig.duplicate_action"
    bl_label = "Duplicate Action"
    bl_description = "Duplicate the current action"

    def execute(self, context):
        DuplicateAction(self, context)
        return {'FINISHED'}
            
class AddActionOperator(Operator):
    bl_idname = "elrig.add_action"
    bl_label = "Add Current Action"
    bl_description = "Add the current action to the list of actions"

    def execute(self, context):
        AddAction(self, context)
        return {'FINISHED'}
    

def AddAction(self, context):
    obj = context.object
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        item = obj.action_list.add()
        item.action = action
        obj.elrig_active_action_index = len(obj.action_list) - 1
        self.report({'INFO'}, f"Added action: {action.name}")
    else:
        self.report({'WARNING'}, "No current action to add.")

def DuplicateAction(self, context):
    obj = context.object
    if obj.animation_data and obj.animation_data.action:
        action = obj.animation_data.action
        new_action = action.copy()
        new_action.name = action.name + ".001"
        item = obj.action_list.add()
        item.action = new_action
        obj.elrig_active_action_index = len(obj.action_list) - 1
        self.report({'INFO'}, f"Duplicated action: {action.name}")
    else:
        self.report({'WARNING'}, "No current action to duplicate.")

# Operator to remove an action from the list
class RemoveActionOperator(Operator):
    bl_idname = "elrig.remove_action"
    bl_label = "Remove Action"
    
    index: IntProperty() # type: ignore

    def execute(self, context):
        obj = context.object
        if 0 <= self.index < len(obj.action_list):
            obj.action_list.remove(self.index)
            self.report({'INFO'}, "Removed action from list.")
        else:
            self.report({'WARNING'}, "Invalid index.")
        return {'FINISHED'}
    
class CUSTOM_OT_SetActiveAction(Operator):
    bl_idname = "elrig.set_active_action"
    bl_label = "Set Active Action"
    bl_description = "Set the selected action as the active action"
    
    action_name: bpy.props.StringProperty() # type: ignore

    def execute(self, context):
        obj = context.object
        action = bpy.data.actions.get(self.action_name)
        if action:
            if not obj.animation_data:
                obj.animation_data_create()
            obj.animation_data.action = action
            self.report({'INFO'}, f"Set active action: {action.name}")
        else:
            self.report({'WARNING'}, "Action not found.")
        return {'FINISHED'}
    
class CUSTOM_OT_MoveActionUp(Operator):
    bl_idname = "elrig.move_action_up"
    bl_label = "Move Action Up"
    
    index: IntProperty() # type: ignore

    def execute(self, context):
        obj = context.object
        index = obj.elrig_active_action_index
        if index > 0:
            obj.action_list.move(index, index - 1)
            obj.elrig_active_action_index -= 1
            self.report({'INFO'}, "Moved action up.")
        else:
            self.report({'WARNING'}, "Action already at the top.")
        return {'FINISHED'}
    
class CUSTOM_OT_MoveActionDown(Operator):
    bl_idname = "elrig.move_action_down"
    bl_label = "Move Action Down"
    
    index: IntProperty() # type: ignore 

    def execute(self, context):
        obj = context.object
        index = obj.elrig_active_action_index
        if index < len(obj.action_list) - 1:
            obj.action_list.move(index, index + 1)
            obj.elrig_active_action_index += 1
        else:
            self.report({'WARNING'}, "Action already at the bottom.")
        return {'FINISHED'}

#### Operators for Exporting Rig ####

class Custom_OT_SetFilePath(Operator):
    bl_idname = "elrig.set_file_path"
    bl_label = "Set File Path"
    bl_description = "Opens Blender File View. Select the directory to export to"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore
    
    def execute(self, context):
        global export_dir
        export_props = context.scene.export_props
        export_dir = export_props.export_filepath = os.path.dirname(self.filepath)
        print("Exporting to folder directory: ", export_props.export_filepath)        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class CUSTOM_OT_ExportRigOperator(Operator):
    bl_idname = "elrig.export_rig"
    bl_label = "Export Rig as FBX"
    bl_description = "Export the selected armature and its actions as an FBX file. Select the armature; any parented and visible items will also be exported"

    def execute(self, context):
        
        obj = bpy.context.active_object        
        starred_list = exportFunctions.get_starred_actions()
        export_list = exportFunctions.get_actions_from_ui_list(obj)

        if len(starred_list) > 0:
            export_list = starred_list        
        pushed_actions = exportFunctions.prep_export_push_NLA(export_list)

        print(f"starred actions: {[action.name for action in starred_list]}")
        
        custom_filename = bpy.context.scene.export_props.SetFileName
        export_dir = bpy.context.scene.export_props.export_filepath

              
        export_filepath = get_export_filepath(custom_filename, export_dir)

        selected_armature = bpy.context.active_object

        print(f"Exporting {selected_armature.name} to {export_filepath}")
        

        if(bpy.context.scene.export_mesh):
            #TODO: Make sure any other selected objects are deselected.            
            get_parented_objects()

        
                    
        exportFunctions.set_export_scene_params(export_filepath)
        clear_added = context.scene.clear_nla_tracks
        clear_all = context.scene.clear_all_nla_tracks

        if clear_added:
            exportFunctions.clear_nla_tracks(selected_armature, pushed_actions)
        if clear_all:
            Action_List_Helper.clear_all_nla_tracks(selected_armature)


        print(f"exported {selected_armature.name} to {export_filepath}")
        
        return {'FINISHED'}
    


def get_latest_version_filepath(custom_filename, export_dir):
    version = 1
    latest_filepath = None
    
    while True:
        # Construct the filename with the version number
        export_filename = f"{custom_filename}_V{version}.fbx"
        export_filepath = os.path.join(export_dir, export_filename)
        
        # If the file exists, store the latest version's path
        if os.path.exists(export_filepath):
            latest_filepath = export_filepath
            version += 1  # Continue searching for higher versions
        else:
            break  # Stop once we reach a version that doesn't exist
    
    # Return the latest version's path (if any) and the next available version's path
    return latest_filepath, export_filepath

def get_export_filepath(custom_filename, export_dir):
    overwrite = bpy.context.scene.overwrite_file
    
    # Get the latest version and the next available version's paths
    latest_filepath, next_filepath = get_latest_version_filepath(custom_filename, export_dir)
    
    if overwrite and latest_filepath:
        # If overwriting is allowed, return the latest file path to overwrite
        return latest_filepath
    else:
        # If not overwriting, return the next available file path (incrementing the version)
        return next_filepath

def get_parented_objects():
    armature = bpy.context.active_object
    if bpy.context.scene.export_mesh:
        if armature and armature.type == 'ARMATURE':
                for obj in bpy.context.scene.objects:
                    if obj.parent == armature:
                        obj.select_set(True)
                        armature.select_set(True)
                    else:
                        #deselect all objects
                        obj.select_set(False)                        
                        armature.select_set(True)
    return armature