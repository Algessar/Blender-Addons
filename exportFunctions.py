from .helpers import Action_List_Helper
from concurrent.futures import ThreadPoolExecutor
import bpy



def get_actions_from_ui_list(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.collect_action_list()

def get_actions_from_object(obj):
    action_list_helper = Action_List_Helper(obj)
    return action_list_helper.get_actual_action()



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

def clear_nla_tracks(obj, added_tracks=None):
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
        Action_List_Helper.clear_all_nla_tracks(self = obj)  # Clear all NLA tracks
        print(f"Removed all NLA tracks from {obj.name}.")


def push_actions_to_nla(obj, actions):
    added_tracks = []
    action_list_helper = Action_List_Helper(obj)
    
    for index, action in enumerate(actions):
        if not isinstance(action, bpy.types.Action):
            print(f"Error: Expected an Action type, but got {type(action)} at index {index}")
            continue

        print(f"Pushing action '{action.name}' to NLA track at index {index}")
        action_list_helper.set_actual_action(action)  # Set the current action
        strip = action_list_helper.push_to_nla(index)  # Push to NLA using index
        
        if strip:
            added_tracks.append(strip)
            print(f"Action '{action.name}' successfully pushed as NLA strip {strip.name}")
        else:
            print(f"Failed to push action '{action.name}' to NLA")

    return added_tracks

def push_actions_to_nla_parallel(obj, actions):
    added_tracks = []
    nla_tracks = obj.animation_data.nla_tracks  # Cache nla_tracks

    def process_action(action):
        if not isinstance(action, bpy.types.Action):
            print(f"Error: Expected an Action type, but got {type(action)}")
            return None

        # Create a new instance of Action_List_Helper for each thread to avoid conflicts
        action_list_helper = Action_List_Helper(obj)
        action_list_helper.set_actual_action(action)  # Set the current action
        
        return action_list_helper.push_to_nla(action)  # Push to NLA using action

    # Use ThreadPoolExecutor to process actions in parallel, isolated by threads
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_action, actions)

    for strip in results:
        if strip:
            added_tracks.append(strip)

    print(f"Pushed actions to NLA: {[action.name for action in actions]}") 
    return added_tracks


def prep_export_push_NLA(action_list):
    obj = bpy.context.active_object
    if obj is None:
        print("No active object selected.")
        return
    
    if not action_list:
        print("ExportFunctions: No actions found for the selected object.")
        return

    push_actions_to_nla_parallel(obj, action_list)
    mute_nla_tracks()
    print(f"Exported actions: {[action.name for action in action_list]}")
    return action_list


def export_unity(export_filepath, add_leaf_bones=False, ):



    return bpy.ops.export_scene.fbx(
        #Scene
        filepath=export_filepath,
        use_selection=True,
        object_types={"MESH", "ARMATURE", 'EMPTY'},
        path_mode="COPY",
        check_existing=False,
        
        embed_textures=True,

        #Geometry
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='Z',
        axis_up='Y',
        use_subsurf=False,

        #Normals
        mesh_smooth_type='FACE',

        #Armature
        use_armature_deform_only=True,
        use_custom_props=False,
        add_leaf_bones=False,

        #Animation
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=0.1,
        bake_anim_simplify_factor=0,
    )

def export_unreal(export_filepath):
    return bpy.ops.export_scene.fbx(
        #Scene
        filepath=export_filepath,
        use_selection=True,
        object_types={"MESH", "ARMATURE"},
        path_mode="COPY",
        check_existing=False,

        #Geometry
        global_scale=1.0,
        axis_forward='X',
        axis_up='Z',
        apply_scale_options='FBX_SCALE_ALL',

        #Normals
        mesh_smooth_type='FACE',
        
        #Armature
        use_armature_deform_only=True,
        use_custom_props=False,
        add_leaf_bones=False,

        #Animation
        bake_anim=True,
        bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=True,
        bake_anim_use_all_actions=False,
        bake_anim_force_startend_keying=True,
        bake_anim_step=0.1,
        bake_anim_simplify_factor=0,
        embed_textures=True,
    )

def prep_UE_export():
    # Exporting armatures to UE requires renaming the root bone, 
    # so it handles root motion correctly.
    return


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


def filter_actions_to_export(obj):
    action_list_helper = Action_List_Helper(obj)
    action_list = action_list_helper.collect_action_list()

    # Collect starred actions
    starred_actions = [action for action in action_list if is_starred(action)]
    # If no actions are starred, return all actions
    if not starred_actions:
        return action_list
    return starred_actions

def is_starred(action):
    if not hasattr(action, 'is_starred'):
        action["is_starred"] = False
        print(f"Action {action.name} has no 'is_starred' attribute. Defaulting to False.")
    return getattr(action, 'is_starred', False)

## NEW 2024-10-20


def get_starred_actions():
    obj = bpy.context.active_object
    action_list_helper = Action_List_Helper(obj)
    action_list = action_list_helper.collect_action_list()

    starred_actions = [action for action in action_list if is_starred(action)]
    # iterate names of actions
    # if action is starred, add to list
    for action in action_list:
        if is_starred(action):
            print(f"Starred actions: {action.name}")
    return starred_actions

                