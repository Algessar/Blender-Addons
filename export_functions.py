


# This file is for export logic. The old version uses the addon FrameRanger as a base, which I want to avoid.


#TODO:
# A collection for animation actions to export
# Convert said actions to NLA strips

# Automatically select all visible objects that are parented to the rig
# Export the rig as FBX
# Remove the NLA strips that were exported

# Get Actions from the active object
    # _actions = _action_list_helper.collect_action_list() # This is the old version, using FrameRanger utilities. 
    # Which means I can see which helper functions I need to write(steal).

import sys
import os

module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "D:/Blender_Projects/Addons/Scripting/TestFolderVSCode"))
if module_path not in sys.path:
    sys.path.append(module_path)
import bpy
from helper_functions import Action_List_Helper   


    
def get_actions_from_ui_list(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.collect_action_list()

def get_actions_from_object(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.get_actual_action()

def push_actions_to_nla(obj, actions):
    added_tracks = []
    action_list_helper = Action_List_Helper(obj)
    actions = action_list_helper.collect_action_list()
    for action in actions:
        action_list_helper.set_actual_action(action)
        action_list_helper.push_to_nla(action)
        added_tracks.append(action)
    return added_tracks

def clear_added_nla_tracks(obj, added_tracks):
    for track in added_tracks:
        obj.animation_data.nla_tracks.remove(track)

def export_with_nla_cleanup(obj, export_filepath):

    added_tracks = push_actions_to_nla(obj)
    set_export_scene_params(export_filepath)
    clear_added_nla_tracks(obj, added_tracks)
    

def prep_export_push_NLA():
    obj = bpy.context.active_object
    if obj is None:
        print("No active object selected.")
        return

    actions = get_actions_from_ui_list(obj)
    if not actions:
        print("No actions found for the selected object.")
        return

    push_actions_to_nla(obj, actions)
    #print(f"Exported actions: {[action.name for action in actions]}")
    return actions


def set_export_scene_params(export_filepath):
    return bpy.ops.export_scene.fbx(
        filepath=export_filepath,
        use_selection=True,
        object_types={"MESH", "ARMATURE"},
        path_mode="COPY",
        check_existing=False,
        axis_forward='Z',
        axis_up='Y',
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_ALL',
        use_armature_deform_only=True,
        use_custom_props=False,
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=0.1,
        bake_anim_simplify_factor=0,
        embed_textures=True,
    )
    

def remove_nla_strips():
    # Remove NLA strips that were exported

    # BELOW IS A PLACEHOLDER
    for track in bpy.context.object.animation_data.nla_tracks:
        for strip in track.strips:
            bpy.context.object.animation_data.nla_tracks.remove(track)
            
            break
    return {'FINISHED'}

def get_actions_in_collection():
    # Get all actions in the collection
    return bpy.data.actions


classes = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    #del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()



