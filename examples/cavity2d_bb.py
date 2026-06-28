# cavity2d_bb.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.render import FluidRenderer

ti.init(arch=ti.gpu, default_fp=ti.f32)

nd = (401, 201)
u, Re = 0.1, 500000.0
nu = u*nd[0]/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d2q9_Cumulant_kernel import ModelConfig
lbm = lbm_skelton(nd, config := ModelConfig(mode="push"), omega)

bc_manager = BounceBackManager(nd, [2, 2, 2, 2], [ [0, 0], [0,0], [0,0], [u,0] ])

renderer = FluidRenderer(lbm, vmin=-u*0.1, vmax=u*0.1) # Taichi realtime rendering #

step, step_end = 0, 1000000 # |--- run your simulation ---> #
while renderer.window.running and step < step_end:
    for _ in range(500):
        f_pre, f_post = lbm.swap(step) # ! pseudo swap ! # this is much faster than value copy
        config.col_stream_core(lbm, f_pre, f_post)
        bc_manager.apply_bc(lbm, config, f_pre, f_post)
        step += 1
    renderer.render(lbm)

ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"img/cavity2d_bb.png")
