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

ti.init(arch=ti.gpu, default_fp=ti.f32)

def get_omega_at_level(omega, target_level):
    if target_level <= 0:
        return omega
    
    prev_omega = get_omega_at_level(omega, target_level - 1) # recursive call to find omega at upper level
    
    return 1.0 / (2.0 / prev_omega - 0.5)


nd0 = (361, 121, 121) # number of nodes@level 0
nd1 = (240, 160, 160) # l1
nd2 = (300, 220, 220) # l2
#nd3 = (400, 320, 320) # l3
offset1 = ( 30, 21, 21) # offset of level 1 grid to level 0
offset2 = ( 30, 25, 25) # offset of level 2 grid to level 1
#offset3 = ( 40, 31, 31) # offset of level 2 grid to level 2

radius = 15. # cylinder radius
obstacle = NestedObstacleManager(center_list=[75., 60.5, 60.5], radius=radius, nd=nd0)

u = 0.1
Re = 100000.0
nu = u*nd0[0]/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d3q27_Cumulant_kernel import ModelConfig
config = ModelConfig(mode="push") # "push" with bounce-back must be used for nested grid

bc_manager = BounceBackManager(nd0, [0, 1, 2, 2, 2, 2], [ [u, 0], [0,0], [0,0], [0,0], [0,0], [0,0] ]) # bounce-back scheme must be used for "push" scheme in collision-streaming kernel

lbm0 = lbm_skelton( nd0, config, get_omega_at_level(omega, 0) )
lbm1 = lbm_skelton( nd1, config, get_omega_at_level(omega, 1) )
lbm2 = lbm_skelton( nd2, config, get_omega_at_level(omega, 2) )
#lbm3 = lbm_skelton( nd3, config, get_omega_at_level(omega, 3) )

tree = GridManager(lbm0, bc_manager, config)                        # plant lbm0 as root
idx1 = tree.push(level=1, root_idx=0,    grid=lbm1, offset=offset1) # blanch 1 from 0
idx2 = tree.push(level=2, root_idx=idx1, grid=lbm2, offset=offset2) # blanch 2 from 1
#idx3 = tree.push(level=3, root_idx=idx2, grid=lbm3, offset=offset3) # blanch 3 from 2

obstacle.apply_to_mask(tree) # mask all levels

print(export_tree_info(tree)) # info will be sent to "tree_info.txt"

step, step_end = 0, 10000 # |--- run your simulation ---> #
while step < step_end:
    tree.run() # recursive run
    step += 1
    if step % 100 == 0:
        print(f"current step {step}")

save_vtk(tree, step, f"./output/nested3d") # read pvd file to import multi-grids in Paraview
