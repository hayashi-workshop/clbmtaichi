# nested.py

import taichi as ti
import taichi.math as tm

from lb_solver.lbm_lib import lbm_skelton
from lb_utils.bback_kernel import BounceBackManager

from lb_utils.nested_grid import GridManager
from examples.nested_obstacle_plate import NestedObstacleManager
from lb_utils.nested_utils.nested_helper import save_vtk
from lb_utils.nested_utils.nested_helper import export_tree_info

#from lb_utils.nested_utils.nested_helper import render
#from lb_utils.render import FluidRenderer

ti.init(arch=ti.gpu, default_fp=ti.f32)

def get_omega_at_level(omega, target_level):
    if target_level <= 0:
        return omega
    
    prev_omega = get_omega_at_level(omega, target_level - 1) # recursive call to find omega at upper level
    
    return 1.0 / (2.0 / prev_omega - 0.5)


nd0 = (1001,  401) # number of nodes@level 0
nd1 = (1500,  600) # l1
nd2 = (2240,  880) # l2
nd3 = (3360, 1280) # l3
nd4 = (5120, 1920) # l4
nd5 = (7680, 2880) # l5

offset1 = ( 80,  50) # offset of level 1 grid to level 0
offset2 = (100,  80) # offset of level 2 grid to level 1
offset3 = (200, 120) # offset of level 2 grid to level 2
offset4 = (320, 160) # offset of level 2 grid to level 3
offset5 = (640, 240) # offset of level 2 grid to level 4

length = 40. 
width  =  3.
obstacle = NestedObstacleManager(center_list=[300., 200.5], length=length, width=width, nd=nd0)

u = 0.05
Re = 1400000.0
nu = u*length/Re; omega = 1/(3*nu + 0.5)

from lb_solver.d2q9_Cumulant_kernel import ModelConfig
config = ModelConfig(mode="push") # "push" with bounce-back must be used for nested grid

bc_manager = BounceBackManager(nd0, [0, 1, 2, 2], [ [u, 0], [0,0], [0,0], [0,0] ]) # bounce-back scheme must be used for "push" scheme in collision-streaming kernel

lbm0 = lbm_skelton( nd0, config, get_omega_at_level(omega, 0) )
lbm1 = lbm_skelton( nd1, config, get_omega_at_level(omega, 1) )
lbm2 = lbm_skelton( nd2, config, get_omega_at_level(omega, 2) )
lbm3 = lbm_skelton( nd3, config, get_omega_at_level(omega, 3) )
lbm4 = lbm_skelton( nd4, config, get_omega_at_level(omega, 4) )
#lbm5 = lbm_skelton( nd5, config, get_omega_at_level(omega, 5) )

tree = GridManager(lbm0, bc_manager, config)                        # plant lbm0 as root
idx1 = tree.push(level=1, root_idx=0,    grid=lbm1, offset=offset1) # blanch 1 from 0
idx2 = tree.push(level=2, root_idx=idx1, grid=lbm2, offset=offset2) # blanch 2 from 1
idx3 = tree.push(level=3, root_idx=idx2, grid=lbm3, offset=offset3) # blanch 3 from 2
idx4 = tree.push(level=4, root_idx=idx3, grid=lbm4, offset=offset4) # blanch 4 from 3
#idx5 = tree.push(level=5, root_idx=idx4, grid=lbm5, offset=offset5) # blanch 5 from 4

obstacle.apply_to_mask(tree) # mask all levels

#renderer = FluidRenderer(lbm0, vmin=-u*2, vmax=u*2)

print(export_tree_info(tree)) # info will be sent to "tree_info.txt"

step, step_end = 0, 100000 # |--- run your simulation ---> #
while step < step_end: #while renderer.window.running and step < step_end:
    for _ in range(10):
        tree.run() # recursive run
        step += 1

        #render(tree, renderer, lbm0)
        if step % 1000 == 0:
            print(f"current step: {step}")


#ti.tools.imwrite(renderer.img_buffer.to_numpy(), f"./img/nested_plate.png")    
save_vtk(tree, step, f"./output/nested_plate") # read pvd file to import multi-grids in Paraview

