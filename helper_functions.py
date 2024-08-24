import bpy


class Action_List_Helper:
    
    def __init__(self, obj):
        self.obj = obj
        
    def get_action_list(self):
        return self.obj.action_list    

    def collect_action_list(self):

        collected_actions = [] 

        action_list = self.get_action_list()  

        if action_list is not None:
            for slot in action_list:

                if slot.action:
                    collected_actions.append(slot.action)
        else:
            print("Failed to get Action List")
                
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

    def get_animation_data(self):
        animation_data = self.obj.animation_data
        if animation_data:
            return animation_data
        else:
            animation_data = self.obj.animation_data_create()
            return animation_data
    
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




    ###### NLA ######
    
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

    def clear_all_nla_tracks(self):
        animation_data = self.get_actual_animation_data()
        if animation_data:
            while len(animation_data.nla_tracks) > 0:
                animation_data.nla_tracks.remove(animation_data.nla_tracks[0])

    def collect_actions_from_nla(self):
        animation_data = self.get_actual_animation_data()
        actions = []
        for track in animation_data.nla_tracks:
            for strip in track.strips:
                actions.append(strip.action)
        return actions

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
    

#def register():
#    bpy.utils.register_class(Action_List_Helper)
#
#def unregister():
#    bpy.utils.unregister_class(Action_List_Helper)

#if __name__ == "__main__":
#    register()