import bpy
import bmesh


class RetopoCheckerPanel(bpy.types.Panel):
    bl_label = "Retopology Checker"
    bl_idname = "RETOPO_CHECKER_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Retopology'
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator("object.object_ot_loopcheck", text="Check and Visualize")
        


class OBJECT_OT_LoopCheck(bpy.types.Operator):
    bl_idname = "object.object_ot_loopcheck"
    bl_label = "Check and Visualize"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        check_loop_evenness()
        enable_vertex_group_weights_overlay()
        return {'FINISHED'}

def check_loop_evenness():
    obj = bpy.context.object
    
    if obj is None or obj.type != 'MESH':
        print("Error: Please select a mesh object.")
        return
    
    # Ensure the object is in edit mode
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.mode_set(mode='EDIT')

    # Get the bmesh of the active object
    mesh = bmesh.from_edit_mesh(obj.data)
    
    # Find the selected edges
    selected_edges = [e for e in mesh.edges if e.select]
    if not selected_edges:
        print("Error: No edges selected.")
        return
    
    # Get edge loops from selected edges
    loops = []
    for edge in selected_edges:
        loop = edge.calc_loop()
        if loop:
            loops.append(loop)

    if not loops:
        print("Error: No edge loops found.")
        return

    # Iterate through loops, calculate vertex count, and assign weights
    for loop in loops:
        num_vertices = len(loop)
        print(f"Loop has {num_vertices} vertices.")
        
        # Create a new vertex group for the object
        vertex_group = obj.vertex_groups.new(name="Loop Evenness Weights")
        
        # Assign weights based on whether the number of vertices is even or odd
        for vert in loop:
            weight = 1.0 if num_vertices % 2 == 0 else 0.5
            vertex_group.add([vert.index], weight, 'REPLACE')
        
        # Update the mesh
        bmesh.update_edit_mesh(obj.data)

def enable_vertex_group_weights_overlay():
    """Enable the Vertex Group Weights overlay in edit mode."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.overlay.show_vertex_group_weights = True
                    print("Enabled Vertex Group Weights overlay.")
                    return

