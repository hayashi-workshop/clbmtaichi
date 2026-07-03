# nested_bubble_d2q9_rho.py

import taichi as ti
import taichi.math as tm

INV_3 = 1.0/3.0

Macrovars = ti.types.struct(rho=float, u=float, v=float)
Cumulants = ti.types.struct(c20=float, c02=float, c11=float)
Coeffs = ti.types.struct(C0=float, Cx=float, Cy=float, Cxy=float, Cx2=float, Cy2=float)
SCoeffs = ti.types.struct(rho_coeffs=Coeffs, u_coeffs=Coeffs, v_coeffs=Coeffs)

@ti.func
def compute_cumulants(f: ti.template(), I): # f[I] is source
    f0 = f[I][0]
    f1 = f[I][1]
    f2 = f[I][2]
    f3 = f[I][3]
    f4 = f[I][4]
    f5 = f[I][5]
    f6 = f[I][6]
    f7 = f[I][7]
    f8 = f[I][8]
    x0 = f1 + f8
    x1 = f3 + f7 + x0
    x2 = f5 + f6
    x3 = f2 + x2
    x4 = f4 + x3
    x5 = -f7
    x6 = f5 - f6
    x7 = -f8
    m00 = f0 + x1 + x4
    m10 = -f3 + x0 + x5 + x6
    m01 = -f4 + x3 + x5 + x7
    m20 = x1 + x2
    m02 = f7 + f8 + x4
    m11 = f7 + x6 + x7
    rho = m00
    inv_rho = 1/rho
    u = m10 * inv_rho
    v = m01 * inv_rho
    c20 = m20 * inv_rho - u**2
    c02 = m02 * inv_rho - v**2
    c11 = m11 * inv_rho - u*v
    return rho, u, v, c20, c02, c11

@ti.func
def compute_interpolation_coeffs(f: ti.template(), I, omega):
    Imm = ti.Vector([I[0]  , I[1]  ])
    Imp = ti.Vector([I[0]  , I[1]+1])
    Ipm = ti.Vector([I[0]+1, I[1]  ])
    Ipp = ti.Vector([I[0]+1, I[1]+1])
    rho_mm, u_mm, v_mm, c20_mm, c02_mm, c11_mm = compute_cumulants(f, Imm)
    rho_mp, u_mp, v_mp, c20_mp, c02_mp, c11_mp = compute_cumulants(f, Imp)
    rho_pm, u_pm, v_pm, c20_pm, c02_pm, c11_pm = compute_cumulants(f, Ipm)
    rho_pp, u_pp, v_pp, c20_pp, c02_pp, c11_pp = compute_cumulants(f, Ipp)
    x0 = 3*omega * 0.0625
    x1 = c11_pm*x0
    x2 = 3*omega * 0.03125
    x3 = c02_pp*x2
    x4 = c20_mm*x2
    x5 = c11_mp*x0
    x6 = c02_mm*x2
    x7 = c20_pp*x2
    x8 = c02_mp*x2 - c02_pm*x2 - c11_mm*x0 + c11_pp*x0 - c20_mp*x2 + c20_pm*x2
    x9 = u_mp * 0.5
    x10 = u_pm * 0.5
    x11 = -x10
    x12 = u_mm * 0.5
    x13 = u_pp * 0.5
    x14 = -x13
    x15 = x12 + x14
    x16 = -x9
    x17 = 3*omega * 0.125
    x18 = c02_mp*x17
    x19 = c20_pm*x17
    x20 = v_mp * 0.5
    x21 = -v_pp * 0.5
    x22 = v_pm * 0.5
    x23 = v_mm * 0.5
    x24 = x20 + x21 + x22 - x23
    x25 = c02_mm*x17 - c02_pp*x17 - c20_mm*x17 + c20_pp*x17
    x26 = 3*omega * 0.25
    x27 = c11_mp*x26
    x28 = c11_pm*x26
    x29 = c11_mm*x26 - c11_pp*x26
    x30 = x21 + x23
    xr0 = rho_mp * 0.5
    xr1 = rho_pm * 0.5
    xr2 = rho_mm * 0.5 - rho_pp * 0.5
    u_coeffs = Coeffs(
        C0 = u_mm * 0.25 + u_mp * 0.25 + u_pm * 0.25 + u_pp * 0.25 - x1 - x3 - x4 + x5 + x6 + x7 + x8,
        Cx = -x11 - x15 - x9,
        Cy = -x10 - x15 - x16,
        Cxy = u_mm - u_mp - u_pm + u_pp,
        Cx2 = 3*c02_pm*omega * 0.125 + 3*c20_mp*omega * 0.125 - x18 - x19 - x24 - x25,
        Cy2 = x24 - x27 + x28 + x29,
    )
    v_coeffs = Coeffs(
        C0 = v_mm * 0.25 + v_mp * 0.25 + v_pm * 0.25 + v_pp * 0.25 + x1 + x3 + x4 - x5 - x6 - x7 + x8,
        Cx = -x20 + x22 - x30,
        Cy = x20 - x22 - x30,
        Cxy = v_mm - v_mp - v_pm + v_pp,
        Cx2 = x10 - x12 + x14 + x27 - x28 + x29 + x9,
        Cy2 = c02_pm*x17 + c20_mp*x17 + x11 + x12 + x13 + x16 - x18 - x19 + x25,
    )
    div_adv_term = 6*u_coeffs.C0*u_coeffs.Cx2 + 3*u_coeffs.C0*v_coeffs.Cxy + 3*u_coeffs.Cx**2 + 3*u_coeffs.Cxy*v_coeffs.C0 + 6*u_coeffs.Cy*v_coeffs.Cx + 6*v_coeffs.C0*v_coeffs.Cy2 + 3*v_coeffs.Cy**2
    rho_coeffs = Coeffs(
        C0 = div_adv_term * 0.125 + rho_mm * 0.25 + rho_mp * 0.25 + rho_pm * 0.25 + rho_pp * 0.25,
        Cx = -xr0 + xr1 - xr2,
        Cy = xr0 - xr1 - xr2,
        Cxy = rho_mm - rho_mp - rho_pm + rho_pp,
        Cx2 = -div_adv_term * 0.25,
        Cy2 = -div_adv_term * 0.25,
        Cz2 = -div_adv_term * 0.25,
    )
    return SCoeffs(rho_coeffs=rho_coeffs, u_coeffs=u_coeffs, v_coeffs=v_coeffs)

@ti.func
def backtrans_c_to_f(f: ti.template(), I, macrovars, cumulants): # f[I] is injection target: F->C or C->F
    rho = macrovars.rho
    u = macrovars.u
    v = macrovars.v
    c20 = cumulants.c20
    c02 = cumulants.c02
    c11 = cumulants.c11
    inv_rho = 1.0/rho
    kappa02 = c02*rho
    kappa11 = c11*rho
    kappa20 = c20*rho
    kappa22 = (kappa02*kappa20 + 2*kappa11**2) * inv_rho
    m_post_idx_0_c_0 = rho
    m_post_idx_0_c_1 = rho*v
    m_post_idx_0_c_2 = kappa02 + rho*v**2
    m_post_idx_1_c_1 = kappa11
    m_post_idx_1_c_2 = 2*kappa11*v
    m_post_idx_2_c_0 = kappa20
    m_post_idx_2_c_1 = kappa20*v
    m_post_idx_2_c_2 = kappa20*v**2 + kappa22
    m00_post = m_post_idx_0_c_0
    m01_post = m_post_idx_0_c_1
    m02_post = m_post_idx_0_c_2
    m10_post = m_post_idx_0_c_0*u
    m11_post = m_post_idx_0_c_1*u + m_post_idx_1_c_1
    m12_post = m_post_idx_0_c_2*u + m_post_idx_1_c_2
    m20_post = m_post_idx_0_c_0*u**2 + m_post_idx_2_c_0
    m21_post = m_post_idx_0_c_1*u**2 + 2*m_post_idx_1_c_1*u + m_post_idx_2_c_1
    m22_post = m_post_idx_0_c_2*u**2 + 2*m_post_idx_1_c_2*u + m_post_idx_2_c_2
    chimera_m_post_0_0 = m00_post - m20_post
    chimera_m_post_m1_0 = -m10_post * 0.5 + m20_post * 0.5
    chimera_m_post_1_0 = m10_post * 0.5 + m20_post * 0.5
    chimera_m_post_0_1 = m01_post - m21_post
    chimera_m_post_m1_1 = -m11_post * 0.5 + m21_post * 0.5
    chimera_m_post_1_1 = m11_post * 0.5 + m21_post * 0.5
    chimera_m_post_0_2 = m02_post - m22_post
    chimera_m_post_m1_2 = -m12_post * 0.5 + m22_post * 0.5
    chimera_m_post_1_2 = m12_post * 0.5 + m22_post * 0.5
    f[I][0] = chimera_m_post_0_0 - chimera_m_post_0_2
    f[I][1] = chimera_m_post_1_0 - chimera_m_post_1_2
    f[I][2] = chimera_m_post_0_1 * 0.5 + chimera_m_post_0_2 * 0.5
    f[I][3] = chimera_m_post_m1_0 - chimera_m_post_m1_2
    f[I][4] = -chimera_m_post_0_1 * 0.5 + chimera_m_post_0_2 * 0.5
    f[I][5] = chimera_m_post_1_1 * 0.5 + chimera_m_post_1_2 * 0.5
    f[I][6] = chimera_m_post_m1_1 * 0.5 + chimera_m_post_m1_2 * 0.5
    f[I][7] = -chimera_m_post_m1_1 * 0.5 + chimera_m_post_m1_2 * 0.5
    f[I][8] = -chimera_m_post_1_1 * 0.5 + chimera_m_post_1_2 * 0.5

@ti.func
def interpolation_FtoC(coeffs, omega):
    RC = coeffs.rho_coeffs
    UC = coeffs.u_coeffs
    VC = coeffs.v_coeffs
    INV_3omega = 1/(3*omega)
    UpScaling=2 # reconstructed gradient at F becomes twice when C observes it (chain rule in x_F <-> x_C)
    u = UC.C0
    v = VC.C0
    rho = RC.C0
    c11 = -(UC.Cy + VC.Cx) * INV_3omega * UpScaling
    c20 = -2*UC.Cx * INV_3omega * UpScaling + INV_3
    c02 = -2*VC.Cy * INV_3omega * UpScaling + INV_3
    macrovars = Macrovars(rho=rho, u=u, v=v)
    cumulants = Cumulants(c20=c20, c02=c02, c11=c11)
    return macrovars, cumulants

@ti.func
def interpolation_CtoF(coeffs, omega, coords):
    RC = coeffs.rho_coeffs
    UC = coeffs.u_coeffs
    VC = coeffs.v_coeffs
    x = coords[0]
    y = coords[1]
    INV_3omega = 1/(3*omega)
    DownScaling=0.5 # reconstructed gradient at C becomes half  when F observes it (chain rule in x_C <-> x_F)
    u = UC.C0 + UC.Cx*x + UC.Cx2*x*x + UC.Cxy*x*y + UC.Cy*y + UC.Cy2*y*y
    v = VC.C0 + VC.Cx*x + VC.Cx2*x*x + VC.Cxy*x*y + VC.Cy*y + VC.Cy2*y*y
    rho = RC.C0 + RC.Cx*x + RC.Cx2*x*x + RC.Cxy*x*y + RC.Cy*y + RC.Cy2*y*y
    c11 = -(UC.Cxy*x + UC.Cy + 2*UC.Cy2*y + VC.Cx + 2*VC.Cx2*x + VC.Cxy*y) * INV_3omega * DownScaling
    c20 = -2*(UC.Cx + 2*UC.Cx2*x + UC.Cxy*y) * INV_3omega * DownScaling + INV_3
    c02 = -2*(VC.Cxy*x + VC.Cy + 2*VC.Cy2*y) * INV_3omega * DownScaling + INV_3
    macrovars = Macrovars(rho=rho, u=u, v=v)
    cumulants = Cumulants(c20=c20, c02=c02, c11=c11)
    return macrovars, cumulants
