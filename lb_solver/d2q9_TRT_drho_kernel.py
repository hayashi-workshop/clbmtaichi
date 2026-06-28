# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D2Q9
# Model: TRT
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

            # CSE expressions of macroscopic variables and f_eq
            xm0 = f1 + f8
            xm1 = f2 + f6
            xm2 = f0 + f3 + f4 + f5 + f7 + xm0 + xm1
            xm3 = f5 - f7
            xm4 = 1/(xm2 + 1)
            rho = xm2
            u = xm4*(-f3 - f6 + xm0 + xm3)
            v = xm4*(-f4 - f8 + xm1 + xm3)
            xe0 = f1 + f8
            xe1 = f2 + f6
            xe2 = f0 + f3 + f4 + f5 + f7 + xe0 + xe1 + 1
            xe3 = f5 - f7
            xe4 = -f4 - f8 + xe1 + xe3
            xe5 = xe4**2
            xe6 = xe2**(-2)
            xe7 = 3*xe6 * 0.5
            xe8 = xe5*xe7
            xe9 = -f3 - f6 + xe0 + xe3
            xe10 = xe9**2
            xe11 = xe10*xe7
            xe12 = xe11 - 1
            xe13 = xe12 + xe8
            xe14 = 1/xe2
            xe15 = xe14*xe9
            xe16 = 3*xe15
            xe17 = 3*xe6
            xe18 = 1 - xe8
            xe19 = xe10*xe17 + xe18
            xe20 = xe2 * self.INV_9
            xe21 = xe14*xe4
            xe22 = 3*xe21
            xe23 = -xe11
            xe24 = xe22 + xe23
            xe25 = -xe16
            xe26 = xe15 + xe21
            xe27 = xe18 + xe24
            xe28 = xe2 * self.INV_36
            xe29 = xe15 - xe21
            feq0 = -4*xe13*xe2 * self.INV_9 - 4 * self.INV_9
            feq1 = xe20*(xe16 + xe19) - self.INV_9
            feq2 = xe20*(xe17*xe5 + xe24 + 1) - self.INV_9
            feq3 = xe20*(xe19 + xe25) - self.INV_9
            feq4 = xe20*(-xe12 - xe22 + 3*xe5*xe6) - self.INV_9
            feq5 = xe28*(xe16 + 9*xe26**2 * 0.5 + xe27) - self.INV_36
            feq6 = xe28*(xe25 + xe27 + 9*xe29**2 * 0.5) - self.INV_36
            feq7 = xe28*(-xe13 - xe16 - xe22 + 9*xe26**2 * 0.5) - self.INV_36
            feq8 = xe28*(xe16 + xe18 - xe22 + xe23 + 9*xe29**2 * 0.5) - self.INV_36
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 - lbm.omega[1]*(f0 - feq0)
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 - f3 + feq1 + feq3) * 0.5 + lbm.omega[2]*(-f1 + f3 + feq1 - feq3) * 0.5
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f2 - f4 + feq2 + feq4) * 0.5 + lbm.omega[2]*(-f2 + f4 + feq2 - feq4) * 0.5
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f1 - f3 + feq1 + feq3) * 0.5 - lbm.omega[2]*(-f1 + f3 + feq1 - feq3) * 0.5
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f2 - f4 + feq2 + feq4) * 0.5 - lbm.omega[2]*(-f2 + f4 + feq2 - feq4) * 0.5
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 - f7 + feq5 + feq7) * 0.5 + lbm.omega[2]*(-f5 + f7 + feq5 - feq7) * 0.5
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f6 - f8 + feq6 + feq8) * 0.5 + lbm.omega[2]*(-f6 + f8 + feq6 - feq8) * 0.5
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f5 - f7 + feq5 + feq7) * 0.5 - lbm.omega[2]*(-f5 + f7 + feq5 - feq7) * 0.5
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f6 - f8 + feq6 + feq8) * 0.5 - lbm.omega[2]*(-f6 + f8 + feq6 - feq8) * 0.5

            # Update arrays of macroscopic vars
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
        self.INV_36 = 1.0/36.0
