# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D2Q9
# Model: Cumulant
# Some intermediate variable names are inspired by the naming conventions used in lbmpy.
# ======================================================================================

import taichi as ti
import taichi.math as tm

#weights = ti.types.vector(9, float)([4.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 9.0, 1.0 / 36.0, 1.0 / 36.0, 1.0 / 36.0, 1.0 / 36.0])
c = (ti.Vector([0, 0]), ti.Vector([1, 0]), ti.Vector([0, 1]), ti.Vector([-1, 0]), ti.Vector([0, -1]), ti.Vector([1, 1]), ti.Vector([-1, 1]), ti.Vector([-1, -1]), ti.Vector([1, -1]))

@ti.data_oriented
class ModelConfig:
    def __init__(self, mode="pull"):
        self.density_shift = 1.0
        self._set_rational()
        self.pop = 1 if mode == "push" else 0 # pull or push
        print(f"mode: {mode} - pop {self.pop}")


    @ti.kernel
    def col_stream_core(self, lbm: ti.template(), f_pre: ti.template(), f_post: ti.template()):
        for i, j in ti.ndrange((ti.static(self.pop), ti.static(lbm.nd[0] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[1] - self.pop))):
            I = ti.Vector([i, j])
            # Fetch f
            f0 = f_pre[I + c[0]*ti.static(self.pop-1)][0]
            f1 = f_pre[I + c[1]*ti.static(self.pop-1)][1]
            f2 = f_pre[I + c[2]*ti.static(self.pop-1)][2]
            f3 = f_pre[I + c[3]*ti.static(self.pop-1)][3]
            f4 = f_pre[I + c[4]*ti.static(self.pop-1)][4]
            f5 = f_pre[I + c[5]*ti.static(self.pop-1)][5]
            f6 = f_pre[I + c[6]*ti.static(self.pop-1)][6]
            f7 = f_pre[I + c[7]*ti.static(self.pop-1)][7]
            f8 = f_pre[I + c[8]*ti.static(self.pop-1)][8]

            xm0 = f1 + f8
            xm1 = f2 + f6
            xm2 = f0 + f3 + f4 + f5 + f7 + xm0 + xm1
            xm3 = f5 - f7
            xm4 = 1/(xm2 + 1)
            rho = xm2 + 1 # real (un-shifted) density
            u = xm4*(-f3 - f6 + xm0 + xm3)
            v = xm4*(-f4 - f8 + xm1 + xm3)
            inv_rho = 1.0 / rho
            # forward chimera transform & macroscopic quantities
            chimera_m_m1_c_0 = f3 + f6 + f7
            chimera_m_m1_c_1 = f6 - f7
            chimera_m_m1_c_2 = f6 + f7
            chimera_m_0_c_0 = f0 + f2 + f4
            chimera_m_0_c_1 = f2 - f4
            chimera_m_0_c_2 = f2 + f4
            chimera_m_1_c_0 = f1 + f5 + f8
            chimera_m_1_c_1 = f5 - f8
            chimera_m_1_c_2 = f5 + f8
            m20 = chimera_m_1_c_0 + chimera_m_m1_c_0 + self.INV_3
            kappa20 = m20 - rho*u**2
            m11 = chimera_m_1_c_1 - chimera_m_m1_c_1
            kappa11 = m11 - rho*u*v
            m02 = chimera_m_0_c_2 + chimera_m_1_c_2 + chimera_m_m1_c_2 + self.INV_3
            kappa02 = m02 - rho*v**2
            m21 = chimera_m_1_c_1 + chimera_m_m1_c_1
            kappa21 = -2*kappa11*u - kappa20*v + m21 - rho*u**2*v
            m12 = chimera_m_1_c_2 - chimera_m_m1_c_2
            kappa12 = -kappa02*u - 2*kappa11*v + m12 - rho*u*v**2
            kappa11_post = -kappa11*lbm.omega[1] + kappa11
            kappa20_post = kappa02*lbm.omega[1] * 0.5 - kappa02*lbm.omega[2] * 0.5 - kappa20*lbm.omega[1] * 0.5 - kappa20*lbm.omega[2] * 0.5 + kappa20 + lbm.omega[2]*rho * self.INV_3
            kappa02_post = -kappa02*lbm.omega[1] * 0.5 - kappa02*lbm.omega[2] * 0.5 + kappa02 + kappa20*lbm.omega[1] * 0.5 - kappa20*lbm.omega[2] * 0.5 + lbm.omega[2]*rho * self.INV_3
            kappa21_post = -kappa21*lbm.omega[3] + kappa21
            kappa12_post = -kappa12*lbm.omega[3] + kappa12
            m22 = chimera_m_1_c_2 + chimera_m_m1_c_2 + self.INV_9
            kappa22 = -2*kappa12*u - 2*kappa21*v + m22 - rho*u**2*v**2
            C22 = -kappa02*kappa20 * inv_rho - 2*kappa11**2 * inv_rho + kappa22
            C22_post = -C22*lbm.omega[6] + C22
            kappa22_post = C22_post + kappa02_post*kappa20_post * inv_rho + 2*kappa11_post**2 * inv_rho
            m_post_idx_0_c_0 = rho
            m_post_idx_0_c_1 = rho*v
            m_post_idx_0_c_2 = kappa02_post + rho*v**2
            m_post_idx_1_c_1 = kappa11_post
            m_post_idx_1_c_2 = 2*kappa11_post*v + kappa12_post
            m_post_idx_2_c_0 = kappa20_post
            m_post_idx_2_c_1 = kappa20_post*v + kappa21_post
            m_post_idx_2_c_2 = kappa20_post*v**2 + 2*kappa21_post*v + kappa22_post
            m00_post = m_post_idx_0_c_0 - 1
            m01_post = m_post_idx_0_c_1
            m02_post = m_post_idx_0_c_2 - self.INV_3
            m10_post = m_post_idx_0_c_0*u
            m11_post = m_post_idx_0_c_1*u + m_post_idx_1_c_1
            m12_post = m_post_idx_0_c_2*u + m_post_idx_1_c_2
            m20_post = m_post_idx_0_c_0*u**2 + m_post_idx_2_c_0 - self.INV_3
            m21_post = m_post_idx_0_c_1*u**2 + 2*m_post_idx_1_c_1*u + m_post_idx_2_c_1
            m22_post = m_post_idx_0_c_2*u**2 + 2*m_post_idx_1_c_2*u + m_post_idx_2_c_2 - self.INV_9
            chimera_m_post_0_0 = m00_post - m20_post
            chimera_m_post_m1_0 = -m10_post * 0.5 + m20_post * 0.5
            chimera_m_post_1_0 = m10_post * 0.5 + m20_post * 0.5
            chimera_m_post_0_1 = m01_post - m21_post
            chimera_m_post_m1_1 = -m11_post * 0.5 + m21_post * 0.5
            chimera_m_post_1_1 = m11_post * 0.5 + m21_post * 0.5
            chimera_m_post_0_2 = m02_post - m22_post
            chimera_m_post_m1_2 = -m12_post * 0.5 + m22_post * 0.5
            chimera_m_post_1_2 = m12_post * 0.5 + m22_post * 0.5
            f_post[I + c[0]*ti.static(self.pop)][0] = chimera_m_post_0_0 - chimera_m_post_0_2
            f_post[I + c[1]*ti.static(self.pop)][1] = chimera_m_post_1_0 - chimera_m_post_1_2
            f_post[I + c[2]*ti.static(self.pop)][2] = chimera_m_post_0_1 * 0.5 + chimera_m_post_0_2 * 0.5
            f_post[I + c[3]*ti.static(self.pop)][3] = chimera_m_post_m1_0 - chimera_m_post_m1_2
            f_post[I + c[4]*ti.static(self.pop)][4] = -chimera_m_post_0_1 * 0.5 + chimera_m_post_0_2 * 0.5
            f_post[I + c[5]*ti.static(self.pop)][5] = chimera_m_post_1_1 * 0.5 + chimera_m_post_1_2 * 0.5
            f_post[I + c[6]*ti.static(self.pop)][6] = chimera_m_post_m1_1 * 0.5 + chimera_m_post_m1_2 * 0.5
            f_post[I + c[7]*ti.static(self.pop)][7] = -chimera_m_post_m1_1 * 0.5 + chimera_m_post_m1_2 * 0.5
            f_post[I + c[8]*ti.static(self.pop)][8] = -chimera_m_post_1_1 * 0.5 + chimera_m_post_1_2 * 0.5

            # update arrays of macroscopic vars
            lbm.rho[I] = xm2
            lbm.vel[I][0] = u
            lbm.vel[I][1] = v

    @ti.func
    def f_eq(self, lbm, I):
        rho = lbm.rho[I] # <- note: actual value stored here is rho - density_shift
        u = lbm.vel[I][0]
        v = lbm.vel[I][1]

        xeq0 = rho + 1
        xeq1 = v**2
        xeq2 = 3*xeq1 * 0.5
        xeq3 = u**2
        xeq4 = 3*xeq3 * 0.5
        xeq5 = xeq4 - 1
        xeq6 = xeq2 + xeq5
        xeq7 = 3*u
        xeq8 = -xeq2
        xeq9 = 3*xeq3 + xeq8 + 1
        xeq10 = xeq0 * self.INV_9
        xeq11 = 3*v
        xeq12 = xeq11 - xeq4 + 1
        xeq13 = -xeq7
        xeq14 = u + v
        xeq15 = xeq0 * self.INV_36
        xeq16 = u - v
        xeq17 = xeq6 + xeq7

        return ti.Vector([
            -4*xeq0*xeq6 * self.INV_9 - 4 * self.INV_9,
            xeq10*(xeq7 + xeq9) - self.INV_9,
            xeq10*(3*xeq1 + xeq12) - self.INV_9,
            xeq10*(xeq13 + xeq9) - self.INV_9,
            xeq10*(3*xeq1 - xeq11 - xeq5) - self.INV_9,
            xeq15*(xeq12 + 9*xeq14**2 * 0.5 + xeq7 + xeq8) - self.INV_36,
            xeq15*(xeq11 + 9*xeq16**2 * 0.5 - xeq17) - self.INV_36,
            xeq15*(-xeq11 + 9*xeq14**2 * 0.5 - xeq17) - self.INV_36,
            xeq15*(-xeq11 - xeq13 + 9*xeq16**2 * 0.5 - xeq6) - self.INV_36,
        ])

    def _set_rational(self):
        self.INV_9 = 1.0/9.0
        self.INV_3 = 1.0/3.0
        self.INV_36 = 1.0/36.0
