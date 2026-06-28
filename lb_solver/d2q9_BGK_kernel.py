# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D2Q9
# Model: BGK
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
            x0 = f1 + f8
            x1 = f2 + f6
            x2 = f0 + f3 + f4 + f5 + f7 + x0 + x1
            x3 = 1/x2
            x4 = f5 - f7
            x5 = -f3 - f6 + x0 + x4
            x6 = x3*x5
            x7 = -f4 - f8 + x1 + x4
            x8 = x3*x7
            x9 = x7**2
            x10 = x2**(-2)
            x11 = 3*x10 * 0.5
            x12 = x11*x9
            x13 = x5**2
            x14 = x11*x13
            x15 = x14 - 1
            x16 = x12 + x15
            x17 = f0 * self.INV_9 + f1 * self.INV_9 + f2 * self.INV_9 + f3 * self.INV_9 + f4 * self.INV_9 + f5 * self.INV_9 + f6 * self.INV_9 + f7 * self.INV_9 + f8 * self.INV_9
            x18 = 3*x6
            x19 = 3*x10
            x20 = 1 - x12
            x21 = x13*x19 + x20
            x22 = 3*x8
            x23 = -x14
            x24 = x22 + x23
            x25 = -x18
            x26 = f0 * self.INV_36 + f1 * self.INV_36 + f2 * self.INV_36 + f3 * self.INV_36 + f4 * self.INV_36 + f5 * self.INV_36 + f6 * self.INV_36 + f7 * self.INV_36 + f8 * self.INV_36
            x27 = x6 + x8
            x28 = x20 + x24
            x29 = x6 - x8
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 + lbm.omega[1]*(-f0 - x16*(4*f0 * self.INV_9 + 4*f1 * self.INV_9 + 4*f2 * self.INV_9 + 4*f3 * self.INV_9 + 4*f4 * self.INV_9 + 4*f5 * self.INV_9 + 4*f6 * self.INV_9 + 4*f7 * self.INV_9 + 4*f8 * self.INV_9))
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 + x17*(x18 + x21))
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f2 + x17*(x19*x9 + x24 + 1))
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f3 + x17*(x21 + x25))
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f4 + x17*(3*x10*x9 - x15 - x22))
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 + x26*(x18 + 9*x27**2 * 0.5 + x28))
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f6 + x26*(x25 + x28 + 9*x29**2 * 0.5))
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f7 + x26*(-x16 - x18 - x22 + 9*x27**2 * 0.5))
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f8 + x26*(x18 + x20 - x22 + x23 + 9*x29**2 * 0.5))
            lbm.rho[I] = x2 # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = x6
            lbm.vel[I][1] = x8

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
