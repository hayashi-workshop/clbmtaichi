# bback_kernel.py
"""
Bounce-back boundary condition

This class apply boundary conditions to macro and distribution functions.
Inspired by the elegant LBM approach in LBM_Taichi (https://github.com/hietwll/LBM_Taichi/tree/master) by Dr. Zhuo Wang.
"""

import taichi as ti
import taichi.math as tm

import numpy as np

from lb_utils.bc_kernel import BoundaryManager
#from lb_utils.obstacle import ObstacleManager

c_d2q9  = (ti.Vector([0, 0]), ti.Vector([1, 0]), ti.Vector([0, 1]), ti.Vector([-1, 0]), ti.Vector([0, -1]), ti.Vector([1, 1]), ti.Vector([-1, 1]), ti.Vector([-1, -1]), ti.Vector([1, -1]))
c_d3q27 = (ti.Vector([0, 0, 0]), ti.Vector([1, 0, 0]), ti.Vector([-1, 0, 0]), ti.Vector([0, 1, 0]), ti.Vector([0, -1, 0]), ti.Vector([0, 0, 1]), ti.Vector([0, 0, -1]), ti.Vector([1, 1, 0]), ti.Vector([-1, -1, 0]), ti.Vector([1, -1, 0]), ti.Vector([-1, 1, 0]), ti.Vector([1, 0, 1]), ti.Vector([-1, 0, -1]), ti.Vector([1, 0, -1]), ti.Vector([-1, 0, 1]), ti.Vector([0, 1, 1]), ti.Vector([0, -1, -1]), ti.Vector([0, 1, -1]), ti.Vector([0, -1, 1]), ti.Vector([1, 1, 1]), ti.Vector([-1, -1, -1]), ti.Vector([1, 1, -1]), ti.Vector([-1, -1, 1]), ti.Vector([1, -1, 1]), ti.Vector([-1, 1, -1]), ti.Vector([1, -1, -1]), ti.Vector([-1, 1, 1]))
inv_idx_d2q9 = ti.Vector([0, 3, 4, 1, 2, 7, 8, 5, 6])
inv_idx_d3q27 = ti.Vector([0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15, 18, 17, 20, 19, 22, 21, 24, 23, 26, 25])

@ti.data_oriented
class BounceBackManager(BoundaryManager):
    # [left,right,bottom,top] boundary conditions: 0 -> inflow ; 1 -> outflow ; 2 -> walls ; 3 -> object mask
    # if bc_type = 0, we need to specify the velocity in bc_value
    def __init__(self, nd, init_bc_type, init_bc_value):
        super().__init__(nd, init_bc_type, init_bc_value)

        if self.dim == 2:
            self.c = c_d2q9
            self.inv_idx = inv_idx_d2q9
        else:
            self.c = c_d3q27
            self.inv_idx = inv_idx_d3q27

        self.INV_9 = 1.0/9.0
        self.INV_3 = 1.0/3.0
        self.INV_36 = 1.0/36.0
        self.INV_6 = 1.0/6.0


    @ti.kernel # with obstacle [override]
    def _apply_bc_obs(self, lbm: ti.template(), config: ti.template(), f_pre: ti.template(), f_post: ti.template(), obs: ti.template()):
        for I in ti.grouped(lbm.mask): # I[0] = i, I[1] = j, I[2] = k
            is_outer_wall, is_obj_node = self._node_ruling(lbm, I)
            if not (is_outer_wall or is_obj_node):
                continue

            if is_obj_node:
                self._apply_bc_core(lbm, config, f_pre, f_post, 3, ti.Vector.zero(ti.f32, self.dim), I, I, I)
            elif is_outer_wall:
                self._apply_bc_outer_wall(lbm, config, f_pre, f_post, I)

    @ti.func # [override]
    def _apply_bc_core(self, lbm, config, f_pre, f_post, bc_id, vbc, x_bc, x_nb, x_nb2):
        if bc_id == 0: # inflow
            lbm.vel[x_bc] = vbc #self.bc_value[dr]
            lbm.rho[x_bc] = 2.0 * lbm.rho[x_nb] - lbm.rho[x_nb2]
        elif bc_id == 1: # outflow
            lbm.vel[x_bc] = lbm.vel[x_nb]
            lbm.rho[x_bc] = lbm.rho[x_nb]
        elif bc_id == 2: # noslip wall
            lbm.vel[x_bc] = vbc # self.bc_value[dr] # load boundary velocity to adopt moving wall
            lbm.rho[x_bc] = lbm.rho[x_nb]
        elif bc_id == 3: # object mask
            lbm.vel[x_bc] = ti.Vector.zero(float, self.dim) # velocity is zero inside solid object
            lbm.rho[x_bc] = lbm.rho[x_nb]
        
        i = x_bc[0]
        j = x_bc[1]

        u = lbm.vel[x_bc][0]
        v = lbm.vel[x_bc][1]

        if bc_id == 1:
            pass # do nothing for outlet approxs (?): (I) 0th order interpolation f_{bc} = f_{nb}, then, push f_{bc} to -> f_{nb}
        else:
            if ti.static(self.dim == 2):
                if i == 0 and j == 0:
                    f_post[x_bc + self.c[5]][5] = f_pre[x_bc][7]
                elif i == 0 and j == lbm.nd[1] - 1:
                    f_post[x_bc + self.c[8]][8] = f_pre[x_bc][6]
                elif i == lbm.nd[0] - 1 and j == 0:
                    f_post[x_bc + self.c[6]][6] = f_pre[x_bc][8]
                elif i == lbm.nd[0] - 1 and j == lbm.nd[1] - 1:
                    f_post[x_bc + self.c[7]][7] = f_pre[x_bc][5]
                elif i == 0:
                    f_post[x_bc + self.c[1]][1] = f_pre[x_bc][3] + 2 * self.INV_3 * ( u )
                    f_post[x_bc + self.c[5]][5] = f_pre[x_bc][7] + self.INV_6 * ( u + v )
                    f_post[x_bc + self.c[8]][8] = f_pre[x_bc][6] + self.INV_6 * ( u - v )
                elif i == lbm.nd[0] - 1:
                    f_post[x_bc + self.c[3]][3] = f_pre[x_bc][1] + 2 * self.INV_3 * ( -u )
                    f_post[x_bc + self.c[6]][6] = f_pre[x_bc][8] + self.INV_6 * ( -u + v )
                    f_post[x_bc + self.c[7]][7] = f_pre[x_bc][5] + self.INV_6 * ( -u - v )
                elif j == 0:
                    f_post[x_bc + self.c[2]][2] = f_pre[x_bc][4] + 2 * self.INV_3 * ( v )
                    f_post[x_bc + self.c[5]][5] = f_pre[x_bc][7] + self.INV_6 * ( u + v )
                    f_post[x_bc + self.c[6]][6] = f_pre[x_bc][8] + self.INV_6 * ( -u + v )
                elif j == lbm.nd[1] - 1:
                    f_post[x_bc + self.c[4]][4] = f_pre[x_bc][2] + 2 * self.INV_3 * ( -v )
                    f_post[x_bc + self.c[7]][7] = f_pre[x_bc][5] + self.INV_6 * ( -u - v )
                    f_post[x_bc + self.c[8]][8] = f_pre[x_bc][6] + self.INV_6 * ( u - v )
                else: # bc_id == 3
                    for q in ti.static(range(lbm.Q)):
                        inv_q = self.inv_idx[q]
                        f_post[x_bc + self.c[q]][q] = f_pre[x_bc][ inv_q ]

            else: # dim == 3
                k = x_bc[2]
                w = lbm.vel[x_bc][2]

                if i == 0 and j == 0 and k == 0:
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20]
                elif i == 0 and j == lbm.nd[1] - 1 and k == 0:
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24]
                elif i == 0 and j == 0 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22]
                elif i == 0 and j == lbm.nd[1] - 1 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26]
                elif i == lbm.nd[0] - 1 and j == 0 and k == 0:
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25]
                elif i == lbm.nd[0] - 1 and j == lbm.nd[1] - 1 and k == 0:
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21]
                elif i == lbm.nd[0] - 1 and j == 0 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23]
                elif i == lbm.nd[0] - 1 and j == lbm.nd[1] - 1 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19]
                elif i == 0 and k == 0:
                    f_post[x_bc + self.c[11]][11] = f_pre[x_bc][12]
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20]
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24]
                elif i == 0 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[13]][13] = f_pre[x_bc][14]
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22]
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26]
                elif i == lbm.nd[0] - 1 and k == 0:
                    f_post[x_bc + self.c[14]][14] = f_pre[x_bc][13]
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21]
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25]
                elif i == lbm.nd[0] - 1 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[12]][12] = f_pre[x_bc][11]
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19]
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23]
                elif j == 0 and k == 0:
                    f_post[x_bc + self.c[15]][15] = f_pre[x_bc][16]
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20]
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25]
                elif j == 0 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[17]][17] = f_pre[x_bc][18]
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22]
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23]
                elif j == lbm.nd[1] - 1 and k == 0:
                    f_post[x_bc + self.c[18]][18] = f_pre[x_bc][17]
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21]
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24]
                elif j == lbm.nd[1] - 1 and k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[16]][16] = f_pre[x_bc][15]
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19]
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26]
                elif i == 0:
                    f_post[x_bc + self.c[1]][1] = f_pre[x_bc][2] + 4 * self.INV_9 * ( u )
                    f_post[x_bc + self.c[7]][7] = f_pre[x_bc][8] + self.INV_9 * ( u + v )
                    f_post[x_bc + self.c[9]][9] = f_pre[x_bc][10] + self.INV_9 * ( u - v )
                    f_post[x_bc + self.c[11]][11] = f_pre[x_bc][12] + self.INV_9 * ( u + w )
                    f_post[x_bc + self.c[13]][13] = f_pre[x_bc][14] + self.INV_9 * ( u - w )
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20] + self.INV_36 * ( u + v + w )
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22] + self.INV_36 * ( u + v - w )
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24] + self.INV_36 * ( u - v + w )
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26] + self.INV_36 * ( u - v - w )
                elif i == lbm.nd[0] - 1:
                    f_post[x_bc + self.c[2]][2] = f_pre[x_bc][1] + 4 * self.INV_9 * ( -u )
                    f_post[x_bc + self.c[8]][8] = f_pre[x_bc][7] + self.INV_9 * ( -u - v )
                    f_post[x_bc + self.c[10]][10] = f_pre[x_bc][9] + self.INV_9 * ( -u + v )
                    f_post[x_bc + self.c[12]][12] = f_pre[x_bc][11] + self.INV_9 * ( -u - w )
                    f_post[x_bc + self.c[14]][14] = f_pre[x_bc][13] + self.INV_9 * ( -u + w )
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19] + self.INV_36 * ( -u - v - w )
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21] + self.INV_36 * ( -u - v + w )
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23] + self.INV_36 * ( -u + v - w )
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25] + self.INV_36 * ( -u + v + w )
                elif j == 0:
                    f_post[x_bc + self.c[3]][3] = f_pre[x_bc][4] + 4 * self.INV_9 * ( v )
                    f_post[x_bc + self.c[7]][7] = f_pre[x_bc][8] + self.INV_9 * ( u + v )
                    f_post[x_bc + self.c[10]][10] = f_pre[x_bc][9] + self.INV_9 * ( -u + v )
                    f_post[x_bc + self.c[15]][15] = f_pre[x_bc][16] + self.INV_9 * ( v + w )
                    f_post[x_bc + self.c[17]][17] = f_pre[x_bc][18] + self.INV_9 * ( v - w )
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20] + self.INV_36 * ( u + v + w )
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22] + self.INV_36 * ( u + v - w )
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23] + self.INV_36 * ( -u + v - w )
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25] + self.INV_36 * ( -u + v + w )
                elif j == lbm.nd[1] - 1:
                    f_post[x_bc + self.c[4]][4] = f_pre[x_bc][3] + 4 * self.INV_9 * ( -v )
                    f_post[x_bc + self.c[8]][8] = f_pre[x_bc][7] + self.INV_9 * ( -u - v )
                    f_post[x_bc + self.c[9]][9] = f_pre[x_bc][10] + self.INV_9 * ( u - v )
                    f_post[x_bc + self.c[16]][16] = f_pre[x_bc][15] + self.INV_9 * ( -v - w )
                    f_post[x_bc + self.c[18]][18] = f_pre[x_bc][17] + self.INV_9 * ( -v + w )
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19] + self.INV_36 * ( -u - v - w )
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21] + self.INV_36 * ( -u - v + w )
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24] + self.INV_36 * ( u - v + w )
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26] + self.INV_36 * ( u - v - w )
                elif k == 0:
                    f_post[x_bc + self.c[5]][5] = f_pre[x_bc][6] + 4 * self.INV_9 * ( w )
                    f_post[x_bc + self.c[11]][11] = f_pre[x_bc][12] + self.INV_9 * ( u + w )
                    f_post[x_bc + self.c[14]][14] = f_pre[x_bc][13] + self.INV_9 * ( -u + w )
                    f_post[x_bc + self.c[15]][15] = f_pre[x_bc][16] + self.INV_9 * ( v + w )
                    f_post[x_bc + self.c[18]][18] = f_pre[x_bc][17] + self.INV_9 * ( -v + w )
                    f_post[x_bc + self.c[19]][19] = f_pre[x_bc][20] + self.INV_36 * ( u + v + w )
                    f_post[x_bc + self.c[22]][22] = f_pre[x_bc][21] + self.INV_36 * ( -u - v + w )
                    f_post[x_bc + self.c[23]][23] = f_pre[x_bc][24] + self.INV_36 * ( u - v + w )
                    f_post[x_bc + self.c[26]][26] = f_pre[x_bc][25] + self.INV_36 * ( -u + v + w )
                elif k == lbm.nd[2] - 1:
                    f_post[x_bc + self.c[6]][6] = f_pre[x_bc][5] + 4 * self.INV_9 * ( -w )
                    f_post[x_bc + self.c[12]][12] = f_pre[x_bc][11] + self.INV_9 * ( -u - w )
                    f_post[x_bc + self.c[13]][13] = f_pre[x_bc][14] + self.INV_9 * ( u - w )
                    f_post[x_bc + self.c[16]][16] = f_pre[x_bc][15] + self.INV_9 * ( -v - w )
                    f_post[x_bc + self.c[17]][17] = f_pre[x_bc][18] + self.INV_9 * ( v - w )
                    f_post[x_bc + self.c[20]][20] = f_pre[x_bc][19] + self.INV_36 * ( -u - v - w )
                    f_post[x_bc + self.c[21]][21] = f_pre[x_bc][22] + self.INV_36 * ( u + v - w )
                    f_post[x_bc + self.c[24]][24] = f_pre[x_bc][23] + self.INV_36 * ( -u + v - w )
                    f_post[x_bc + self.c[25]][25] = f_pre[x_bc][26] + self.INV_36 * ( u - v - w )
                else: # bc_id == 3
                    for q in ti.static(range(lbm.Q)):
                        inv_q = self.inv_idx[q]
                        f_post[x_bc + self.c[q]][q] = f_pre[x_bc][ inv_q ]
