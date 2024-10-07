
#TODO: Add a check to see if the rig is already converted to a game rig 
#TODO: Add an operator to change existing vertex groups on an already rigged mesh (DONE)
#TODO: Add an operator to add a root bone specifically for exporting to Unity. (Change the name of def_root_pivot to ROOT)

import bpy
from bpy.types import Collection

#create classes for operators
class OBJECT_OT_ConvertToGameRig(bpy.types.Operator):
    bl_idname = "elrig.convert_to_game_rig"
    bl_label = "Convert to Game Rig"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convert any Rigify rig to Game Rig"

    def execute(self, context):
        main()  # Call your main logic here
        return {'FINISHED'}

class VIEW3D_PT_RigifyGameConverter(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rigify GameRig Converter"
    bl_idname = "VIEW3D_PT_rigify_game_converter"
    bl_category = 'ElRig'

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        layout.operator("elrig.convert_to_game_rig", text="Convert to Game Rig")
        layout.operator("elrig.change_vertex_groups", text="Change Vertex Groups")

class OBJECT_OT_change_vertex_groups(bpy.types.Operator):
    bl_idname = "elrig.change_vertex_groups"
    bl_label = "Change Vertex Groups"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Change vertex group prefixes to match bone names"

    def execute(self, context):
        change_vertex_group_prefix()
        return {'FINISHED'}
    
def get_bones_by_prefix(prefix):
    armature = bpy.context.object
    
    bones = []
    
    for bone in armature.data.bones:
        if bone.name.startswith(prefix):
            bones.append(bone)
    
    return bones              

def duplicate_and_join():
    # Ensure we are in object mode
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    # Select the metarig
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["metarig"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["metarig"]
    bpy.context.view_layer.update()
    
    # Duplicate the metarig
    bpy.ops.object.duplicate()
    
    # Move bones to the new collection in the metarig 
    #move_bones_to_collection()    
    
    
    # Select the rig        
    bpy.data.objects["rig"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["rig"]
    bpy.context.view_layer.update()
    
    # Join the duplicate to the rig
    bpy.ops.object.join()
    
    
def delete_bones():
    armature = bpy.context.object
    
    # Ensure we're in Edit mode
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    bpy.ops.armature.select_all(action='DESELECT')
    
    bones_to_delete = []
    
    # Find bones containing "glue" or "master" in their names
    for bone in armature.data.edit_bones:
        if "glue" in bone.name.lower() or "master" in bone.name.lower():
            bones_to_delete.append(bone.name)
    
    # Delete the selected bones
    for bone_name in bones_to_delete:
        bone = armature.data.edit_bones.get(bone_name)
        if bone:
            bone.select = True
            
    bpy.ops.armature.delete()  # Delete all selected bones
    
    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='POSE')     
    
def rename_bones_with_prefix(armature, prefix="def_"):
    bpy.ops.object.mode_set(mode='EDIT')  # Ensure we're in Edit mode

    for bone in armature.data.edit_bones:
        if bone.select and not bone.name.startswith(prefix):
            bone.name = prefix + bone.name
            print(f"Renamed bone to: {bone.name}")      
    
    disconnect_and_split_bones(armature)
    
    bpy.ops.object.mode_set(mode='POSE')  # Switch back to Pose mode
    
def disconnect_and_split_bones(armature):
    
    bone_list = ["def_thigh.L", "def_thigh.R", "def_shin.L" ,"def_shin.R", "def_upper_arm.L", "def_upper_arm.R", "def_forearm.L", "def_forearm.R"]
    
    armature = bpy.context.object
    
    #Make sure we are in Edit mode
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    bpy.ops.armature.select_all(action='DESELECT')    

    for bone_name in bone_list:
        print ("bone name: " + bone_name)
        bone = armature.data.edit_bones.get(bone_name)
        if bone:
            bpy.ops.armature.select_all(action='DESELECT')
            bone.select = True            
    
            # Subdivide the bone
            bpy.ops.armature.subdivide(number_cuts=1)            
    
            print(f"Split bone: {bone.name}")

    # disconnect selected bones
    bpy.ops.armature.select_all(action='SELECT')
    for bone in armature.data.edit_bones:
        bone.use_connect = False
        
        
    return 0

def move_bones_to_collection():
    # Select the duplicated metarig
    

    bpy.data.objects["metarig.001"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["metarig.001"]
    bpy.context.view_layer.update()
    armature = bpy.context.object
    
    

   # disconnect_and_split_bones(armature)

    # Go to Pose mode
    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    
    # Select all bones
    bpy.ops.pose.select_all(action='SELECT')    
    
    # Create a new collection
    armature = bpy.context.active_object
    new_bone_collection = None
    
    rename_bones_with_prefix(armature, "def_")
    
    if "NEW_DEF_BONES" not in armature.data.collections:
        new_bone_collection = armature.data.collections.new("NEW_DEF_BONES")
    
    if new_bone_collection:
        for bone in armature.data.bones:
            new_bone_collection.assign(bone)
    else:
        for coll in armature.data.collections:
            coll.unassign(bone)

def move_def_bones_to_collection(armature_name = "rig", collection_name="NEW_DEF_BONES"):
    
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != 'ARMATURE':
        print(f"No valid armature named '{armature_name}' found.")
        return

    # Ensure the collection exists, or create it
    collection = None
    for coll in armature.data.collections:
        if coll.name == collection_name:
            collection = coll
            break
    if not collection:
        collection = armature.data.collections.new(collection_name)

    def assign_to_collection(bone):
        collection.assign(bone)

    def unassign_from_other_collections(bone):
        for coll in armature.data.collections:
            if coll.name != collection.name:
                coll.unassign(bone)   
                
    #selected_bones = get_bones_by_prefix("def_")

    # Iterate over bones and assign them to the collection
    for bone in armature.pose.bones:
        if bone.name.lower().startswith("def_"):
            assign_to_collection(bone)
            unassign_from_other_collections(bone)
            print(f"Moved bone {bone.name} to collection {collection_name}")
            

def constrain_bones_to_def():
    armature = bpy.context.object
    
    # Ensure we're in Pose mode
    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    # Get the selected bones
    selected_bones = bpy.context.selected_pose_bones
    
    if not selected_bones:
        print("No bones selected.")
        return

    for bone in selected_bones:
        def_bone_name = bone.name.replace("def_", "DEF-")

        def_bone = armature.pose.bones.get(def_bone_name)
        
        if def_bone:
            # Add Copy Location Constraint
            loc_constraint = bone.constraints.new(type='COPY_LOCATION')
            loc_constraint.target = armature
            loc_constraint.subtarget = def_bone.name

            # Add Copy Rotation Constraint
            rot_constraint = bone.constraints.new(type='COPY_ROTATION')
            rot_constraint.target = armature
            rot_constraint.subtarget = def_bone.name

            #print(f"Constrained {bone.name} to {def_bone_name}")
        #else:
            #print(f"DEF bone {def_bone_name} not found for {bone.name}")

def toggle_deform():
    armature = bpy.context.object

    # Ensure we are in Pose mode
    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    selected_bones = bpy.context.selected_pose_bones
    
    # Turn on deform for new bones
    for bone in selected_bones:
        bone.bone.use_deform = True

    # Turn off deform for all DEF- bones
    bpy.ops.pose.select_all(action='SELECT')
    
    for bone in armature.pose.bones:
        if bone.name.startswith("DEF-"):
            bone.bone.use_deform = False
            #move_bones_to_collection()
            print(f"Turned off deform for bone: {bone.name}")
            

def main():
    duplicate_and_join()
    constrain_bones_to_def()
    toggle_deform()
    move_def_bones_to_collection()
    delete_bones()
    change_root_name()

def change_vertex_group_prefix():
    
    # get the object
    # check if the mesh has vertex groups
    # check if the vertex group name matches the bone name
    # if the vertex groups has DEF- prefix, change corresponding to def_ 
    
    obj = bpy.context.object

    if obj.type != 'MESH':
        print("No mesh object selected.")
        return
    
    if not obj.vertex_groups:
        print("No vertex groups found.")
        return
    
    for vgroup in obj.vertex_groups:
        if vgroup.name.startswith('DEF-'):

            new_name = vgroup.name.replace('DEF-', 'def_', 1)

            vgroup.name = new_name
            print(f"Renamed vertex group to: {new_name}")
        else:
            print(f"Vertex group {vgroup.name} does not have the DEF- prefix.")
    print("Vertex group prefixes changed.")


def change_root_name(old_root_name="def_root-pivot" ,root_name="ROOT"):
    armature = bpy.context.object
    root_bone = armature.data.bones.get(old_root_name)
    if root_bone:
        root_bone.name = root_name
        root_bone.use_deform = False
        print("Root bone renamed to ROOT.")
    else:
        print("Root bone not found.")

def set_root_parent():
    armature = bpy.context.object
    root_bone = armature.data.bones.get("ROOT")
    if not root_bone:
        print("Root bone not found.")
        return
    
    # Get the selected bones

class OBJECT_OT_set_flat_hierarchy(bpy.types.Operator):
    bl_idname = "elrig.set_flat_hierarchy"
    bl_label = "Set Flat Hierarchy"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        set_flat_hierarchy()
        return {'FINISHED'}

def set_flat_hierarchy():

    armature = bpy.context.object

    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    selected_bones = bpy.context.selected_pose_bones
    root_bone = armature.data.bones.get('ROOT')
    if not selected_bones:
        print("No bones selected.")
        return
    for bone in selected_bones:
        bone.parent = root_bone
        print(f"Parented {bone.name} to ROOT.")

classes = [OBJECT_OT_ConvertToGameRig, VIEW3D_PT_RigifyGameConverter, OBJECT_OT_change_vertex_groups, OBJECT_OT_set_flat_hierarchy]
    

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls  in reversed (classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":    
    register()   