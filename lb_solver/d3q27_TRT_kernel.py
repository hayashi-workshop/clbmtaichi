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
            xm0 = f1 + f13 + f25 + f9
            xm1 = f10 + f17 + f24 + f3
            xm2 = f14 + f18 + f19 + f22 + f5
            xm3 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + xm0 + xm1 + xm2
            xm4 = 1/xm3
            xm5 = -f20
            xm6 = f19 + f21 - f22 + f7 - f8 + xm5
            xm7 = f11 - f12 + f23 - f24
            xm8 = f15 - f16 - f25 + f26
            rho = xm3
            u = xm4*(-f10 - f14 - f2 - f26 + xm0 + xm6 + xm7)
            v = xm4*(-f18 - f23 - f4 - f9 + xm1 + xm6 + xm8)
            w = xm4*(-f13 - f17 - f21 - f6 + xm2 + xm5 + xm7 + xm8)
            xe0 = -f20
            xe1 = f19 + f21 - f22 + f7 - f8 + xe0
            xe2 = f11 - f12 + f23 - f24
            xe3 = f1 + f13 + f25 + f9
            xe4 = -f10 - f14 - f2 - f26 + xe1 + xe2 + xe3
            xe5 = xe4**2
            xe6 = f10 + f17 + f24 + f3
            xe7 = f14 + f18 + f19 + f22 + f5
            xe8 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + xe3 + xe6 + xe7
            xe9 = xe8**(-2)
            xe10 = 3*xe9 * 0.5
            xe11 = xe10*xe5
            xe12 = f15 - f16 - f25 + f26
            xe13 = -f18 - f23 - f4 - f9 + xe1 + xe12 + xe6
            xe14 = xe13**2
            xe15 = xe10*xe14
            xe16 = -f13 - f17 - f21 - f6 + xe0 + xe12 + xe2 + xe7
            xe17 = xe16**2
            xe18 = xe10*xe17
            xe19 = xe15 + xe18 - 1
            xe20 = xe11 + xe19
            xe21 = 2*f0 * self.INV_27 + 2*f1 * self.INV_27 + 2*f10 * self.INV_27 + 2*f11 * self.INV_27 + 2*f12 * self.INV_27 + 2*f13 * self.INV_27 + 2*f14 * self.INV_27 + 2*f15 * self.INV_27 + 2*f16 * self.INV_27 + 2*f17 * self.INV_27 + 2*f18 * self.INV_27 + 2*f19 * self.INV_27 + 2*f2 * self.INV_27 + 2*f20 * self.INV_27 + 2*f21 * self.INV_27 + 2*f22 * self.INV_27 + 2*f23 * self.INV_27 + 2*f24 * self.INV_27 + 2*f25 * self.INV_27 + 2*f26 * self.INV_27 + 2*f3 * self.INV_27 + 2*f4 * self.INV_27 + 2*f5 * self.INV_27 + 2*f6 * self.INV_27 + 2*f7 * self.INV_27 + 2*f8 * self.INV_27 + 2*f9 * self.INV_27
            xe22 = 3*xe9
            xe23 = 1/xe8
            xe24 = xe23*xe4
            xe25 = 3*xe24
            xe26 = -xe15
            xe27 = 1 - xe18
            xe28 = xe26 + xe27
            xe29 = xe25 + xe28
            xe30 = xe13*xe23
            xe31 = 3*xe30
            xe32 = -xe11
            xe33 = xe31 + xe32
            xe34 = xe11 - 1
            xe35 = xe16*xe23
            xe36 = 3*xe35
            xe37 = xe32 + xe36
            xe38 = f0 * self.INV_54 + f1 * self.INV_54 + f10 * self.INV_54 + f11 * self.INV_54 + f12 * self.INV_54 + f13 * self.INV_54 + f14 * self.INV_54 + f15 * self.INV_54 + f16 * self.INV_54 + f17 * self.INV_54 + f18 * self.INV_54 + f19 * self.INV_54 + f2 * self.INV_54 + f20 * self.INV_54 + f21 * self.INV_54 + f22 * self.INV_54 + f23 * self.INV_54 + f24 * self.INV_54 + f25 * self.INV_54 + f26 * self.INV_54 + f3 * self.INV_54 + f4 * self.INV_54 + f5 * self.INV_54 + f6 * self.INV_54 + f7 * self.INV_54 + f8 * self.INV_54 + f9 * self.INV_54
            xe39 = xe24 + xe30
            xe40 = xe29 + xe33
            xe41 = xe20 + xe31
            xe42 = xe25 + xe41
            xe43 = xe24 - xe30
            xe44 = -xe25
            xe45 = xe41 + xe44
            xe46 = -xe31
            xe47 = xe20 + xe25
            xe48 = xe46 + xe47
            xe49 = xe24 + xe35
            xe50 = xe29 + xe37
            xe51 = -xe35
            xe52 = xe24 + xe51
            xe53 = xe20 + xe36
            xe54 = -xe36
            xe55 = xe30 + xe35
            xe56 = xe28 + xe33 + xe36
            xe57 = xe30 + xe51
            xe58 = f0 * self.INV_216 + f1 * self.INV_216 + f10 * self.INV_216 + f11 * self.INV_216 + f12 * self.INV_216 + f13 * self.INV_216 + f14 * self.INV_216 + f15 * self.INV_216 + f16 * self.INV_216 + f17 * self.INV_216 + f18 * self.INV_216 + f19 * self.INV_216 + f2 * self.INV_216 + f20 * self.INV_216 + f21 * self.INV_216 + f22 * self.INV_216 + f23 * self.INV_216 + f24 * self.INV_216 + f25 * self.INV_216 + f26 * self.INV_216 + f3 * self.INV_216 + f4 * self.INV_216 + f5 * self.INV_216 + f6 * self.INV_216 + f7 * self.INV_216 + f8 * self.INV_216 + f9 * self.INV_216
            xe59 = xe35 + xe39
            xe60 = xe39 + xe51
            xe61 = xe35 + xe43
            xe62 = -xe24 + xe55
            feq0 = -xe20*(8*f0 * self.INV_27 + 8*f1 * self.INV_27 + 8*f10 * self.INV_27 + 8*f11 * self.INV_27 + 8*f12 * self.INV_27 + 8*f13 * self.INV_27 + 8*f14 * self.INV_27 + 8*f15 * self.INV_27 + 8*f16 * self.INV_27 + 8*f17 * self.INV_27 + 8*f18 * self.INV_27 + 8*f19 * self.INV_27 + 8*f2 * self.INV_27 + 8*f20 * self.INV_27 + 8*f21 * self.INV_27 + 8*f22 * self.INV_27 + 8*f23 * self.INV_27 + 8*f24 * self.INV_27 + 8*f25 * self.INV_27 + 8*f26 * self.INV_27 + 8*f3 * self.INV_27 + 8*f4 * self.INV_27 + 8*f5 * self.INV_27 + 8*f6 * self.INV_27 + 8*f7 * self.INV_27 + 8*f8 * self.INV_27 + 8*f9 * self.INV_27)
            feq1 = xe21*(xe22*xe5 + xe29)
            feq2 = xe21*(-xe19 - xe25 + 3*xe5*xe9)
            feq3 = xe21*(xe14*xe22 + xe27 + xe33)
            feq4 = xe21*(3*xe14*xe9 - xe18 - xe31 - xe34)
            feq5 = xe21*(xe17*xe22 + xe26 + xe37 + 1)
            feq6 = xe21*(-xe15 + 3*xe17*xe9 - xe34 - xe36)
            feq7 = xe38*(9*xe39**2 * 0.5 + xe40)
            feq8 = xe38*(9*xe39**2 * 0.5 - xe42)
            feq9 = xe38*(9*xe43**2 * 0.5 - xe45)
            feq10 = xe38*(9*xe43**2 * 0.5 - xe48)
            feq11 = xe38*(9*xe49**2 * 0.5 + xe50)
            feq12 = xe38*(-xe36 - xe47 + 9*xe49**2 * 0.5)
            feq13 = xe38*(-xe44 + 9*xe52**2 * 0.5 - xe53)
            feq14 = xe38*(-xe47 + 9*xe52**2 * 0.5 - xe54)
            feq15 = xe38*(9*xe55**2 * 0.5 + xe56)
            feq16 = xe38*(-xe36 - xe41 + 9*xe55**2 * 0.5)
            feq17 = xe38*(-xe46 - xe53 + 9*xe57**2 * 0.5)
            feq18 = xe38*(-xe41 - xe54 + 9*xe57**2 * 0.5)
            feq19 = xe58*(xe36 + xe40 + 9*xe59**2 * 0.5)
            feq20 = xe58*(-xe36 - xe42 + 9*xe59**2 * 0.5)
            feq21 = xe58*(xe40 + xe54 + 9*xe60**2 * 0.5)
            feq22 = xe58*(-xe42 - xe54 + 9*xe60**2 * 0.5)
            feq23 = xe58*(xe46 + xe50 + 9*xe61**2 * 0.5)
            feq24 = xe58*(-xe36 - xe48 + 9*xe61**2 * 0.5)
            feq25 = xe58*(-xe36 - xe45 + 9*xe62**2 * 0.5)
            feq26 = xe58*(xe44 + xe56 + 9*xe62**2 * 0.5)
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
