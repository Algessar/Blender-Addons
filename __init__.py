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
    "description": "Game rig conversion for Rigify, UI Exporting for Unity and various tools. "
    "To Export an armature, add your actions to the list, then click Export Rig.",
}

import sys
import os
import bpy
#path_with_forward_slashes = os.path.replace("\\", "/")
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "D:/Blender_Projects/Addons/Scripting/ElRig/Blender-Addons"))
if module_path not in sys.path:
    sys.path.append(module_path)


from .export_functions import register as register_export_actions, unregister as unregister_export_actions
from .ExportUI import register as register_export_ui, unregister as unregister_export_ui
from .convert_rig import register as register_convert_rig, unregister as unregister_convert_rig
from .helper_functions import Action_List_Helper as Action_List_Helper
from .auto_FK_IK_switch import register as register_auto_FK_IK_switch, unregister as unregister_auto_FK_IK_switch
#from .simple_auto_switch import register as register_simple_auto_switch, unregister as unregister_simple_auto_switch

### REGISTER ###

def register():
    register_export_actions()
    register_export_ui()
    register_convert_rig()
    register_auto_FK_IK_switch()
    #bpy.utils.register_class(Action_List_Helper)
    #register_simple_auto_switch()


def unregister():
    unregister_export_actions()
    unregister_export_ui()
    unregister_convert_rig()
    unregister_auto_FK_IK_switch()
    #bpy.utils.unregister_class(Action_List_Helper)
    #unregister_simple_auto_switch()
    

    
   