# nested_obstacle.py
"""
Obstacle manager for Taichi-accelerated LBM

This class apply boundary conditions to macro and distribution functions.
Inspired by the elegant LBM approach in LBM_Taichi (https://github.com/hietwll/LBM_Taichi/tree/master) by Dr. Zhuo Wang.
"""

import taichi as ti
import taichi.math as tm

from lb_utils.obstacle import ObstacleManager

@ti.data_oriented
class NestedObstacleManager(ObstacleManager): # circle (2D) / sphere (3D)
    def __init__(self, center_list, length, width, nd):
        super().__init__(center_list, length, nd)
        self.length = length
        self.width  = width

    def apply_to_mask(self, grids): # wrapper function for private kernel _generate_mask_kernel
        for level in range(grids.max_level+1):
            for idx in grids.tree[level]:
                lbm = grids.grid[idx]
                length_orig = self.length
                width_orig  = self.width
                center_orig = ti.Vector( [0., 0., 0.][:self.dim] )
                for dim in range(self.dim):
                    center_orig[dim] = self.center[None][dim]
                self.length = length_orig * 2**level
                self.width  = width_orig  * 2**level
                if level == 0:
                    shift = (0, 0, 0)[:self.dim]
                else:
                    shift = (0.25, 0.25, 0.25)[:self.dim] # nested grid is staggerred. the first node starts from (offset-1/4, offset-1/4)
                self.center[None] = ( center_orig - grids.offset_glb[idx] ) * 2**level + shift
                self._generate_mask_kernel(lbm.mask)
                self.length = length_orig 
                self.width  = width_orig  

                for dim in range(self.dim):
                    self.center[None][dim] = center_orig[dim]

    @ti.kernel
    def _generate_mask_kernel(self, mask: ti.template()):
        mask.fill(0)
        width2  = (0.5*self.width)**2
        length2 = (0.5*self.length)**2
        for I in ti.grouped(mask):
            distance = ti.cast(I, ti.f32) - self.center[None]
            if distance[0]**2 < width2 and distance[1]**2 < length2:
                mask[I] = 1.0
