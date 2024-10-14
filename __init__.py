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
    "version": (1, 0, 3),
    "author": "Elric Steelsword",
    "location": "View3D tools panel (N-panel) -> ElRig",
    "description": "Game rig conversion for Rigify, UI Exporting for Unity and various tools. "
    "To Export an armature, add your actions to the list, then click Export Rig.",
}

import bpy
from bpy.props import IntProperty, CollectionProperty, PointerProperty, StringProperty, BoolProperty
from . import RigifyConverter, Exporter


classes = [RigifyConverter.OBJECT_OT_ConvertToGameRig, RigifyConverter.VIEW3D_PT_RigifyGameConverter,
            Exporter.VIEW_3D_UI_Elements,  Exporter.ACTION__UI_UL_actions, 
            Exporter.AddActionOperator, Exporter.RemoveActionOperator, Exporter.CUSTOM_OT_SetActiveAction,
            Exporter.Custom_OT_SetFilePath, Exporter.CUSTOM_OT_ExportRigOperator, 
            Exporter.ElRigActionItem, Exporter.ExportProperties,
            Exporter.CUSTOM_OT_MoveActionDown, Exporter.CUSTOM_OT_MoveActionUp,
            Exporter.CreateActionOperator, Exporter.DuplicateActionOperator,
            Exporter.FilterActionsOperator, 
            ]




def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    #Converter props
    
    bpy.types.Scene.split_bones_prop = BoolProperty(
            name="Split Bones",
            description="Enable splitting of bones",
            default=True
        )
    bpy.types.Scene.delete_root = BoolProperty(
            name="Delete Root",
            description="If you want to remove the separate root bone, check this box",
            default=False
        )
    
    #Exporter props
    bpy.types.Object.elrig_active_action_index = IntProperty()
    bpy.types.Object.action_list = CollectionProperty(type=Exporter.ElRigActionItem)
    bpy.types.Scene.my_tool = PointerProperty(type=Exporter.ExportProperties)
    bpy.types.Scene.clear_nla_tracks = BoolProperty(
        name="Clear NLA Tracks",
        description="Clear NLA tracks after export. If neither is selected, the NLA tracks will be kept",
        default=True
    )
    bpy.types.Scene.clear_all_nla_tracks = BoolProperty(
        name="Clear All NLA Tracks",
        description="Clear all NLA tracks after export. If neither is selected, the NLA tracks will be kept",
        default=False
    )

    bpy.types.Action.is_starred = bpy.props.BoolProperty(name="Starred", default=False)

    

    

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    #Converter props
    del bpy.types.Scene.split_bones_prop
    del bpy.types.Scene.delete_root

    #Exporter props
    del bpy.types.Object.elrig_active_action_index
    del bpy.types.Object.action_list
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.clear_nla_tracks
    del bpy.types.Scene.clear_all_nla_tracks

    del bpy.types.Action.is_starred



if __name__ == "__main__":
    register()
    Exporter.register


    
    
    