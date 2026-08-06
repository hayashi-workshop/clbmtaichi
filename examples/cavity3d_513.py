# cavity3d.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bc_kernel import BoundaryManager

from lb_utils.lbm_utils import save_vtk

ti.init(arch=ti.gpu, default_fp=ti.f32)

nd = (513, 513, 513)
u, Re = 0.1, 10000.0
nu = u*nd[0]/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d3q27_Cumulant_kernel import ModelConfig # <- import 3D collision kernel -|
lbm = lbm_skelton(nd, config := ModelConfig(), omega)

bc_manager = BoundaryManager(nd, [2, 2, 2, 2, 2, 2], [ [0,0,0], [0,0,0], [0,0,0], [u,0,0], [0,0,0], [0,0,0] ])

step, step_end = 0, 500000 # |--- run your simulation ---> #
while step < step_end:#renderer.window.running and step < step_end:
    f_pre, f_post = lbm.swap(step) # ! pseudo swap ! # this is much faster than value copy
    config.col_stream_core(lbm, f_pre, f_post)
    bc_manager.apply_bc(lbm, config, f_pre, f_post)
    step += 1

    if step % 10000 == 0:
        print(f"current step {step}")

save_vtk(lbm, step, f"output/cavity3d_513")
