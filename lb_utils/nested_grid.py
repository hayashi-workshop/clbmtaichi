# nested_grid.py

# Staggerred nested grids based on bubble function proposed in
#     Geier, M., A. Greiner, and J. G. Korvink. 2009. Bubble Functions for the Lattice Boltzmann Method and Their Application to Grid Refinement. The European Physical Journal. Special Topics 171 (1): 173-79.
#     https://www.youtube.com/@tubs-irmb6980/videos
# 
#     quadratic pressure interpolation is introduced in 
#     Geier, Martin, Konstantin Kutscher, Martin Schonherr, Anna Wellmann, Soren Peters, Hussein Alihussein, Jan Linxweiler, and Manfred Krafczyk. 2025. VirtualFluids - Open Source Parallel LBM Solver. Computer Physics Communications 317: 109810.
#
#   [+ +] 
#   [+ +] Fine   nodes updated by interpolation from 4 Coase nodes
#
#   (o)   Coarse nodes updated by interpolation from 4 Fine  nodes
#
#   [!NOTE]
#   nd[] (Fine) must be even numbers
#   even when offset (0, 0), the coarse node (interpolated by fines) starts from ir, jr = 2, 2
#
#   [!NOTE] Algorithm
#   The interpolation must be done before Collision step (see Sec 4 of the above referenced paper), 
#   therefore, pull scheme is not comptatible with the bubble function. 
#              push scheme is employed intead. 
#
#   [!NOTE] Boundary Condition
#   With push scheme, Guo's boundary condition is not compatible,
#   therefore,        delayed bounce back scheme is employed.
#
#   One halo line of Fines (+) is required to prevent push streaming in delayed Bounce Back scheme
#
# The following ascii art shows a case of
#     o : Coarse (15, 11)
#     + : Fine   (18, 14)
#         Offset ( 3,  2)
#
# 10o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#  9o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |13 + | + + | + + | + + | + + | + + | + + | + + | + + | +   |     |     |
#  8o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |12 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#   |     |     |11 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#  7o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |10 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 9 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  6o - - o - - o - - o - - o - -(o)- -(o)- -(o)- -(o)- -(o)- - o - - o - - o - - o - - o
#   |     |     | 8 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 7 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  5o - - o - - o - - o - - o - -(o)- - o - - o - - o - -(o)- - o - - o - - o - - o - - o
#   |     |     | 6 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 5 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  4o - - o - - o - - o - - o - -(o)- -(o)- -(o)- -(o)- -(o)- - o - - o - - o - - o - - o
#   |     |     | 4 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 3 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  3o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     | 2 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     | 
#   |     |     | 1 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#  2o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     | 0 + | + + | + + | + + | + + | + + | + + | + + | + + | +   |     |     |
#   |     |     |   0 | 1 2 | 3 4 | 5 6 | 7 8 | 9 10|11 12|13 14|15 16|17   |     |     |
#  1o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#  0o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   0     1     2     3     4     5     6     7     8     9     10    11    12    13    14
#
#   [recursive procedure with push-type collision kernel]
#   [3 level example]
#   Level 0: proceed dt_{Coarse} x 1
#   - Collision (1)
#   - Push (streaming) (1)
#   - Boundary condition (1)
#     ---> Call Level 1
#          Level 1: proceed dt_{Fine} x 2 (= dt_{Coarse})
#        - Collision (1)
#        - Push (streaming) (1)
#        - [Boundary condition (1)] <- (can be skipped)
#          ---> Call Level 2
#               Level 2: proceed dt_{Fine} x 2 (= dt_{Coarse})
#             - Collision (1)
#             - Push (streaming) (1)
#             - [Boundary condition (1)] <- (can be skipped)
#             - Collision (2)
#             - Push (streaming) (2)
#             - [Boundary condition (2)] <- (can be skipped)
#          <--- Back to Level 1
#        - interpolation between neighboring level grids (1 <-> 2)
#        - Collision (2)
#        - Push (streaming) (2)
#        - [Boundary condition (2)] <- (can be skipped)
#          ---> Call Level 2
#               Level 2: proceed dt_{Fine} x 2 (= dt_{Coarse})
#             - Collision (1)
#             - Push (streaming) (1)
#             - [Boundary condition (1)] <- (can be skipped)
#             - Collision (2)
#             - Push (streaming) (2)
#             - [Boundary condition (2)] <- (can be skipped)
#          <--- Back to Level 1
#        - interpolation between neighboring level grids (1 <-> 2)
#     <--- Back to Level 0
#   - interpolation between neighboring level grids (0 <-> 1)


import taichi as ti
import taichi.math as tm 

import os
import io
import numpy as np
import importlib

@ti.data_oriented
class GridManager:
    # grid access via grid id, idx
    # idx is stored in tree
    def __init__(self, root, bc_manager, config):
        self.bc_manager = bc_manager
        self.config = config

        # import bubble function module ---> #
        dim = len(root.nd)
        Q = 3**dim
        drho_mode   = "rho" if config.density_shift == 0 else "drho"
        module_path = f"lb_utils.nested_utils.nested_bubble_d{dim}q{Q}_{drho_mode}"
        module      = importlib.import_module(module_path)

        self.compute_interpolation_coeffs = module.compute_interpolation_coeffs
        self.backtrans_c_to_f             = module.backtrans_c_to_f
        self.interpolation_FtoC           = module.interpolation_FtoC
        self.interpolation_CtoF           = module.interpolation_CtoF
        # <---

        self.tree = {}     # grid tree dict
                           #
                           # tree[0]->root grid (idx=0) level 0
                           #      |
                           # tree[1] - [idx, idx, ...] level 1 grids
                           #             |    |
                           #    tree[2]  |   [idx, idx,...]
                           #            [idx, idx, ...]

        self.idx = 0                 # grid id, starting from 0
        self.tree[0] = [self.idx]    # append root grid
        self.tree[1] = []            # open next level
        _, _ = self.get_tree_info()  # commit 

        self.offset    = {}          # offset dict 
        self.offset_glb= {}          # offset@global coordinate
        self.grid      = {}          # pointor to grid via id
        self.root_idx  = {}          # pointor to parent grid
        self.stepLocal = {}          # store total step in each grid

        # - * - originator - * - #
        offset = np.zeros(root.dim)
        self.offset[self.idx]    = offset             # offset to my root grid; one real root has no offset -> (0, 0)
        self.offset_glb[self.idx]= np.array( offset ) # coordinates of offset in level 0 coordinate system
        self.grid[self.idx]      = root               # 
        self.root_idx[self.idx]  = None               # this is the one root
        self.stepLocal[self.idx] = 0                  # time step of local grid 

        self.leaf_idx    = {}        
        self.leaf_idx[0] = []        # open leaf index dict

        self.pvd = None              # vtm list for paraview


    def get_tree_info(self):
        tree_count = -1
        grid_count =  0
        for level, idxs in zip(self.tree.keys(), self.tree.values()):
            if len(idxs) == 0:
                continue
            else:
                tree_count += 1
                grid_count += len(idxs)
        self.max_level    = tree_count
        self.num_of_grids = grid_count

        return tree_count, grid_count


    def get_current_level(self, idx=0):
        if self.root_idx[idx] is None:
            return 0
        
        level = 1 + self.get_current_level(self.root_idx[idx])        
        return level


    def push(self, level, root_idx, grid, offset):
        # - * - check requirements - * - [!NOTE] only some fundamentals. all requirements not checked 
        if level > self.max_level + 1:
            raise ValueError(f"level {level} exceeds the level next to the max level. Set grid at level {self.max_level+1} first.")

        if not all(x % 2 == 0 for x in grid.nd):
            raise ValueError(f"nd, domain size, {nd} of leaf must be even (nd[d] % 2 == 0).")

        if not all(0 <= x < limit for x, limit in zip(offset, self.grid[root_idx].nd)):
            raise ValueError(f"offset {offset} is set in invalid range; not covered by root grid.")

        end_point = (np.array(grid.nd) - 2) // 2 + np.array(offset)
        if not all(x < limit for x, limit in zip(end_point, self.grid[root_idx].nd)):
            raise ValueError(f"nd {grid.nd} of leaf grid is out of bound; not covered by root grid.")

        if not all(x > 10 for x in grid.nd):
            raise ValueError(f"nd {grid.nd} of leaf grid is too small; minimum is 10.")


        self.idx += 1                            # increment global id for new grid
        self.tree[level].append(self.idx)        # push grid to grid tree

        self.offset[self.idx]    = offset        # store offset of new grid
        self.grid[self.idx]      = grid          # store grid as id = idx
        self.stepLocal[self.idx] = 0             # time step of local grid 
        self.root_idx[self.idx]  = root_idx      # id of parent
        self.leaf_idx[self.idx]  = []            # id of leaf; set [] since new grid[idx] has still no leaf

        if level >= self.max_level:
            self.tree[level + 1] = []            # activate list in next level

        self.root_idx[self.idx] = root_idx       # remember who is my root
        self.leaf_idx[root_idx].append(self.idx) # set leaf idx to root grid 
        _, _ = self.get_tree_info()              # update tree info

        # calculate global offset (coordinate of local origin in level 0 coordinate system) --->
        offset_glb = np.zeros(grid.dim)

        current_level = level                        # start from new grid
        current_idx   = self.idx 
        while current_level > 1: 
            for d in range(grid.dim):
                offset_glb[d] += ( (self.offset[current_idx][d] - 1) * 0.5 + 0.25 ) / 2**(current_level-2)
                                                               # -1: ignore halo 
                                                                     # 0.5: dx_{F} = 0.5 dx_{C}
                                                                           # 0.25: staggerred -- upper level i_{C}=1 starts from offset + 0.25
                                                                                    # 2^{l-2}: scale conversion
            current_idx = self.root_idx[current_idx] # climb tree upward
            current_level -= 1

        for d in range(grid.dim):
            offset_glb[d] = offset_glb[d] + self.offset[current_idx][d] # add level 1 offset: common for all leaves

        self.offset_glb[self.idx] = offset_glb

        return self.idx # return id of registered grid


    def lbm_core(self, idx): # standard lbm solution algorithm (pull scheme must be used)
        lbm = self.grid[idx]
        f_pre, f_post = lbm.swap( self.stepLocal[idx] )
        self.config.col_stream_core(lbm, f_pre, f_post)
        self.bc_manager.apply_bc(lbm, self.config, f_pre, f_post) # use Bounce-Back since Guo's bc is not compatible

        self.stepLocal[idx] += 1

    
    def run(self, level=0, stepEnd=1): # recursive run 
        for step in range(stepEnd):
            for idx in self.tree[level]:              # update once all grids at current level
                self.lbm_core(idx)
            
            if level < self.max_level:                # recursive call if leaf grid is present
                self.run(level=level+1, stepEnd=2)

                for idx in self.tree[level]:
                    if len( self.leaf_idx[idx] ) > 0: # handshake between the current level and next level
                        self.handshake(idx)


    def handshake(self, idx): # Bubble Function Coase <-> Fine syncronization
    # Geier, M., A. Greiner, and J. G. Korvink. 2009. Bubble Functions for the Lattice Boltzmann Method and Their Application to Grid Refinement. The European Physical Journal. Special Topics 171 (1): 173-79.
        gr      = self.grid[idx]     # root grid
        gls_idx = self.leaf_idx[idx] # leaf grids [list]

        for gl_idx in gls_idx:       # sweep all leaves belonging to gr
            gl = self.grid[gl_idx]   # pick leaf
            off_z = 0 if gr.dim == 2 else self.offset[gl_idx][2]
            offset = ti.Vector( [self.offset[gl_idx][0], self.offset[gl_idx][1], off_z] )
            f_root_tag, _ = gr.swap(self.stepLocal[idx]     ) # root target [pick pre-collision f]
            f_leaf_tag, _ = gl.swap(self.stepLocal[gl_idx]  ) # leaf target [pick pre-collision f]

            self._FineToCoarse_sweep(gr, gl, f_root_tag, f_leaf_tag, offset)
            self._CoarseToFine_sweep(gr, gl, f_root_tag, f_leaf_tag, offset)


    @ti.func
    def _FineToCoarse_core(self, f_root_tag, f_leaf_tag, omega_root, omega_leaf, Ir, Il):
        coeffs = self.compute_interpolation_coeffs(f_leaf_tag, Il, omega_leaf) # omega_{F} in reconstruction on Fine nodes
        macrovars, cumulants = self.interpolation_FtoC(coeffs, omega_root) # omega_{C} in injection onto Coarse nodes
        self.backtrans_c_to_f(f_root_tag, Ir, macrovars, cumulants) # injection


    @ti.kernel
    def _FineToCoarse_sweep(self, 
                            gr: ti.template(), gl: ti.template(), 
                            f_root_tag: ti.template(), f_leaf_tag: ti.template(), 
                            offset: ti.types.vector(3, ti.i32)):
        #      |       o: Coarse
        #    + | +     +: Fine
        # - - -o- - - 
        #    + | +
        #      |
        for Il in ti.grouped(gl.rho):
            in_valid_range = True
            for i in ti.static(range(gl.dim)): ## all nodes must not be in halo 
                if Il[i] < 4 or Il[i] > gl.nd[i] - 6:
                    in_valid_range = False
                    
            is_even_coord = True
            for i in ti.static(range(gl.dim)): # fine nodes of odd indices are skipped
                if Il[i] % 2 != 0:
                    is_even_coord = False

            is_boundary = False
            for i in ti.static(range(gl.dim)): # check whether one of the indices on interpolation boundary
                if Il[i] == 4 or Il[i] == gl.nd[i] - 6:
                    is_boundary = True
            
            if in_valid_range and is_even_coord and is_boundary: # provilege of getting into the core
                Ir = ti.Vector.zero(ti.i32, gl.dim)
                for i in ti.static(range(gl.dim)):
                    Ir[i] = offset[i] + (Il[i]) // 2 # target on Coarse (root)  

                self._FineToCoarse_core(f_root_tag, f_leaf_tag, gr.omega[1], gl.omega[1], Ir, Il)


    @ti.func
    def _CoarseToFine_core(self, f_root_tag, f_leaf_tag, omega_root, omega_leaf, Ir, Il_mm):
        
        # get coeffs on Coarse nodes
        coeffs = self.compute_interpolation_coeffs(f_root_tag, Ir, omega_root) # omega_{C} in reconstruction on Coarse nodes

        dim = Il_mm.n
        num_vertices = 1 << dim # bit shift
        for vertex in range(num_vertices): ## sweep vertices I_mm, I_pm, I_pp, I_mp in 2D
            Il = ti.Vector.zero(ti.i32, Il_mm.n)
            for i in ti.static(range(Il_mm.n)):
                if i < dim:
                    shift_bit = (vertex >> i) & 1
                    Il[i] = Il_mm[i] + shift_bit

            coords = ti.Vector.zero(ti.f32, Il_mm.n) # fine node cooredinates for interpolation function (-0.25, -0.25), (0.25, -0.25), ...
            for i in ti.static(range(Il_mm.n)):
                if i < dim:
                    bit = (vertex >> i) & 1
                    coords[i] = -0.25 if bit == 0 else 0.25

            macrovars, cumulants = self.interpolation_CtoF(coeffs, omega_leaf, coords) # omega_{F} in injection onto Fine nodes
            self.backtrans_c_to_f(f_leaf_tag, Il, macrovars, cumulants) # injection # (m,m) # 


    @ti.kernel
    def _CoarseToFine_sweep(self,
                            gr: ti.template(), gl: ti.template(), 
                            f_root_tag: ti.template(), f_leaf_tag: ti.template(), 
                            offset: ti.types.vector(3, ti.i32)):
        # o - - o
        # | + + |  (m,p) (p,p)
        # | + + |  (m,m) (p,m)
        # o - - o        
        #sizes = [(gl.nd[i] - 4) // 2 + 1 for i in ti.static(range(gl.dim))]
        #ranges = [(offset[i], offset[i] + sizes[i]) for i in ti.static(range(gl.dim))]
        for Il_mm in ti.grouped(gl.rho):
            is_boundary = False
            for i in ti.static(range(gl.dim)):
                if (Il_mm[i] == 1) or (Il_mm[i] == gl.nd[i] - 3):
                    is_boundary = True

            if is_boundary:
                Ir = ti.Vector.zero(ti.i32, gl.dim)
                for i in ti.static(range(gl.dim)):
                    Ir[i] = (Il_mm[i] - 1) // 2 + offset[i]
            
                self._CoarseToFine_core(f_root_tag, f_leaf_tag, gr.omega[1], gl.omega[1], Ir, Il_mm)
