# Fluid flow solver based on lattice boltzmann method using taichi language
# BGK, TRT, non-orthogonal MRT, Cumulant
#
# collision_model = "BGK", "TRT", "MRT", "Cumulant"

# dimension = 2 (D2Q9) or 3 (D3Q27)
    # omega[1]  : shear -> omega
    # omega[2]  : bulk  -> omP (use this for omega_{-} in TRT)
    # omega[3]  : for sum  of combinations of 120, 102, 210, 012, 201, 021 in D3Q27; for 12, 21 in D2Q9 (om3)
    # omega[4]  : for diff of combinations of 120, 102, 210, 012, 201, 021 in D3Q27; for 12, 21 in D2Q9 (om3)
    # omega[5]  : for 111
    # omega[6]  : for 220, 202, 022; for 22 in D2Q9 (om4)
    # omega[7]  : for 220, 202, 022; for 22 in D2Q9 (om4)
    # omega[8]  : for 211, 121, 112
    # omega[9]  : for 221, 212, 122
    # omega[10] : for 222

import taichi as ti
import taichi.math as tm

import os
import sys
import argparse # runtime arg control 

from lb_solver.lbm_lib import lbm_skelton         # lbm field manager: f, rho, velocity... are stored
from lb_utils.bc_kernel import BoundaryManager    # boundary condition to lbm object
from lb_utils.obstacle import ObstacleManager     # circular/spherical object applying mask to lbm object
from lb_utils.render import FluidRenderer         # rendering class supported by Taichi graphic api

from lb_utils.lbm_utils import get_model_config   # helper: runtime model loading 
from lb_utils.lbm_utils import PerformanceMonitor # simple MLUPS monitoring
from lb_utils.lbm_utils import save_vtk           # import pyevtk for Paraview visualization

ti.init(arch=ti.gpu, default_fp=ti.f32)

# wrapper #
def main():
    parser = argparse.ArgumentParser(description="LBM Solver Controller")
    
    parser.add_argument(
        'mode', 
        choices=['run', 'gen'], 
        help="Run mode: 'run' (lb simulator), 'gen' (lb code generator)"
    )

    parser.add_argument("--nd", type=int, nargs='+', default=[241, 61, 61], 
                        help="Simulation dimensions (e.g., 241 61 61 or 801 201)")

    parser.add_argument("--Re", type=float, default=10000, 
                        help="Reynolds number; default 10000")

    parser.add_argument("--u", type=float, default=0.1, 
                        help="Inlet velocity; default 0.1")

    parser.add_argument("--render", type=str, default="vorticity", 
                        help="Render mode: default vorticity [vorticity, velocity]")

    args = parser.parse_args()

    if args.mode == 'run':
        nd = tuple(args.nd)
        dim = len(nd)
        if (dim != 2) & (dim != 3): raise ValueError("Dimension must be 2 or 3.")
        Re = abs(args.Re)
        if (Re < 1e-2): raise ValueError("Reynolds number maybe too small.")
        u = abs(args.u)
        if (u < 1e-8): raise ValueError("Inlet velocity must be positive.")
        render_mode = args.render
        if (render_mode != "vorticity") & (render_mode != "velocity"): raise ValueError("Render mode must be vorticity or velocity.")        
        run(nd, Re, u, render_mode)
    elif args.mode == 'gen':
        code_gen()
    
    sys.exit(0)

# code generation only #
def code_gen():
    from generator.cumulant_generator import allrun
    allrun() # generate all kernels

# run numerical simulation #
def run(nd, Re, u, render_mode):
    # constructing LB model -> #

    GEN_PATH = "generated_kernel.py" # if None, existing kernel module will be imported

    model_libs = ["BGK", "TRT", "MRT", "Cumulant"]
    MODEL_TYPE = model_libs[3]

#    nd = (241, 61, 61) # <- managed in main()
#    nd = (801, 201)
#    Re = 10000.0
#    u  = 0.1                                         # inlet velocity
    radius = nd[1] * 0.25 if len(nd) == 3 else 20.0  # radius of object
    nu = u*2*radius/Re                               # kinematic viscosity
    omega = 1/(3*nu + 0.5)                           # relaxation parameter
    print(f"## nu= {nu:.8f}, omega= {omega:.8f}, Re= {Re}, u= {u:4f}")

    if not (GEN_PATH == None):
#        omega_list = [omega] # need to specify at least one value for shear vicosity, omega_{1}
        omega_list = [
            omega, # 1
            1.05, # 2 : use this for omega_{-} in TRT
            1.04, # 3 om3
            1.03, # 4 om3
            1.02, # 5
            1.01, # 6 om4
            1.08, # 7 om4
            1.07, # 8
            1.06, # 9
            1.05, # 10
        ]
        from generator.cumulant_generator import run_generator
        run_generator(collision_model=MODEL_TYPE, dimension=len(nd), silent=True, omega_config_input=omega_list, output_filename=GEN_PATH)
    ModelConfig = get_model_config(nd, MODEL_TYPE, GEN_PATH)
    config = ModelConfig()
    print("## selected kernel module:", config)

    lbm = lbm_skelton(nd, config, omega)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Only when you use the existing kernel module, you can change omega_{i > 1} value here.        #
    #   like lbm.omega[2] = 1.2                                                                     #
    #   If you do not specify omega_{i > 1}, they were set to 1 in the constructor of lbm.          #
    # When you generate the code at runtime, the omegas are "baked" and are'nt changeable.          # 
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # VTK file (for ParaView) output settings #
    output_step = 1000 # <- NOTE: frequent call (data dump onto numpy array) significantly deteriorates computing speed 
    output_flag = False
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_dir = os.path.join(desktop_path, "output")
    print(f"## result output directory: {output_dir}")

    # boundary conditions: 0 -> inflow ; 1 -> outflow ; 2 -> walls ; 3 -> object mask
    if len(nd) == 2:
        wall = [0.0, 0.0]
        U = [u, 0.0]
        bc_type_list  = [0, 1, 2, 2]
        bc_value_list = [ U, wall, wall, wall]
        center_list = [nd[0] * 0.25, (nd[1]-1)/2]
    else:
        wall = [0.0, 0.0, 0.0]
        U = [u, 0.0, 0.0]
        bc_type_list  = [ 0, 1, 2, 2, 2, 2]
        bc_value_list = [ U, wall, wall, wall, wall, wall ]
        center_list = [nd[0] * 0.25, (nd[1]-1)/2, (nd[2]-1)/2]

    bc_manager = BoundaryManager(nd, bc_type_list, bc_value_list)
    # <- model construction ends #

    # setting spherical object #
    obstacle = ObstacleManager(center_list=center_list, radius=radius, nd=nd)
    obstacle.apply_to_mask(lbm)

    def convert_mouse_pos(lbm, m_pos): # convert mouse position to sphere position in LB world
        if lbm.dim == 2:
            new_pos = ti.Vector([m_pos[0] * lbm.nx, m_pos[1] * lbm.ny])
        else:
            y_pos = m_pos[1] * (lbm.ny + lbm.nz)
            if y_pos > lbm.ny:
                y_pos -= lbm.ny
                new_pos = ti.Vector([m_pos[0] * (lbm.nx+lbm.nz), obstacle.center[None][1], y_pos])
            else:
                new_pos = ti.Vector([m_pos[0] * (lbm.nx+lbm.nz), y_pos, obstacle.center[None][2]])
        return new_pos

    # Taichi realtime rendering #
    if render_mode == "vorticity":
        vmin, vmax = -u, u
    else:
        vmin, vmax = 0, u*3
    renderer = FluidRenderer(lbm, vmin=vmin, vmax=vmax)
    render_step = 10 if len(nd) == 3 else 200

    # monitoring model performance in MLUPS #
    mlups_monitor = PerformanceMonitor(nd)

    # |--- run your simulation ---> #
    step, step_end = 0, 10000000
    while renderer.window.running and step < step_end:
        if renderer.window.is_pressed(ti.ui.LMB): # mouse on
            m_pos = renderer.window.get_cursor_pos()
            obstacle.move_center( convert_mouse_pos(lbm, m_pos) ) # update object position
            obstacle.apply_to_mask(lbm) # update mask field

        for _ in range(render_step):
            f_pre, f_post = lbm.swap(step) # ! pseudo swap ! # this is much faster than value copy 
            config.col_stream_core(lbm, f_pre, f_post)
            bc_manager.apply_bc(lbm, config, f_pre, f_post, obstacle)
            step += 1

        renderer.render(lbm, render_mode)
        mlups_monitor.update(step)
        if step % output_step and output_flag:
            save_vtk(lbm, step, output_dir)


if __name__ == "__main__":
    main()
