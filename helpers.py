
import bpy
from bpy.types import Action
from bpy_extras import anim_utils

class Action_List_Helper:
    
    def __init__(self, obj):
        self.obj = obj


    def get_slot(self, index):

        if self.check_index(index): 
            action_list = self.get_action_list()
            return action_list[index]
        else:
            print("Failed to Get Slot")
            return None

    def get_active_slot(self):
        
        index = self.get_active_index()

        return self.get_slot(index)
   
    def get_action(self, index):

        slot = self.get_slot(index) 

        if slot is not None:
            return slot.action

    def get_active_action(self):

        slot = self.get_active_slot() 

        if slot is not None: 
            return slot.action
        # else:
        #     print("Slot not Found")


    def get_nla_tracks_from_list(self, action_list):
        """
        Get the NLA track(s) that correspond to the provided action list.
        """
        action_list = self.get_action_list()
        nla_tracks = self.obj.animation_data.nla_tracks
        corresponding_tracks = []

        # Find the NLA tracks that have strips using this action
        for track in nla_tracks:
            corresponding_tracks.append(track)
            return corresponding_tracks
    
    def get_action_list(self):
        """
        Fetch the action list from the object. This action list should contain slots that point to actual actions.
        """
        return getattr(self.obj, 'action_list', None)  # Safely access action_list attribute

    def collect_action_list(self):
        """
        Collect all actions from the object's action list and return them.
        """
        collected_actions = []  # List to store the collected actions
        action_list = self.get_action_list()

        if action_list is None:
            print(f"Failed to get Action List from {self.obj.name}")
            return collected_actions

        print(f"Found {len(action_list)} slots in the action list.")

        # Iterate through the action slots and collect valid actions
        for index, slot in enumerate(action_list):
            if hasattr(slot, 'action') and slot.action:
                collected_actions.append(slot.action)
                print(f"Action collected from slot {index}: {slot.action.name}")
            else:
                print(f"No valid action found in slot {index}")

        print(f"Action_List_Helper: Collected Actions: {[action.name for action in collected_actions]}")
        return collected_actions
    
    def get_total_actions(self):
        return len(self.get_action_list())
    
    def get_active_index(self):
        return self.obj.action_list_index

    def get_first_index(self):
        return 0

    def get_last_index(self):        
        amount = self.get_total_actions()
        last_index = amount - 1
        return last_index 
    
    def check_index(self, index):

        if index >= 0:
            if self.get_total_actions() > index:
                return True
            else:
                print("Index Out of Bound")
        else:
            print("Index Is Lower than 0")
              
        return False

    def get_animation_data(self):
        """
        Returns the animation data for the object. If it doesn't exist, it creates the animation data.
        """        
    # Directly check if the object has animation data, if not create it
        return self.obj.animation_data or self.obj.animation_data_create()
    
    def get_actual_animation_data(self):
        animation_data = self.get_animation_data()
        if animation_data is None:
            print("Failed to Get Animation Data")
        return animation_data

    def get_actual_action(self):
        animation_data = self.get_actual_animation_data()
        if animation_data is not None:
            return animation_data.action    

    def set_actual_action(self, action):
        animation_data = self.get_actual_animation_data()
        if animation_data is not None:
            animation_data.action = action
    


    def clear_all_nla_tracks(self):
        """
        Clears all NLA tracks from the given object's animation data.
        """
        # Get the animation data, create it if it doesn't exist
        animation_data = bpy.context.object.animation_data or bpy.context.object.animation_data_create()
        obj = bpy.context.object
        # Clear NLA tracks if they exist
        if animation_data.nla_tracks:
            while len(animation_data.nla_tracks) > 0:
                animation_data.nla_tracks.remove(animation_data.nla_tracks[0])
                print("Cleared NLA Track")

            # Update the view layer to reflect changes
            bpy.context.view_layer.update()
            print(f"All NLA tracks cleared for {obj.name}.")
        else:
            print(f"{self.obj.name} has no NLA tracks to clear.")

    def collect_actions_from_nla(self):

        animation_data = self.get_actual_animation_data()

        actions = []

        for track in animation_data.nla_tracks:
            for strip in track.strips:
                actions.append(strip.action)

        return actions

    def push_to_nla(self, index):
            animation_data = self.get_actual_animation_data()
            action = self.get_action(index)
            if animation_data:
                track = animation_data.nla_tracks.new()
                strip = track.strips.new(action.name, 0, action)
                track.name = strip.name
                return strip
            else:
                print("Failed to get Animation Data")

    def push_all_to_nla(self, selected_only=False, preclear="NONE"):
        strips = []
        action_list = self.get_action_list()
        nla_actions = self.collect_actions_from_nla()
        skipped = []

        if preclear == "ALL":
            self.clear_all_nla_tracks() 

        for index, slot in enumerate(action_list): 
            check = True
            if selected_only:
                if slot.select:
                    check = True
                else:
                    check = False

            if check:
                second_check = True 
                if preclear == "PUSH_IF_NON_EXIST":
                    if slot.action in nla_actions:
                        second_check = False
                if second_check: 
                    strip = self.push_to_nla(index)
                else:
                    skipped.append(slot.action)
        return skipped