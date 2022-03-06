import bpy
import bmesh
from .walkers import bmesh_edge_loop_walker


class MESH_OT_EdgeLoopSelect(bpy.types.Operator):
    bl_idname = "mesh.edgeloop_select"
    bl_label = "Select an edge loop"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description  = 'Select an edge loop. Select a single edge or two adjacent edges to control direction'

    stop_at_seams: bpy.props.BoolProperty(
    name='Seams',
    description='Limit the selection to edges marked as seams',
    default=False,
    )

    mark_seams: bpy.props.BoolProperty(
    name='Seams',
    description='Mark the selected edges as seams',
    default=False,
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        row = col.row()
        label = row.label(text="Limit")
        col.prop(self, "stop_at_seams")

        row2 = col.row()
        label = row2.label(text="Mark Selection")
        col.prop(self, "mark_seams")
        

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH')


    def execute(self, context):
        return self.select_edgeloop(context)

    def select_edgeloop(self, context):

        mesh = context.active_object.data
        bm = bmesh.from_edit_mesh(mesh)

        selected_edges = bm.select_history

        if len(selected_edges) == 2:
            first_edge = selected_edges[0]
            start_edge = selected_edges[1]

            reverse_loop_direction = False

            for edge in bmesh_edge_loop_walker(start_edge, stop_at_seams=self.stop_at_seams, skip_rewind=True, reverse=False):
                if edge != first_edge:
                    edge.select = True
                    if self.mark_seams:
                        edge.seam = True
                else:
                    reverse_loop_direction = True
                    break

                    
            if reverse_loop_direction:
                start_edge = selected_edges[1]
                for edge in bmesh_edge_loop_walker(start_edge, stop_at_seams=self.stop_at_seams, skip_rewind=True, reverse=True):
                    edge.select = True

                    if self.mark_seams:
                        edge.seam = True
            
            # Mark the first selected edge as a seam
            if self.mark_seams:
                first_edge.seam = True
        else:
            start_edge = selected_edges[0]
            for edge in bmesh_edge_loop_walker(start_edge, stop_at_seams=self.stop_at_seams):
                edge.select = True

                if self.mark_seams:
                    edge.seam = True

        bmesh.update_edit_mesh(mesh, destructive=False)
        return {'FINISHED'}