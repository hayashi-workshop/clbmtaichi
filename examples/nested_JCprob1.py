# nested.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.nested_grid import GridManager
from examples.nested_obstacle_JCprob1 import NestedObstacleManager
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


nd0 = (1201, 201) # number of nodes@level 0
nd1 = ( 200, 200) # l1
nd2 = ( 200, 200) # l2
nd3 = ( 200, 200) # l3
nd4 = ( 200, 200) # l4
offset1 = (700,   75) # offset of level 1 grid to level 0
offset2 = (550,   25) # offset of level 1 grid to level 0
offset3 = (400,   75) # offset of level 1 grid to level 0
offset4 = ( 50,   50) # offset of level 2 grid to level 1

radius_list = [ 30., 7.5, 15., 15. ] # cylinder radius
center_list = [ [300, 100], [450., 125.], [600., 75.], [750., 125.] ]
theta_list = [ 0., 50., 100., 150. ]
obstacle = NestedObstacleManager(center_list=center_list, radius_list=radius_list, theta_list=theta_list, nd=nd0)

u, Re = 0.01, 10000000.0
nu = u*nd0[0]/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d2q9_Cumulant_kernel import ModelConfig
config = ModelConfig(mode="push") # "push" with bounce-back must be used for nested grid

bc_manager = BounceBackManager(nd0, [0, 1, 2, 2], [ [u, 0], [0,0], [0,0], [0,0] ]) # bounce-back scheme must be used for "push" scheme in collision-streaming kernel

lbm0 = lbm_skelton( nd0, config, get_omega_at_level(omega, 0) )
lbm1 = lbm_skelton( nd1, config, get_omega_at_level(omega, 1) )
lbm2 = lbm_skelton( nd2, config, get_omega_at_level(omega, 1) )
lbm3 = lbm_skelton( nd3, config, get_omega_at_level(omega, 1) )
lbm4 = lbm_skelton( nd4, config, get_omega_at_level(omega, 2) )

tree = GridManager(lbm0, bc_manager, config)                     # plant lbm0 as root
idx1 = tree.push(level=1, root_idx=0,    grid=lbm1, offset=offset1) # blanch 1 from 0
idx2 = tree.push(level=1, root_idx=0,    grid=lbm2, offset=offset2) # blanch 1 from 0
idx3 = tree.push(level=1, root_idx=0,    grid=lbm3, offset=offset3) # blanch 1 from 0
idx4 = tree.push(level=2, root_idx=idx3, grid=lbm4, offset=offset4) # blanch 2 from 1

obstacle.apply_to_mask(tree) # mask all levels

renderer = FluidRenderer(lbm0, vmin=0, vmax=u*5)

print(export_tree_info(tree)) # info will be sent to "tree_info.txt"

step, step_end = 0, 200000 # |--- run your simulation ---> #
while renderer.window.running and step < step_end:
    for _ in range(50):
        tree.run() # recursive run
        step += 1

    render(tree, renderer, lbm0)

    #if step % 100 == 0:
    #    ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"./output/nested_JCprob1/nested_JCprob1-{step:09d}.png")

ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"./img/nested_JCprob1.png")
save_vtk(tree, step, f"./output/nested_JCprob1") # read pvd file to import multi-grids in Paraview

