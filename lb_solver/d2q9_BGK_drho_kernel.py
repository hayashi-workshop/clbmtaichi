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
            x0 = f1 + f8
            x1 = f2 + f6
            x2 = f0 + f3 + f4 + f5 + f7 + x0 + x1
            x3 = f5 - f7
            x4 = -f3 - f6 + x0 + x3
            x5 = x2 + 1
            x6 = 1/x5
            x7 = x4*x6
            x8 = -f4 - f8 + x1 + x3
            x9 = x6*x8
            x10 = x8**2
            x11 = x5**(-2)
            x12 = 3*x11 * 0.5
            x13 = x10*x12
            x14 = x4**2
            x15 = x12*x14
            x16 = x15 - 1
            x17 = x13 + x16
            x18 = 3*x7
            x19 = 3*x11
            x20 = 1 - x13
            x21 = x14*x19 + x20
            x22 = 3*x9
            x23 = -x15
            x24 = x22 + x23
            x25 = -x18
            x26 = x7 + x9
            x27 = x20 + x24
            x28 = x7 - x9
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 + lbm.omega[1]*(-f0 - 4*x17*x5 * self.INV_9 - 4 * self.INV_9)
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 + x5*(x18 + x21) * self.INV_9 - self.INV_9)
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f2 + x5*(x10*x19 + x24 + 1) * self.INV_9 - self.INV_9)
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f3 + x5*(x21 + x25) * self.INV_9 - self.INV_9)
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f4 + x5*(3*x10*x11 - x16 - x22) * self.INV_9 - self.INV_9)
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 + x5*(x18 + 9*x26**2 * 0.5 + x27) * self.INV_36 - self.INV_36)
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f6 + x5*(x25 + x27 + 9*x28**2 * 0.5) * self.INV_36 - self.INV_36)
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f7 + x5*(-x17 - x18 - x22 + 9*x26**2 * 0.5) * self.INV_36 - self.INV_36)
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f8 + x5*(x18 + x20 - x22 + x23 + 9*x28**2 * 0.5) * self.INV_36 - self.INV_36)
            lbm.rho[I] = x2 # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = x7
            lbm.vel[I][1] = x9

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
