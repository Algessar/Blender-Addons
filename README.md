# Blender Addons
 
Unity Exporter:

This part of the addon has basic functionality for keeping track of your animation Actions and clean export.

You can use the Export Rig button to:

Export the armature and all parented and visible objects.
- Only the Actions set in the Export UI list will be exported.
- Delete NLA tracks that were pushed on export.
- Delete ALL NLA tracks currently on the object.


Rigify Game Rig Converter:

A generic converter for Rigify, to transform any generated rig into a working game rig.

The script is fully agnostic to which type of metarig is used. 

Just select your generated rig and make sure the metarig is visible in the scene (it is used for the conversion!).

You can decide if you want to have 4 limb bones or 2 with the split bones bool.

There is also a bool check for deleting a separate root bone. It is there for if you're using Rigify feature sets like the Experimental rigs from Alexander Gavrilov.


TODO:
- More error handling is likely needed.

- Refactor to not be reliant on the metarig

- 




// Elric Steelsword
