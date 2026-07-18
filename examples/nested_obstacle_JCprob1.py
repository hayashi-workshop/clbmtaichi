# nested_obstacle.py
"""
Obstacle manager for Taichi-accelerated LBM

This class apply boundary conditions to macro and distribution functions.
Inspired by the elegant LBM approach in LBM_Taichi (https://github.com/hietwll/LBM_Taichi/tree/master) by Dr. Zhuo Wang.
"""

import taichi as ti
import taichi.math as tm

from examples.obstacle_bump import ObstacleManager

@ti.data_oriented
class NestedObstacleManager(ObstacleManager): # circle (2D) / sphere (3D)
    def __init__(self, center_list, radius_list, theta_list, nd):
        super().__init__(center_list, radius_list, nd)
        self.theta0 = ti.field(dtype=ti.f32, shape=self.num_objects)        
        for i in range(self.num_objects):
            self.theta0[i] = theta_list[i]

    def apply_to_mask(self, grids): # wrapper function for private kernel _generate_mask_kernel
        for level in range(grids.max_level+1):
            for idx in grids.tree[level]:
                lbm = grids.grid[idx]
                self._reset_mask(lbm.mask)
                for i in range(self.num_objects):
                    radius_orig = self.radius[i]
                    center_orig = ti.Vector( [0., 0., 0.][:self.dim] )
                    for dim in range(self.dim):
                        center_orig[dim] = self.center[i][dim]
                    self.radius[i] = radius_orig * 2**level
                    if level == 0:
                        shift = (0, 0, 0)[:self.dim]
                    else:
                        shift = (0.25, 0.25, 0.25)[:self.dim] # nested grid is staggerred. the first node starts from (offset-1/4, offset-1/4)
                    self.center[i] = ( center_orig - grids.offset_glb[idx] ) * 2**level + shift
                    self._generate_mask_kernel(lbm.mask, i)
                    self.radius[i] = radius_orig
                    for dim in range(self.dim):
                        self.center[i][dim] = center_orig[dim]

    @ti.kernel
    def _reset_mask(self, mask: ti.template()):
        mask.fill(0)

    #Johansen and Phillip Colella, JCP 1998
    @ti.kernel
    def _generate_mask_kernel(self, mask: ti.template(), i: ti.i32):
        for I in ti.grouped(mask):
            distance = ti.cast(I, ti.f32) - self.center[i]
            d2 = distance.norm_sqr()
            eps = 1e-6
            r  = tm.sqrt(d2) + eps
            theta = ti.atan2(distance[1], distance[0]) + self.theta0[i]
            dr = r - self.radius[i]*((1 + 0.5*tm.cos(6.0*theta)))*1.5 
            if dr < 0.0:
                mask[I] = 1.0
            nx = tm.cos(theta) - tm.sin(theta) * 0.9*tm.sin(6.0*theta)/r
            ny = tm.sin(theta) + tm.cos(theta) * 0.9*tm.sin(6.0*theta)/r
            self.n[I] = ti.Vector([nx,ny])
