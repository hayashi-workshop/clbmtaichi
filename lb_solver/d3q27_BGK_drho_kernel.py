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
        self.density_shift = 1.0
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
            x4 = x3 + 1
            x5 = 1/x4
            x6 = -f20
            x7 = f19 + f21 - f22 + f7 - f8 + x6
            x8 = f11 - f12 + f23 - f24
            x9 = -f10 - f14 - f2 - f26 + x0 + x7 + x8
            x10 = x5*x9
            x11 = f15 - f16 - f25 + f26
            x12 = -f18 - f23 - f4 - f9 + x1 + x11 + x7
            x13 = x12*x5
            x14 = -f13 - f17 - f21 - f6 + x11 + x2 + x6 + x8
            x15 = x14*x5
            x16 = x9**2
            x17 = x4**(-2)
            x18 = 3*x17 * 0.5
            x19 = x16*x18
            x20 = x12**2
            x21 = x18*x20
            x22 = x14**2
            x23 = x18*x22
            x24 = x21 + x23 - 1
            x25 = x19 + x24
            x26 = 3*x17
            x27 = 3*x10
            x28 = -x21
            x29 = 1 - x23
            x30 = x28 + x29
            x31 = x27 + x30
            x32 = 3*x13
            x33 = -x19
            x34 = x32 + x33
            x35 = x19 - 1
            x36 = 3*x15
            x37 = x33 + x36
            x38 = x10 + x13
            x39 = x31 + x34
            x40 = x25 + x32
            x41 = x27 + x40
            x42 = x10 - x13
            x43 = -x27
            x44 = x40 + x43
            x45 = -x32
            x46 = x25 + x27
            x47 = x45 + x46
            x48 = x10 + x15
            x49 = x31 + x37
            x50 = -x15
            x51 = x10 + x50
            x52 = x25 + x36
            x53 = -x36
            x54 = x13 + x15
            x55 = x30 + x34 + x36
            x56 = x13 + x50
            x57 = x15 + x38
            x58 = x38 + x50
            x59 = x15 + x42
            x60 = -x10 + x54
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 + lbm.omega[1]*(-f0 - 8*x25*x4 * self.INV_27 - 8 * self.INV_27)
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 + 2*x4*(x16*x26 + x31) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f2 + 2*x4*(3*x16*x17 - x24 - x27) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f3 + 2*x4*(x20*x26 + x29 + x34) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f4 + 2*x4*(3*x17*x20 - x23 - x32 - x35) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 + 2*x4*(x22*x26 + x28 + x37 + 1) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f6 + 2*x4*(3*x17*x22 - x21 - x35 - x36) * self.INV_27 - 2 * self.INV_27)
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f7 + x4*(9*x38**2 * 0.5 + x39) * self.INV_54 - self.INV_54)
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f8 + x4*(9*x38**2 * 0.5 - x41) * self.INV_54 - self.INV_54)
            f_post[I + c[9]*ti.static(self.pop)][9] = f9 + lbm.omega[1]*(-f9 + x4*(9*x42**2 * 0.5 - x44) * self.INV_54 - self.INV_54)
            f_post[I + c[10]*ti.static(self.pop)][10] = f10 + lbm.omega[1]*(-f10 + x4*(9*x42**2 * 0.5 - x47) * self.INV_54 - self.INV_54)
            f_post[I + c[11]*ti.static(self.pop)][11] = f11 + lbm.omega[1]*(-f11 + x4*(9*x48**2 * 0.5 + x49) * self.INV_54 - self.INV_54)
            f_post[I + c[12]*ti.static(self.pop)][12] = f12 + lbm.omega[1]*(-f12 + x4*(-x36 - x46 + 9*x48**2 * 0.5) * self.INV_54 - self.INV_54)
            f_post[I + c[13]*ti.static(self.pop)][13] = f13 + lbm.omega[1]*(-f13 + x4*(-x43 + 9*x51**2 * 0.5 - x52) * self.INV_54 - self.INV_54)
            f_post[I + c[14]*ti.static(self.pop)][14] = f14 + lbm.omega[1]*(-f14 + x4*(-x46 + 9*x51**2 * 0.5 - x53) * self.INV_54 - self.INV_54)
            f_post[I + c[15]*ti.static(self.pop)][15] = f15 + lbm.omega[1]*(-f15 + x4*(9*x54**2 * 0.5 + x55) * self.INV_54 - self.INV_54)
            f_post[I + c[16]*ti.static(self.pop)][16] = f16 + lbm.omega[1]*(-f16 + x4*(-x36 - x40 + 9*x54**2 * 0.5) * self.INV_54 - self.INV_54)
            f_post[I + c[17]*ti.static(self.pop)][17] = f17 + lbm.omega[1]*(-f17 + x4*(-x45 - x52 + 9*x56**2 * 0.5) * self.INV_54 - self.INV_54)
            f_post[I + c[18]*ti.static(self.pop)][18] = f18 + lbm.omega[1]*(-f18 + x4*(-x40 - x53 + 9*x56**2 * 0.5) * self.INV_54 - self.INV_54)
            f_post[I + c[19]*ti.static(self.pop)][19] = f19 + lbm.omega[1]*(-f19 + x4*(x36 + x39 + 9*x57**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[20]*ti.static(self.pop)][20] = f20 + lbm.omega[1]*(-f20 + x4*(-x36 - x41 + 9*x57**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[21]*ti.static(self.pop)][21] = f21 + lbm.omega[1]*(-f21 + x4*(x39 + x53 + 9*x58**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[22]*ti.static(self.pop)][22] = f22 + lbm.omega[1]*(-f22 + x4*(-x41 - x53 + 9*x58**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[23]*ti.static(self.pop)][23] = f23 + lbm.omega[1]*(-f23 + x4*(x45 + x49 + 9*x59**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[24]*ti.static(self.pop)][24] = f24 + lbm.omega[1]*(-f24 + x4*(-x36 - x47 + 9*x59**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[25]*ti.static(self.pop)][25] = f25 + lbm.omega[1]*(-f25 + x4*(-x36 - x44 + 9*x60**2 * 0.5) * self.INV_216 - self.INV_216)
            f_post[I + c[26]*ti.static(self.pop)][26] = f26 + lbm.omega[1]*(-f26 + x4*(x43 + x55 + 9*x60**2 * 0.5) * self.INV_216 - self.INV_216)
            lbm.rho[I] = x3 # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = x10
            lbm.vel[I][1] = x13
            lbm.vel[I][2] = x15

    @ti.func
    def f_eq(self, lbm, I):
        rho = lbm.rho[I] # <- note: actual value stored here is rho - density_shift
        u = lbm.vel[I][0]
        v = lbm.vel[I][1]
        w = lbm.vel[I][2]

        xeq0 = rho + 1
        xeq1 = u**2
        xeq2 = 3*xeq1 * 0.5
        xeq3 = v**2
        xeq4 = 3*xeq3 * 0.5
        xeq5 = w**2
        xeq6 = 3*xeq5 * 0.5
        xeq7 = xeq4 + xeq6 - 1
        xeq8 = xeq2 + xeq7
        xeq9 = 3*u
        xeq10 = -xeq4
        xeq11 = 1 - xeq6
        xeq12 = xeq10 + xeq11
        xeq13 = xeq12 + xeq9
        xeq14 = 2*xeq0 * self.INV_27
        xeq15 = 3*v
        xeq16 = -xeq2
        xeq17 = xeq15 + xeq16
        xeq18 = xeq2 - 1
        xeq19 = 3*w
        xeq20 = xeq16 + xeq19
        xeq21 = u + v
        xeq22 = xeq13 + xeq17
        xeq23 = xeq0 * self.INV_54
        xeq24 = xeq15 + xeq8
        xeq25 = xeq24 + xeq9
        xeq26 = u - v
        xeq27 = -xeq9
        xeq28 = xeq24 + xeq27
        xeq29 = -xeq15
        xeq30 = xeq8 + xeq9
        xeq31 = xeq29 + xeq30
        xeq32 = u + w
        xeq33 = -w
        xeq34 = u + xeq33
        xeq35 = xeq19 + xeq8
        xeq36 = xeq27 + xeq35
        xeq37 = -xeq19
        xeq38 = v + w
        xeq39 = v + xeq33
        xeq40 = w + xeq21
        xeq41 = xeq0 * self.INV_216
        xeq42 = xeq21 + xeq33
        xeq43 = w + xeq26
        xeq44 = -u + xeq38

        return ti.Vector([
            -8*xeq0*xeq8 * self.INV_27 - 8 * self.INV_27,
            xeq14*(3*xeq1 + xeq13) - 2 * self.INV_27,
            xeq14*(3*xeq1 - xeq7 - xeq9) - 2 * self.INV_27,
            xeq14*(xeq11 + xeq17 + 3*xeq3) - 2 * self.INV_27,
            xeq14*(-xeq15 - xeq18 + 3*xeq3 - xeq6) - 2 * self.INV_27,
            xeq14*(xeq10 + xeq20 + 3*xeq5 + 1) - 2 * self.INV_27,
            xeq14*(-xeq18 - xeq19 - xeq4 + 3*xeq5) - 2 * self.INV_27,
            xeq23*(9*xeq21**2 * 0.5 + xeq22) - self.INV_54,
            xeq23*(9*xeq21**2 * 0.5 - xeq25) - self.INV_54,
            xeq23*(9*xeq26**2 * 0.5 - xeq28) - self.INV_54,
            xeq23*(9*xeq26**2 * 0.5 - xeq31) - self.INV_54,
            xeq23*(xeq13 + xeq20 + 9*xeq32**2 * 0.5) - self.INV_54,
            xeq23*(-xeq19 - xeq30 + 9*xeq32**2 * 0.5) - self.INV_54,
            xeq23*(9*xeq34**2 * 0.5 - xeq36) - self.INV_54,
            xeq23*(-xeq30 + 9*xeq34**2 * 0.5 - xeq37) - self.INV_54,
            xeq23*(xeq12 + xeq17 + xeq19 + 9*xeq38**2 * 0.5) - self.INV_54,
            xeq23*(-xeq19 - xeq24 + 9*xeq38**2 * 0.5) - self.INV_54,
            xeq23*(-xeq29 - xeq35 + 9*xeq39**2 * 0.5) - self.INV_54,
            xeq23*(-xeq24 - xeq37 + 9*xeq39**2 * 0.5) - self.INV_54,
            xeq41*(xeq19 + xeq22 + 9*xeq40**2 * 0.5) - self.INV_216,
            xeq41*(-xeq19 - xeq25 + 9*xeq40**2 * 0.5) - self.INV_216,
            xeq41*(-xeq29 - xeq36 + 9*xeq42**2 * 0.5) - self.INV_216,
            xeq41*(-xeq25 - xeq37 + 9*xeq42**2 * 0.5) - self.INV_216,
            xeq41*(-xeq28 - xeq37 + 9*xeq43**2 * 0.5) - self.INV_216,
            xeq41*(-xeq19 - xeq31 + 9*xeq43**2 * 0.5) - self.INV_216,
            xeq41*(-xeq19 - xeq28 + 9*xeq44**2 * 0.5) - self.INV_216,
            xeq41*(-xeq31 - xeq37 + 9*xeq44**2 * 0.5) - self.INV_216,
        ])

    def _set_rational(self):
        self.INV_216 = 1.0/216.0
        self.INV_27 = 1.0/27.0
        self.INV_54 = 1.0/54.0
