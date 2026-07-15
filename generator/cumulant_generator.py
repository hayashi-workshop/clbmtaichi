# cumulant_generator.py

import sys
import os
import sympy as sp
import itertools
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# weights w, lattice vectors c, equilibrium distribution f_eq, matrix M for raw moment
from generator.generator_utils.common_utils import calculate_weight, create_vectors
from generator.generator_utils.common_utils import create_feq_list
from generator.generator_utils.common_utils import create_trans_matrix

from generator.generator_utils.cumulant_utils import create_moment_dictionary
from generator.generator_utils.cumulant_utils import chimera_moment
from generator.generator_utils.cumulant_utils import generate_central_moment_expr
from generator.generator_utils.cumulant_utils import generate_cumulant_from_central
from generator.generator_utils.cumulant_utils import back_trans_kappa_to_raw
from generator.generator_utils.cumulant_utils import back_trans_raw_to_f

# code generator
from generator.generator_utils.export_utils import TypeWriter

def normalize_omega_config(input_vals, num_params):
    if input_vals is None:
        return [f"lbm.omega[{i}]" for i in range(1, num_params + 1)]    
    if not isinstance(input_vals, list):
        vals = [input_vals]
    else:
        vals = input_vals
    omega_values = vals + [1.0] * (num_params - len(vals)) # fill in omega list, and fill 1 if the given list is short
    return omega_values[:num_params] # if list size is too large, cut overflow

def create_omega_mapper(om_syms, input_vals, num_params):
    omega_values = normalize_omega_config(input_vals, num_params)
    omega_config = {}
    for i in range(1, len(om_syms)):
        val = omega_values[i-1] # note: 0-indexed, so shift i
        if isinstance(val, (int, float)):
            omega_config[om_syms[i]] = sp.sympify(val)
        else:
            omega_config[om_syms[i]] = sp.Symbol(val)            
    return omega_config

# collision_model = "BGK", "TRT", "MRT", "Cumulant"
# dimension = 2 (D2Q9) or 3 (D3Q27)
    # omega[1]  : shear -> omega
    # omega[2]  : bulk  -> omP (use this for omega_{-} in TRT)
    # omega[3]  : for sum  of combinations of 120, 102, 210, 012, 201, 021 in D3Q27; for 12, 21 in D2Q9 (om3)
    # omega[4]  : for diff of combinations of 120, 102, 210, 012, 201, 021 in D3Q27; for 12, 21 in D2Q9 (om3)
    # omega[5]  : for 111
    # omega[6]  : for 220, 202, 022; for 22 in D2Q9 (om4)
    # omega[7]  : for 220, 202, 022; for 22 in D2Q9 (om4)
    # omega[8]  : for 211, 121, 112
    # omega[9]  : for 221, 212, 122
    # omega[10] : for 222


def allrun(target_directory="./lb_solver/"):
    models  = ["BGK", "TRT", "MRT", "Cumulant"]
    vmodels = [(2, 9), (3, 27)]
    drho_mode = ["rho", "drho"]
    for model in models:
        for vmodel in vmodels:
            for rho in drho_mode:
                dim, Q = vmodel
                filename = f"d{dim}q{Q}_{model}_kernel.py" if rho=="rho" else f"d{dim}q{Q}_{model}_{rho}_kernel.py"
                run_generator(collision_model=model, drho_mode=rho, dimension=dim, omega_config_input=None, output_filename=filename)


def run_generator(collision_model="Cumulant", drho_mode="rho", dimension=3, omega_config_input=None, silent=False, output_filename="generated_kernel.py", target_directory="./lb_solver/"):
    density_shift = sp.Integer(1) if drho_mode == 'drho' else sp.Integer(0)

    output_filename = target_directory + output_filename

    dim = dimension
    num_params = 10 # [10 omegas]
    om_syms = [None] + list(sp.symbols(f'om1:{num_params + 1}')) # sp.symbols('om1 om2 ... om10') # om_syms[1] -> om1
    omega_config = create_omega_mapper(om_syms, omega_config_input, num_params)
    if not (silent):
        print("\n# omega setting: \n", omega_config)

    vectors = create_vectors(dim)                    # lattice vector c
    weights = [calculate_weight(v) for v in vectors] # weights w
    num_pops = len(vectors)                          # Q (9 or 27)

    all_orders = list(itertools.product((0, 1, 2), repeat=dim))
    moment_orders = sorted(all_orders, key=lambda x: (sum(x), -x[0]))
    mom_names = ["m" + "".join(map(str, order)) for order in moment_orders] # raw moment named m
    cum_names = ["c" + "".join(map(str, order)) for order in moment_orders] # cumulant named c

    # macroscopic variables
    rho_name = 'rho'
    vel_names = ['u', 'v', 'w'][:dim]
    rho = sp.Symbol(rho_name) # sympy symbol
    vel_syms = sp.symbols(vel_names) # sympy symbol
    cs2 = sp.Rational(1, 3) # sound speed square [not used]

    # distribution functions
    f_syms = sp.symbols([f'f{i}' for i in range(num_pops)]) # sympy symbol of f

    # packing moments symbols
    # moment, central moment, cumulant
    # pre/post
    M_raw, M_post, K_cen, K_post, C_cum, C_post = create_moment_dictionary(moment_orders, rho)
    moments_pack   = [M_raw, K_cen]
    cumulants_pack = [K_cen, K_post, C_cum, C_post]

    # will be sent to TypeWriter
    class_name, new_name, old_name = 'lbm', 'f_post', 'f_pre'
    default_pack = [dim, num_pops, collision_model, vectors, weights]
    misc_pack    = [ class_name, old_name, new_name ]

    # - * - macroscopic variables - * - #
    # physics : rho = sum f
    rho_expr = sum(f_syms) # rho = f0 + f1 + ...
    vel_exprs = []
    for d_idx in range(dim): # physics : v = sum c f / rho
        momentum_expr = sum(vec[d_idx] * f_syms[i] for i, vec in enumerate(vectors))
        vel_exprs.append( momentum_expr / ( rho_expr + density_shift ) ) # u = (f1 - f3 + ...)/(f0 + f1 + ...)

    macro_keys   = [rho_name] + vel_names
    macro_values = [rho_expr] + vel_exprs[:dim]
    macro_exprs  = dict(zip(macro_keys, macro_values)) # dict loos like macro_exprs = {'rho': rho_expr, 'u': vel_exprs[0], 'v': vel_exprs[1], 'w': vel_exprs[2]}

    feq_syms     = sp.symbols([f'feq{i}' for i in range(num_pops)])
    feq_exprs    = create_feq_list(dim, rho_expr, vel_exprs, vectors, weights, trunc=2) # expanded with f
    feq_raw_list = create_feq_list(dim, sp.Symbol(rho_name), sp.symbols(vel_names), vectors, weights, trunc=2) # raw equation (not expanded with f)

    # for drho mode
    # note: rho -> 1 + drho
    #              for coding simplicity, drho is written as rho
    feq_shift_list = [f - w for f, w in zip(feq_raw_list, weights)] # shifted distribution
    feq_shift_list = [ feq.xreplace({rho: density_shift + rho}) for feq in feq_shift_list ]

    feq_function = feq_raw_list if drho_mode=='rho' else feq_shift_list

    # console massage
    print(f"\n# -------------------------------------------------------------------------")
    print(f"# ")
    print(f"# >>> invoking {collision_model} code generator >>>")
    print(f"# ")
    print(f"# density shift mode :  {density_shift}")
    if drho_mode == 'drho' and collision_model is not "Cumulant":
        print(f"#                       [rho] in the generated eqs. should read [delta rho] ")
    print(f"# ")
    print(f"# -------------------------------------------------------------------------\n")


    pipe_exprs = {} # store expressions to pass all to code generator
    code_bundle = [] # to be updated in the following
    # -------------------------------------------------------------------------
    # <Model construction section>
    # -------------------------------------------------------------------------
    if collision_model == "BGK":
        # phase 1: constructing symbolic equations #
        if drho_mode == 'rho':
            feq_pipe = feq_raw_list
            feq_subs = feq_exprs
        else: # density shift
            feq_pipe = feq_shift_list
            feq_subs = [
                feq_shift_list[i].xreplace({sp.Symbol(k): v for k, v in macro_exprs.items()}) # need to cast 'rho' as sp.Symbol('rho') 
                for i in range(num_pops)
            ]

        f_new_map = { # collision modeling
            f"f{i}": (f_syms[i] + omega_config[om_syms[1]] * (feq_syms[i] - f_syms[i]))
            for i in range(num_pops)
        }
        pipe_exprs.update(macro_exprs)
        pipe_exprs.update( {f'feq{q}': feq_pipe[q] for q in range(num_pops)} ) 
        pipe_exprs['f'] = f_new_map

        # phase 2: conversion to LBM code enpowered by CSE
        subs_map = {feq_syms[i]: feq_subs[i] for i in range(num_pops)} # mapping feq0 -> (rho + 3*u...) for CSE
        cse_targets = [ # substitute equations to feq (feq_syms)
            expr.xreplace(subs_map) for expr in (list(macro_exprs.values()) + list(f_new_map.values()))
        ] # <- xreplace is much faster than subs. xreplace is good enough for the present purpose
        cse_targets = [sp.nsimplify(expr, tolerance=1e-15) for expr in cse_targets] # eliminate very small float value; 
        replacements, reduced_exprs = sp.cse(cse_targets)
        code_bundle = [replacements, reduced_exprs]


    elif collision_model == "TRT":
        # phase 1: constructing symbolic equations #
        pipe_exprs.update(macro_exprs)

        if drho_mode == 'rho':
            feq_pipe = feq_raw_list
            feq_subs = feq_exprs
        else: # density shift
            # note: rho -> 1 + drho
            #              for coding simplicity, drho is written as rho
            feq_shift_list = [f - w for f, w in zip(feq_raw_list, weights)] # shifted distribution
            feq_shift_list = [ feq.xreplace({rho: density_shift + rho}) for feq in feq_shift_list ]

            feq_pipe = feq_shift_list
            feq_subs = [
                feq_shift_list[i].xreplace({sp.Symbol(k): v for k, v in macro_exprs.items()}) # need to cast 'rho' as sp.Symbol('rho') 
                for i in range(num_pops)
            ]

        pipe_exprs.update( {f'feq{q}': feq_pipe[q] for q in range(num_pops)} ) 

        opp_map = {} # search opposite (-) direction
        for i, v in enumerate(vectors):
            opp_v = tuple(-c for c in v)
            opp_map[i] = vectors.index(opp_v)

        def generate_trt_collision(q, opp_q, om1, om2): # symbolic construction of collision terms
            f_plus     = sp.simplify((f_syms[q]   + f_syms[opp_q]  ) * sp.Rational(1,2))
            f_minus    = sp.simplify((f_syms[q]   - f_syms[opp_q]  ) * sp.Rational(1,2))
            f_eq_plus  = sp.simplify((feq_syms[q] + feq_syms[opp_q]) * sp.Rational(1,2))
            f_eq_minus = sp.simplify((feq_syms[q] - feq_syms[opp_q]) * sp.Rational(1,2))
            collision_expr_q     = sp.simplify(- om1 * (f_plus  - f_eq_plus))
            collision_expr_opp_q = sp.simplify(- om2 * (f_minus - f_eq_minus))
            return collision_expr_q, collision_expr_opp_q

        f_keys = list(sp.symbols(f'f:{num_pops}'))
        f_new_list = {}

        f_new_0 = f_syms[0] - omega_config[om_syms[1]] * (f_syms[0] - feq_syms[0]) 
        f_new_list[f_keys[0]] = f_new_0
        processed = set([0]) # to skip 0
        for q, opp_q in opp_map.items():
            if q in processed: continue
            expr_q, expr_opp = generate_trt_collision( q, opp_q, omega_config[om_syms[1]], omega_config[om_syms[2]] )
            f_new_list[f_keys[q]]     = f_syms[q]     + expr_q + expr_opp
            f_new_list[f_keys[opp_q]] = f_syms[opp_q] + expr_q - expr_opp
            processed.add(q)
            processed.add(opp_q)
        pipe_exprs['f_new'] = f_new_list

        # phase 2: conversion to LBM code enpowered by CSE
        cse_target_macro = list(macro_exprs.values())
        cse_target_feq   = feq_subs # cse_target_feq   = feq_exprs
        replacements_macro, reduced_macro = sp.cse(cse_target_macro, symbols=sp.symbols('xm0:500'))           
        replacements_feq  , reduced_feq   = sp.cse(cse_target_feq, symbols=sp.symbols('xe0:1000'))
        code_bundle = [
            [replacements_macro, reduced_macro],
            [replacements_feq, reduced_feq],
            [f_keys, f_new_list],
            [macro_keys, macro_exprs]
        ]


    elif collision_model == "MRT":        
        u, v = vel_syms[0], vel_syms[1] # eliminate 4th order terms (u^4) generated from more accurate Gauss-Hermite approximation in f_eq
        w = vel_syms[2] if len(vel_syms) > 2 else sp.Integer(0) 
        #high_order_subs = { # eliminating fourth-order tems u^4 from m_eq...
        #    u**4: 0, v**4: 0, w**4: 0,
        #    u**5: 0, v**5: 0, w**5: 0,
        #    u**6: 0, v**6: 0, w**6: 0
        #}
        M, M_inv = create_trans_matrix(moment_orders, vectors) # >>> Setting up transformation matrix from f to m

        # ---> updated feq is feq, not expand as 1 + drho at this phase
        feq_list_2nd = create_feq_list(dim, rho, vel_syms, vectors, weights, trunc=2) # constructing f_eq
        # < --- updated

        # v--- [previous version] we do not need to use 4th order feq
        #feq_list_4th = create_feq_list(dim, rho, vel_syms, vectors, weights, trunc=4) # constructing f_eq: (NOTE) f_eq generator retains 4th order (u^4) to derive correct m_eq (set trunc = 4)
        #if drho_mode == 'drho':
            # note: rho -> 1 + drho
            #              for coding simplicity, drho is written as rho
        #    feq_list_4th = [ feq.xreplace({rho: density_shift + rho}) for feq in feq_list_4th ]

        # phase 1: constructing symbolic equations #

        # generating equilibrium moments meq = M feq

        # v--- [previous version] incomplete moment reconstruction
        #m_eq_computed = M * sp.Matrix(feq_list_4th) - M * sp.Matrix(weights) * density_shift # subtract M w in 'drho' mode
        #m_eq_dict = {name: sp.expand(expr) for name, expr in zip(mom_names, m_eq_computed)}
        #
        #for name in m_eq_dict.keys():
        #    m_eq_dict[name] = sp.expand(m_eq_dict[name]).subs(high_order_subs)

        # ---> updated
        m_eq_computed = M * sp.Matrix(feq_list_2nd) # feq may be okay for 2nd order
        m_eq_dict = {name: sp.expand(expr) for name, expr in zip(mom_names, m_eq_computed)} # convert from sp.Matrix to dict

        W_vec_mat  = M * sp.Matrix(weights) * density_shift # subtract M w in 'drho' mode
        W_vec_dict = {name: sp.expand(expr) for name, expr in zip(mom_names, W_vec_mat)} # convert from sp.Matrix to dict

        # construction of moments m11, m21, m12, m22
        # 2D case
        # m11^eq = m10^eq * m01^eq / rho
        # m21^eq = m20^eq * m01^eq / rho
        # m12^eq = m10^eq * m02^eq / rho
        # m22^eq = m20^eq * m02^eq / rho
        #
        # 3D case example
        # m210^eq = m200^eq * m010^eq / rho
        # m101^eq = m100^eq * m001^eq / rho
        # m111^eq = m100^eq * m010^eq * m001^eq / rho^2
        # m222^eq = m200^eq * m020^eq * m002^eq / rho^2
        #
        for o, name in zip(moment_orders, mom_names): 
            partial_order_list = []
            for i in range(dim):
                val = o[i]
                if val in [1, 2]: # capture nonzero suffix in m_{alpha beta gamma}
                    partial_order_tmp = [0] * dim
                    partial_order_tmp[i] = val
                    partial_order = tuple(partial_order_tmp)

                    partial_order_list.append(partial_order)
            
            if len(partial_order_list) > 1: # skip m10, m01, m20, m02
                m_product = sp.Integer(1)/ ( rho ** (len(partial_order_list) - 1) ) # 1/rho or 1/rho^2
                for p_order in partial_order_list:
                    num_str = "".join(map(str, p_order))
                    partial_m_name = f"m{num_str}"
                    # e.g.) m21^eq = m20^eq * m01^eq / rho
                    #       m222^eq = m200^eq * m020^eq * m002^eq / rho^2
                    m_product *= m_eq_dict[partial_m_name] 

                m_eq_dict[name] = m_product # overwrite dict component
            
            m_eq_dict[name] = sp.expand( sp.simplify(m_eq_dict[name]) ) # expand eliminates rho in denominator

        for o, name in zip(moment_orders, mom_names):
            m_eq_dict[name] = sp.expand( m_eq_dict[name].subs({rho: density_shift + rho}) - W_vec_dict[name] )
            #print(f"0: {name} {m_eq_dict[name]} {W_vec_dict[name]}") # leftovers for debug
        # <--- updated


        # constructing collision/relaxation equations...
        processed_diagonal_2nd = set()
        processed_diagonal_3a4 = set()
        for o, name in zip(moment_orders, mom_names):
            total_order = sum(o)
            max_order = max(o)
            min_order = min(o)
            max_idx = max(o) if o else 0
            meq = sp.Symbol(f"{name}_eq")
            if total_order <= 1:
                M_post[o] = M_raw[o]
            elif total_order == 2:
                if max_idx == 1:
                    M_post[o] = M_raw[o] + omega_config[om_syms[1]] * (meq - M_raw[o])
                elif max_idx == 2:
                    if name in processed_diagonal_2nd: continue
                    if dim == 2:
                        mP_eq, mxx_eq = sp.symbols("mP_eq mxx_eq")
                        mP  = M_raw[(2,0)] + M_raw[(0,2)]
                        mxx = M_raw[(2,0)] - M_raw[(0,2)]
                        m_eq_dict["mP"]   = (m_eq_dict["m20"] + m_eq_dict["m02"])
                        m_eq_dict["mxx"]  = (m_eq_dict["m20"] - m_eq_dict["m02"])
                        mP_post  = (mP  + omega_config[om_syms[2]] * (mP_eq  - mP))
                        mxx_post = (mxx + omega_config[om_syms[1]] * (mxx_eq - mxx))
                        M_post[(2,0)] = (sp.Rational(1, 2) * (mP_post + mxx_post))
                        M_post[(0,2)] = (sp.Rational(1, 2) * (mP_post - mxx_post))
                        processed_diagonal_2nd.update(["m20", "m02"])
                    elif dim == 3:
                        mP_eq, mxx_eq, mzz_eq = sp.symbols("mP_eq mxx_eq mzz_eq")
                        mxx = M_raw[(2,0,0)] - M_raw[(0,2,0)]
                        mzz = M_raw[(2,0,0)] - M_raw[(0,0,2)]
                        mP  = M_raw[(2,0,0)] + M_raw[(0,2,0)] + M_raw[(0,0,2)]
                        m_eq_dict["mxx"] = (m_eq_dict["m200"] - m_eq_dict["m020"])
                        m_eq_dict["mzz"] = (m_eq_dict["m200"] - m_eq_dict["m002"])
                        m_eq_dict["mP"]  = (m_eq_dict["m200"] + m_eq_dict["m020"] + m_eq_dict["m002"])
                        mxx_post = (mxx  + omega_config[om_syms[1]] * (mxx_eq - mxx))
                        mzz_post = (mzz  + omega_config[om_syms[1]] * (mzz_eq - mzz))
                        mP_post  = (mP   + omega_config[om_syms[2]] * (mP_eq  - mP))
                        M_post[(2,0,0)] = ((mP_post + mxx_post + mzz_post) / 3)
                        M_post[(0,2,0)] = ((mP_post - 2 * mxx_post + mzz_post) / 3)
                        M_post[(0,0,2)] = ((mP_post + mxx_post - 2 * mzz_post) / 3)
                        processed_diagonal_2nd.update(["m200", "m020", "m002"])
            elif total_order >= 3:
                if dim == 2:
                    current_omega = omega_config[om_syms[6]] if total_order >= 4 else omega_config[om_syms[3]]
                    if current_omega == 1:
                        M_post[o] = meq
                    else:
                        M_post[o] = M_raw[o] + current_omega * (meq - M_raw[o])
                else: # 3D
                    current_omega = sp.Rational(1.0)
                    if total_order == 6: # 222
                        current_omega = omega_config[om_syms[10]]
                    elif total_order == 5: # 221, 212, 122
                        current_omega = omega_config[om_syms[9]]
                    # ---> updated: moved from lower part
                    elif total_order == 4 and min_order == 0: # 220, 202, 022 # no reason to repeat three times, but...
                        m220_eq = sp.Symbol('m220_eq') # added 
                        m202_eq = sp.Symbol('m202_eq') # added
                        m022_eq = sp.Symbol('m022_eq') # added
                        cross1_post = (M_raw[(2,2,0)] - 2 * M_raw[(2,0,2)] +     M_raw[(0,2,2)]) * (1.0 - omega_config[om_syms[6]]) + (m220_eq - 2 * m202_eq +     m022_eq)*omega_config[om_syms[6]] # meq corrected
                        cross2_post = (M_raw[(2,2,0)] +     M_raw[(2,0,2)] - 2 * M_raw[(0,2,2)]) * (1.0 - omega_config[om_syms[6]]) + (m220_eq +     m202_eq - 2 * m022_eq)*omega_config[om_syms[6]] # meq corrected
                        cross3_post = (M_raw[(2,2,0)] +     M_raw[(2,0,2)]     + M_raw[(0,2,2)]) * (1.0 - omega_config[om_syms[7]]) + (m220_eq +     m202_eq     + m022_eq)*omega_config[om_syms[7]] # meq corrected
                        M_post[(2,2,0)] = (   cross1_post + cross2_post + cross3_post ) / 3
                        M_post[(2,0,2)] = ( - cross1_post               + cross3_post ) / 3
                        M_post[(0,2,2)] = (               - cross2_post + cross3_post ) / 3
                        processed_diagonal_3a4.update(["m220","m202","m022"])
                    # <--- updated
                    elif total_order == 4: # 211, 121, 112
                        current_omega = omega_config[om_syms[8]]
                    elif total_order == 3:
                        if min_order == 1: # 111
                            current_omega = omega_config[om_syms[5]] 
                        else: # 120, 102, 210, 012, 201, 021
                            # ---> updated
                            m120_eq, m102_eq = sp.Symbol('m120_eq'), sp.Symbol('m102_eq') #m_eq_dict["m120"], m_eq_dict["m102"]
                            m210_eq, m012_eq = sp.Symbol('m210_eq'), sp.Symbol('m012_eq') #m_eq_dict["m210"], m_eq_dict["m012"]
                            m201_eq, m021_eq = sp.Symbol('m201_eq'), sp.Symbol('m021_eq') #m_eq_dict["m201"], m_eq_dict["m021"]
                            # <--- updated
                            sum1_post  = (1 - omega_config[om_syms[3]]) * (M_raw[(1,2,0)] + M_raw[(1,0,2)]) + (m120_eq + m102_eq)
                            sum2_post  = (1 - omega_config[om_syms[3]]) * (M_raw[(2,1,0)] + M_raw[(0,1,2)]) + (m210_eq + m012_eq)
                            sum3_post  = (1 - omega_config[om_syms[3]]) * (M_raw[(2,0,1)] + M_raw[(0,2,1)]) + (m201_eq + m021_eq)
                            diff1_post = (1 - omega_config[om_syms[4]]) * (M_raw[(1,2,0)] - M_raw[(1,0,2)]) + (m120_eq - m102_eq)
                            diff2_post = (1 - omega_config[om_syms[4]]) * (M_raw[(2,1,0)] - M_raw[(0,1,2)]) + (m210_eq - m012_eq)
                            diff3_post = (1 - omega_config[om_syms[4]]) * (M_raw[(2,0,1)] - M_raw[(0,2,1)]) + (m201_eq - m021_eq)
                            M_post[(1,2,0)] = (sum1_post + diff1_post) / 2
                            M_post[(2,1,0)] = (sum2_post + diff2_post) / 2
                            M_post[(2,0,1)] = (sum3_post + diff3_post) / 2
                            M_post[(1,0,2)] = (sum1_post - diff1_post) / 2
                            M_post[(0,1,2)] = (sum2_post - diff2_post) / 2
                            M_post[(0,2,1)] = (sum3_post - diff3_post) / 2
                            processed_diagonal_3a4.update(["m120","m210","m201","m102","m012","m021"])

                    elif total_order == 2:
                        if min_order == 1: # 110, 101, 011
                            current_omega = omega_config[om_syms[1]]
                        else: # 200, 020, 002
                            processed_diagonal_3a4.update(["m200","m020","m002"])

                    if name in processed_diagonal_3a4: 
                        continue
                    else:
                        if current_omega == 1.0:
                            M_post[o] = meq
                        else:
                            M_post[o] = M_raw[o] + current_omega * (meq - M_raw[o])

        m_post_syms = sp.symbols([f'{name}_post' for name in mom_names]) # computing post-collision f as M^(-1) m
        f_new_expr  = M_inv * sp.Matrix(m_post_syms)

        # ---> updated
        pipe_exprs.update( {f'feq{q}': feq_list_2nd[q] for q in range(num_pops)} ) 
        #pipe_exprs.update( {f'feq4th{q}': feq_list_4th[q] for q in range(num_pops)} ) 
        # <--- updated
        pipe_exprs['M']     = M
        pipe_exprs['M_inv'] = M_inv
        pipe_exprs.update( m_eq_dict )
        pipe_exprs.update( M_post )
        pipe_exprs.update( {f'f{q}': f_new_expr[q] for q in range(num_pops)} )

        # phase 2: conversion to LBM code enpowered by CSE
        m_exprs = [] # forward transformation from f to m
        # by definition m_ijk = sum cx^{i} cy^{j} cz^{k} f 
        for order in moment_orders:
            expr = 0
            for idx, vec in enumerate(vectors):
                term = 1
                for c, alpha in zip(vec, order):
                    term *= (c ** alpha)
                expr += term * f_syms[idx]
            m_exprs.append(expr)

        replacements, reduced = sp.cse(m_exprs) # applying CSE to forward transformation from f to m
        # ---> updated
        skip_eq_moms = {"m00", "m10", "m01", "m20", "m02", "m000", "m100", "m010", "m001", "m200", "m020", "m002"} # not to be included in kernel
        m_eq_dict = {k: v for k, v in m_eq_dict.items() if k not in skip_eq_moms}
        meq_replacements, meq_reduced = sp.cse(m_eq_dict.values()) # applying CSE to forward transformation from f to m
        # <--- updated
        inv_replacements, inv_reduced = sp.cse(list(f_new_expr)) # applying CSE to backward transformation from m to f

        code_bundle = [
            [replacements, reduced], 
            [meq_replacements, meq_reduced], # <--- updated
            [inv_replacements, inv_reduced],
            vel_names,
            [m_eq_dict, moment_orders, mom_names, M_post]
        ]


    elif collision_model == "Cumulant":
        # load generating function module
        # solve search path for generating_functions.py, in which path begins "from generator_utils."
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)

        from generator.generator_utils.generating_functions import CumulantGenerator
        from generator.generator_utils.generating_functions import MomentGenerator

        Cgen = CumulantGenerator(dim)
        Kgen = MomentGenerator(vectors, is_central_moment=True)

        # preparation for drho_mode = 'drho': transformed weight vector : M w
        M, M_inv = create_trans_matrix(moment_orders, vectors) # >>> Setting up transformation matrix from f to m
        w_vec = M * sp.Matrix(weights) * density_shift # M w in 'drho' mode
        order_to_weight = {order: w_vec[i] for i, order in enumerate(moment_orders)}


        # # # # # # # # # # # # # # # # # # # # # # #
        # phase 1: constructing symbolic equations  #
        # # # # # # # # # # # # # # # # # # # # # # #
        one = sp.Integer(1)
        orders_2nd = [o for o in moment_orders if sum(o) == 2]
        orders_3rd = [o for o in moment_orders if sum(o) == 3]
        orders_4th = [o for o in moment_orders if sum(o) == 4]
        orders_5th = [o for o in moment_orders if sum(o) == 5]
        orders_6th = [o for o in moment_orders if sum(o) == 6]


        from generator.generator_utils.cumulant_utils import generate_moment_expr
        from sympy import Eq

        # # # # # # # # # # # # # # # # # # # # # # # #
        # - * - forward transformation pipeline - * - #
        #             f -> m -> kappa -> C            #
        # # # # # # # # # # # # # # # # # # # # # # # #
        pipe_forward = {}

        # forward: f -> m
        pipe_exprs_m_chimera = {}

        first_chimera, second_chimera, v_map, pipe_exprs_m_chimera = chimera_moment(dim, vectors) 
        moment_chimera = [first_chimera, second_chimera] # forward transformation from f to central moment/cumulant

        M_raw_expr = {}
        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            M_raw_expr[o] = generate_moment_expr(moment_orders[i], first_chimera, second_chimera)

        # forward: m -> kappa
        K_cen_expr = {}

        kappa_subs_dict = {}
        cen_names = ["kappa" + "".join(map(str, order)) for order in moment_orders]

        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]

            kappa_eq = Kgen.derive_central_moment_from_moment(order=o, expr_with_velocity=True) # get kappa in terms of raw moments from generating fucntion
            
            k_sym, expr = kappa_eq.lhs, kappa_eq.rhs
            K_cen_expr[o] = expr # register kappa expr

            if sum(o) == 2:
                kappa_subs_dict.update({name: sp.solve(kappa_eq, name)[0]}) # solver for raw moment and add to subs_dict 

            if sum(o) > 2:
                K_cen_expr[o] = sp.simplify(K_cen_expr[o].subs(kappa_subs_dict)) # replace raw moments with lower order central moments
                kappa_subs_dict.update({k_sym: K_cen_expr[o]}) # add kappa expression to subs_dict for replacement at the next order
                kappa_subs_dict.update({name: sp.solve( Eq(k_sym, K_cen_expr[o]), name)[0]}) # solve for raw moment of the same order and add to sub_dict for replacement at the next order

        # ---> replace symbol \kappa_{o} with kappa'o' in equations 
        # prepare subs map
        ksym_subs_map = {}
        for o in moment_orders:
            o_name = "".join(map(str, o))
            raw_symbol_str = r"\kappa_{" + o_name + "}"
            ksym_subs_map.update({sp.Symbol(raw_symbol_str): sp.Symbol(f"kappa{o_name}")})

        for o in moment_orders:
            K_cen_expr[o] = K_cen_expr[o].subs(ksym_subs_map)
        # <---

        # forward: kappa -> cumulant
        C_cum_expr = {}
        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            C_eq = Cgen(o, density_scaling=True) # get cumulant
            C_cum_expr[o] = C_eq.rhs # register cumulant expr


        # - * - register forward transformation to pipeline - * - #
        #       pipeline to be exported to console 
        pipe_forward = pipe_forward | pipe_exprs_m_chimera

        for o in moment_orders:
            pipe_forward[M_raw[o]] = M_raw_expr[o] + order_to_weight[o]

        dm = sp.Symbol('dm'+'0'*dim)
        if drho_mode == 'drho':
            pipe_forward[dm] = M_raw_expr[(0,0,0)[:dim]]

        for o in moment_orders:
            if sum(o) > 1:
                pipe_forward[K_cen[o]] = K_cen_expr[o]

        for o in moment_orders:
            if sum(o) > 3:
                pipe_forward[C_cum[o]] = C_cum_expr[o]


        # # # # # # # # # # # # # # # # # # # # # # # #
        # - * -   collision in cumulant space   - * - #
        #                  C -> C^{*}                 #
        # # # # # # # # # # # # # # # # # # # # # # # #
        pipe_collision = {}

        # register all 0th and 1st order moments and kappa # -> # like (0,0,0), (0,1,0) and so on
        macro_orders = [(0,0,0), (1,0,0), (0,1,0), (0,0,1)] if dim == 3 else [(0,0), (1,0), (0,1)]
        for o in macro_orders:
            raw_expr, _ = generate_central_moment_expr(dim, o, rho, vel_syms, moment_chimera, moments_pack)

        # register all 2nd and 3rd order moments and kappa # -> # like (2,0,0), (2,1,1) and so on
        for o in orders_2nd + orders_3rd:
            raw_expr, cen_expr = generate_central_moment_expr(dim, o, rho, vel_syms, moment_chimera, moments_pack)

        # collision/relaxation process in Cumulant space
        cross_orders_2nd = [o for o in orders_2nd if max(o) == 1]
        for o in cross_orders_2nd:
            relaxation_expr = K_cen[o] + omega_config[om_syms[1]] * (0 - K_cen[o])
            pipe_collision[K_post[o]] = sp.simplify(relaxation_expr)

        kappa_diag_eq = sp.Rational(1, 3) * rho # isotropic component (pressure): rho * cs**2 = rho / 3
        if dim == 2:
            trace_mode = K_cen[(2, 0)] + K_cen[(0, 2)]
            trace_eq   = 2 * kappa_diag_eq # trace of eqilibrium values: 2 * rho / 3
            trace_post = trace_mode + omega_config[om_syms[2]] * (trace_eq - trace_mode)
            
            diff_mode  = K_cen[(2, 0)] - K_cen[(0, 2)]
            diff_post  = diff_mode + omega_config[om_syms[1]] * (0 - diff_mode)
            
            pipe_collision[K_post[(2, 0)]] = sp.simplify((trace_post + diff_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(0, 2)]] = sp.simplify((trace_post - diff_post) * sp.Rational(1, 2))
        else:
            trace_mode = K_cen[(2,0,0)] + K_cen[(0,2,0)] + K_cen[(0,0,2)]
            trace_eq   = 3 * kappa_diag_eq # trace of eqilibrium values: 3 * (rho/3) = rho
            trace_post = trace_mode + omega_config[om_syms[2]] * (trace_eq - trace_mode)

            diff1_mode = (K_cen[(2,0,0)] - K_cen[(0,2,0)])
            diff1_post = diff1_mode + omega_config[om_syms[1]] * (0 - diff1_mode)        
            diff2_mode = (K_cen[(2,0,0)] + K_cen[(0,2,0)] - 2 * K_cen[(0,0,2)])
            diff2_post = diff2_mode + omega_config[om_syms[1]] * (0 - diff2_mode)

            pipe_collision[K_post[(2,0,0)]] = sp.simplify((2 * trace_post + 3 * diff1_post + diff2_post) * sp.Rational(1, 6))
            pipe_collision[K_post[(0,2,0)]] = sp.simplify((2 * trace_post - 3 * diff1_post + diff2_post) * sp.Rational(1, 6))
            pipe_collision[K_post[(0,0,2)]] = sp.simplify((trace_post - diff2_post) * sp.Rational(1, 3))

        if dim == 2:
            for o in orders_3rd: # goes to zero equilibria
                relaxation_expr = K_cen[o] + omega_config[om_syms[3]] * (sp.Integer(0) - K_cen[o])
                pipe_collision[K_post[o]] = sp.simplify(relaxation_expr)
        else: 
            # 120, 102, 210, 012, 201, 021
            sum1_post  = (one - omega_config[om_syms[3]]) * (K_cen[(1,2,0)] + K_cen[(1,0,2)])
            sum2_post  = (one - omega_config[om_syms[3]]) * (K_cen[(2,1,0)] + K_cen[(0,1,2)])
            sum3_post  = (one - omega_config[om_syms[3]]) * (K_cen[(2,0,1)] + K_cen[(0,2,1)])
            diff1_post = (one - omega_config[om_syms[4]]) * (K_cen[(1,2,0)] - K_cen[(1,0,2)])
            diff2_post = (one - omega_config[om_syms[4]]) * (K_cen[(2,1,0)] - K_cen[(0,1,2)])
            diff3_post = (one - omega_config[om_syms[4]]) * (K_cen[(2,0,1)] - K_cen[(0,2,1)])
            pipe_collision[K_post[(1,2,0)]] = sp.simplify((sum1_post + diff1_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(2,1,0)]] = sp.simplify((sum2_post + diff2_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(2,0,1)]] = sp.simplify((sum3_post + diff3_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(1,0,2)]] = sp.simplify((sum1_post - diff1_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(0,1,2)]] = sp.simplify((sum2_post - diff2_post) * sp.Rational(1, 2))
            pipe_collision[K_post[(0,2,1)]] = sp.simplify((sum3_post - diff3_post) * sp.Rational(1, 2))

            # 111 
            o = (1,1,1)
            pipe_collision[K_post[o]] = sp.simplify( (one - omega_config[om_syms[5]]) * K_cen[o] )

        # cumulant transformation for orders higher than 3
        all_higher_orders = orders_4th + orders_5th + orders_6th
        special_4th_cross = {(2, 2, 0), (2, 0, 2), (0, 2, 2)}
        if dim == 3:

            cross1_post = (C_cum[(2,2,0)] - 2 * C_cum[(2,0,2)] + C_cum[(0,2,2)]) * (one - omega_config[om_syms[6]])
            cross2_post = (C_cum[(2,2,0)] + C_cum[(2,0,2)] - 2 * C_cum[(0,2,2)]) * (one - omega_config[om_syms[6]])
            cross3_post = (C_cum[(2,2,0)] + C_cum[(2,0,2)] + C_cum[(0,2,2)]) * (one - omega_config[om_syms[7]])
            pipe_collision[C_post[(2,2,0)]] = sp.simplify( (   cross1_post + cross2_post + cross3_post ) * sp.Rational(1, 3) )
            pipe_collision[C_post[(2,0,2)]] = sp.simplify( ( - cross1_post               + cross3_post ) * sp.Rational(1, 3) )
            pipe_collision[C_post[(0,2,2)]] = sp.simplify( ( - cross2_post               + cross3_post ) * sp.Rational(1, 3) )

            for o in special_4th_cross:
                _, k_post_expr = generate_cumulant_from_central(o, rho, cumulants_pack)
                pipe_collision[K_post[o]] = sp.expand(k_post_expr)

        processed = False
        for o in all_higher_orders:
            if dim == 2: # (2, 2) is the only case for 2D, and C22_eq = 0
                if processed:
                    pass
                else:
                    _, k_post_expr = generate_cumulant_from_central(o, rho, cumulants_pack)
                    if omega_config[om_syms[6]] == 1.0:
                        pipe_collision[C_post[o]] = sp.Integer(0)
                        pass
                    else:
                        pipe_collision[C_post[o]] = sp.simplify( (one - omega_config[om_syms[6]]) * C_cum[o] )
                    pipe_collision[K_post[o]] = sp.expand(k_post_expr)
                continue

            if dim == 3 and o in special_4th_cross:
                continue

            _, k_post_expr = generate_cumulant_from_central(o, rho, cumulants_pack)

            current_omega = omega_config[om_syms[8]]
            if sum(o) == 5: current_omega = omega_config[om_syms[9]]
            elif sum(o) == 6: current_omega = omega_config[om_syms[10]]

            pipe_collision[C_post[o]] = sp.simplify( (one - current_omega) * C_cum[o] )
            pipe_collision[K_post[o]] = sp.expand(k_post_expr)



        # # # # # # # # # # # # # # # # # # # # # # # #
        # - * - backward transformation pipeline - * -#
        #             C -> kappa -> m -> f            #
        # # # # # # # # # # # # # # # # # # # # # # # #
        pipe_backward = {}

        # backward Transformation from c_post to m_post
        pipe_backward = back_trans_kappa_to_raw(dim, moment_orders, vel_syms, K_post, M_post, pipe_backward) # backward transform: kappa to moment

        # shift post-collision raw moment to "shifted" raw moment before transforming back to f
        # this process does do nothing if drho_mode is 'rho'
        for o in moment_orders:
            if M_post[o] in pipe_backward:
                pipe_backward[M_post[o]] -= order_to_weight[o]

        # backward Transformation from m_post to f_post
        pipe_mtof = {}

        pipe_mtof, f_post_exprs = back_trans_raw_to_f(dim, v_map, M_post, pipe_mtof) # backward transform: moment to f

        ######################################### concat pipelines 
        pipe_exprs = pipe_forward | pipe_collision | pipe_backward | pipe_mtof


        # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # phase 2: conversion to LBM code enpowered by CSE  #
        # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # # # # # # # # # #
        # - * -Sympy CSE to forward transformation- * #
        # # # # # # # # # # # # # # # # # # # # # # # #

        # CSE -> only to chimera 
        chimera1st_targets = {}
        for suffix, chimera_sym in zip(first_chimera.keys(), first_chimera.values()):
            chimera1st_targets[chimera_sym] = pipe_exprs_m_chimera[chimera_sym]

        cse_targets_mc = ( list(chimera1st_targets.values()) )
        replacements_mc, reduced_exprs_mc = sp.cse(cse_targets_mc, symbols=sp.symbols('xm0:500'))

        # CSE -> central moment
        cse_targets_cm = []
        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            cse_targets_cm.append(K_cen_expr[o])

        replacements_cm, reduced_exprs_cm = sp.cse(cse_targets_cm, symbols=sp.symbols('xk0:500'))

        # CSE -> cumulant
        # first, expand expr to better replacement for 1/rho, 1/rho**2
        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            C_cum_expr[o] = sp.expand( C_cum_expr[o] )
       
        cse_targets_cl = []
        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            cse_targets_cl.append( C_cum_expr[o] )

        replacements_cl, reduced_exprs_cl = sp.cse(cse_targets_cl, symbols=sp.symbols('xc0:500'))

        # # # # CSE-based pipeline # # # #
        pipe_all = {}

        # [forward] raw moment
        for var, expr in replacements_mc:
            pipe_all[var] = expr

        for i, chimera_sym in enumerate(first_chimera.values()):
            pipe_all[chimera_sym] = reduced_exprs_mc[i]

        for suffix, key in zip(second_chimera.keys(), second_chimera.values()):
            pipe_all[key] = pipe_exprs_m_chimera[key]

        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            pipe_all[M_raw[o]] = M_raw_expr[o] + order_to_weight[o]

        if dm in pipe_forward:
            pipe_all[dm] = pipe_forward[dm]

        pipe_all[rho] = M_raw[(0,0,0)[:dim]]

        # [macroscopic variables]
        inv_rho = sp.Symbol('inv_rho')
        pipe_all[inv_rho] = 1.0/rho

        vel_orders = [(1,0,0)[:dim], (0,1,0)[:dim], (0,0,1)[:dim]][:dim]
        for d in range(dim):
            pipe_all[vel_syms[d]] = M_raw[vel_orders[d]]*inv_rho

        # [forward] central moment
        #
        # non CSE for kappa reconstruction
        # 
        # we have to decide Cascading or CSE
        #                   the former seems better
        '''
        for var, expr in replacements_cm:
            pipe_all[var] = expr

        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            if sum(o) > 1:
                pipe_all[K_cen[o]] = reduced_exprs_cm[i]
        '''
        for o in moment_orders:
            if sum(o) > 1:
                pipe_all[K_cen[o]] = K_cen_expr[o]

        # [forward] cumulant
        for var, expr in replacements_cl:
            pipe_all[var] = expr

        for i in range(len(moment_orders)):
            o, name = moment_orders[i], mom_names[i]
            if sum(o) > 3:
                pipe_all[C_cum[o]] = reduced_exprs_cl[i]

        # [collision]
        for key, expr in zip(pipe_collision.keys(), pipe_collision.values()):
            pipe_all[key] = expr

        # [backward]
        for key, expr in zip(pipe_backward.keys(), pipe_backward.values()):
            pipe_all[key] = expr

        # clean zeros # x = 0 may happen when omega=1 is set; 
        # trivial zeros are removed in this procedure
        pipe_clean = pipe_all

        zero_subs_map = {}

        while True:
            new_zeros_found = False
            keys_to_remove = []

            for key, expr in pipe_clean.items():
                substituted_expr = expr.subs(zero_subs_map) # eliminate zeros in expr

                if substituted_expr == 0:
                    zero_subs_map[key] = 0
                    keys_to_remove.append(key)
                    new_zeros_found = True
                else:
                    pipe_clean[key] = substituted_expr # store zero-eliminated expr

            for key in keys_to_remove:
                pipe_clean.pop(key) # remove zero vars

            if not new_zeros_found: # jump out when all zeros have been removed
                break

        code_bundle = [pipe_clean, pipe_mtof, macro_keys, vel_names]

        # -------------------------------------------------------------------------
        # <----------------------------------------------------- model construction
        # -------------------------------------------------------------------------

    # Boltzmann in the discretizaed world #
    def export_pipe(pipe, indent_str): # helper to write out symbolic equations #
        for key, val in pipe.items():
            if isinstance(val, dict):
                export_pipe(val, indent_str)
            else:
                print(f"{indent_str}{key} = {val}")

    if not (silent):
        print(f"\n# distributions: {f_syms}\n")
        if collision_model == "MRT" or collision_model == "Cumulant":
            print(f"\n# orders of moments: {moment_orders}\n\n")
        export_pipe(pipe_exprs, "") # export symblic equations

    replacements_eq, reduced_eq = sp.cse(feq_function, symbols=sp.symbols('xeq0:1000'))
    f_eq_pack = [replacements_eq, reduced_eq]

    # generate code #
    with TypeWriter(output_filename, collision_model, drho_mode, default_pack, misc_pack, code_bundle, f_eq_pack) as code_writer:
        code_writer.write()


    print(f"# ")
    print(f"# This is {collision_model} generator reporting;")
    print(f"# Generated code has been saved as {output_filename}")
    print(f"# Enjoy LB simulations!")
    print(f"# ")
    print(f"# tips: if you need to check the lb equations running, set silent=False.")
    print(f"# ")


if __name__ == "__main__":
    run_generator(collision_model="Cumulant", output_filename="lb_solver/generated_kernel.py")