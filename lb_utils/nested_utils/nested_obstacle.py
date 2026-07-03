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
    def __init__(self, center_list, radius, nd):
        super().__init__(center_list, radius, nd)

    def apply_to_mask(self, grids): # wrapper function for private kernel _generate_mask_kernel
        for level in range(grids.max_level+1):
            for idx in grids.tree[level]:
                lbm = grids.grid[idx]
                radius_orig = self.radius
                center_orig = ti.Vector( [0., 0., 0.][:self.dim] )
                for dim in range(self.dim):
                    center_orig[dim] = self.center[None][dim]
                self.radius = radius_orig * 2**level
                if level == 0:
                    shift = (0, 0, 0)[:self.dim]
                else:
                    shift = (0.25, 0.25, 0.25)[:self.dim] # nested grid is staggerred. the first node starts from (offset-1/4, offset-1/4)
                self.center[None] = ( center_orig - grids.offset_glb[idx] ) * 2**level + shift
                self._generate_mask_kernel(lbm.mask)
                self.radius = radius_orig
                for dim in range(self.dim):
                    self.center[None][dim] = center_orig[dim]

    @ti.kernel
    def _generate_mask_kernel(self, mask: ti.template()):
        mask.fill(0)
        for I in ti.grouped(mask):
            distance = ti.cast(I, ti.f32) - self.center[None]
            d2 = distance.norm_sqr()
            if d2 <= self.radius ** 2:
                mask[I] = 1.0
