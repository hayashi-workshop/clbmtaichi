# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D3Q27
# Model: Cumulant
# Some intermediate variable names are inspired by the naming conventions used in lbmpy.
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

            xm0 = f1 + f13 + f25 + f9
            xm1 = f10 + f17 + f24 + f3
            xm2 = f14 + f18 + f19 + f22 + f5
            xm3 = f0 + f11 + f12 + f15 + f16 + f2 + f20 + f21 + f23 + f26 + f4 + f6 + f7 + f8 + xm0 + xm1 + xm2
            xm4 = 1/(xm3 + 1)
            xm5 = -f20
            xm6 = f19 + f21 - f22 + f7 - f8 + xm5
            xm7 = f11 - f12 + f23 - f24
            xm8 = f15 - f16 - f25 + f26
            rho = xm3 + 1 # real (un-shifted) density
            u = xm4*(-f10 - f14 - f2 - f26 + xm0 + xm6 + xm7)
            v = xm4*(-f18 - f23 - f4 - f9 + xm1 + xm6 + xm8)
            w = xm4*(-f13 - f17 - f21 - f6 + xm2 + xm5 + xm7 + xm8)
            inv_rho = 1.0 / rho
            # forward chimera transform & macroscopic quantities
            chimera_m_m1_m1_c_0 = f20 + f22 + f8
            chimera_m_m1_m1_c_1 = -f20 + f22
            chimera_m_m1_m1_c_2 = f20 + f22
            chimera_m_m1_0_c_0 = f12 + f14 + f2
            chimera_m_m1_0_c_1 = -f12 + f14
            chimera_m_m1_0_c_2 = f12 + f14
            chimera_m_m1_1_c_0 = f10 + f24 + f26
            chimera_m_m1_1_c_1 = -f24 + f26
            chimera_m_m1_1_c_2 = f24 + f26
            chimera_m_0_m1_c_0 = f16 + f18 + f4
            chimera_m_0_m1_c_1 = -f16 + f18
            chimera_m_0_m1_c_2 = f16 + f18
            chimera_m_0_0_c_0 = f0 + f5 + f6
            chimera_m_0_0_c_1 = f5 - f6
            chimera_m_0_0_c_2 = f5 + f6
            chimera_m_0_1_c_0 = f15 + f17 + f3
            chimera_m_0_1_c_1 = f15 - f17
            chimera_m_0_1_c_2 = f15 + f17
            chimera_m_1_m1_c_0 = f23 + f25 + f9
            chimera_m_1_m1_c_1 = f23 - f25
            chimera_m_1_m1_c_2 = f23 + f25
            chimera_m_1_0_c_0 = f1 + f11 + f13
            chimera_m_1_0_c_1 = f11 - f13
            chimera_m_1_0_c_2 = f11 + f13
            chimera_m_1_1_c_0 = f19 + f21 + f7
            chimera_m_1_1_c_1 = f19 - f21
            chimera_m_1_1_c_2 = f19 + f21
            chimera_m_m1_c_0_0 = chimera_m_m1_0_c_0 + chimera_m_m1_1_c_0 + chimera_m_m1_m1_c_0
            chimera_m_m1_c_0_1 = chimera_m_m1_0_c_1 + chimera_m_m1_1_c_1 + chimera_m_m1_m1_c_1
            chimera_m_m1_c_0_2 = chimera_m_m1_0_c_2 + chimera_m_m1_1_c_2 + chimera_m_m1_m1_c_2
            chimera_m_m1_c_1_0 = chimera_m_m1_1_c_0 - chimera_m_m1_m1_c_0
            chimera_m_m1_c_1_1 = chimera_m_m1_1_c_1 - chimera_m_m1_m1_c_1
            chimera_m_m1_c_1_2 = chimera_m_m1_1_c_2 - chimera_m_m1_m1_c_2
            chimera_m_m1_c_2_0 = chimera_m_m1_1_c_0 + chimera_m_m1_m1_c_0
            chimera_m_m1_c_2_1 = chimera_m_m1_1_c_1 + chimera_m_m1_m1_c_1
            chimera_m_m1_c_2_2 = chimera_m_m1_1_c_2 + chimera_m_m1_m1_c_2
            chimera_m_0_c_0_0 = chimera_m_0_0_c_0 + chimera_m_0_1_c_0 + chimera_m_0_m1_c_0
            chimera_m_0_c_0_1 = chimera_m_0_0_c_1 + chimera_m_0_1_c_1 + chimera_m_0_m1_c_1
            chimera_m_0_c_0_2 = chimera_m_0_0_c_2 + chimera_m_0_1_c_2 + chimera_m_0_m1_c_2
            chimera_m_0_c_1_0 = chimera_m_0_1_c_0 - chimera_m_0_m1_c_0
            chimera_m_0_c_1_1 = chimera_m_0_1_c_1 - chimera_m_0_m1_c_1
            chimera_m_0_c_1_2 = chimera_m_0_1_c_2 - chimera_m_0_m1_c_2
            chimera_m_0_c_2_0 = chimera_m_0_1_c_0 + chimera_m_0_m1_c_0
            chimera_m_0_c_2_1 = chimera_m_0_1_c_1 + chimera_m_0_m1_c_1
            chimera_m_0_c_2_2 = chimera_m_0_1_c_2 + chimera_m_0_m1_c_2
            chimera_m_1_c_0_0 = chimera_m_1_0_c_0 + chimera_m_1_1_c_0 + chimera_m_1_m1_c_0
            chimera_m_1_c_0_1 = chimera_m_1_0_c_1 + chimera_m_1_1_c_1 + chimera_m_1_m1_c_1
            chimera_m_1_c_0_2 = chimera_m_1_0_c_2 + chimera_m_1_1_c_2 + chimera_m_1_m1_c_2
            chimera_m_1_c_1_0 = chimera_m_1_1_c_0 - chimera_m_1_m1_c_0
            chimera_m_1_c_1_1 = chimera_m_1_1_c_1 - chimera_m_1_m1_c_1
            chimera_m_1_c_1_2 = chimera_m_1_1_c_2 - chimera_m_1_m1_c_2
            chimera_m_1_c_2_0 = chimera_m_1_1_c_0 + chimera_m_1_m1_c_0
            chimera_m_1_c_2_1 = chimera_m_1_1_c_1 + chimera_m_1_m1_c_1
            chimera_m_1_c_2_2 = chimera_m_1_1_c_2 + chimera_m_1_m1_c_2
            m200 = chimera_m_1_c_0_0 + chimera_m_m1_c_0_0 + self.INV_3
            kappa200 = m200 - rho*u**2
            m101 = chimera_m_1_c_0_1 - chimera_m_m1_c_0_1
            kappa101 = m101 - rho*u*w
            m110 = chimera_m_1_c_1_0 - chimera_m_m1_c_1_0
            kappa110 = m110 - rho*u*v
            m002 = chimera_m_0_c_0_2 + chimera_m_1_c_0_2 + chimera_m_m1_c_0_2 + self.INV_3
            kappa002 = m002 - rho*w**2
            m011 = chimera_m_0_c_1_1 + chimera_m_1_c_1_1 + chimera_m_m1_c_1_1
            kappa011 = m011 - rho*v*w
            m020 = chimera_m_0_c_2_0 + chimera_m_1_c_2_0 + chimera_m_m1_c_2_0 + self.INV_3
            kappa020 = m020 - rho*v**2
            m201 = chimera_m_1_c_0_1 + chimera_m_m1_c_0_1
            kappa201 = -2*kappa101*u - kappa200*w + m201 - rho*u**2*w
            m210 = chimera_m_1_c_1_0 + chimera_m_m1_c_1_0
            kappa210 = -2*kappa110*u - kappa200*v + m210 - rho*u**2*v
            m102 = chimera_m_1_c_0_2 - chimera_m_m1_c_0_2
            kappa102 = -kappa002*u - 2*kappa101*w + m102 - rho*u*w**2
            m111 = chimera_m_1_c_1_1 - chimera_m_m1_c_1_1
            kappa111 = -kappa011*u - kappa101*v - kappa110*w + m111 - rho*u*v*w
            m120 = chimera_m_1_c_2_0 - chimera_m_m1_c_2_0
            kappa120 = -kappa020*u - 2*kappa110*v + m120 - rho*u*v**2
            m012 = chimera_m_0_c_1_2 + chimera_m_1_c_1_2 + chimera_m_m1_c_1_2
            kappa012 = -kappa002*v - 2*kappa011*w + m012 - rho*v*w**2
            m021 = chimera_m_0_c_2_1 + chimera_m_1_c_2_1 + chimera_m_m1_c_2_1
            kappa021 = -2*kappa011*v - kappa020*w + m021 - rho*v**2*w
            kappa101_post = -kappa101*lbm.omega[1] + kappa101
            kappa110_post = -kappa110*lbm.omega[1] + kappa110
            kappa011_post = -kappa011*lbm.omega[1] + kappa011
            kappa200_post = kappa002*lbm.omega[1] * self.INV_3 - kappa002*lbm.omega[2] * self.INV_3 + kappa020*lbm.omega[1] * self.INV_3 - kappa020*lbm.omega[2] * self.INV_3 - 2*kappa200*lbm.omega[1] * self.INV_3 - kappa200*lbm.omega[2] * self.INV_3 + kappa200 + lbm.omega[2]*rho * self.INV_3
            kappa020_post = kappa002*lbm.omega[1] * self.INV_3 - kappa002*lbm.omega[2] * self.INV_3 - 2*kappa020*lbm.omega[1] * self.INV_3 - kappa020*lbm.omega[2] * self.INV_3 + kappa020 + kappa200*lbm.omega[1] * self.INV_3 - kappa200*lbm.omega[2] * self.INV_3 + lbm.omega[2]*rho * self.INV_3
            kappa002_post = -2*kappa002*lbm.omega[1] * self.INV_3 - kappa002*lbm.omega[2] * self.INV_3 + kappa002 + kappa020*lbm.omega[1] * self.INV_3 - kappa020*lbm.omega[2] * self.INV_3 + kappa200*lbm.omega[1] * self.INV_3 - kappa200*lbm.omega[2] * self.INV_3 + lbm.omega[2]*rho * self.INV_3
            kappa120_post = -kappa102*lbm.omega[3] * 0.5 + kappa102*lbm.omega[4] * 0.5 - kappa120*lbm.omega[3] * 0.5 - kappa120*lbm.omega[4] * 0.5 + kappa120
            kappa210_post = -kappa012*lbm.omega[3] * 0.5 + kappa012*lbm.omega[4] * 0.5 - kappa210*lbm.omega[3] * 0.5 - kappa210*lbm.omega[4] * 0.5 + kappa210
            kappa201_post = -kappa021*lbm.omega[3] * 0.5 + kappa021*lbm.omega[4] * 0.5 - kappa201*lbm.omega[3] * 0.5 - kappa201*lbm.omega[4] * 0.5 + kappa201
            kappa102_post = -kappa102*lbm.omega[3] * 0.5 - kappa102*lbm.omega[4] * 0.5 + kappa102 - kappa120*lbm.omega[3] * 0.5 + kappa120*lbm.omega[4] * 0.5
            kappa012_post = -kappa012*lbm.omega[3] * 0.5 - kappa012*lbm.omega[4] * 0.5 + kappa012 - kappa210*lbm.omega[3] * 0.5 + kappa210*lbm.omega[4] * 0.5
            kappa021_post = -kappa021*lbm.omega[3] * 0.5 - kappa021*lbm.omega[4] * 0.5 + kappa021 - kappa201*lbm.omega[3] * 0.5 + kappa201*lbm.omega[4] * 0.5
            kappa111_post = -kappa111*lbm.omega[5] + kappa111
            m022 = chimera_m_0_c_2_2 + chimera_m_1_c_2_2 + chimera_m_m1_c_2_2 + self.INV_9
            kappa022 = -2*kappa012*v - 2*kappa021*w + m022 - rho*v**2*w**2
            C022 = -kappa002*kappa020 * inv_rho - 2*kappa011**2 * inv_rho + kappa022
            m202 = chimera_m_1_c_0_2 + chimera_m_m1_c_0_2 + self.INV_9
            kappa202 = -2*kappa102*u - 2*kappa201*w + m202 - rho*u**2*w**2
            C202 = -kappa002*kappa200 * inv_rho - 2*kappa101**2 * inv_rho + kappa202
            m220 = chimera_m_1_c_2_0 + chimera_m_m1_c_2_0 + self.INV_9
            kappa220 = -2*kappa120*u - 2*kappa210*v + m220 - rho*u**2*v**2
            C220 = -kappa020*kappa200 * inv_rho - 2*kappa110**2 * inv_rho + kappa220
            C220_post = C022*lbm.omega[6] * self.INV_3 - C022*lbm.omega[7] * self.INV_3 + C202*lbm.omega[6] * self.INV_3 - C202*lbm.omega[7] * self.INV_3 - 2*C220*lbm.omega[6] * self.INV_3 - C220*lbm.omega[7] * self.INV_3 + C220
            C202_post = C022*lbm.omega[6] * self.INV_3 - C022*lbm.omega[7] * self.INV_3 - 2*C202*lbm.omega[6] * self.INV_3 - C202*lbm.omega[7] * self.INV_3 + C202 + C220*lbm.omega[6] * self.INV_3 - C220*lbm.omega[7] * self.INV_3
            C022_post = -2*C022*lbm.omega[6] * self.INV_3 - C022*lbm.omega[7] * self.INV_3 + C022 + C202*lbm.omega[6] * self.INV_3 - C202*lbm.omega[7] * self.INV_3 + C220*lbm.omega[6] * self.INV_3 - C220*lbm.omega[7] * self.INV_3
            kappa022_post = C022_post + kappa002_post*kappa020_post * inv_rho + 2*kappa011_post**2 * inv_rho
            kappa202_post = C202_post + kappa002_post*kappa200_post * inv_rho + 2*kappa101_post**2 * inv_rho
            kappa220_post = C220_post + kappa020_post*kappa200_post * inv_rho + 2*kappa110_post**2 * inv_rho
            m211 = chimera_m_1_c_1_1 + chimera_m_m1_c_1_1
            kappa211 = -2*kappa111*u - kappa201*v - kappa210*w + m211 - rho*u**2*v*w
            C211 = -kappa011*kappa200 * inv_rho - 2*kappa101*kappa110 * inv_rho + kappa211
            C211_post = -C211*lbm.omega[8] + C211
            kappa211_post = C211_post + kappa011_post*kappa200_post * inv_rho + 2*kappa101_post*kappa110_post * inv_rho
            m112 = chimera_m_1_c_1_2 - chimera_m_m1_c_1_2
            kappa112 = -kappa012*u - kappa102*v - 2*kappa111*w + m112 - rho*u*v*w**2
            C112 = -kappa002*kappa110 * inv_rho - 2*kappa011*kappa101 * inv_rho + kappa112
            C112_post = -C112*lbm.omega[8] + C112
            kappa112_post = C112_post + kappa002_post*kappa110_post * inv_rho + 2*kappa011_post*kappa101_post * inv_rho
            m121 = chimera_m_1_c_2_1 - chimera_m_m1_c_2_1
            kappa121 = -kappa021*u - 2*kappa111*v - kappa120*w + m121 - rho*u*v**2*w
            C121 = -2*kappa011*kappa110 * inv_rho - kappa020*kappa101 * inv_rho + kappa121
            C121_post = -C121*lbm.omega[8] + C121
            kappa121_post = C121_post + 2*kappa011_post*kappa110_post * inv_rho + kappa020_post*kappa101_post * inv_rho
            m212 = chimera_m_1_c_1_2 + chimera_m_m1_c_1_2
            kappa212 = -2*kappa112*u - kappa202*v - 2*kappa211*w + m212 - rho*u**2*v*w**2
            C212 = -kappa002*kappa210 * inv_rho - 2*kappa011*kappa201 * inv_rho - kappa012*kappa200 * inv_rho - 4*kappa101*kappa111 * inv_rho - 2*kappa102*kappa110 * inv_rho + kappa212
            C212_post = -C212*lbm.omega[9] + C212
            kappa212_post = C212_post + kappa002_post*kappa210_post * inv_rho + 2*kappa011_post*kappa201_post * inv_rho + kappa012_post*kappa200_post * inv_rho + 4*kappa101_post*kappa111_post * inv_rho + 2*kappa102_post*kappa110_post * inv_rho
            m221 = chimera_m_1_c_2_1 + chimera_m_m1_c_2_1
            kappa221 = -2*kappa121*u - 2*kappa211*v - kappa220*w + m221 - rho*u**2*v**2*w
            C221 = -2*kappa011*kappa210 * inv_rho - kappa020*kappa201 * inv_rho - kappa021*kappa200 * inv_rho - 2*kappa101*kappa120 * inv_rho - 4*kappa110*kappa111 * inv_rho + kappa221
            C221_post = -C221*lbm.omega[9] + C221
            kappa221_post = C221_post + 2*kappa011_post*kappa210_post * inv_rho + kappa020_post*kappa201_post * inv_rho + kappa021_post*kappa200_post * inv_rho + 2*kappa101_post*kappa120_post * inv_rho + 4*kappa110_post*kappa111_post * inv_rho
            m122 = chimera_m_1_c_2_2 - chimera_m_m1_c_2_2
            kappa122 = -kappa022*u - 2*kappa112*v - 2*kappa121*w + m122 - rho*u*v**2*w**2
            C122 = -kappa002*kappa120 * inv_rho - 4*kappa011*kappa111 * inv_rho - 2*kappa012*kappa110 * inv_rho - kappa020*kappa102 * inv_rho - 2*kappa021*kappa101 * inv_rho + kappa122
            C122_post = -C122*lbm.omega[9] + C122
            kappa122_post = C122_post + kappa002_post*kappa120_post * inv_rho + 4*kappa011_post*kappa111_post * inv_rho + 2*kappa012_post*kappa110_post * inv_rho + kappa020_post*kappa102_post * inv_rho + 2*kappa021_post*kappa101_post * inv_rho
            m222 = chimera_m_1_c_2_2 + chimera_m_m1_c_2_2 + self.INV_27
            kappa222 = -2*kappa122*u - 2*kappa212*v - 2*kappa221*w + m222 - rho*u**2*v**2*w**2
            C222 = 2*kappa002*kappa020*kappa200 * inv_rho**2 + 4*kappa002*kappa110**2 * inv_rho**2 - kappa002*kappa220 * inv_rho + 4*kappa011**2*kappa200 * inv_rho**2 + 16*kappa011*kappa101*kappa110 * inv_rho**2 - 4*kappa011*kappa211 * inv_rho - 2*kappa012*kappa210 * inv_rho + 4*kappa020*kappa101**2 * inv_rho**2 - kappa020*kappa202 * inv_rho - 2*kappa021*kappa201 * inv_rho - kappa022*kappa200 * inv_rho - 4*kappa101*kappa121 * inv_rho - 2*kappa102*kappa120 * inv_rho - 4*kappa110*kappa112 * inv_rho - 4*kappa111**2 * inv_rho + kappa222
            C222_post = -C222*lbm.omega[10] + C222
            kappa222_post = C222_post - 2*kappa002_post*kappa020_post*kappa200_post * inv_rho**2 - 4*kappa002_post*kappa110_post**2 * inv_rho**2 + kappa002_post*kappa220_post * inv_rho - 4*kappa011_post**2*kappa200_post * inv_rho**2 - 16*kappa011_post*kappa101_post*kappa110_post * inv_rho**2 + 4*kappa011_post*kappa211_post * inv_rho + 2*kappa012_post*kappa210_post * inv_rho - 4*kappa020_post*kappa101_post**2 * inv_rho**2 + kappa020_post*kappa202_post * inv_rho + 2*kappa021_post*kappa201_post * inv_rho + kappa022_post*kappa200_post * inv_rho + 4*kappa101_post*kappa121_post * inv_rho + 2*kappa102_post*kappa120_post * inv_rho + 4*kappa110_post*kappa112_post * inv_rho + 4*kappa111_post**2 * inv_rho
            m_post_idx_0_0_c_0 = rho
            m_post_idx_0_0_c_1 = rho*w
            m_post_idx_0_0_c_2 = kappa002_post + rho*w**2
            m_post_idx_0_1_c_1 = kappa011_post
            m_post_idx_0_1_c_2 = 2*kappa011_post*w + kappa012_post
            m_post_idx_0_2_c_0 = kappa020_post
            m_post_idx_0_2_c_1 = kappa020_post*w + kappa021_post
            m_post_idx_0_2_c_2 = kappa020_post*w**2 + 2*kappa021_post*w + kappa022_post
            m_post_idx_1_0_c_1 = kappa101_post
            m_post_idx_1_0_c_2 = 2*kappa101_post*w + kappa102_post
            m_post_idx_1_1_c_0 = kappa110_post
            m_post_idx_1_1_c_1 = kappa110_post*w + kappa111_post
            m_post_idx_1_1_c_2 = kappa110_post*w**2 + 2*kappa111_post*w + kappa112_post
            m_post_idx_1_2_c_0 = kappa120_post
            m_post_idx_1_2_c_1 = kappa120_post*w + kappa121_post
            m_post_idx_1_2_c_2 = kappa120_post*w**2 + 2*kappa121_post*w + kappa122_post
            m_post_idx_2_0_c_0 = kappa200_post
            m_post_idx_2_0_c_1 = kappa200_post*w + kappa201_post
            m_post_idx_2_0_c_2 = kappa200_post*w**2 + 2*kappa201_post*w + kappa202_post
            m_post_idx_2_1_c_0 = kappa210_post
            m_post_idx_2_1_c_1 = kappa210_post*w + kappa211_post
            m_post_idx_2_1_c_2 = kappa210_post*w**2 + 2*kappa211_post*w + kappa212_post
            m_post_idx_2_2_c_0 = kappa220_post
            m_post_idx_2_2_c_1 = kappa220_post*w + kappa221_post
            m_post_idx_2_2_c_2 = kappa220_post*w**2 + 2*kappa221_post*w + kappa222_post
            m_post_idx_0_c_0_0 = m_post_idx_0_0_c_0
            m_post_idx_0_c_0_1 = m_post_idx_0_0_c_1
            m_post_idx_0_c_0_2 = m_post_idx_0_0_c_2
            m_post_idx_0_c_1_0 = m_post_idx_0_0_c_0*v
            m_post_idx_0_c_1_1 = m_post_idx_0_0_c_1*v + m_post_idx_0_1_c_1
            m_post_idx_0_c_1_2 = m_post_idx_0_0_c_2*v + m_post_idx_0_1_c_2
            m_post_idx_0_c_2_0 = m_post_idx_0_0_c_0*v**2 + m_post_idx_0_2_c_0
            m_post_idx_0_c_2_1 = m_post_idx_0_0_c_1*v**2 + 2*m_post_idx_0_1_c_1*v + m_post_idx_0_2_c_1
            m_post_idx_0_c_2_2 = m_post_idx_0_0_c_2*v**2 + 2*m_post_idx_0_1_c_2*v + m_post_idx_0_2_c_2
            m_post_idx_1_c_0_0 = 0
            m_post_idx_1_c_0_1 = m_post_idx_1_0_c_1
            m_post_idx_1_c_0_2 = m_post_idx_1_0_c_2
            m_post_idx_1_c_1_0 = m_post_idx_1_1_c_0
            m_post_idx_1_c_1_1 = m_post_idx_1_0_c_1*v + m_post_idx_1_1_c_1
            m_post_idx_1_c_1_2 = m_post_idx_1_0_c_2*v + m_post_idx_1_1_c_2
            m_post_idx_1_c_2_0 = 2*m_post_idx_1_1_c_0*v + m_post_idx_1_2_c_0
            m_post_idx_1_c_2_1 = m_post_idx_1_0_c_1*v**2 + 2*m_post_idx_1_1_c_1*v + m_post_idx_1_2_c_1
            m_post_idx_1_c_2_2 = m_post_idx_1_0_c_2*v**2 + 2*m_post_idx_1_1_c_2*v + m_post_idx_1_2_c_2
            m_post_idx_2_c_0_0 = m_post_idx_2_0_c_0
            m_post_idx_2_c_0_1 = m_post_idx_2_0_c_1
            m_post_idx_2_c_0_2 = m_post_idx_2_0_c_2
            m_post_idx_2_c_1_0 = m_post_idx_2_0_c_0*v + m_post_idx_2_1_c_0
            m_post_idx_2_c_1_1 = m_post_idx_2_0_c_1*v + m_post_idx_2_1_c_1
            m_post_idx_2_c_1_2 = m_post_idx_2_0_c_2*v + m_post_idx_2_1_c_2
            m_post_idx_2_c_2_0 = m_post_idx_2_0_c_0*v**2 + 2*m_post_idx_2_1_c_0*v + m_post_idx_2_2_c_0
            m_post_idx_2_c_2_1 = m_post_idx_2_0_c_1*v**2 + 2*m_post_idx_2_1_c_1*v + m_post_idx_2_2_c_1
            m_post_idx_2_c_2_2 = m_post_idx_2_0_c_2*v**2 + 2*m_post_idx_2_1_c_2*v + m_post_idx_2_2_c_2
            m000_post = m_post_idx_0_c_0_0 - 1
            m001_post = m_post_idx_0_c_0_1
            m002_post = m_post_idx_0_c_0_2 - self.INV_3
            m010_post = m_post_idx_0_c_1_0
            m011_post = m_post_idx_0_c_1_1
            m012_post = m_post_idx_0_c_1_2
            m020_post = m_post_idx_0_c_2_0 - self.INV_3
            m021_post = m_post_idx_0_c_2_1
            m022_post = m_post_idx_0_c_2_2 - self.INV_9
            m100_post = m_post_idx_0_c_0_0*u + m_post_idx_1_c_0_0
            m101_post = m_post_idx_0_c_0_1*u + m_post_idx_1_c_0_1
            m102_post = m_post_idx_0_c_0_2*u + m_post_idx_1_c_0_2
            m110_post = m_post_idx_0_c_1_0*u + m_post_idx_1_c_1_0
            m111_post = m_post_idx_0_c_1_1*u + m_post_idx_1_c_1_1
            m112_post = m_post_idx_0_c_1_2*u + m_post_idx_1_c_1_2
            m120_post = m_post_idx_0_c_2_0*u + m_post_idx_1_c_2_0
            m121_post = m_post_idx_0_c_2_1*u + m_post_idx_1_c_2_1
            m122_post = m_post_idx_0_c_2_2*u + m_post_idx_1_c_2_2
            m200_post = m_post_idx_0_c_0_0*u**2 + 2*m_post_idx_1_c_0_0*u + m_post_idx_2_c_0_0 - self.INV_3
            m201_post = m_post_idx_0_c_0_1*u**2 + 2*m_post_idx_1_c_0_1*u + m_post_idx_2_c_0_1
            m202_post = m_post_idx_0_c_0_2*u**2 + 2*m_post_idx_1_c_0_2*u + m_post_idx_2_c_0_2 - self.INV_9
            m210_post = m_post_idx_0_c_1_0*u**2 + 2*m_post_idx_1_c_1_0*u + m_post_idx_2_c_1_0
            m211_post = m_post_idx_0_c_1_1*u**2 + 2*m_post_idx_1_c_1_1*u + m_post_idx_2_c_1_1
            m212_post = m_post_idx_0_c_1_2*u**2 + 2*m_post_idx_1_c_1_2*u + m_post_idx_2_c_1_2
            m220_post = m_post_idx_0_c_2_0*u**2 + 2*m_post_idx_1_c_2_0*u + m_post_idx_2_c_2_0 - self.INV_9
            m221_post = m_post_idx_0_c_2_1*u**2 + 2*m_post_idx_1_c_2_1*u + m_post_idx_2_c_2_1
            m222_post = m_post_idx_0_c_2_2*u**2 + 2*m_post_idx_1_c_2_2*u + m_post_idx_2_c_2_2 - self.INV_27
            chimera_m_post_0_0_c_0 = m000_post - m200_post
            chimera_m_post_m1_0_c_0 = -m100_post * 0.5 + m200_post * 0.5
            chimera_m_post_1_0_c_0 = m100_post * 0.5 + m200_post * 0.5
            chimera_m_post_0_0_c_1 = m001_post - m201_post
            chimera_m_post_m1_0_c_1 = -m101_post * 0.5 + m201_post * 0.5
            chimera_m_post_1_0_c_1 = m101_post * 0.5 + m201_post * 0.5
            chimera_m_post_0_0_c_2 = m002_post - m202_post
            chimera_m_post_m1_0_c_2 = -m102_post * 0.5 + m202_post * 0.5
            chimera_m_post_1_0_c_2 = m102_post * 0.5 + m202_post * 0.5
            chimera_m_post_0_1_c_0 = m010_post - m210_post
            chimera_m_post_m1_1_c_0 = -m110_post * 0.5 + m210_post * 0.5
            chimera_m_post_1_1_c_0 = m110_post * 0.5 + m210_post * 0.5
            chimera_m_post_0_1_c_1 = m011_post - m211_post
            chimera_m_post_m1_1_c_1 = -m111_post * 0.5 + m211_post * 0.5
            chimera_m_post_1_1_c_1 = m111_post * 0.5 + m211_post * 0.5
            chimera_m_post_0_1_c_2 = m012_post - m212_post
            chimera_m_post_m1_1_c_2 = -m112_post * 0.5 + m212_post * 0.5
            chimera_m_post_1_1_c_2 = m112_post * 0.5 + m212_post * 0.5
            chimera_m_post_0_2_c_0 = m020_post - m220_post
            chimera_m_post_m1_2_c_0 = -m120_post * 0.5 + m220_post * 0.5
            chimera_m_post_1_2_c_0 = m120_post * 0.5 + m220_post * 0.5
            chimera_m_post_0_2_c_1 = m021_post - m221_post
            chimera_m_post_m1_2_c_1 = -m121_post * 0.5 + m221_post * 0.5
            chimera_m_post_1_2_c_1 = m121_post * 0.5 + m221_post * 0.5
            chimera_m_post_0_2_c_2 = m022_post - m222_post
            chimera_m_post_m1_2_c_2 = -m122_post * 0.5 + m222_post * 0.5
            chimera_m_post_1_2_c_2 = m122_post * 0.5 + m222_post * 0.5
            chimera_m_post_m1_c_0_0 = chimera_m_post_m1_0_c_0 - chimera_m_post_m1_2_c_0
            chimera_m_post_m1_c_m1_0 = -chimera_m_post_m1_1_c_0 * 0.5 + chimera_m_post_m1_2_c_0 * 0.5
            chimera_m_post_m1_c_1_0 = chimera_m_post_m1_1_c_0 * 0.5 + chimera_m_post_m1_2_c_0 * 0.5
            chimera_m_post_m1_c_0_1 = chimera_m_post_m1_0_c_1 - chimera_m_post_m1_2_c_1
            chimera_m_post_m1_c_m1_1 = -chimera_m_post_m1_1_c_1 * 0.5 + chimera_m_post_m1_2_c_1 * 0.5
            chimera_m_post_m1_c_1_1 = chimera_m_post_m1_1_c_1 * 0.5 + chimera_m_post_m1_2_c_1 * 0.5
            chimera_m_post_m1_c_0_2 = chimera_m_post_m1_0_c_2 - chimera_m_post_m1_2_c_2
            chimera_m_post_m1_c_m1_2 = -chimera_m_post_m1_1_c_2 * 0.5 + chimera_m_post_m1_2_c_2 * 0.5
            chimera_m_post_m1_c_1_2 = chimera_m_post_m1_1_c_2 * 0.5 + chimera_m_post_m1_2_c_2 * 0.5
            chimera_m_post_0_c_0_0 = chimera_m_post_0_0_c_0 - chimera_m_post_0_2_c_0
            chimera_m_post_0_c_m1_0 = -chimera_m_post_0_1_c_0 * 0.5 + chimera_m_post_0_2_c_0 * 0.5
            chimera_m_post_0_c_1_0 = chimera_m_post_0_1_c_0 * 0.5 + chimera_m_post_0_2_c_0 * 0.5
            chimera_m_post_0_c_0_1 = chimera_m_post_0_0_c_1 - chimera_m_post_0_2_c_1
            chimera_m_post_0_c_m1_1 = -chimera_m_post_0_1_c_1 * 0.5 + chimera_m_post_0_2_c_1 * 0.5
            chimera_m_post_0_c_1_1 = chimera_m_post_0_1_c_1 * 0.5 + chimera_m_post_0_2_c_1 * 0.5
            chimera_m_post_0_c_0_2 = chimera_m_post_0_0_c_2 - chimera_m_post_0_2_c_2
            chimera_m_post_0_c_m1_2 = -chimera_m_post_0_1_c_2 * 0.5 + chimera_m_post_0_2_c_2 * 0.5
            chimera_m_post_0_c_1_2 = chimera_m_post_0_1_c_2 * 0.5 + chimera_m_post_0_2_c_2 * 0.5
            chimera_m_post_1_c_0_0 = chimera_m_post_1_0_c_0 - chimera_m_post_1_2_c_0
            chimera_m_post_1_c_m1_0 = -chimera_m_post_1_1_c_0 * 0.5 + chimera_m_post_1_2_c_0 * 0.5
            chimera_m_post_1_c_1_0 = chimera_m_post_1_1_c_0 * 0.5 + chimera_m_post_1_2_c_0 * 0.5
            chimera_m_post_1_c_0_1 = chimera_m_post_1_0_c_1 - chimera_m_post_1_2_c_1
            chimera_m_post_1_c_m1_1 = -chimera_m_post_1_1_c_1 * 0.5 + chimera_m_post_1_2_c_1 * 0.5
            chimera_m_post_1_c_1_1 = chimera_m_post_1_1_c_1 * 0.5 + chimera_m_post_1_2_c_1 * 0.5
            chimera_m_post_1_c_0_2 = chimera_m_post_1_0_c_2 - chimera_m_post_1_2_c_2
            chimera_m_post_1_c_m1_2 = -chimera_m_post_1_1_c_2 * 0.5 + chimera_m_post_1_2_c_2 * 0.5
            chimera_m_post_1_c_1_2 = chimera_m_post_1_1_c_2 * 0.5 + chimera_m_post_1_2_c_2 * 0.5
            f_post[I + c[0]*ti.static(self.pop)][0] = chimera_m_post_0_c_0_0 - chimera_m_post_0_c_0_2
            f_post[I + c[1]*ti.static(self.pop)][1] = chimera_m_post_1_c_0_0 - chimera_m_post_1_c_0_2
            f_post[I + c[2]*ti.static(self.pop)][2] = chimera_m_post_m1_c_0_0 - chimera_m_post_m1_c_0_2
            f_post[I + c[3]*ti.static(self.pop)][3] = chimera_m_post_0_c_1_0 - chimera_m_post_0_c_1_2
            f_post[I + c[4]*ti.static(self.pop)][4] = chimera_m_post_0_c_m1_0 - chimera_m_post_0_c_m1_2
            f_post[I + c[5]*ti.static(self.pop)][5] = chimera_m_post_0_c_0_1 * 0.5 + chimera_m_post_0_c_0_2 * 0.5
            f_post[I + c[6]*ti.static(self.pop)][6] = -chimera_m_post_0_c_0_1 * 0.5 + chimera_m_post_0_c_0_2 * 0.5
            f_post[I + c[7]*ti.static(self.pop)][7] = chimera_m_post_1_c_1_0 - chimera_m_post_1_c_1_2
            f_post[I + c[8]*ti.static(self.pop)][8] = chimera_m_post_m1_c_m1_0 - chimera_m_post_m1_c_m1_2
            f_post[I + c[9]*ti.static(self.pop)][9] = chimera_m_post_1_c_m1_0 - chimera_m_post_1_c_m1_2
            f_post[I + c[10]*ti.static(self.pop)][10] = chimera_m_post_m1_c_1_0 - chimera_m_post_m1_c_1_2
            f_post[I + c[11]*ti.static(self.pop)][11] = chimera_m_post_1_c_0_1 * 0.5 + chimera_m_post_1_c_0_2 * 0.5
            f_post[I + c[12]*ti.static(self.pop)][12] = -chimera_m_post_m1_c_0_1 * 0.5 + chimera_m_post_m1_c_0_2 * 0.5
            f_post[I + c[13]*ti.static(self.pop)][13] = -chimera_m_post_1_c_0_1 * 0.5 + chimera_m_post_1_c_0_2 * 0.5
            f_post[I + c[14]*ti.static(self.pop)][14] = chimera_m_post_m1_c_0_1 * 0.5 + chimera_m_post_m1_c_0_2 * 0.5
            f_post[I + c[15]*ti.static(self.pop)][15] = chimera_m_post_0_c_1_1 * 0.5 + chimera_m_post_0_c_1_2 * 0.5
            f_post[I + c[16]*ti.static(self.pop)][16] = -chimera_m_post_0_c_m1_1 * 0.5 + chimera_m_post_0_c_m1_2 * 0.5
            f_post[I + c[17]*ti.static(self.pop)][17] = -chimera_m_post_0_c_1_1 * 0.5 + chimera_m_post_0_c_1_2 * 0.5
            f_post[I + c[18]*ti.static(self.pop)][18] = chimera_m_post_0_c_m1_1 * 0.5 + chimera_m_post_0_c_m1_2 * 0.5
            f_post[I + c[19]*ti.static(self.pop)][19] = chimera_m_post_1_c_1_1 * 0.5 + chimera_m_post_1_c_1_2 * 0.5
            f_post[I + c[20]*ti.static(self.pop)][20] = -chimera_m_post_m1_c_m1_1 * 0.5 + chimera_m_post_m1_c_m1_2 * 0.5
            f_post[I + c[21]*ti.static(self.pop)][21] = -chimera_m_post_1_c_1_1 * 0.5 + chimera_m_post_1_c_1_2 * 0.5
            f_post[I + c[22]*ti.static(self.pop)][22] = chimera_m_post_m1_c_m1_1 * 0.5 + chimera_m_post_m1_c_m1_2 * 0.5
            f_post[I + c[23]*ti.static(self.pop)][23] = chimera_m_post_1_c_m1_1 * 0.5 + chimera_m_post_1_c_m1_2 * 0.5
            f_post[I + c[24]*ti.static(self.pop)][24] = -chimera_m_post_m1_c_1_1 * 0.5 + chimera_m_post_m1_c_1_2 * 0.5
            f_post[I + c[25]*ti.static(self.pop)][25] = -chimera_m_post_1_c_m1_1 * 0.5 + chimera_m_post_1_c_m1_2 * 0.5
            f_post[I + c[26]*ti.static(self.pop)][26] = chimera_m_post_m1_c_1_1 * 0.5 + chimera_m_post_m1_c_1_2 * 0.5

            # update arrays of macroscopic vars
            lbm.rho[I] = xm3
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
        self.INV_3 = 1.0/3.0
        self.INV_9 = 1.0/9.0
        self.INV_54 = 1.0/54.0
        self.INV_216 = 1.0/216.0
        self.INV_27 = 1.0/27.0
