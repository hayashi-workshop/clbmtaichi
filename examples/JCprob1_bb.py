# JCprob1.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.render import FluidRenderer

#from lb_utils.obstacle import ObstacleManager
#from examples.obstacle_bump import ObstacleManager
from examples.obstacle_JCprob1 import ObstacleManager # <- import irregular shape

from lb_utils.lbm_utils import save_vtk
from lb_utils.lbm_utils import PerformanceMonitor

ti.init(arch=ti.gpu, default_fp=ti.f32)

nd = (1201, 201)
u, Re = 0.01, 10000.0
radius = 30.0
nu = u*2*radius/Re; omega = 1/(3*nu + 0.5)

center_list = [(nd[0]-1.0)/4, (nd[1]-1.0)/2]

from lb_solver.d2q9_Cumulant_drho_kernel import ModelConfig
lbm = lbm_skelton(nd, config := ModelConfig(mode="push"), omega)

bc_manager = BounceBackManager(nd, [0, 1, 2, 2], [ [u,0], [0,0], [0,0], [0,0] ])

obstacle = ObstacleManager(center_list=center_list, radius=radius, nd=nd)
obstacle.apply_to_mask(lbm)

renderer = FluidRenderer(lbm, vmin=0, vmax=u*5) # Taichi realtime rendering #
renderer.obstacle_color=1.0

mlups_monitor = PerformanceMonitor(nd)

step, step_end = 0, 200000 # |--- run your simulation ---> #
while renderer.window.running and step < step_end:
    for _ in range(100):
        f_pre, f_post = lbm.swap(step)
        config.col_stream_core(lbm, f_pre, f_post)
        bc_manager.apply_bc(lbm, config, f_pre, f_post, obstacle)
        step += 1

    renderer.render(lbm, "velocity")
    mlups_monitor.update(step)

ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"img/JCprob1_bb.png")