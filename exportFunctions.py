from .helpers import Action_List_Helper
from concurrent.futures import ThreadPoolExecutor
import bpy



def get_actions_from_ui_list(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.collect_action_list()

def get_actions_from_object(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.get_actual_action()

def push_actions_to_nla(obj, actions):
    added_tracks = []
    action_list_helper = Action_List_Helper(obj)
    for index, action in enumerate(actions):
        if not isinstance(action, bpy.types.Action):
            print(f"Error: Expected an Action type, but got {type(action)} at index {index}")
            continue

        action_list_helper.set_actual_action(action)  # Set the current action
        strip = action_list_helper.push_to_nla(index)  # Push to NLA using index
        if strip:
            added_tracks.append(strip)
    print(f"Pushed actions to NLA: {[action.name for action in actions]}")
    return added_tracks

def push_actions_to_nla_parallel(obj, actions):
    added_tracks = []
    action_list_helper = Action_List_Helper(obj)
    nla_tracks = obj.animation_data.nla_tracks  # Cache nla_tracks

    def process_action(index, action):
        if not isinstance(action, bpy.types.Action):
            print(f"Error: Expected an Action type, but got {type(action)} at index {index}")
            return None

        action_list_helper.set_actual_action(action)  # Set the current action
        return action_list_helper.push_to_nla(index)  # Push to NLA using index

    with ThreadPoolExecutor() as executor:
        results = executor.map(process_action, range(len(actions)), actions)

    for strip in results:
        if strip:
            added_tracks.append(strip)

    print(f"Pushed actions to NLA: {[action.name for action in actions]}")
    return added_tracks

def get_nla_tracks_by_action(obj, action):
    """
    Get the NLA track(s) that correspond to the provided action.
    """
    nla_tracks = obj.animation_data.nla_tracks
    corresponding_tracks = []

    # Find the NLA tracks that have strips using this action
    for track in nla_tracks:
        for strip in track.strips:
            if strip.action == action:
                corresponding_tracks.append(track)
                break  # Only need to match once per track
    
    return corresponding_tracks

def clear_added_nla_tracks(obj, added_tracks=None):
    """
    Deletes the specified NLA tracks (from added_tracks) or clears all tracks if added_tracks is None.
    """
    if not obj.animation_data or not obj.animation_data.nla_tracks:
        print(f"{obj.name} has no NLA tracks.")
        return

    nla_tracks = obj.animation_data.nla_tracks

    if added_tracks:
        # Convert actions in added_tracks to their corresponding NLA tracks
        for action in added_tracks:
            tracks_to_remove = get_nla_tracks_by_action(obj, action)
            for track in tracks_to_remove:
                if track.name in nla_tracks:
                    print(f"Removed NLA track: {track.name}")
                    nla_tracks.remove(track)
    else:
        nla_tracks.clear()  # Clear all NLA tracks
        print(f"Removed all NLA tracks from {obj.name}.")

def export_with_nla_cleanup(obj, export_filepath):

    actions = obj.animation_data.nla_tracks if obj.animation_data else []

    added_tracks = push_actions_to_nla(obj, actions)
    set_export_scene_params(export_filepath)
    clear_added_nla_tracks(obj, added_tracks)

    

def prep_export_push_NLA():
    obj = bpy.context.active_object
    if obj is None:
        print("No active object selected.")
        return

    actions = get_actions_from_ui_list(obj)
    if not actions:
        print("ExportFunctions: No actions found for the selected object.")
        return

    #push_actions_to_nla(obj, actions)
    push_actions_to_nla_parallel(obj, actions)
    mute_nla_tracks()
    print(f"Exported actions: {[action.name for action in actions]}")
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
    

def delete_nla_tracks(obj, track_list=None):
    """
    Deletes the specified NLA tracks from the object.
    If no track list is provided, it deletes all NLA tracks from the object.

    Args:
    - obj: The object from which to delete NLA tracks (bpy.types.Object).
    - track_list: Optional list of NLA tracks to delete (list of bpy.types.NlaTrack).
    """
    # Ensure the object has NLA tracks to work with
    if not hasattr(obj, "animation_data") or obj.animation_data is None or obj.animation_data.nla_tracks is None:
        print(f"Object {obj.name} has no NLA tracks.")
        return

    nla_tracks = obj.animation_data.nla_tracks
    
    # If no track list is provided, delete all tracks
    if track_list is None:
        print(f"Deleting all NLA tracks on {obj.name}...")
        track_list = nla_tracks[:]
    
    # Iterate through the list and remove each track
    for track in track_list:
        if track.name in nla_tracks:
            print(f"Deleted NLA track: {track.name}")
            nla_tracks.remove(track)
        else:
            print(f"NLA track {track.name} not found on {obj.name}.")

    # Clean up empty animation data
    if len(obj.animation_data.nla_tracks) == 0:
        obj.animation_data.use_nla = False
        print(f"All NLA tracks deleted from {obj.name}, disabling NLA.")

def get_actions_in_collection():
    # Get all actions in the collection
    return bpy.data.actions

def mute_nla_tracks():
    # any NLA track not in the action list should be muted
    obj = bpy.context.active_object
    action_list_helper = Action_List_Helper(obj)
    action_list = action_list_helper.collect_action_list()
    nla_tracks = obj.animation_data.nla_tracks
    for track in nla_tracks:
        if track.strips[0].action not in action_list:
            track.mute = True
        else:
            track.mute = False