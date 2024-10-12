import os
import bpy
from bpy.types import Operator, Panel, UIList

from .helpers import Action_List_Helper
from . import exportFunctions

from bpy.props import StringProperty, PointerProperty, BoolProperty, CollectionProperty, IntProperty

export_dir = ""
#base_filename = "exported_rig"

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
        export_tool = scene.my_tool
        #clear_nla_tracks = scene.clear_nla_tracks

        if obj is not None:
            row = layout.row()
            row.template_list("ACTION__UI_UL_actions", "", obj, "action_list", obj, "elrig_active_action_index")
            
            row = layout.row()
            row.operator("elrig.add_action", text="Add Current Action")
        else:    
            box = layout.box()
            box.label(text="No object selected")      
        
        folder_directory = export_dir       
       
        
        layout.label(text="Export Directory: " + folder_directory)
        layout.separator()
        layout.operator("elrig.set_file_path", text="Set File Path")
        layout.separator()
        layout.prop(export_tool, "SetFileName")
        layout.separator()
        
        layout.separator()
        layout.label(text="Export Cleanup Options:")
        layout.prop(scene, "clear_nla_tracks")
        layout.prop(scene, "clear_all_nla_tracks")
        layout.separator()
        layout.operator("elrig.export_rig", text="Export Rig") 
        layout.separator()
        #layout.operator("elrig.push_to_nla", text="Push to NLA")
        
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
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            if item.action:
                layout.label(text="", icon_value=icon)
            else:
                layout.label(text="No Action", icon='ERROR')
            
# Operator to add the current action to the list
class AddActionOperator(Operator):
    bl_idname = "elrig.add_action"
    bl_label = "Add Current Action"
    #bl_info = "Add the current action to the list of actions"
    bl_description = "Add the current action to the list of actions"

    def execute(self, context):
        obj = context.object
        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action
            item = obj.action_list.add()
            item.action = action
            obj.elrig_active_action_index = len(obj.action_list) - 1
            self.report({'INFO'}, f"Added action: {action.name}")
        else:
            self.report({'WARNING'}, "No current action to add.")
        return {'FINISHED'}

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
    
    # Operator to set an action as the active one
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

#### Operators for Exporting Rig ####

class Custom_OT_SetFilePath(Operator):
    bl_idname = "elrig.set_file_path"
    bl_label = "Set File Path"
    bl_description = "Opens Blender File View. Select the directory to export to"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH") # type: ignore
    
    def execute(self, context):
        global export_dir
        export_dir = os.path.dirname(self.filepath)
        print("Exporting to folder directory: ", export_dir)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
class CUSTOM_OT_ExportRigOperator(Operator):
    bl_idname = "elrig.export_rig"
    bl_label = "Export Rig as FBX"
    bl_description = "Export the selected armature and its actions as an FBX file. Select the armature; any parented and visible items will also be exported"

    def execute(self, context):

        
        pushed_actions = exportFunctions.prep_export_push_NLA()

        #for action in pushed_actions:
        #    print(action.name)
       

        #print(f"Pushed actions: {[action.name for action in pushed_actions]}")

        #exportFunctions.push_actions_to_nla(bpy.context.active_object, pushed_actions)

        #print(f"Exported actions: {[action.name for action in actions]}")
        
        custom_filename = bpy.context.scene.my_tool.SetFileName
        export_filename = f"{custom_filename}.fbx"
        
        version = 1
        while True:
            export_filepath = os.path.join(export_dir, export_filename)
            if not os.path.exists(export_filepath):
                break
            version += 1
            export_filename = f"{custom_filename}_V{version}.fbx"
        #refactor to work with any object
        selected_armature = bpy.context.active_object

        if selected_armature and selected_armature.type == 'ARMATURE':
            for obj in bpy.context.scene.objects:
                if obj.parent == selected_armature:
                    obj.select_set(True)
                    selected_armature.select_set(True)
                    #exportFunctions.set_export_scene_params(export_filepath)
                    
        exportFunctions.set_export_scene_params(export_filepath)
        clear_added = context.scene.clear_nla_tracks
        clear_all = context.scene.clear_all_nla_tracks

        if clear_added:
            exportFunctions.clear_added_nla_tracks(selected_armature, pushed_actions)
        if clear_all:
            Action_List_Helper.clear_all_nla_tracks(selected_armature)
           # exportFunctions.delete_nla_tracks(selected_armature)
        print(f"exported {selected_armature.name} to {export_filepath}")
       
        
        return {'FINISHED'}
    


# DEBUG


        


