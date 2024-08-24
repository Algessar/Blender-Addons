import bpy
from bpy.types import Panel, Operator
from bpy.props import BoolProperty, StringProperty, PointerProperty, FloatProperty, CollectionProperty
#if "rigify" in bpy.context.preferences.addons:
#    from rigify import rig_ui


# thigh_parent.L/R contains the prop IK/FK (float). This is the driver for the IK/FK switch.
# I can find that bone and prop, and then drive it directly with my auto switch.

#bpy.ops.pose.rigify_generic_snap_04vtcac80eac9c66(
#    input_bones="[\"thigh_ik.L\", \"MCH-shin_ik.L\", \"MCH-thigh_ik_target.L\", \"toe_ik.L\"]", 
#    output_bones="[\"thigh_fk.L\", \"shin_fk.L\", \"foot_fk.L\", \"toe_fk.L\"]", 
#    ctrl_bones="[\"thigh_ik.L\", \"thigh_ik_target.L\", \"foot_ik.L\", \"toe_ik.L\", \"foot_heel_ik.L\", \"foot_spin_ik.L\"]")
### PROPS AND HELPERS ###

# Property group for string properties
class StringProps(bpy.types.PropertyGroup):
    FK_bone_name: StringProperty(
        name="Target FK Bone",
        default="FK"
    )#type: ignore
    IK_bone_name: StringProperty(
        name="Target IK Bone",
        default="IK"
    )#type: ignore
    property_name: StringProperty(
        name="Property Name",
        default="IK_FK"
    )#type: ignore
    prop_bone_name: StringProperty(
        name="Name of prop bone",
        default="thigh_parent.L"
    )#type: ignore

# Property group for boolean properties
class BoolProps(bpy.types.PropertyGroup):
    autoswitch_bool: BoolProperty(
        name="Auto Switch IK/FK",
        default=False
    )#type: ignore
    enable_autoswitch: BoolProperty(
        name="Enable Auto Switch",
        default=False,
        update=lambda self, context: context.scene.update_ik_fk_switch()

    )#type: ignore

class FloatProps(bpy.types.PropertyGroup):
    float_prop: FloatProperty(
        name="Float Property",
        default=0,
        min=0,
        max=1,
    )#type: ignore


### CLASSES ###
# UI Panel to display the properties
class VIEW3D_PT_Auto_IK_FK_switch(bpy.types.Panel):
    bl_label = "Auto FK/IK Switch (WIP)"
    bl_idname = "VIEW3D_PT_switch"
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'ElRig'

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Set names of the IK and FK control bones
        layout.prop(scene.prop_bone_name, "prop_bone_name")
        layout.separator()
        layout.prop(scene.FK_bone_name, "FK_bone_name")
        layout.prop(scene.IK_bone_name, "IK_bone_name")

        # Toggle for auto IK/FK switching
        layout.prop(scene.autoswitch_bool, "autoswitch_bool")
        bpy.context.view_layer.update()

        layout.prop(scene.float_prop, "float_prop", slider=True)
        layout.prop(scene.property_name, "property_name")

        layout.operator("view3d.simple_switch")

class VIEW3D_OT_SimpleSwitch(bpy.types.Operator):
    bl_idname = "view3d.simple_switch"
    bl_label = "Simple Switch"
    bl_description = "Simple Switch"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        armature = context.object       

        scene.autoswitch_bool.autoswitch_bool = not scene.autoswitch_bool.autoswitch_bool

        target_value = scene.autoswitch_bool.autoswitch_bool
        #switch_fk_ik(context, context.scene.FK_bone_name.FK_bone_name)
        #set_custom_prop(armature, bone_name, bone_prop, target_value)

        #rigify test
        prop_bone_name = scene.prop_bone_name.prop_bone_name
        prop = "IK_FK"
        set_prop_float_value(armature, prop_bone_name, prop, target_value)
        
        bpy.context.view_layer.update()
        print(f"")
        #print("Simple Switch")
        return {'FINISHED'}
    
def set_prop_float_value(armature, bone_name, prop, target_value):
    scene = bpy.context.scene
    #float_value = scene.float_prop.float_prop
    prop = scene.property_name.property_name
    if target_value: #== True and float_value == 1.0:
        set_custom_prop(armature, bone_name, prop, 1)
    else:
        set_custom_prop(armature, bone_name, prop, 0.0)
    

def get_custom_prop(armature, bone_name, prop):
    #Get the value of a custom property
    bone = armature.pose.bones[bone_name]
    return bone.get(prop)

def set_custom_prop(armature, bone_name, prop, value):
    #Assign the value of a custom property
    from rna_prop_ui import rna_idprop_ui_prop_update
    bone = armature.pose.bones[bone_name]
    bone[prop] = value
    rna_idprop_ui_prop_update(bone, prop)

#########################################################
    
def switch_based_on_selection(context):
    # when selecting a bone with the name of FK_bone_name or IK_bone_name (string props)
    # the switch will be toggled.
    # 
    #get selected bone
    #check if selected bone is FK or IK bone
    #toggle switch
    #set custom prop

    scene = context.scene
    armature = context.object
    selected_bone = context.active_pose_bone
    enable_switch = scene.autoswitch_bool.autoswitch_bool

    if not selected_bone:
        return
    FK_bones_list = ["shin_fk.L", "thigh_fk.L", "foot_fk.L", "toe_fk.L"]

    selected_bone_name = selected_bone.name
    FK_bone_name = scene.FK_bone_name.FK_bone_name
    IK_bone_name = scene.IK_bone_name.IK_bone_name

    prop_bone_name = scene.prop_bone_name.prop_bone_name
    prop_name = scene.property_name.property_name

    if selected_bone_name in FK_bones_list and enable_switch:
        set_custom_prop(armature,prop_bone_name, prop_name, 1.0)
    if selected_bone_name == IK_bone_name and enable_switch:
        set_custom_prop(armature,prop_bone_name, prop_name, 0.0)    
    
   


def selection_handler(scene, depsgraph):
    context = bpy.context
    if context.object and context.object.type == 'ARMATURE':
        switch_based_on_selection(context)

def switch_fk_ik(context, bone_name):
    #switch the IK/FK prop of the bone
    scene = context.scene
    armature = context.object
    bone = armature.pose.bones[bone_name]
    prop = scene.property_name.property_name
    current_value = bone.get(prop)
    if current_value == 1.0:
        bone[prop] = 0.0
    else:
        bone[prop] = 1.0
    bpy.context.view_layer.update()

# List of classes to register/unregister
classes = [
        StringProps, 
        BoolProps,
        FloatProps, 
        VIEW3D_PT_Auto_IK_FK_switch,
        VIEW3D_OT_SimpleSwitch
        ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.app.handlers.depsgraph_update_post.append(selection_handler)
    
    # Register the property groups with the Scene
    bpy.types.Scene.autoswitch_bool = PointerProperty(type=BoolProps)
    bpy.types.Scene.enable_autoswitch = PointerProperty(type=BoolProps)
    bpy.types.Scene.prop_bone_name = PointerProperty(type=StringProps)
    bpy.types.Scene.FK_bone_name = PointerProperty(type=StringProps)
    bpy.types.Scene.IK_bone_name = PointerProperty(type=StringProps)
    bpy.types.Scene.property_name = PointerProperty(type=StringProps)
    bpy.types.Scene.float_prop = PointerProperty(type=FloatProps)



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


    bpy.app.handlers.depsgraph_update_post.remove(selection_handler)
    # Unregister properties from the Scene
    del bpy.types.Scene.autoswitch_bool
    del bpy.types.Scene.enable_autoswitch
    del bpy.types.Scene.FK_bone_name
    del bpy.types.Scene.IK_bone_name
    del bpy.types.Scene.float_prop

if __name__ == "__main__":
    register()
    #bpy.ops.elrig.auto_fk_ik_switch('INVOKE_DEFAULT')
    
