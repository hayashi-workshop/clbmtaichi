# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D3Q27
# Model: BGK
# ======================================================================================

import taichi as ti
import taichi.math as tm

#weights = ti.types.vector(27, float)([8.0 / 27.0, 2.0 / 27.0, 2.0 / 27.0, 2.0 / 27.0, 2.0 / 27.0, 2.0 / 27.0, 2.0 / 27.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 54.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0, 1.0 / 216.0])
c = (ti.Vector([0, 0, 0]), ti.Vector([1, 0, 0]), ti.Vector([-1, 0, 0]), ti.Vector([0, 1, 0]), ti.Vector([0, -1, 0]), ti.Vector([0, 0, 1]), ti.Vector([0, 0, -1]), ti.Vector([1, 1, 0]), ti.Vector([-1, -1, 0]), ti.Vector([1, -1, 0]), ti.Vector([-1, 1, 0]), ti.Vector([1, 0, 1]), ti.Vector([-1, 0, -1]), ti.Vector([1, 0, -1]), ti.Vector([-1, 0, 1]), ti.Vector([0, 1, 1]), ti.Vector([0, -1, -1]), ti.Vector([0, 1, -1]), ti.Vector([0, -1, 1]), ti.Vector([1, 1, 1]), ti.Vector([-1, -1, -1]), ti.Vector([1, 1, -1]), ti.Vector([-1, -1, 1]), ti.Vector([1, -1, 1]), ti.Vector([-1, 1, -1]), ti.Vector([1, -1, -1]), ti.Vector([-1, 1, 1]))

@ti.data_oriented
class ModelConfig:
    def __init__(self, mode="pull"):
        self.density_shift = 0.0
        self._set_rational()
        self.pop = 1 if mode == "push" else 0 # pull or push
        print(f"mode: {mode} - pop {self.pop}")


    @ti.kernel
    def col_stream_core(self, lbm: ti.template(), f_pre: ti.template(), f_post: ti.template()):
        for i, j, k in ti.ndrange((ti.static(self.pop), ti.static(lbm.nd[0] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[1] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[2] - self.pop))):
            I = ti.Vector([i, j, k])
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
            f9 = f_pre[I + c[9]*ti.static(self.pop-1)][9]
            f10 = f_pre[I + c[10]*ti.static(self.pop-1)][10]
            f11 = f_pre[I + c[11]*ti.static(self.pop-1)][11]
            f12 = f_pre[I + c[12]*ti.static(self.pop-1)][12]
            f13 = f_pre[I + c[13]*ti.static(self.pop-1)][13]
            f14 = f_pre[I + c[14]*ti.static(self.pop-1)][14]
            f15 = f_pre[I + c[15]*ti.static(self.pop-1)][15]
            f16 = f_pre[I + c[16]*ti.static(self.pop-1)][16]
            f17 = f_pre[I + c[17]*ti.static(self.pop-1)][17]
            f18 = f_pre[I + c[18]*ti.static(self.pop-1)][18]
            f19 = f_pre[I + c[19]*ti.static(self.pop-1)][19]
            f20 = f_pre[I + c[20]*ti.static(self.pop-1)][20]
            f21 = f_pre[I + c[21]*ti.static(self.pop-1)][21]
            f22 = f_pre[I + c[22]*ti.static(self.pop-1)][22]
            f23 = f_pre[I + c[23]*ti.static(self.pop-1)][23]
            f24 = f_pre[I + c[24]*ti.static(self.pop-1)][24]
            f25 = f_pre[I + c[25]*ti.static(self.pop-1)][25]
            f26 = f_pre[I + c[26]*ti.static(self.pop-1)][26]

            # CSE expressions of macroscopic variables and f_eq
            x0 = f1 + f13 + f25 + f9
            x1 = f10 + f17 + f24 + f3
            x2 = f14 + f18 + f19 + f22 + f5
            x3 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + x0 + x1 + x2
            x4 = 1/x3
            x5 = -f20
            x6 = f19 + f21 - f22 + f7 - f8 + x5
            x7 = f11 - f12 + f23 - f24
            x8 = -f10 - f14 - f2 - f26 + x0 + x6 + x7
            x9 = x4*x8
            x10 = f15 - f16 - f25 + f26
            x11 = -f18 - f23 - f4 - f9 + x1 + x10 + x6
            x12 = x11*x4
            x13 = -f13 - f17 - f21 - f6 + x10 + x2 + x5 + x7
            x14 = x13*x4
            x15 = x8**2
            x16 = x3**(-2)
            x17 = 3*x16 * 0.5
            x18 = x15*x17
            x19 = x11**2
            x20 = x17*x19
            x21 = x13**2
            x22 = x17*x21
            x23 = x20 + x22 - 1
            x24 = x18 + x23
            x25 = 2*f0 * self.INV_27 + 2*f1 * self.INV_27 + 2*f10 * self.INV_27 + 2*f11 * self.INV_27 + 2*f12 * self.INV_27 + 2*f13 * self.INV_27 + 2*f14 * self.INV_27 + 2*f15 * self.INV_27 + 2*f16 * self.INV_27 + 2*f17 * self.INV_27 + 2*f18 * self.INV_27 + 2*f19 * self.INV_27 + 2*f2 * self.INV_27 + 2*f20 * self.INV_27 + 2*f21 * self.INV_27 + 2*f22 * self.INV_27 + 2*f23 * self.INV_27 + 2*f24 * self.INV_27 + 2*f25 * self.INV_27 + 2*f26 * self.INV_27 + 2*f3 * self.INV_27 + 2*f4 * self.INV_27 + 2*f5 * self.INV_27 + 2*f6 * self.INV_27 + 2*f7 * self.INV_27 + 2*f8 * self.INV_27 + 2*f9 * self.INV_27
            x26 = 3*x16
            x27 = 3*x9
            x28 = -x20
            x29 = 1 - x22
            x30 = x28 + x29
            x31 = x27 + x30
            x32 = 3*x12
            x33 = -x18
            x34 = x32 + x33
            x35 = x18 - 1
            x36 = 3*x14
            x37 = x33 + x36
            x38 = f0 * self.INV_54 + f1 * self.INV_54 + f10 * self.INV_54 + f11 * self.INV_54 + f12 * self.INV_54 + f13 * self.INV_54 + f14 * self.INV_54 + f15 * self.INV_54 + f16 * self.INV_54 + f17 * self.INV_54 + f18 * self.INV_54 + f19 * self.INV_54 + f2 * self.INV_54 + f20 * self.INV_54 + f21 * self.INV_54 + f22 * self.INV_54 + f23 * self.INV_54 + f24 * self.INV_54 + f25 * self.INV_54 + f26 * self.INV_54 + f3 * self.INV_54 + f4 * self.INV_54 + f5 * self.INV_54 + f6 * self.INV_54 + f7 * self.INV_54 + f8 * self.INV_54 + f9 * self.INV_54
            x39 = x12 + x9
            x40 = x31 + x34
            x41 = x24 + x32
            x42 = x27 + x41
            x43 = -x12 + x9
            x44 = -x27
            x45 = x41 + x44
            x46 = -x32
            x47 = x24 + x27
            x48 = x46 + x47
            x49 = x14 + x9
            x50 = x31 + x37
            x51 = -x14
            x52 = x51 + x9
            x53 = x24 + x36
            x54 = -x36
            x55 = x12 + x14
            x56 = x30 + x34 + x36
            x57 = x12 + x51
            x58 = f0 * self.INV_216 + f1 * self.INV_216 + f10 * self.INV_216 + f11 * self.INV_216 + f12 * self.INV_216 + f13 * self.INV_216 + f14 * self.INV_216 + f15 * self.INV_216 + f16 * self.INV_216 + f17 * self.INV_216 + f18 * self.INV_216 + f19 * self.INV_216 + f2 * self.INV_216 + f20 * self.INV_216 + f21 * self.INV_216 + f22 * self.INV_216 + f23 * self.INV_216 + f24 * self.INV_216 + f25 * self.INV_216 + f26 * self.INV_216 + f3 * self.INV_216 + f4 * self.INV_216 + f5 * self.INV_216 + f6 * self.INV_216 + f7 * self.INV_216 + f8 * self.INV_216 + f9 * self.INV_216
            x59 = x14 + x39
            x60 = x39 + x51
            x61 = x14 + x43
            x62 = x55 - x9
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 + lbm.omega[1]*(-f0 - x24*(8*f0 * self.INV_27 + 8*f1 * self.INV_27 + 8*f10 * self.INV_27 + 8*f11 * self.INV_27 + 8*f12 * self.INV_27 + 8*f13 * self.INV_27 + 8*f14 * self.INV_27 + 8*f15 * self.INV_27 + 8*f16 * self.INV_27 + 8*f17 * self.INV_27 + 8*f18 * self.INV_27 + 8*f19 * self.INV_27 + 8*f2 * self.INV_27 + 8*f20 * self.INV_27 + 8*f21 * self.INV_27 + 8*f22 * self.INV_27 + 8*f23 * self.INV_27 + 8*f24 * self.INV_27 + 8*f25 * self.INV_27 + 8*f26 * self.INV_27 + 8*f3 * self.INV_27 + 8*f4 * self.INV_27 + 8*f5 * self.INV_27 + 8*f6 * self.INV_27 + 8*f7 * self.INV_27 + 8*f8 * self.INV_27 + 8*f9 * self.INV_27))
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 + x25*(x15*x26 + x31))
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f2 + x25*(3*x15*x16 - x23 - x27))
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f3 + x25*(x19*x26 + x29 + x34))
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f4 + x25*(3*x16*x19 - x22 - x32 - x35))
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 + x25*(x21*x26 + x28 + x37 + 1))
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f6 + x25*(3*x16*x21 - x20 - x35 - x36))
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f7 + x38*(9*x39**2 * 0.5 + x40))
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f8 + x38*(9*x39**2 * 0.5 - x42))
            f_post[I + c[9]*ti.static(self.pop)][9] = f9 + lbm.omega[1]*(-f9 + x38*(9*x43**2 * 0.5 - x45))
            f_post[I + c[10]*ti.static(self.pop)][10] = f10 + lbm.omega[1]*(-f10 + x38*(9*x43**2 * 0.5 - x48))
            f_post[I + c[11]*ti.static(self.pop)][11] = f11 + lbm.omega[1]*(-f11 + x38*(9*x49**2 * 0.5 + x50))
            f_post[I + c[12]*ti.static(self.pop)][12] = f12 + lbm.omega[1]*(-f12 + x38*(-x36 - x47 + 9*x49**2 * 0.5))
            f_post[I + c[13]*ti.static(self.pop)][13] = f13 + lbm.omega[1]*(-f13 + x38*(-x44 + 9*x52**2 * 0.5 - x53))
            f_post[I + c[14]*ti.static(self.pop)][14] = f14 + lbm.omega[1]*(-f14 + x38*(-x47 + 9*x52**2 * 0.5 - x54))
            f_post[I + c[15]*ti.static(self.pop)][15] = f15 + lbm.omega[1]*(-f15 + x38*(9*x55**2 * 0.5 + x56))
            f_post[I + c[16]*ti.static(self.pop)][16] = f16 + lbm.omega[1]*(-f16 + x38*(-x36 - x41 + 9*x55**2 * 0.5))
            f_post[I + c[17]*ti.static(self.pop)][17] = f17 + lbm.omega[1]*(-f17 + x38*(-x46 - x53 + 9*x57**2 * 0.5))
            f_post[I + c[18]*ti.static(self.pop)][18] = f18 + lbm.omega[1]*(-f18 + x38*(-x41 - x54 + 9*x57**2 * 0.5))
            f_post[I + c[19]*ti.static(self.pop)][19] = f19 + lbm.omega[1]*(-f19 + x58*(x36 + x40 + 9*x59**2 * 0.5))
            f_post[I + c[20]*ti.static(self.pop)][20] = f20 + lbm.omega[1]*(-f20 + x58*(-x36 - x42 + 9*x59**2 * 0.5))
            f_post[I + c[21]*ti.static(self.pop)][21] = f21 + lbm.omega[1]*(-f21 + x58*(x40 + x54 + 9*x60**2 * 0.5))
            f_post[I + c[22]*ti.static(self.pop)][22] = f22 + lbm.omega[1]*(-f22 + x58*(-x42 - x54 + 9*x60**2 * 0.5))
            f_post[I + c[23]*ti.static(self.pop)][23] = f23 + lbm.omega[1]*(-f23 + x58*(x46 + x50 + 9*x61**2 * 0.5))
            f_post[I + c[24]*ti.static(self.pop)][24] = f24 + lbm.omega[1]*(-f24 + x58*(-x36 - x48 + 9*x61**2 * 0.5))
            f_post[I + c[25]*ti.static(self.pop)][25] = f25 + lbm.omega[1]*(-f25 + x58*(-x36 - x45 + 9*x62**2 * 0.5))
            f_post[I + c[26]*ti.static(self.pop)][26] = f26 + lbm.omega[1]*(-f26 + x58*(x44 + x56 + 9*x62**2 * 0.5))
            lbm.rho[I] = x3 # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = x9
            lbm.vel[I][1] = x12
            lbm.vel[I][2] = x14

    @ti.func
    def f_eq(self, lbm, I):
        rho = lbm.rho[I] # <- note: actual value stored here is rho - density_shift
        u = lbm.vel[I][0]
        v = lbm.vel[I][1]
        w = lbm.vel[I][2]

        xeq0 = u**2
        xeq1 = 3*xeq0 * 0.5
        xeq2 = v**2
        xeq3 = 3*xeq2 * 0.5
        xeq4 = w**2
        xeq5 = 3*xeq4 * 0.5
        xeq6 = xeq3 + xeq5 - 1
        xeq7 = xeq1 + xeq6
        xeq8 = 3*u
        xeq9 = -xeq3
        xeq10 = 1 - xeq5
        xeq11 = xeq10 + xeq9
        xeq12 = xeq11 + xeq8
        xeq13 = 2*rho * self.INV_27
        xeq14 = 3*v
        xeq15 = -xeq1
        xeq16 = xeq14 + xeq15
        xeq17 = xeq1 - 1
        xeq18 = 3*w
        xeq19 = xeq15 + xeq18
        xeq20 = u + v
        xeq21 = xeq12 + xeq16
        xeq22 = rho * self.INV_54
        xeq23 = xeq14 + xeq7
        xeq24 = xeq23 + xeq8
        xeq25 = u - v
        xeq26 = -xeq8
        xeq27 = xeq23 + xeq26
        xeq28 = -xeq14
        xeq29 = xeq7 + xeq8
        xeq30 = xeq28 + xeq29
        xeq31 = u + w
        xeq32 = -w
        xeq33 = u + xeq32
        xeq34 = xeq18 + xeq7
        xeq35 = xeq26 + xeq34
        xeq36 = -xeq18
        xeq37 = v + w
        xeq38 = v + xeq32
        xeq39 = w + xeq20
        xeq40 = rho * self.INV_216
        xeq41 = xeq20 + xeq32
        xeq42 = w + xeq25
        xeq43 = -u + xeq37

        return ti.Vector([
            -8*rho*xeq7 * self.INV_27,
            xeq13*(3*xeq0 + xeq12),
            xeq13*(3*xeq0 - xeq6 - xeq8),
            xeq13*(xeq10 + xeq16 + 3*xeq2),
            xeq13*(-xeq14 - xeq17 + 3*xeq2 - xeq5),
            xeq13*(xeq19 + 3*xeq4 + xeq9 + 1),
            xeq13*(-xeq17 - xeq18 - xeq3 + 3*xeq4),
            xeq22*(9*xeq20**2 * 0.5 + xeq21),
            xeq22*(9*xeq20**2 * 0.5 - xeq24),
            xeq22*(9*xeq25**2 * 0.5 - xeq27),
            xeq22*(9*xeq25**2 * 0.5 - xeq30),
            xeq22*(xeq12 + xeq19 + 9*xeq31**2 * 0.5),
            xeq22*(-xeq18 - xeq29 + 9*xeq31**2 * 0.5),
            xeq22*(9*xeq33**2 * 0.5 - xeq35),
            xeq22*(-xeq29 + 9*xeq33**2 * 0.5 - xeq36),
            xeq22*(xeq11 + xeq16 + xeq18 + 9*xeq37**2 * 0.5),
            xeq22*(-xeq18 - xeq23 + 9*xeq37**2 * 0.5),
            xeq22*(-xeq28 - xeq34 + 9*xeq38**2 * 0.5),
            xeq22*(-xeq23 - xeq36 + 9*xeq38**2 * 0.5),
            xeq40*(xeq18 + xeq21 + 9*xeq39**2 * 0.5),
            xeq40*(-xeq18 - xeq24 + 9*xeq39**2 * 0.5),
            xeq40*(-xeq28 - xeq35 + 9*xeq41**2 * 0.5),
            xeq40*(-xeq24 - xeq36 + 9*xeq41**2 * 0.5),
            xeq40*(-xeq27 - xeq36 + 9*xeq42**2 * 0.5),
            xeq40*(-xeq18 - xeq30 + 9*xeq42**2 * 0.5),
            xeq40*(-xeq18 - xeq27 + 9*xeq43**2 * 0.5),
            xeq40*(-xeq30 - xeq36 + 9*xeq43**2 * 0.5),
        ])

    def _set_rational(self):
        self.INV_216 = 1.0/216.0
        self.INV_27 = 1.0/27.0
        self.INV_54 = 1.0/54.0
