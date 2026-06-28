# -*- coding: utf-8 -*-
# ======================================================================================
# This code was generated with SymPy CSE code generator
# Discr: D3Q27
# Model: MRT
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

            # 1) Forward transformation from f to raw moment
            x0 = f19 + f21 + f23 + f25
            x1 = f20 + f24
            x2 = f22 + f26
            x3 = x1 + x2
            x4 = x0 + x3
            x5 = f11 + f13
            x6 = f12 + f14 + x4 + x5
            x7 = f10 + f8
            x8 = f7 + f9
            x9 = x7 + x8
            x10 = f1 + f2 + x6 + x9
            x11 = f15 + f18
            x12 = f16 + f17 + x11
            x13 = f5 + f6 + x12
            x14 = f3 + f4
            x15 = -f8
            x16 = -f14
            x17 = -f12
            x18 = -f26
            x19 = -f22
            x20 = x18 + x19
            x21 = -f20
            x22 = -f24
            x23 = x21 + x22
            x24 = x0 + x20 + x23
            x25 = x16 + x17 + x24 + x5
            x26 = -f25
            x27 = f19 + x26
            x28 = -f21
            x29 = f23 + x28
            x30 = x27 + x29
            x31 = x2 + x23 + x30
            x32 = f11 - f13
            x33 = f14 + x17 + x31 + x32
            x34 = -f17
            x35 = -f16
            x36 = x11 + x34 + x35
            x37 = -f9
            x38 = -f23
            x39 = f21 + x27 + x38
            x40 = f24 + x21
            x41 = f26 + x19
            x42 = x40 + x41
            x43 = x39 + x42
            x44 = f10 + x15
            x45 = f7 + x37 + x43 + x44
            x46 = f15 - f18
            x47 = f17 + x35 + x46
            x48 = x1 + x20 + x30
            x49 = -f19 - f7
            x50 = f19 + f25 + x28 + x38
            x51 = f20 + x22
            x52 = x41 + x50 + x51
            x53 = x4 + x9
            x54 = f22 + x18
            m000 = f0 + x10 + x13 + x14
            m100 = f1 - f10 - f2 + x15 + x25 + x8
            m001 = f5 - f6 + x33 + x36
            m010 = f3 - f4 + x45 + x47
            m200 = x10
            m101 = f12 + x16 + x32 + x48
            m110 = -f25 - f9 - x29 - x42 - x44 - x49
            m002 = x13 + x6
            m011 = f16 + x34 + x46 + x52
            m020 = x12 + x14 + x53
            m201 = x33
            m210 = x45
            m102 = x25
            m111 = x40 + x50 + x54
            m120 = -x26 - x28 - x3 - x37 - x38 - x49 - x7
            m012 = x43 + x47
            m021 = x31 + x36
            m202 = x6
            m211 = x52
            m220 = x53
            m112 = x39 + x51 + x54
            m121 = x48
            m022 = x12 + x4
            m212 = x43
            m221 = x31
            m122 = x24
            m222 = x4

            rho = m000
            inv_rho = 1.0 / rho
            u = m100 * inv_rho
            v = m010 * inv_rho
            w = m001 * inv_rho

            # Equilibrium moments (m_eq)
            m101_eq = rho*u*w
            m110_eq = rho*u*v
            m011_eq = rho*v*w
            m201_eq = rho*u**2*w + rho*w * self.INV_3
            m210_eq = rho*u**2*v + rho*v * self.INV_3
            m102_eq = rho*u*w**2 + rho*u * self.INV_3
            m111_eq = rho*u*v*w
            m120_eq = rho*u*v**2 + rho*u * self.INV_3
            m012_eq = rho*v*w**2 + rho*v * self.INV_3
            m021_eq = rho*v**2*w + rho*w * self.INV_3
            m202_eq = rho*u**2*w**2 + rho*u**2 * self.INV_3 + rho*w**2 * self.INV_3 + rho * self.INV_9
            m211_eq = rho*u**2*v*w + rho*v*w * self.INV_3
            m220_eq = rho*u**2*v**2 + rho*u**2 * self.INV_3 + rho*v**2 * self.INV_3 + rho * self.INV_9
            m112_eq = rho*u*v*w**2 + rho*u*v * self.INV_3
            m121_eq = rho*u*v**2*w + rho*u*w * self.INV_3
            m022_eq = rho*v**2*w**2 + rho*v**2 * self.INV_3 + rho*w**2 * self.INV_3 + rho * self.INV_9
            m212_eq = rho*u**2*v * self.INV_3 + rho*v*w**2 * self.INV_3 + rho*v * self.INV_9
            m221_eq = rho*u**2*w * self.INV_3 + rho*v**2*w * self.INV_3 + rho*w * self.INV_9
            m122_eq = rho*u*v**2 * self.INV_3 + rho*u*w**2 * self.INV_3 + rho*u * self.INV_9
            m222_eq = rho*u**2*v**2 * self.INV_3 + rho*u**2*w**2 * self.INV_3 + rho*u**2 * self.INV_9 + rho*v**2*w**2 * self.INV_3 + rho*v**2 * self.INV_9 + rho*w**2 * self.INV_9 + rho * self.INV_27
            mxx_eq = rho*u**2 - rho*v**2
            mzz_eq = rho*u**2 - rho*w**2
            mP_eq = rho*u**2 + rho*v**2 + rho*w**2 + rho

            # 2) Collision/relaxation in moment space
            m000_post = m000
            m100_post = m100
            m001_post = m001
            m010_post = m010
            m200_post = lbm.omega[1]*(m002 - m200 + mzz_eq) * self.INV_3 + lbm.omega[1]*(m020 - m200 + mxx_eq) * self.INV_3 + lbm.omega[2]*(-m002 - m020 - m200 + mP_eq) * self.INV_3 + m200
            m101_post = lbm.omega[1]*(-m101 + m101_eq) + m101
            m110_post = lbm.omega[1]*(-m110 + m110_eq) + m110
            m002_post = -2*lbm.omega[1]*(m002 - m200 + mzz_eq) * self.INV_3 + lbm.omega[1]*(m020 - m200 + mxx_eq) * self.INV_3 + lbm.omega[2]*(-m002 - m020 - m200 + mP_eq) * self.INV_3 + m002
            m011_post = lbm.omega[1]*(-m011 + m011_eq) + m011
            m020_post = lbm.omega[1]*(m002 - m200 + mzz_eq) * self.INV_3 - 2*lbm.omega[1]*(m020 - m200 + mxx_eq) * self.INV_3 + lbm.omega[2]*(-m002 - m020 - m200 + mP_eq) * self.INV_3 + m020
            m201_post = rho*u**2*w + rho*w * self.INV_3 + (1 - lbm.omega[3])*(m021 + m201) * 0.5 + (1 - lbm.omega[4])*(-m021 + m201) * 0.5
            m210_post = rho*u**2*v + rho*v * self.INV_3 + (1 - lbm.omega[3])*(m012 + m210) * 0.5 + (1 - lbm.omega[4])*(-m012 + m210) * 0.5
            m102_post = rho*u*w**2 + rho*u * self.INV_3 + (1 - lbm.omega[3])*(m102 + m120) * 0.5 - (1 - lbm.omega[4])*(-m102 + m120) * 0.5
            m111_post = lbm.omega[5]*(-m111 + m111_eq) + m111
            m120_post = rho*u*v**2 + rho*u * self.INV_3 + (1 - lbm.omega[3])*(m102 + m120) * 0.5 + (1 - lbm.omega[4])*(-m102 + m120) * 0.5
            m012_post = rho*v*w**2 + rho*v * self.INV_3 + (1 - lbm.omega[3])*(m012 + m210) * 0.5 - (1 - lbm.omega[4])*(-m012 + m210) * 0.5
            m021_post = rho*v**2*w + rho*w * self.INV_3 + (1 - lbm.omega[3])*(m021 + m201) * 0.5 - (1 - lbm.omega[4])*(-m021 + m201) * 0.5
            m202_post = lbm.omega[8]*(-m202 + m202_eq) + m202
            m211_post = lbm.omega[8]*(-m211 + m211_eq) + m211
            m220_post = lbm.omega[8]*(-m220 + m220_eq) + m220
            m112_post = lbm.omega[8]*(-m112 + m112_eq) + m112
            m121_post = lbm.omega[8]*(-m121 + m121_eq) + m121
            m022_post = lbm.omega[8]*(-m022 + m022_eq) + m022
            m212_post = lbm.omega[9]*(-m212 + m212_eq) + m212
            m221_post = lbm.omega[9]*(-m221 + m221_eq) + m221
            m122_post = lbm.omega[9]*(-m122 + m122_eq) + m122
            m222_post = lbm.omega[10]*(-m222 + m222_eq) + m222

            # 3) Backward transformation from m to f
            inv_x0 = m202_post * 0.5
            inv_x1 = -inv_x0
            inv_x2 = m222_post * 0.5
            inv_x3 = m220_post * 0.5
            inv_x4 = inv_x2 - inv_x3
            inv_x5 = (m100_post - m102_post - m120_post + m122_post) * 0.5
            inv_x6 = -m222_post * 0.5
            inv_x7 = inv_x3 + inv_x6
            inv_x8 = m022_post * 0.5
            inv_x9 = -inv_x8
            inv_x10 = (m010_post - m012_post - m210_post + m212_post) * 0.5
            inv_x11 = (m001_post - m021_post - m201_post + m221_post) * 0.5
            inv_x12 = m120_post * 0.25
            inv_x13 = m122_post * 0.25
            inv_x14 = -inv_x13
            inv_x15 = m222_post * 0.25
            inv_x16 = -inv_x15
            inv_x17 = inv_x14 + inv_x16
            inv_x18 = -m112_post * 0.25
            inv_x19 = m110_post * 0.25
            inv_x20 = (m220_post + 4*inv_x18 + 4*inv_x19) * 0.25
            inv_x21 = m212_post * 0.25
            inv_x22 = -inv_x21
            inv_x23 = m210_post * 0.25
            inv_x24 = inv_x22 + inv_x23
            inv_x25 = -inv_x12 + inv_x13
            inv_x26 = inv_x21 - inv_x23
            inv_x27 = (-m220_post + 4*inv_x15 + 4*inv_x18 + 4*inv_x19) * 0.25
            inv_x28 = m102_post * 0.25
            inv_x29 = -m121_post * 0.25
            inv_x30 = m101_post * 0.25
            inv_x31 = (m202_post + 4*inv_x29 + 4*inv_x30) * 0.25
            inv_x32 = m221_post * 0.25
            inv_x33 = -inv_x32
            inv_x34 = m201_post * 0.25
            inv_x35 = inv_x33 + inv_x34
            inv_x36 = inv_x13 - inv_x28
            inv_x37 = inv_x32 - inv_x34
            inv_x38 = (-m202_post + 4*inv_x15 + 4*inv_x29 + 4*inv_x30) * 0.25
            inv_x39 = -m211_post * 0.25
            inv_x40 = m011_post * 0.25
            inv_x41 = (m022_post + 4*inv_x16 + 4*inv_x39 + 4*inv_x40) * 0.25
            inv_x42 = m021_post * 0.25
            inv_x43 = inv_x33 + inv_x42
            inv_x44 = m012_post * 0.25
            inv_x45 = inv_x22 + inv_x44
            inv_x46 = inv_x21 - inv_x44
            inv_x47 = inv_x32 - inv_x42
            inv_x48 = (-m022_post + 4*inv_x15 + 4*inv_x39 + 4*inv_x40) * 0.25
            inv_x49 = m111_post * 0.125
            inv_x50 = m122_post * 0.125
            inv_x51 = m212_post * 0.125
            inv_x52 = m221_post * 0.125
            inv_x53 = inv_x49 + inv_x50 + inv_x51 + inv_x52
            inv_x54 = m121_post * 0.125
            inv_x55 = m211_post * 0.125
            inv_x56 = inv_x54 + inv_x55
            inv_x57 = m112_post * 0.125
            inv_x58 = m222_post * 0.125
            inv_x59 = inv_x57 + inv_x58
            inv_x60 = -inv_x57
            inv_x61 = -m222_post * 0.125
            inv_x62 = inv_x60 + inv_x61
            inv_x63 = -inv_x54
            inv_x64 = -inv_x55
            inv_x65 = inv_x63 + inv_x64
            inv_x66 = -inv_x51
            inv_x67 = inv_x49 - inv_x50
            inv_x68 = inv_x52 + inv_x66 + inv_x67
            inv_x69 = -inv_x52
            inv_x70 = inv_x51 + inv_x67 + inv_x69
            inv_x71 = inv_x55 + inv_x63
            inv_x72 = inv_x57 + inv_x61
            inv_x73 = inv_x58 + inv_x60
            inv_x74 = inv_x54 + inv_x64
            inv_x75 = inv_x49 + inv_x50 + inv_x66 + inv_x69
            f_post[I + c[0]*ti.static(self.pop)][0] = m000_post - m002_post - m020_post + m022_post - m200_post + m202_post + m220_post - m222_post
            f_post[I + c[1]*ti.static(self.pop)][1] = m200_post * 0.5 + inv_x1 + inv_x4 + inv_x5
            f_post[I + c[2]*ti.static(self.pop)][2] = m200_post * 0.5 - inv_x0 - inv_x5 - inv_x7
            f_post[I + c[3]*ti.static(self.pop)][3] = m020_post * 0.5 + inv_x10 + inv_x4 + inv_x9
            f_post[I + c[4]*ti.static(self.pop)][4] = m020_post * 0.5 - inv_x10 - inv_x7 - inv_x8
            f_post[I + c[5]*ti.static(self.pop)][5] = m002_post * 0.5 + inv_x1 + inv_x11 + inv_x2 + inv_x9
            f_post[I + c[6]*ti.static(self.pop)][6] = m002_post * 0.5 - inv_x0 - inv_x11 - inv_x6 - inv_x8
            f_post[I + c[7]*ti.static(self.pop)][7] = inv_x12 + inv_x17 + inv_x20 + inv_x24
            f_post[I + c[8]*ti.static(self.pop)][8] = inv_x16 + inv_x20 + inv_x25 + inv_x26
            f_post[I + c[9]*ti.static(self.pop)][9] = -inv_x24 - inv_x25 - inv_x27
            f_post[I + c[10]*ti.static(self.pop)][10] = -inv_x12 - inv_x14 - inv_x26 - inv_x27
            f_post[I + c[11]*ti.static(self.pop)][11] = inv_x17 + inv_x28 + inv_x31 + inv_x35
            f_post[I + c[12]*ti.static(self.pop)][12] = inv_x16 + inv_x31 + inv_x36 + inv_x37
            f_post[I + c[13]*ti.static(self.pop)][13] = -inv_x35 - inv_x36 - inv_x38
            f_post[I + c[14]*ti.static(self.pop)][14] = -inv_x14 - inv_x28 - inv_x37 - inv_x38
            f_post[I + c[15]*ti.static(self.pop)][15] = inv_x41 + inv_x43 + inv_x45
            f_post[I + c[16]*ti.static(self.pop)][16] = inv_x41 + inv_x46 + inv_x47
            f_post[I + c[17]*ti.static(self.pop)][17] = -inv_x43 - inv_x46 - inv_x48
            f_post[I + c[18]*ti.static(self.pop)][18] = -inv_x45 - inv_x47 - inv_x48
            f_post[I + c[19]*ti.static(self.pop)][19] = inv_x53 + inv_x56 + inv_x59
            f_post[I + c[20]*ti.static(self.pop)][20] = -inv_x53 - inv_x62 - inv_x65
            f_post[I + c[21]*ti.static(self.pop)][21] = -inv_x56 - inv_x62 - inv_x68
            f_post[I + c[22]*ti.static(self.pop)][22] = inv_x59 + inv_x65 + inv_x68
            f_post[I + c[23]*ti.static(self.pop)][23] = -inv_x70 - inv_x71 - inv_x72
            f_post[I + c[24]*ti.static(self.pop)][24] = inv_x70 + inv_x73 + inv_x74
            f_post[I + c[25]*ti.static(self.pop)][25] = inv_x71 + inv_x73 + inv_x75
            f_post[I + c[26]*ti.static(self.pop)][26] = -inv_x72 - inv_x74 - inv_x75

            # 4) Update arrays of macroscopic vars
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
        self.INV_3 = 1.0/3.0
        self.INV_9 = 1.0/9.0
        self.INV_54 = 1.0/54.0
        self.INV_216 = 1.0/216.0
        self.INV_27 = 1.0/27.0
