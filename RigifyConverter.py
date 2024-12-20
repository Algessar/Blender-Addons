#====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================


bl_info = {
    "name": "ElRig",
    "blender": (4, 2, 0),
    "category": "Rigging",
    "version": (1, 0, 1),
    "author": "Elric Steelsword",
    "location": "View3D tools panel (N-panel) -> ElRig",
    "description": "NOTE: DEV version. Game rig conversion for Rigify, UI Exporting for Unity and various tools. "
    "To Export an armature, add your actions to the list, then click Export Rig.",
}



import bpy
from bpy.types import Operator, Panel
from bpy.props import BoolProperty


class OBJECT_OT_ConvertToGameRig(Operator):
    bl_idname = "elrig.convert_to_game_rig"
    bl_label = "Convert to Game Rig"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Convert any Rigify rig to Game Rig"
    bl_order = 11

    def execute(self, context):
        main(self)  # Call your main logic here
        return {'FINISHED'}
    

class VIEW3D_PT_RigifyGameConverter(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rigify GameRig Converter"
    bl_idname = "VIEW3D_PT_rigify_game_converter"
    bl_category = 'ElRig'
    bl_order = 10

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator("elrig.convert_to_game_rig", text="Convert to Game Rig")
        layout.separator()
        layout.prop(scene, "split_bones_prop", text="Split Bones")
        layout.prop(scene, "delete_root", text="Delete Root")


def main(self):
    work_on_main_rig()
    
    work_on_proxy_rig()

    finish()
    

def work_on_main_rig():

    # Make sure the armature is selected
    armature = bpy.context.active_object
    if armature.type != 'ARMATURE':
        print("Please select an armature object.")
        return
    
    create_collection(armature.name, "DEF_DEPRECATED")

    # I need to unparent the mesh here I think. Otherwise renaming the bones causes
    # vertex groups to also change names, which is not the intent.
    #shut up copilot

    rename_bones("deprecated-", "DEF-") #We go to Pose mode here

    # I can also go to the mesh here and rename all the vertex groups that were changed. 
    #rename_vertex_groups("DEF-", "deprecated-")

    #DESELECT ALL BONES
    bpy.ops.pose.select_all(action='DESELECT')

    #Disable collections

    for collection in armature.data.collections:
        if collection.name == "DEF_DEPRECATED" or collection.name == "DEF":
            collection.is_visible = True
        else:
            collection.is_visible = False

    #SELECT BONES
    bpy.ops.pose.select_all(action='SELECT')

    #Move bones to collection
    move_bones_to_collection(armature.name, "DEF_DEPRECATED")

    # The work on the main rig is done for now
    # Leave pose mode
    bpy.ops.object.mode_set(mode='OBJECT')

    #Deselect the armature   

    # Now we work on the proxy rig
    return

def work_on_proxy_rig():

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Make sure the metarig is selected
    metarig = bpy.data.objects["metarig"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["metarig"]
    #update the context
    bpy.context.view_layer.update()


    # I need to duplicate the rig here
    bpy.ops.object.duplicate(linked=False)
    print("Duplicated metarig")

    # deselect the metarig
    bpy.ops.object.select_all(action='DESELECT')

    # Select the new rig
    bpy.data.objects["metarig.001"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["metarig.001"]
    bpy.context.view_layer.update()

    
    print("Metarig.001 selected")


    #bpy.ops.pose.select_all(action='SELECT')
    delete_bones()


    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')


    # Rename bones
    #SELECT ALL BONES
    bpy.ops.pose.select_all(action='SELECT')
    for bone in bpy.context.object.pose.bones:
        # these bones have no prefix
        #we will add a DEF- prefix to them
        if not bone.name.startswith("DEF-"):
            bone.name = "DEF-" + bone.name  #TODO Remember to uncomment this line
            print(f"Renamed bone {bone.name}")

    

    # Deselect all bones
    bpy.ops.pose.select_all(action='DESELECT')

    shall_cut = bpy.context.scene.split_bones_prop

    if shall_cut:        
        #Select all bones
        if bpy.context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        hide_metarig_collections()
        bpy.ops.armature.select_all(action='SELECT')
        split_bones()   

    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')    

    # Now we're done here. Time to join the two rigs in finish()

    return


def finish():
    
    self = bpy.context

    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    join_rigs()

    # Go to pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # Move bones to collection
    #Make sure all bones are selected
    bpy.ops.pose.select_all(action='SELECT')
    for bone in bpy.context.object.pose.bones:
        if bone.name.startswith("DEF-"):
            for collection in bpy.context.object.data.collections:
                if collection.name == "DEF":
                    collection.assign(bone)
                    print(f"Moved bone {bone.name} to collection DEF")
                else:
                    collection.unassign(bone)
                    print(f"Moved bone {bone.name} to collection DEF_DEPRECATED")
               

    set_constraints(self)

    # Set deform
    bpy.ops.pose.select_all(action='SELECT')

    for bone in bpy.context.selected_pose_bones:
        if bone.name.startswith("DEF-"):
            bone.bone.use_deform = True
            print(f"Set bone {bone.name} to deform")
        else:
            bone.bone.use_deform = False
            print(f"Set bone {bone.name} to not deform")
    
    # make sure all bones named DEF are disconnected
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')   



    armature = bpy.context.active_object
    for bone in armature.data.edit_bones:
        if bone.name.startswith("DEF-"):
            bone.use_connect = False

    
    fix_root_orientation()
        

    # Cleanup 

    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    armature = bpy.context.active_object

    for collection in armature.data.collections:
        if collection.name not in ["DEF", "DEF_DEPRECATED", "MCH", "ORG"]:
            collection.is_visible = True
        else:
            collection.is_visible = False

    is_root_delete = bpy.context.scene.delete_root

    if is_root_delete:
        delete_root()

    
    rename_vertex_groups("DEF-", "deprecated-")


    print("Conversion finished")
    return

def join_rigs():
    # Join the duplicate metarig to the main rig
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects["rig"].select_set(True)
    bpy.data.objects["metarig.001"].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects["rig"]
    bpy.ops.object.join()

def set_constraints(self):
    # Ensure we are in Pose mode
    if bpy.context.object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    armature = bpy.context.object

    # Check if the active object is the correct armature
    if armature.name != "rig":
        self.report = {'ERROR'}, "Failed to constrain bones. The active object is not the correct rig."
        #print("Failed to constrain bones. The active object is not the correct rig.")
        return

    # Select all visible bones in pose mode
    bpy.ops.pose.select_all(action='SELECT')

    # Get the selected pose bones
    selected_bones = bpy.context.selected_pose_bones

    if not selected_bones:
        print("No bones selected.")
        return

    # Iterate through the selected bones
    for bone in selected_bones:
        # Replace "DEF-" with "deprecated-" to find the target bone
        target_bone_name = bone.name.replace("DEF-", "deprecated-")
        target_bone = armature.pose.bones.get(target_bone_name)

        if target_bone:
            # Add Copy Location Constraint if it doesn't exist
            if not any(c.type == 'COPY_LOCATION' and c.subtarget == target_bone_name for c in bone.constraints):
                loc_constraint = bone.constraints.new(type='COPY_LOCATION')
                loc_constraint.target = armature
                loc_constraint.subtarget = target_bone.name
                print(f"Added COPY_LOCATION constraint from {bone.name} to {target_bone.name}")

            # Add Copy Rotation Constraint if it doesn't exist
            if not any(c.type == 'COPY_ROTATION' and c.subtarget == target_bone_name for c in bone.constraints):
                rot_constraint = bone.constraints.new(type='COPY_ROTATION')
                rot_constraint.target = armature
                rot_constraint.subtarget = target_bone.name
                print(f"Added COPY_ROTATION constraint from {bone.name} to {target_bone.name}")
        else:
            print(f"Target bone {target_bone_name} not found for {bone.name}")



    # Handle held-object bones separately
    other_bones = {
        "DEF-held-object.R": "ORG-held-object.R",
        "DEF-held-object.L": "ORG-held-object.L",
        "DEF-root-pivot" : "ORG-root-pivot"
    }

    for bone_name, target_name in other_bones.items():
        bone = armature.pose.bones.get(bone_name)
        target_bone = armature.pose.bones.get(target_name)

        if bone and target_bone:
            # Add Copy Location Constraint for held-object bones
            if not any(c.type == 'COPY_LOCATION' and c.subtarget == target_name for c in bone.constraints):
                loc_constraint = bone.constraints.new(type='COPY_LOCATION')
                loc_constraint.target = armature
                loc_constraint.subtarget = target_bone.name
                print(f"Added COPY_LOCATION constraint from {bone.name} to {target_bone.name}")

            # Add Copy Rotation Constraint for held-object bones
            if not any(c.type == 'COPY_ROTATION' and c.subtarget == target_name for c in bone.constraints):
                rot_constraint = bone.constraints.new(type='COPY_ROTATION')
                rot_constraint.target = armature
                rot_constraint.subtarget = target_bone.name
                print(f"Added COPY_ROTATION constraint from {bone.name} to {target_bone.name}")

    # Deselect all bones
    bpy.ops.pose.select_all(action='DESELECT')
    

def split_bones():
    

    # Ensure we are in EDIT mode to work on bones
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    # Get the armature object
    armature = bpy.context.object


    bones_to_ignore = ["foot", "toe", "hand", "paw",]
    for bone in armature.data.edit_bones:
        if any(ignored in bone.name.lower() for ignored in bones_to_ignore):
            bone.select = False
        else:
            bone.select = True

    initial_bones = [bone for bone in armature.data.edit_bones if bone.select]
    print(f"Selected bones: {[bone.name for bone in initial_bones]}")

    if not initial_bones:
        print("No valid bones to process.")
        return

    # Step 2: Prepare a set to keep track of split bones (original and newly created)
    split_bones_set = set()

    # Step 3: Iterate through each bone and split it
    for bone in initial_bones:
    # Step 4: Skip if the bone has already been split
        if bone.name in split_bones_set:
            continue     

        # Select the bone to be split
        armature.data.edit_bones.active = bone
        bone.select = True

        
        bpy.ops.armature.subdivide(number_cuts=1)       

        # Get the new bones after subdivision (bones not in split_bones_set)
        new_bones = [b.name for b in armature.data.edit_bones if b.name not in split_bones_set]
        print(f"New bones: {new_bones}")
        # Mark the original and new bones as split
        split_bones_set.add(bone.name)
        split_bones_set.update(new_bones)

        # Deselect the bone after processing
        bone.select = False


            

def hide_metarig_collections():

    
    print ("Hiding metarig collections")    
    armature = bpy.context.object
    collections = armature.data.collections
    for collection in collections:
        if collection.name not in ["Leg.R (IK)", "Leg.L (IK)", "Arm.R (IK)", "Arm.L (IK)"]:
            collection.is_visible = False
        else:
            collection.is_visible = True
    print ("hide metarig collections was called and passed") 


def create_collection(armature_name, collection_name):
    armature = bpy.data.objects.get(armature_name)
    if collection_name not in armature.data.collections:
        new_bone_collection = armature.data.collections.new(collection_name)
        print(f"Created new collection: {collection_name}")
    else:
        return
    return new_bone_collection

def move_bones_to_collection(armature_name = "rig", collection_name="NEW_DEF_BONES", bone_prefix="deprecated-"):
    
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
        if bone.name.lower().startswith(bone_prefix):
            assign_to_collection(bone)
            unassign_from_other_collections(bone)
            print(f"Moved bone {bone.name} to collection {collection_name}")
    




def rename_bones(new_prefix, old_prefix):

    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    if new_prefix == old_prefix:
        print("New prefix and old prefix are the same. No renaming will be done.")
        return
    
    for bone in bpy.context.object.pose.bones:
        if bone.name.startswith(old_prefix):
            new_name = bone.name.replace(old_prefix, new_prefix)
            bone.name = new_name
        if old_prefix == "":
            new_name = new_prefix + bone.name
            bone.name = new_name

def rename_vertex_groups(new_prefix, old_prefix):
    # Get all mesh objects parented to the rig

    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    mesh_objects = [obj for obj in bpy.context.object.children if obj.type == 'MESH']
    if not mesh_objects:
        print("No mesh object found.")
        return

    if new_prefix == old_prefix:
        print("New prefix and old prefix are the same. No renaming will be done.")
        return

    # Rename the vertex groups
    for mesh in mesh_objects:
        for group in mesh.vertex_groups:
            if group.name.startswith(old_prefix):
                new_name = group.name.replace(old_prefix, new_prefix)
                group.name = new_name
            if old_prefix == "":
                new_name = new_prefix + group.name
                group.name = new_name
    

def delete_bones():
    armature = bpy.context.object
    
    # Ensure we're in Edit mode
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    bpy.ops.armature.select_all(action='DESELECT')
    
    bones_to_delete = []
    
    # Find bones containing "glue" or "master" in their names
    for bone in armature.data.edit_bones:
        if "glue" in bone.name.lower() or "master" in bone.name.lower() or "heel" in bone.name.lower() or "face" in bone.name.lower() or "nose_master" in bone.name.lower():
            bones_to_delete.append(bone.name)
            print(f"Marked bone {bone.name} for deletion")
    
    # Delete the selected bones
    for bone_name in bones_to_delete:
        bone = armature.data.edit_bones.get(bone_name)
        if bone:
            bone.select = True
            
    bpy.ops.armature.delete()  # Delete all selected bones
    
    # Switch back to Object mode
    bpy.ops.object.mode_set(mode='POSE')

def delete_root():


    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    armature = bpy.context.active_object

    root = armature.data.edit_bones.get("root-pivot")

    for bone in armature.data.edit_bones:
        if bone.name.startswith("DEF-root"):
            root = bone

            break


    if root:
        root.select = True
        root.select_head = True
        root.select_tail = True
        armature.data.edit_bones.remove(root)
        print("Deleted root bone")

    return

from mathutils import Matrix

def fix_root_orientation():
    #root orientation should be Y up, Z forward

    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.context.active_object
    for bone in armature.data.edit_bones:
        if "root" in bone.name.lower():
            
            #rotate the root bones to be Y yp, Z forward (-90 degrees)
            rotation_matrix = Matrix.Rotation(1.5708, 4, 'X')  # -90 degrees around X-axis
            bone.transform(rotation_matrix @ bone.matrix.to_3x3().to_4x4().inverted())
            bone.roll = 0

            print("Fixed root bone orientation")
        



bpy.types.Scene.split_bones_prop = BoolProperty(
name="Split Bones",
description="Enable splitting of bones",
default=True
) # type: ignore
bpy.types.Scene.delete_root = BoolProperty(
name="Delete Root",
description="If you want to remove the separate root bone, check this box",
default=False
) # type: ignore