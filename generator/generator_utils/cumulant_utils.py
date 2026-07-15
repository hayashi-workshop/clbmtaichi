# cumulant_utils.py

import sympy as sp
import itertools
import math

chimera_name = 'chimera'
chimera_delimiter = 'c'

def chimera_moment(dim, vectors, pipe_exprs=None):
    if pipe_exprs == None:
        pipe_exprs = {} # register chimera pipeline

    # dynamic loop based on vectors
    # dim=3: grouping (v[0], v[1]) and product sum for v[2] (k)
    # dim=2: grouping v[0] and product sum for v[1] (j)
    sum_axis = dim - 1
    group_keys = sorted(list(set(v[:sum_axis] for v in vectors)))
    v_map = {-1: "m1", 0: "0", 1: "1"}
    
    first_chimera = {}
    for g_key in group_keys:
        for gamma in [0, 1, 2]:
            expr = 0
            for idx, v in enumerate(vectors):
                if v[:sum_axis] == g_key:
                    k_val = v[sum_axis]
                    k_pow = 1 if (k_val == 0 and gamma == 0) else (k_val ** gamma)
                    expr += k_pow * sp.Symbol(f"f{idx}")

            expr = sp.simplify(expr)
            if dim == 3:
                var_sym = sp.Symbol(f"{chimera_name}_m_{v_map[g_key[0]]}_{v_map[g_key[1]]}_{chimera_delimiter}_{gamma}")
            else:
                var_sym = sp.Symbol(f"{chimera_name}_m_{v_map[g_key[0]]}_{chimera_delimiter}_{gamma}")
                
            first_chimera[(g_key, gamma)] = var_sym
            pipe_exprs[var_sym] = expr
                        
    second_chimera = {}
    if dim == 3:
        x_keys = sorted(list(set(v[0] for v in vectors)))
        for i_val in x_keys:
            for beta in [0, 1, 2]:
                for gamma in [0, 1, 2]:
                    expr = 0
                    for j_val in [-1, 0, 1]:
                        if ((i_val, j_val), gamma) in first_chimera:
                            j_pow = 1 if (j_val == 0 and beta == 0) else (j_val ** beta)
                            expr += j_pow * first_chimera[((i_val, j_val), gamma)]

                    expr = sp.simplify(expr)
                    var_sym = sp.Symbol(f"{chimera_name}_m_{v_map[i_val]}_{chimera_delimiter}_{beta}_{gamma}")
                    second_chimera[(i_val, beta, gamma)] = var_sym
                    pipe_exprs[var_sym] = expr
    
    return first_chimera, second_chimera, v_map, pipe_exprs


def create_moment_dictionary(moment_orders, rho):
    M_raw, M_post = {}, {} # raw moment
    K_cen, K_post = {}, {} # central moment 
    C_cum, C_post = {}, {} # cumulant (density scaled) 

    for o in moment_orders:
        o_name = "".join(map(str, o))
        order_sum = sum(o)
        
        M_raw[o]  = sp.Symbol(f"m{o_name}")
        M_post[o] = sp.Symbol(f"m{o_name}_post")

        if order_sum == 0:
            K_cen[o]  = rho
            K_post[o] = rho
        elif order_sum == 1:
            K_cen[o]  = sp.Rational(0)
            K_post[o] = sp.Rational(0)
        else:
            K_cen[o]  = sp.Symbol(f"kappa{o_name}")
            K_post[o] = sp.Symbol(f"kappa{o_name}_post")

        C_cum[o]  = sp.Symbol(f"C{o_name}")
        if order_sum == 0:
            C_post[o] = rho
        elif order_sum == 1:
            C_post[o] = sp.Rational(0)
        elif order_sum == 3:
            C_post[o] = sp.Rational(0)
        else:
            C_post[o] = sp.Symbol(f"C{o_name}_post")
    return M_raw, M_post, K_cen, K_post, C_cum, C_post

# ---> added 15 July
def generate_moment_expr(o, first_chimera, second_chimera):
    dim = len(o)

    expr_raw = 0
    if dim == 3:
        alpha, beta, gamma = o
        for i_val in [-1, 0, 1]:
            if (i_val, beta, gamma) in second_chimera:
                i_pow = 1 if (i_val == 0 and alpha == 0) else (i_val ** alpha)
                expr_raw += i_pow * second_chimera[(i_val, beta, gamma)]
    else:  # dim == 2
        alpha, beta = o
        for i_val in [-1, 0, 1]:
            target_key = ((i_val,), beta)
            if target_key in first_chimera:
                i_pow = 1 if (i_val == 0 and alpha == 0) else (i_val ** alpha)
                expr_raw += i_pow * first_chimera[target_key]
                
    return sp.simplify(expr_raw)
# <---

def generate_central_moment_expr(dim, o, rho, vel, m_chimeras, moments): # o is tupple like (2,0,1) expressing order of moment
    # this helper function generates 
    # raw moment expression     : expr_raw
    # central moment expression : expr_cen
    first_chimera, second_chimera = m_chimeras
    M_raw, K_cen = moments
    if dim == 2:
        u_sym, v_sym = vel
    else:
        u_sym, v_sym, w_sym = vel
    # -------------------------------------------------------------------------
    # Raw moment from chimera
    # -------------------------------------------------------------------------
    expr_raw = 0
    if dim == 3:
        alpha, beta, gamma = o
        for i_val in [-1, 0, 1]:
            if (i_val, beta, gamma) in second_chimera:
                i_pow = 1 if (i_val == 0 and alpha == 0) else (i_val ** alpha)
                expr_raw += i_pow * second_chimera[(i_val, beta, gamma)]
    else:  # dim == 2
        alpha, beta = o
        for i_val in [-1, 0, 1]:
            target_key = ((i_val,), beta)
            if target_key in first_chimera:
                i_pow = 1 if (i_val == 0 and alpha == 0) else (i_val ** alpha)
                expr_raw += i_pow * first_chimera[target_key]
                
    expr_raw = sp.simplify(expr_raw)

    # -------------------------------------------------------------------------
    # Central moment from raw moment
    # -------------------------------------------------------------------------
    if dim == 3:
        a, b, c = o
        term_a = u_sym * K_cen[(a-1, b, c)] if a >= 1 else 0
        term_b = v_sym * K_cen[(a, b-1, c)] if b >= 1 else 0
        term_c = w_sym * K_cen[(a, b, c-1)] if c >= 1 else 0
        vel_highest = rho * (u_sym**a) * (v_sym**b) * (w_sym**c)
        blend_expr = (a * term_a + b * term_b + c * term_c) + vel_highest
    else:  # dim == 2
        a, b = o
        term_a = u_sym * K_cen[(a-1, b)] if a >= 1 else 0
        term_b = v_sym * K_cen[(a, b-1)] if b >= 1 else 0
        vel_highest = rho * (u_sym**a) * (v_sym**b)
        blend_expr = (a * term_a + b * term_b) + vel_highest

    expr_cen = M_raw[o] - blend_expr

    return expr_raw, expr_cen


def generate_cumulant_from_central(o, rho, cumulants_pack):
    # Statistics (density scaled)
    # formulas for generating cumulative quantities
    # C_{n} = k_{n} - rho^{-1} sum_{parts_2} W_{2} kappa_{p1} kappa_{p2} + 2*rho^{-2} sum_{parts_3} W_{3} kappa_{p1} kappa_{p2} kappa_{p3} 
    # k_{n} = C_{n} + rho^{-1} sum_{parts_2} W_{2} kappa_{p1} kappa_{p2} - 2*rho^{-2} sum_{parts_3} W_{3} kappa_{p1} kappa_{p2} kappa_{p3}
    K_cen, K_post, C_cum, C_post = cumulants_pack

    if sum(o) <= 3:
        return K_cen[o], C_post[o]

    import itertools
    from collections import Counter

    # decompose given tuple into non-zero lower order tuples
    def find_tuple_partitions(target_tuple, n): # <- n = 2 and 3
        def p_parts(val, num_pieces):
            # ex) val=2, num_pieces=3 -> (2,0,0), (1,1,0)
            return [p for p in itertools.product(range(val + 1), repeat=num_pieces) if sum(p) == val]

        # list of choices
        axis_choices = [p_parts(val, n) for val in target_tuple]
        
        valid_partitions = []
        # search all combination
        for choices in itertools.product(*axis_choices):
            # choices -> ( (x1, x2, x3), (y1, y2, y3), (z1, z2, z3) )
            # ex) piece1 = (x1, y1, z1), piece2 = (x2, y2, z2)...
            pieces = tuple(tuple(choices[axis][i] for axis in range(len(target_tuple))) for i in range(n))
            
            # order 0 is not allowed
            if any(sum(p) == 0 for p in pieces):
                continue
            
            # sort and block duplication
            sorted_pieces = tuple(sorted(pieces))
            if sorted_pieces not in valid_partitions:
                valid_partitions.append(sorted_pieces)
                
        results = []
        for pieces in valid_partitions:
            num = 1
            for val in target_tuple:
                import math
                num *= math.factorial(val)
                
            den = 1
            for p in pieces:
                for val in p:
                    den *= math.factorial(val)
            
            counts = Counter(pieces)
            dup_div = 1
            for p, count in counts.items():
                dup_div *= math.factorial(count)
                
            weight = (num // den) // dup_div
            results.append((pieces, weight))
            
        return results

    parts_2 = find_tuple_partitions(o, 2) # kappa * kappa 
    cascade_sub_2 = 0
    cascade_add_2 = 0
    for pieces, w in parts_2:
        p1, p2 = pieces
        cascade_sub_2 += w * K_cen[p1] * K_cen[p2]
        cascade_add_2 += w * K_post[p1] * K_post[p2]

    parts_3 = find_tuple_partitions(o, 3) # kappa * kappa * kappa
    cascade_sub_3 = 0
    cascade_add_3 = 0
    for pieces, w in parts_3:
        p1, p2, p3 = pieces
        cascade_sub_3 += w * K_cen[p1] * K_cen[p2] * K_cen[p3]
        cascade_add_3 += w * K_post[p1] * K_post[p2] * K_post[p3]

    expr_c = K_cen[o] - (cascade_sub_2 / rho) + (2 * cascade_sub_3 / (rho**2))       # pre  collision, C = kappa + ...
    expr_k_post = C_post[o] + (cascade_add_2 / rho) - (2 * cascade_add_3 / (rho**2)) # post collision, kappa^* = C^* + ...

    return sp.simplify(expr_c), sp.simplify(expr_k_post)



def back_trans_kappa_to_raw(dim, moment_orders, vsym, K_post, M_post, pipe_exprs):
    current_k = {o: K_post[o] for o in moment_orders}
    if dim == 2:
        u_sym, v_sym = vsym
    else:
        u_sym, v_sym, w_sym = vsym

    if dim == 3:
        m_ij_gamma = {}
        for i in [0, 1, 2]:
            for j in [0, 1, 2]:
                for gamma in [0, 1, 2]:
                    expr = 0
                    for k in range(gamma + 1):
                        binom = math.comb(gamma, k)
                        u_pow = w_sym**(gamma - k) if (gamma - k) > 0 else 1
                        expr += binom * u_pow * current_k[(i, j, k)]

                    var_sym = sp.Symbol(f"m_post_idx_{i}_{j}_{chimera_delimiter}_{gamma}")
                    m_ij_gamma[(i, j, gamma)] = var_sym
                    pipe_exprs[var_sym] = sp.simplify(expr)
                    
        m_i_beta_gamma = {}
        for i in [0, 1, 2]:
            for beta in [0, 1, 2]:
                for gamma in [0, 1, 2]:
                    expr = 0
                    for j in range(beta + 1):
                        binom = math.comb(beta, j)
                        u_pow = v_sym**(beta - j) if (beta - j) > 0 else 1
                        expr += binom * u_pow * m_ij_gamma[(i, j, gamma)]

                    var_sym = sp.Symbol(f"m_post_idx_{i}_{chimera_delimiter}_{beta}_{gamma}")
                    m_i_beta_gamma[(i, beta, gamma)] = var_sym
                    pipe_exprs[var_sym] = sp.simplify(expr)
                    
        m_post_dict = {}
        for alpha in [0, 1, 2]:
            for beta in [0, 1, 2]:
                for gamma in [0, 1, 2]:
                    expr = 0
                    for i in range(alpha + 1):
                        binom = math.comb(alpha, i)
                        u_pow = u_sym**(alpha - i) if (alpha - i) > 0 else 1
                        expr += binom * u_pow * m_i_beta_gamma[(i, beta, gamma)]

                    o = (alpha, beta, gamma)
                    pipe_exprs[M_post[o]] = sp.simplify(expr)
                    
    else: # dim == 2
        m_i_gamma = {}
        for i in [0, 1, 2]:
            for gamma in [0, 1, 2]:
                expr = 0
                for j in range(gamma + 1):
                    binom = math.comb(gamma, j)
                    u_pow = v_sym**(gamma - j) if (gamma - j) > 0 else 1
                    expr += binom * u_pow * current_k[(i, j)]

                var_sym = sp.Symbol(f"m_post_idx_{i}_{chimera_delimiter}_{gamma}")
                m_i_gamma[(i, gamma)] = var_sym
                pipe_exprs[var_sym] = sp.simplify(expr)
                
        m_post_dict = {}
        for alpha in [0, 1, 2]:
            for beta in [0, 1, 2]:
                expr = 0
                for i in range(alpha + 1):
                    binom = math.comb(alpha, i)
                    u_pow = u_sym**(alpha - i) if (alpha - i) > 0 else 1
                    expr += binom * u_pow * m_i_gamma[(i, beta)]

                o = (alpha, beta)
                pipe_exprs[M_post[o]] = sp.simplify(expr)

    return pipe_exprs


def back_trans_raw_to_f(dim, v_map, M_post, pipe_exprs):
    f_post_exprs = {}

    if dim == 3:
        pm_a_b_e_g = {}
        for beta in [0, 1, 2]:
            for gamma in [0, 1, 2]:
                m0 = M_post[(0, beta, gamma)]
                m1 = M_post[(1, beta, gamma)]
                m2 = M_post[(2, beta, gamma)]
                pm0  = sp.simplify(  m0 - m2)
                pmm1 = sp.simplify((-m1 + m2) / 2)
                pm1  = sp.simplify(( m1 + m2) / 2)
                for i, expr in [(0, pm0), (-1, pmm1), (1, pm1)]:
                    var_sym = sp.Symbol(f"{chimera_name}_m_post_{v_map[i]}_{beta}_{chimera_delimiter}_{gamma}")
                    pm_a_b_e_g[(i, beta, gamma)] = var_sym
                    pipe_exprs[var_sym] = expr
                    
        pm_a_e_b_g = {}
        for i in [-1, 0, 1]:
            for gamma in [0, 1, 2]:
                pm_b0 = pm_a_b_e_g[(i, 0, gamma)]
                pm_b1 = pm_a_b_e_g[(i, 1, gamma)]
                pm_b2 = pm_a_b_e_g[(i, 2, gamma)]
                pm0  = sp.simplify(  pm_b0 - pm_b2)
                pmm1 = sp.simplify((-pm_b1 + pm_b2) / 2)
                pm1  = sp.simplify(( pm_b1 + pm_b2) / 2)
                for j, expr in [(0, pm0), (-1, pmm1), (1, pm1)]:
                    var_sym = sp.Symbol(f"{chimera_name}_m_post_{v_map[i]}_{chimera_delimiter}_{v_map[j]}_{gamma}")
                    pm_a_e_b_g[(i, j, gamma)] = var_sym
                    pipe_exprs[var_sym] = expr
                    
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                pm_g0 = pm_a_e_b_g[(i, j, 0)]
                pm_g1 = pm_a_e_b_g[(i, j, 1)]
                pm_g2 = pm_a_e_b_g[(i, j, 2)]
                f0  = sp.simplify(  pm_g0 - pm_g2)
                fm1 = sp.simplify((-pm_g1 + pm_g2) / 2)
                f1  = sp.simplify(( pm_g1 + pm_g2) / 2)
                for k, expr in [(0, f0), (-1, fm1), (1, f1)]:
                    f_post_sym = sp.Symbol(f"f_post_idx_{v_map[i]}_{v_map[j]}_{v_map[k]}")
                    f_post_exprs[(i, j, k)] = f_post_sym
                    pipe_exprs[f_post_sym] = expr
                    
    else: # dim == 2
        pm_a_e_g = {}
        for beta in [0, 1, 2]:
            m0 = sp.Symbol(f"m0{beta}_post")
            m1 = sp.Symbol(f"m1{beta}_post")
            m2 = sp.Symbol(f"m2{beta}_post")
            pm0  = sp.simplify(  m0 - m2)
            pmm1 = sp.simplify((-m1 + m2) / 2)
            pm1  = sp.simplify(( m1 + m2) / 2)
            for i, expr in [(0, pm0), (-1, pmm1), (1, pm1)]:
                var_sym = sp.Symbol(f"{chimera_name}_m_post_{v_map[i]}_{beta}")
                pm_a_e_g[(i, beta)] = var_sym
                pipe_exprs[var_sym] = expr
                
        for i in [-1, 0, 1]:
            pm_b0 = pm_a_e_g[(i, 0)]
            pm_b1 = pm_a_e_g[(i, 1)]
            pm_b2 = pm_a_e_g[(i, 2)]
            f0  = sp.simplify(  pm_b0 - pm_b2)
            fm1 = sp.simplify((-pm_b1 + pm_b2) / 2)
            f1  = sp.simplify(( pm_b1 + pm_b2) / 2)
            for j, expr in [(0, f0), (-1, fm1), (1, f1)]:
                f_post_sym = sp.Symbol(f"f_post_idx_{v_map[i]}_{v_map[j]}")
                f_post_exprs[(i, j)] = f_post_sym
                pipe_exprs[f_post_sym] = expr

    return pipe_exprs, f_post_exprs
