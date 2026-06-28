# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D3Q27
# Model: TRT
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
            xm0 = f1 + f13 + f25 + f9
            xm1 = f10 + f17 + f24 + f3
            xm2 = f14 + f18 + f19 + f22 + f5
            xm3 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + xm0 + xm1 + xm2
            xm4 = 1/(xm3 + 1)
            xm5 = -f20
            xm6 = f19 + f21 - f22 + f7 - f8 + xm5
            xm7 = f11 - f12 + f23 - f24
            xm8 = f15 - f16 - f25 + f26
            rho = xm3
            u = xm4*(-f10 - f14 - f2 - f26 + xm0 + xm6 + xm7)
            v = xm4*(-f18 - f23 - f4 - f9 + xm1 + xm6 + xm8)
            w = xm4*(-f13 - f17 - f21 - f6 + xm2 + xm5 + xm7 + xm8)
            xe0 = f1 + f13 + f25 + f9
            xe1 = f10 + f17 + f24 + f3
            xe2 = f14 + f18 + f19 + f22 + f5
            xe3 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + xe0 + xe1 + xe2 + 1
            xe4 = -f20
            xe5 = f19 + f21 - f22 + f7 - f8 + xe4
            xe6 = f11 - f12 + f23 - f24
            xe7 = -f10 - f14 - f2 - f26 + xe0 + xe5 + xe6
            xe8 = xe7**2
            xe9 = xe3**(-2)
            xe10 = 3*xe9 * 0.5
            xe11 = xe10*xe8
            xe12 = f15 - f16 - f25 + f26
            xe13 = -f18 - f23 - f4 - f9 + xe1 + xe12 + xe5
            xe14 = xe13**2
            xe15 = xe10*xe14
            xe16 = -f13 - f17 - f21 - f6 + xe12 + xe2 + xe4 + xe6
            xe17 = xe16**2
            xe18 = xe10*xe17
            xe19 = xe15 + xe18 - 1
            xe20 = xe11 + xe19
            xe21 = 3*xe9
            xe22 = 1/xe3
            xe23 = xe22*xe7
            xe24 = 3*xe23
            xe25 = -xe15
            xe26 = 1 - xe18
            xe27 = xe25 + xe26
            xe28 = xe24 + xe27
            xe29 = 2*xe3 * self.INV_27
            xe30 = xe13*xe22
            xe31 = 3*xe30
            xe32 = -xe11
            xe33 = xe31 + xe32
            xe34 = xe11 - 1
            xe35 = xe16*xe22
            xe36 = 3*xe35
            xe37 = xe32 + xe36
            xe38 = xe23 + xe30
            xe39 = xe28 + xe33
            xe40 = xe3 * self.INV_54
            xe41 = xe20 + xe31
            xe42 = xe24 + xe41
            xe43 = xe23 - xe30
            xe44 = -xe24
            xe45 = xe41 + xe44
            xe46 = -xe31
            xe47 = xe20 + xe24
            xe48 = xe46 + xe47
            xe49 = xe23 + xe35
            xe50 = xe28 + xe37
            xe51 = -xe35
            xe52 = xe23 + xe51
            xe53 = xe20 + xe36
            xe54 = -xe36
            xe55 = xe30 + xe35
            xe56 = xe27 + xe33 + xe36
            xe57 = xe30 + xe51
            xe58 = xe35 + xe38
            xe59 = xe3 * self.INV_216
            xe60 = xe38 + xe51
            xe61 = xe35 + xe43
            xe62 = -xe23 + xe55
            feq0 = -8*xe20*xe3 * self.INV_27 - 8 * self.INV_27
            feq1 = xe29*(xe21*xe8 + xe28) - 2 * self.INV_27
            feq2 = xe29*(-xe19 - xe24 + 3*xe8*xe9) - 2 * self.INV_27
            feq3 = xe29*(xe14*xe21 + xe26 + xe33) - 2 * self.INV_27
            feq4 = xe29*(3*xe14*xe9 - xe18 - xe31 - xe34) - 2 * self.INV_27
            feq5 = xe29*(xe17*xe21 + xe25 + xe37 + 1) - 2 * self.INV_27
            feq6 = xe29*(-xe15 + 3*xe17*xe9 - xe34 - xe36) - 2 * self.INV_27
            feq7 = xe40*(9*xe38**2 * 0.5 + xe39) - self.INV_54
            feq8 = xe40*(9*xe38**2 * 0.5 - xe42) - self.INV_54
            feq9 = xe40*(9*xe43**2 * 0.5 - xe45) - self.INV_54
            feq10 = xe40*(9*xe43**2 * 0.5 - xe48) - self.INV_54
            feq11 = xe40*(9*xe49**2 * 0.5 + xe50) - self.INV_54
            feq12 = xe40*(-xe36 - xe47 + 9*xe49**2 * 0.5) - self.INV_54
            feq13 = xe40*(-xe44 + 9*xe52**2 * 0.5 - xe53) - self.INV_54
            feq14 = xe40*(-xe47 + 9*xe52**2 * 0.5 - xe54) - self.INV_54
            feq15 = xe40*(9*xe55**2 * 0.5 + xe56) - self.INV_54
            feq16 = xe40*(-xe36 - xe41 + 9*xe55**2 * 0.5) - self.INV_54
            feq17 = xe40*(-xe46 - xe53 + 9*xe57**2 * 0.5) - self.INV_54
            feq18 = xe40*(-xe41 - xe54 + 9*xe57**2 * 0.5) - self.INV_54
            feq19 = xe59*(xe36 + xe39 + 9*xe58**2 * 0.5) - self.INV_216
            feq20 = xe59*(-xe36 - xe42 + 9*xe58**2 * 0.5) - self.INV_216
            feq21 = xe59*(xe39 + xe54 + 9*xe60**2 * 0.5) - self.INV_216
            feq22 = xe59*(-xe42 - xe54 + 9*xe60**2 * 0.5) - self.INV_216
            feq23 = xe59*(xe46 + xe50 + 9*xe61**2 * 0.5) - self.INV_216
            feq24 = xe59*(-xe36 - xe48 + 9*xe61**2 * 0.5) - self.INV_216
            feq25 = xe59*(-xe36 - xe45 + 9*xe62**2 * 0.5) - self.INV_216
            feq26 = xe59*(xe44 + xe56 + 9*xe62**2 * 0.5) - self.INV_216
            # Collision/relaxation
            f_post[I + c[0]*ti.static(self.pop)][0] = f0 - lbm.omega[1]*(f0 - feq0)
            f_post[I + c[1]*ti.static(self.pop)][1] = f1 + lbm.omega[1]*(-f1 - f2 + feq1 + feq2) * 0.5 + lbm.omega[2]*(-f1 + f2 + feq1 - feq2) * 0.5
            f_post[I + c[2]*ti.static(self.pop)][2] = f2 + lbm.omega[1]*(-f1 - f2 + feq1 + feq2) * 0.5 - lbm.omega[2]*(-f1 + f2 + feq1 - feq2) * 0.5
            f_post[I + c[3]*ti.static(self.pop)][3] = f3 + lbm.omega[1]*(-f3 - f4 + feq3 + feq4) * 0.5 + lbm.omega[2]*(-f3 + f4 + feq3 - feq4) * 0.5
            f_post[I + c[4]*ti.static(self.pop)][4] = f4 + lbm.omega[1]*(-f3 - f4 + feq3 + feq4) * 0.5 - lbm.omega[2]*(-f3 + f4 + feq3 - feq4) * 0.5
            f_post[I + c[5]*ti.static(self.pop)][5] = f5 + lbm.omega[1]*(-f5 - f6 + feq5 + feq6) * 0.5 + lbm.omega[2]*(-f5 + f6 + feq5 - feq6) * 0.5
            f_post[I + c[6]*ti.static(self.pop)][6] = f6 + lbm.omega[1]*(-f5 - f6 + feq5 + feq6) * 0.5 - lbm.omega[2]*(-f5 + f6 + feq5 - feq6) * 0.5
            f_post[I + c[7]*ti.static(self.pop)][7] = f7 + lbm.omega[1]*(-f7 - f8 + feq7 + feq8) * 0.5 + lbm.omega[2]*(-f7 + f8 + feq7 - feq8) * 0.5
            f_post[I + c[8]*ti.static(self.pop)][8] = f8 + lbm.omega[1]*(-f7 - f8 + feq7 + feq8) * 0.5 - lbm.omega[2]*(-f7 + f8 + feq7 - feq8) * 0.5
            f_post[I + c[9]*ti.static(self.pop)][9] = f9 + lbm.omega[1]*(-f10 - f9 + feq10 + feq9) * 0.5 + lbm.omega[2]*(f10 - f9 - feq10 + feq9) * 0.5
            f_post[I + c[10]*ti.static(self.pop)][10] = f10 + lbm.omega[1]*(-f10 - f9 + feq10 + feq9) * 0.5 - lbm.omega[2]*(f10 - f9 - feq10 + feq9) * 0.5
            f_post[I + c[11]*ti.static(self.pop)][11] = f11 + lbm.omega[1]*(-f11 - f12 + feq11 + feq12) * 0.5 + lbm.omega[2]*(-f11 + f12 + feq11 - feq12) * 0.5
            f_post[I + c[12]*ti.static(self.pop)][12] = f12 + lbm.omega[1]*(-f11 - f12 + feq11 + feq12) * 0.5 - lbm.omega[2]*(-f11 + f12 + feq11 - feq12) * 0.5
            f_post[I + c[13]*ti.static(self.pop)][13] = f13 + lbm.omega[1]*(-f13 - f14 + feq13 + feq14) * 0.5 + lbm.omega[2]*(-f13 + f14 + feq13 - feq14) * 0.5
            f_post[I + c[14]*ti.static(self.pop)][14] = f14 + lbm.omega[1]*(-f13 - f14 + feq13 + feq14) * 0.5 - lbm.omega[2]*(-f13 + f14 + feq13 - feq14) * 0.5
            f_post[I + c[15]*ti.static(self.pop)][15] = f15 + lbm.omega[1]*(-f15 - f16 + feq15 + feq16) * 0.5 + lbm.omega[2]*(-f15 + f16 + feq15 - feq16) * 0.5
            f_post[I + c[16]*ti.static(self.pop)][16] = f16 + lbm.omega[1]*(-f15 - f16 + feq15 + feq16) * 0.5 - lbm.omega[2]*(-f15 + f16 + feq15 - feq16) * 0.5
            f_post[I + c[17]*ti.static(self.pop)][17] = f17 + lbm.omega[1]*(-f17 - f18 + feq17 + feq18) * 0.5 + lbm.omega[2]*(-f17 + f18 + feq17 - feq18) * 0.5
            f_post[I + c[18]*ti.static(self.pop)][18] = f18 + lbm.omega[1]*(-f17 - f18 + feq17 + feq18) * 0.5 - lbm.omega[2]*(-f17 + f18 + feq17 - feq18) * 0.5
            f_post[I + c[19]*ti.static(self.pop)][19] = f19 + lbm.omega[1]*(-f19 - f20 + feq19 + feq20) * 0.5 + lbm.omega[2]*(-f19 + f20 + feq19 - feq20) * 0.5
            f_post[I + c[20]*ti.static(self.pop)][20] = f20 + lbm.omega[1]*(-f19 - f20 + feq19 + feq20) * 0.5 - lbm.omega[2]*(-f19 + f20 + feq19 - feq20) * 0.5
            f_post[I + c[21]*ti.static(self.pop)][21] = f21 + lbm.omega[1]*(-f21 - f22 + feq21 + feq22) * 0.5 + lbm.omega[2]*(-f21 + f22 + feq21 - feq22) * 0.5
            f_post[I + c[22]*ti.static(self.pop)][22] = f22 + lbm.omega[1]*(-f21 - f22 + feq21 + feq22) * 0.5 - lbm.omega[2]*(-f21 + f22 + feq21 - feq22) * 0.5
            f_post[I + c[23]*ti.static(self.pop)][23] = f23 + lbm.omega[1]*(-f23 - f24 + feq23 + feq24) * 0.5 + lbm.omega[2]*(-f23 + f24 + feq23 - feq24) * 0.5
            f_post[I + c[24]*ti.static(self.pop)][24] = f24 + lbm.omega[1]*(-f23 - f24 + feq23 + feq24) * 0.5 - lbm.omega[2]*(-f23 + f24 + feq23 - feq24) * 0.5
            f_post[I + c[25]*ti.static(self.pop)][25] = f25 + lbm.omega[1]*(-f25 - f26 + feq25 + feq26) * 0.5 + lbm.omega[2]*(-f25 + f26 + feq25 - feq26) * 0.5
            f_post[I + c[26]*ti.static(self.pop)][26] = f26 + lbm.omega[1]*(-f25 - f26 + feq25 + feq26) * 0.5 - lbm.omega[2]*(-f25 + f26 + feq25 - feq26) * 0.5

            # Update arrays of macroscopic vars
            lbm.rho[I] = rho # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = u
            lbm.vel[I][1] = v
            lbm.vel[I][2] = w

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
