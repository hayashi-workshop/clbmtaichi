# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D2Q9
# Model: MRT
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

            # 1) Forward transformation from f to raw moment
            x0 = f5 + f8
            x1 = f6 + f7 + x0
            x2 = f1 + f3 + x1
            x3 = f2 + f4
            x4 = -f6
            x5 = -f7
            x6 = x0 + x4 + x5
            x7 = f5 - f8
            x8 = f6 + x5 + x7
            m00 = f0 + x2 + x3
            m10 = f1 - f3 + x6
            m01 = f2 - f4 + x8
            m20 = x2
            m11 = f7 + x4 + x7
            m02 = x1 + x3
            m21 = x8
            m12 = x6
            m22 = x1

            rho = m00
            inv_rho = 1.0 / (rho + 1)
            u = m10 * inv_rho
            v = m01 * inv_rho

            # Equilibrium moments (m_eq)
            x0 = u*v
            x1 = v * self.INV_3
            x2 = u**2
            x3 = v*x2
            x4 = u * self.INV_3
            x5 = v**2
            x6 = u*x5
            x7 = x2 * self.INV_3
            x8 = x5 * self.INV_3
            x9 = x2*x5
            x10 = rho*x5
            x11 = rho*x2 + x2
            m11_eq = rho*x0 + x0
            m21_eq = rho*x1 + rho*x3 + x1 + x3
            m12_eq = rho*x4 + rho*x6 + x4 + x6
            m22_eq = rho*x7 + rho*x8 + rho*x9 + rho * self.INV_9 + x7 + x8 + x9
            mP_eq = 2*rho * self.INV_3 + x10 + x11 + x5
            mxx_eq = -x10 + x11 - x5

            # 2) Collision/relaxation in moment space
            m00_post = m00
            m10_post = m10
            m01_post = m01
            m20_post = lbm.omega[1]*(m02 - m20 + mxx_eq) * 0.5 + lbm.omega[2]*(-m02 - m20 + mP_eq) * 0.5 + m20
            m11_post = lbm.omega[1]*(-m11 + m11_eq) + m11
            m02_post = -lbm.omega[1]*(m02 - m20 + mxx_eq) * 0.5 + lbm.omega[2]*(-m02 - m20 + mP_eq) * 0.5 + m02
            m21_post = lbm.omega[3]*(-m21 + m21_eq) + m21
            m12_post = lbm.omega[3]*(-m12 + m12_eq) + m12
            m22_post = lbm.omega[6]*(-m22 + m22_eq) + m22

            # 3) Backward transformation from m to f
            inv_x0 = m22_post * 0.5
            inv_x1 = -inv_x0
            inv_x2 = (m10_post - m12_post) * 0.5
            inv_x3 = (m01_post - m21_post) * 0.5
            inv_x4 = m21_post * 0.25
            inv_x5 = m22_post * 0.25
            inv_x6 = m11_post * 0.25
            inv_x7 = m12_post * 0.25
            inv_x8 = inv_x6 + inv_x7
            inv_x9 = -inv_x4
            inv_x10 = -m22_post * 0.25
            inv_x11 = inv_x6 - inv_x7
            f_post[I + c[0]*ti.static(self.pop)][0] = m00_post - m02_post - m20_post + m22_post
            f_post[I + c[1]*ti.static(self.pop)][1] = m20_post * 0.5 + inv_x1 + inv_x2
            f_post[I + c[2]*ti.static(self.pop)][2] = m02_post * 0.5 + inv_x1 + inv_x3
            f_post[I + c[3]*ti.static(self.pop)][3] = m20_post * 0.5 - inv_x0 - inv_x2
            f_post[I + c[4]*ti.static(self.pop)][4] = m02_post * 0.5 - inv_x0 - inv_x3
            f_post[I + c[5]*ti.static(self.pop)][5] = inv_x4 + inv_x5 + inv_x8
            f_post[I + c[6]*ti.static(self.pop)][6] = -inv_x10 - inv_x8 - inv_x9
            f_post[I + c[7]*ti.static(self.pop)][7] = inv_x11 + inv_x5 + inv_x9
            f_post[I + c[8]*ti.static(self.pop)][8] = -inv_x10 - inv_x11 - inv_x4

            # 4) Update arrays of macroscopic vars
            lbm.rho[I] = rho # <- note: actual value stored here is rho - density_shift
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
