# nested_helper.py

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                                                             #
#                      Utility functions                      #
#                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import taichi as ti
import taichi.math as tm 

import os
import io
import numpy as np
from pyevtk.hl import gridToVTK


def export_tree_info(tree, output_dir=".", filename=None):
    buffer = io.StringIO()
    
    if filename == None:
        filename = "tree_info.txt"

    buffer.write(f"- * - NESTED GRIDS - * -\n\n")
    buffer.write(f"[tree (level: [grid indices])] {tree.tree}\n\n")
    buffer.write(f"max level {tree.max_level}\n")
    buffer.write(f"number of grids {tree.num_of_grids}\n\n")
    buffer.write(f"[models]\n")
    buffer.write(f"{tree.bc_manager}\n")
    buffer.write(f"{tree.config}\n\n")

    buffer.write(f"[grids]\n")
    for level in range(tree.max_level+1):
        buffer.write(f"grids in tree level {level} ---> {tree.tree[level]}\n")
        buffer.write(f"omega@level {level} = {(tree.grid[tree.tree[level][0]].omega[1]):06f}\n")
        for idx in tree.tree[level]:
            buffer.write(f"grid index {idx}\n")
            buffer.write(f"root index {tree.root_idx[idx]}\n")
            buffer.write(f"leaf index {tree.leaf_idx[idx]}\n")
            buffer.write(f"num of nodes (nd) {tree.grid[idx].nd}\n")
            buffer.write(f"offset to root {tree.offset[idx]}\n")
            buffer.write(f"offset to global origin {tree.offset_glb[idx]}\n\n")

    def indent(depth):
        base = "    "
        idt = ""
        for i in range(depth):
            idt = idt + base
        return idt
    idt = [indent(i) for i in range(20)]

    def pseudo_run(level=0, stepEnd=1):
        for step in range(stepEnd):
            for idx in tree.tree[level]:
                buffer.write(f"{idt[level]}run lbm on grid {idx} @level {level}\n")
            
            if level < tree.max_level:
                buffer.write(f"{idt[level]}recursive run -> called grids@level {level+1} from root grid@level {level}\n")
                pseudo_run(level=level+1, stepEnd=2)

                for idx in tree.tree[level]:
                    if len( tree.leaf_idx[idx] ) > 0:
                        buffer.write(f"{idt[level]}grid {idx} @level {level} invokes Coarse <-> Fine interpolation with leaves @level {level+1}; leaves {tree.leaf_idx[idx]}\n\n")

    buffer.write(f"[recursive run]\n\n")
    pseudo_run()

    all_content = buffer.getvalue()
    with open(output_dir + "/" + filename, "w", encoding="utf-8") as f:
        f.write(all_content)

    buffer.close()

    return all_content


@ti.kernel # GGUI realtime rendering
def paint(renderer: ti.template(), lbm:ti.template(), level: ti.i32, nx: ti.i32, ny: ti.i32, x0: ti.f32, y0: ti.f32):
    # fill img_buffer
    # start from level 0, img_buffer pix overwritten by leaves
    # only "velocity" mode is currently supported

    shift = 3 # remove halo at leaves
    if level == 0:
        shift = 0 # draw all pix at level 0
    for i, j in ti.ndrange( (shift, nx-shift), (shift, ny-shift) ): # loop on leaf grid
        vmag = lbm.vel[i,j].norm()

        coords_glb = ti.Vector([i*1., j*1.])
        coords = ti.Vector([i*1., j*1.])
        if level > 0:
            coords_glb = (coords - 0.5) / (2**level) + ti.Vector([x0, y0]) # pick global coordinates
        
        Imap = ti.Vector( [ ti.cast(coords_glb[0], ti.i32), ti.cast(coords_glb[1], ti.i32) ] ) # buffer index to be filled

        renderer.img_buffer[Imap] = renderer._apply_colormap_velocity(vmag)

        if lbm.mask[i,j] > 0:
            renderer.img_buffer[Imap] = tm.vec3(renderer.obstacle_color)


@ti.kernel
def draw_line(img_buffer: ti.template(), x1: ti.f32, y1: ti.f32, x2: ti.f32, y2: ti.f32, color: ti.types.vector(3, ti.f32)):
    x1_i = ti.cast(x1, ti.i32)
    x2_i = ti.cast(x2, ti.i32)
    y1_i = ti.cast(y1, ti.i32)
    y2_i = ti.cast(y2, ti.i32)

    dx = abs(x2_i - x1_i)
    dy = abs(y2_i - y1_i)
    steps = max(dx, dy)
    for i in range(dx):
        img_buffer[x1_i + i, y1_i] = color
        img_buffer[x1_i + i, y2_i] = color

    for j in range(dy):
        img_buffer[x1_i, y1_i + j] = color
        img_buffer[x2_i, y1_i + j] = color


def render(tree, renderer, lbm, box_drawing=True):
    renderer.obstacle_color = 1.

    # fill img_buffer
    # start from level 0, img_buffer pix overwritten by leaves
    # only "velocity" mode is currently supported
    img = renderer.img_buffer
    for level in range(tree.max_level+1):
        for idx in tree.tree[level]:
            x0, y0 = tree.offset_glb[idx]
            nx, ny = tree.grid[idx].nd
            paint(renderer, tree.grid[idx], level, nx, ny, x0, y0 )

    # draw boxes 
    if box_drawing:
        for level in range(tree.max_level+1):
            for idx in tree.tree[level]:
                if idx > 0:
                    Org0 = tree.offset_glb[idx][0]
                    Org1 = tree.offset_glb[idx][1]
                    x1 = Org0
                    y1 = Org1
                    x2 = Org0 + tree.grid[idx].nd[0] / 2**(level)
                    y2 = Org1 + tree.grid[idx].nd[1] / 2**(level)

                    draw_line(renderer.img_buffer, x1, y1, x2, y2, ti.Vector([1.0, 1.0, 1.0]))

    renderer.canvas.set_image(renderer.img_buffer)
    renderer.window.show()


def render_single(renderer, lbm, mode=None):
    # single level GGUI rendering

    renderer.obstacle_color = 1.

    if mode:
        renderer.mode = mode

    if renderer.mode == "vorticity":
        renderer.color_map = renderer._apply_colormap_vorticity
        renderer._compute_vorticity(lbm)
        renderer._render_kernel_vorticity(lbm)
    else:
        renderer.color_map = renderer._apply_colormap_velocity
        renderer._render_kernel_velocity(lbm)

    renderer.canvas.set_image(renderer.img_buffer)
    renderer.window.show()



# - * - vtk file dump - * - #
# vtm binds grids
# pvd binds steps
def save_vtk(tree, step, root_dir=None):

    if root_dir == None:
        root_dir = "./output"

    files = []

    for level in range(tree.max_level+1):
        for idx in tree.tree[level]:
            output_dir = root_dir + "/" + str(step) + f"/level{level}idx{idx}"
            os.makedirs(output_dir, exist_ok=True)

            lbm = tree.grid[idx]
            u_np = lbm.vel.get_scalar_field(0).to_numpy()
            v_np = lbm.vel.get_scalar_field(1).to_numpy()
            x = np.arange(lbm.nx)
            y = np.arange(lbm.ny)
            if level > 0:
                x = x[3:-3]
                y = y[3:-3]
            x = (x - 0.5) / 2**level + tree.offset_glb[idx][0]
            y = (y - 0.5) / 2**level + tree.offset_glb[idx][1]

            if lbm.dim == 2:
                if level > 0:
                    u_np = u_np[3:-3, 3:-3].ravel(order='F') # remove halo
                    v_np = v_np[3:-3, 3:-3].ravel(order='F')

                w_np = np.zeros_like(u_np)
                z = np.zeros(1)
            else:
                w_np = lbm.vel.get_scalar_field(2).to_numpy()
                z = np.arange(lbm.nz)

                if level > 0:
                    u_np = u_np[3:-3, 3:-3, 3:-3].ravel(order='F') # remove halo
                    v_np = v_np[3:-3, 3:-3, 3:-3].ravel(order='F')
                    w_np = w_np[3:-3, 3:-3, 3:-3].ravel(order='F')
                    z = z[3:-3]

                z = (z - 0.5) / 2**level + tree.offset_glb[idx][2]

            filename = f"step_{step:06d}"
            filename_abs = output_dir + "/" + filename
            gridToVTK(
                filename_abs, 
                x, y, z, 
                pointData={"velocity": (u_np, v_np, w_np)}
            )

            files.append(filename_abs)

    vtm_dir = root_dir + '/vtm'
    os.makedirs(vtm_dir, exist_ok=True)
    vtm_file = vtm_dir + "/" + str(step) + '.vtm'
    with open(vtm_file, "w", encoding="utf-8") as f:
        f.write(f"<VTKFile type=\"vtkMultiBlockDataSet\" version=\"1.0\">\n")
        f.write(f"  <vtkMultiBlockDataSet>\n")
        for idx in range(len(files)):
            f.write(f"    <DataSet index=\"{idx}\" file=\"{files[idx].replace(root_dir, '..')}.vtr\"/>\n")
        f.write(f"  </vtkMultiBlockDataSet>\n")
        f.write(f"</VTKFile>\n")

    if tree.pvd == None:
        tree.pvd = {}

    tree.pvd[step] = f"./vtm/{step}.vtm"

    pvd_file = root_dir + "/nested.pvd"
    with open(pvd_file, "w", encoding="utf-8") as f:
        f.write(f"<VTKFile type=\"Collection\" version=\"0.1\">\n")
        f.write(f"  <Collection>\n")
        for step_vtm, name_vtm in zip(tree.pvd.keys(), tree.pvd.values()):
            f.write(f"    <DataSet timestep=\"{step_vtm}\" file=\"{name_vtm}\" />\n")
        f.write(f"  </Collection>\n")
        f.write(f"</VTKFile>\n")