# nested.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.nested_grid import GridManager
from lb_utils.nested_utils.nested_obstacle import NestedObstacleManager
from lb_utils.nested_utils.nested_helper import render
from lb_utils.nested_utils.nested_helper import save_vtk
from lb_utils.nested_utils.nested_helper import export_tree_info

from lb_utils.render import FluidRenderer

ti.init(arch=ti.gpu, default_fp=ti.f32)

def get_omega_at_level(omega, target_level):
    if target_level <= 0:
        return omega
    
    prev_omega = get_omega_at_level(omega, target_level - 1) # recursive call to find omega at upper level
    
    return 1.0 / (2.0 / prev_omega - 0.5)


nd0 = (801, 201) # number of nodes@level 0
nd1 = (400, 280) # l1
nd2 = (440, 320) # l2
nd3 = (580, 480) # l3
offset1 = (100,  30) # offset of level 1 grid to level 0
offset2 = ( 30,  60) # offset of level 2 grid to level 1
offset3 = ( 50,  40) # offset of level 3 grid to level 2

radius = 20. # cylinder radius
obstacle = NestedObstacleManager(center_list=[160, 100.5], radius=radius, nd=nd0)

u = 0.1
Re = 50000.0
nu = u*2*radius/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d2q9_Cumulant_kernel import ModelConfig
config = ModelConfig(mode="push") # "push" with bounce-back must be used for nested grid

bc_manager = BounceBackManager(nd0, [0, 1, 2, 2], [ [u, 0], [0,0], [0,0], [0,0] ]) # bounce-back scheme must be used for "push" scheme in collision-streaming kernel

lbm0 = lbm_skelton( nd0, config, get_omega_at_level(omega, 0) )
lbm1 = lbm_skelton( nd1, config, get_omega_at_level(omega, 1) )
lbm2 = lbm_skelton( nd2, config, get_omega_at_level(omega, 2) )
lbm3 = lbm_skelton( nd3, config, get_omega_at_level(omega, 3) )

tree = GridManager(lbm0, bc_manager, config)                        # plant lbm0 as root
idx1 = tree.push(level=1, root_idx=0,    grid=lbm1, offset=offset1) # blanch 1 from 0
idx2 = tree.push(level=2, root_idx=idx1, grid=lbm2, offset=offset2) # blanch 2 from 1
idx3 = tree.push(level=3, root_idx=idx2, grid=lbm3, offset=offset3) # blanch 3 from 2

obstacle.apply_to_mask(tree) # mask all levels

renderer = FluidRenderer(lbm0, vmin=-u*2, vmax=u*2)

print(export_tree_info(tree)) # info will be sent to "tree_info.txt"

step, step_end = 0, 10000 # |--- run your simulation ---> #
while renderer.window.running and step < step_end:
    for _ in range(10):
        tree.run() # recursive run
        step += 1

        if step % 1000 == 0:
            save_vtk(tree, step, f"./output/nested") # read pvd file to import multi-grids in Paraview

    render(tree, renderer, lbm0)

ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"./img/nested.png")

