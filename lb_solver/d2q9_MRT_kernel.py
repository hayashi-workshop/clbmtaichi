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
        self.density_shift = 0.0
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
            inv_rho = 1.0 / rho
            u = m10 * inv_rho
            v = m01 * inv_rho

            # Equilibrium moments (m_eq)
            x0 = rho*v
            x1 = rho*u**2
            x2 = v**2
            x3 = rho*x2
            m11_eq = u*x0
            m21_eq = v*x1 + x0 * self.INV_3
            m12_eq = rho*u * self.INV_3 + u*x3
            m22_eq = rho * self.INV_9 + x1*x2 + x1 * self.INV_3 + x3 * self.INV_3
            mP_eq = 2*rho * self.INV_3 + x1 + x3
            mxx_eq = x1 - x3

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

        xeq0 = v**2
        xeq1 = 3*xeq0 * 0.5
        xeq2 = u**2
        xeq3 = 3*xeq2 * 0.5
        xeq4 = xeq3 - 1
        xeq5 = xeq1 + xeq4
        xeq6 = 3*u
        xeq7 = -xeq1
        xeq8 = 3*xeq2 + xeq7 + 1
        xeq9 = rho * self.INV_9
        xeq10 = 3*v
        xeq11 = xeq10 - xeq3 + 1
        xeq12 = -xeq6
        xeq13 = u + v
        xeq14 = rho * self.INV_36
        xeq15 = u - v
        xeq16 = xeq5 + xeq6

        return ti.Vector([
            -4*rho*xeq5 * self.INV_9,
            xeq9*(xeq6 + xeq8),
            xeq9*(3*xeq0 + xeq11),
            xeq9*(xeq12 + xeq8),
            xeq9*(3*xeq0 - xeq10 - xeq4),
            xeq14*(xeq11 + 9*xeq13**2 * 0.5 + xeq6 + xeq7),
            xeq14*(xeq10 + 9*xeq15**2 * 0.5 - xeq16),
            xeq14*(-xeq10 + 9*xeq13**2 * 0.5 - xeq16),
            xeq14*(-xeq10 - xeq12 + 9*xeq15**2 * 0.5 - xeq5),
        ])

    def _set_rational(self):
        self.INV_9 = 1.0/9.0
        self.INV_3 = 1.0/3.0
        self.INV_36 = 1.0/36.0
