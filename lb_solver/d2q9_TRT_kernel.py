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

            # CSE expressions of macroscopic variables and f_eq
            xm0 = f1 + f8
            xm1 = f2 + f6
            xm2 = f0 + f3 + f4 + f5 + f7 + xm0 + xm1
            xm3 = 1/xm2
            xm4 = f5 - f7
            rho = xm2
            u = xm3*(-f3 - f6 + xm0 + xm4)
            v = xm3*(-f4 - f8 + xm1 + xm4)
            xe0 = f5 - f7
            xe1 = f2 + f6
            xe2 = -f4 - f8 + xe0 + xe1
            xe3 = xe2**2
            xe4 = f1 + f8
            xe5 = f0 + f3 + f4 + f5 + f7 + xe1 + xe4
            xe6 = xe5**(-2)
            xe7 = 3*xe6 * 0.5
            xe8 = xe3*xe7
            xe9 = -f3 - f6 + xe0 + xe4
            xe10 = xe9**2
            xe11 = xe10*xe7
            xe12 = xe11 - 1
            xe13 = xe12 + xe8
            xe14 = f0 * self.INV_9 + f1 * self.INV_9 + f2 * self.INV_9 + f3 * self.INV_9 + f4 * self.INV_9 + f5 * self.INV_9 + f6 * self.INV_9 + f7 * self.INV_9 + f8 * self.INV_9
            xe15 = 1/xe5
            xe16 = xe15*xe9
            xe17 = 3*xe16
            xe18 = 3*xe6
            xe19 = 1 - xe8
            xe20 = xe10*xe18 + xe19
            xe21 = xe15*xe2
            xe22 = 3*xe21
            xe23 = -xe11
            xe24 = xe22 + xe23
            xe25 = -xe17
            xe26 = f0 * self.INV_36 + f1 * self.INV_36 + f2 * self.INV_36 + f3 * self.INV_36 + f4 * self.INV_36 + f5 * self.INV_36 + f6 * self.INV_36 + f7 * self.INV_36 + f8 * self.INV_36
            xe27 = xe16 + xe21
            xe28 = xe19 + xe24
            xe29 = xe16 - xe21
            feq0 = -xe13*(4*f0 * self.INV_9 + 4*f1 * self.INV_9 + 4*f2 * self.INV_9 + 4*f3 * self.INV_9 + 4*f4 * self.INV_9 + 4*f5 * self.INV_9 + 4*f6 * self.INV_9 + 4*f7 * self.INV_9 + 4*f8 * self.INV_9)
            feq1 = xe14*(xe17 + xe20)
            feq2 = xe14*(xe18*xe3 + xe24 + 1)
            feq3 = xe14*(xe20 + xe25)
            feq4 = xe14*(-xe12 - xe22 + 3*xe3*xe6)
            feq5 = xe26*(xe17 + 9*xe27**2 * 0.5 + xe28)
            feq6 = xe26*(xe25 + xe28 + 9*xe29**2 * 0.5)
            feq7 = xe26*(-xe13 - xe17 - xe22 + 9*xe27**2 * 0.5)
            feq8 = xe26*(xe17 + xe19 - xe22 + xe23 + 9*xe29**2 * 0.5)
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
        self.INV_36 = 1.0/36.0
