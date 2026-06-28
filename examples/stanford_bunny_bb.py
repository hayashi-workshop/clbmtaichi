# stanford_bunny.py

# this class uses trimesh to handle mesh data
# install the following if not yet inplemented
#pip install 'trimesh[easy]'
#pip install networkx
import trimesh

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.render import FluidRenderer

from examples.obstacle_stanford_bunny import ObstacleManager

from lb_utils.lbm_utils import save_vtk
from lb_utils.lbm_utils import PerformanceMonitor

ti.init(arch=ti.gpu, default_fp=ti.f32)

nd = (241, 121, 121)
length_scale = 60    # size of bunny 
offset = (50, 0, 30) # offset (measured for lower-left corner)

bunny = ObstacleManager(nd=nd, offset=offset, length_scale=length_scale)

u, Re = 0.1, 40000.0 # object-size-based Reynolds number
nu = u*length_scale/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d3q27_Cumulant_kernel import ModelConfig
lbm = lbm_skelton(nd, config := ModelConfig(mode="push"), omega)

bc_manager = BounceBackManager(nd, [0, 1, 2, 2, 2, 2], [ [u,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0] ])

bunny.apply_to_mask(lbm)

renderer = FluidRenderer(lbm, vmin=-u*0.5, vmax=u*0.5) 

mlups_monitor = PerformanceMonitor(nd)

step, step_end = 0, 20000 # |--- run your simulation ---> #
while renderer.window.running and step < step_end:
    for _ in range(10):
        f_pre, f_post = lbm.swap(step)
        config.col_stream_core(lbm, f_pre, f_post)
        bc_manager.apply_bc(lbm, config, f_pre, f_post, bunny)
        step += 1

    renderer.render(lbm)
    mlups_monitor.update(step)

ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"img/stanford_bunny_bb.png")
save_vtk(lbm, step, f"output/stanford_bunny_bb")
