# nested_bubble_generator.py

import sys
import os
import io
import math

import sympy as sp
from sympy import symbols, Eq

import itertools
from itertools import product

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


from generator_utils.common_utils import calculate_weight
from generator_utils.common_utils import create_vectors
from generator_utils.common_utils import create_trans_matrix

from generator_utils.generating_functions import CumulantGenerator
from generator_utils.generating_functions import MomentGenerator


import re
def clean_symbol_name(symbol):
    name = str(symbol)
    clean_name = re.sub(r'_\{?([^{}]+)\}?', r'\1', name) # remove _{} srt
    return sp.symbols(clean_name)

def clean_symbol_name_kappa(symbol):
    name = symbol.name
    clean_name = (
        name.replace('_{', '')
            .replace('}', '')
            .replace('\\', '')
    )    
    return sp.symbols(clean_name)

def clean_symbol_name_kappa_to_c(symbol):
    name = symbol.name
    clean_name = (
        name.replace('_{', '')
            .replace('}', '')
            .replace('\\', '')
            .replace('kappa', 'c')
    )    
    return sp.symbols(clean_name)

def indent(level):
    base = "    "
    idt = ""
    for i in range(level):
        idt = idt + base
    return idt
idt = [indent(i) for i in range(10)]

def process_expression(used_inverses, expr_str):
    for i in range(1000, 0, -1):
        pattern = f"/{i}"
        if pattern in expr_str:
            temp_i = i
            while temp_i % 2 == 0: temp_i //= 2
            while temp_i % 5 == 0: temp_i //= 5

            if temp_i == 1:
                val = 1.0 / i 
                val_str = f"{val:.12g}".rstrip('0').rstrip('.')
                expr_str = expr_str.replace(pattern, f" * {val_str}")
            else:
                expr_str = expr_str.replace(pattern, f" * INV_{i}")
                used_inverses.add(i)

    # delete 1 * if the expression is 1 * INV_
    expr_str = expr_str.replace(" + 1 * ", " + ") 
    expr_str = expr_str.replace(" - 1 * ", " - ")

    return expr_str

def clean_div_terms(used_inverses, expr_str):
    expr_str = expr_str.replace("log(", "ti.log(")
    expr_str = re.sub(r'\b1/inv_rho\b', 'rho', expr_str)    
    expr_str = re.sub(r'/inv_rho\*\*2', ' * rho**2', expr_str)
    expr_str = re.sub(r'/inv_rho', ' * rho', expr_str)
    expr_str = re.sub(r'/rho\*\*2', ' * inv_rho**2', expr_str)
    expr_str = re.sub(r'/rho', ' * inv_rho', expr_str)
    expr_str = process_expression(used_inverses, expr_str)
    
    return expr_str


dims   = [2, 3]
rmodes = ["rho", "drho"]
output_dir = "../lb_utils/nested_utils/"

for dim, drho_mode in itertools.product(dims, rmodes):
    #dim = 2
    #drho_mode = 'drho' # 'rho'
    density_shift = sp.Integer(1) if drho_mode == 'drho' else sp.Integer(0)

    filename = f"nested_bubble_d{dim}q{3**dim}_{drho_mode}.py"
    file_abs = output_dir + filename

    buffer = io.StringIO()

    args_x         = ['x', 'y', 'z'][:dim]
    args_C_vels    = ['UC', 'VC', 'WC'][:dim]
    return_vels    = ['u', 'v', 'w'][:dim]
    args_x_str     = ", ".join(args_x)
    args_C_str     = ", ".join(args_C_vels)
    return_vel_str = ", ".join(return_vels)

    used_inverses = set()

    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #     preparation of symbols, macro vars, moment name dicts     #
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
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

    # preparation for drho_mode = 'drho': transformed weight vector : M w
    M, M_inv = create_trans_matrix(moment_orders, vectors) # >>> Setting up transformation matrix from f to m
    w_vec = M * sp.Matrix(weights) * density_shift # M w in 'drho' mode
    order_to_weight = {order: w_vec[i] for i, order in enumerate(moment_orders)}

    # moment generating function 
    moment_gen = MomentGenerator(vectors=create_vectors(dim=dim), is_central_moment=False)
    moment_gen.derive_symbolic_moment_sum()

    # relaxation parameter symbol
    omega = sp.Symbol('omega')



    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #                       compute cumulant                        #
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #

    rho_expr = sum(f_syms) # rho = f0 + f1 + ...

    # # # # # # # # # # # # # # 
    #         moments         #
    # # # # # # # # # # # # # # 

    # list of moments required in bubble function
    moment_pipe = {}

    mom_list = [ (2,0,0)[:dim], (0,2,0)[:dim], (1,1,0)[:dim], (0,0,2), (1,0,1), (0,1,1) ][:(dim*(dim-2)+3)]
    mom_eqs = {order: moment_gen(order) for order in mom_list}
    mom = {
        order: {
            'lhs': clean_symbol_name(eq.lhs), 
            'rhs': eq.rhs
        }
        for order, eq in mom_eqs.items()
    }
    mom_names = {order: data['lhs'] for order, data in mom.items()}
    mom_exprs = {order: data['rhs'] for order, data in mom.items()}

    # zeroth order moment
    zero_order_key = tuple([0] * dim)
    moment_pipe[f"m{''.join(map(str, zero_order_key))}"] = rho_expr + density_shift

    # first order moments 
    for d in range(dim):
        order = [0] * dim
        order[d] = 1
        order_tuple = tuple(order)
        
        key_name = f"m{''.join(map(str, order_tuple))}"
        moment_pipe[key_name] = sum(vec[d] * f_syms[i] for i, vec in enumerate(vectors))

    # second order moments 
    for order, data in mom.items(): 
        moment_pipe[str(data['lhs'])] = data['rhs']

    cse_target_keys = [ expr for expr in list(moment_pipe.keys()) ] 
    cse_targets     = [ expr for expr in list(moment_pipe.values()) ] 

    replacements_mom, reduced_mom = sp.cse(cse_targets)

    #print(moment_pipe) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging
    #print(replacements_mom) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging
    #print(reduced_mom) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging


    # # # # # # # # # # # # # # 
    #        cumulants        #
    # # # # # # # # # # # # # # 

    # construct second order cumulants 
    cumulant_pipe = {}

    kappa = {}
    for order in mom_list:
        eq = moment_gen.derive_central_moment_from_moment(order, expr_with_velocity=True)    
        clean_lhs = clean_symbol_name_kappa(eq.lhs)
        
        kappa[order] = {
            'lhs': clean_lhs,
            'rhs': eq.rhs
        }

    cum = {}
    for order in mom_list:
        eq = moment_gen.derive_central_moment_from_moment(order, expr_with_velocity=True)    
        clean_lhs = clean_symbol_name_kappa_to_c(eq.lhs)
        
        cum[order] = {
            'lhs': clean_lhs,
            'rhs': eq.rhs / rho
        }

    for order, data in cum.items():
        cumulant_pipe[str(data['lhs'])] = data['rhs']

    cumulant_list = [str(val['lhs']) for val in cum.values()] # list cumulants to be returned

    #print(kappa) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging
    #print(cum) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging
    #print(cumulant_pipe) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging



    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #                      compute coefficients                     #
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #

    cdiff = []
    if dim == 3:
        cdiff = ['c200Mc020', 'c200Mc002']
    vars_list = ['rho'] + vel_names + [str(s) for s in cumulant_list] + cdiff

    #print(vars_list) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging


    def create_var_grid(dim, vars_list):
        coords = list(product([0, 1], repeat=dim)) # dim=2 -> [(0,0), (0,1), (1,0), (1,1)]

        def get_suffix(coord): # 0='m', 1='p'
            return "".join(['m' if c == 0 else 'p' for c in coord])
        
        grid_map = {coord: get_suffix(coord) for coord in coords} # (0,0) -> 'mm', (0,1) -> 'mp', ...

        var_mats = {v: {} for v in vars_list} # var_mats[var_name][(z, y, x)] = symbol    
        for coord in coords:
            suffix = get_suffix(coord)
            for v in vars_list:
                symbol_name = f"{v}_{suffix}"
                var_mats[v][coord] = sp.Symbol(symbol_name)
                
        return var_mats, grid_map

    var_mats, grid_map = create_var_grid(dim, vars_list)

    #print(var_mats) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging
    #print(grid_map) # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # leftovers of debugging



    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - - - - - - - - - - - -        setup equations         - - - - - - - - - - - - - ->
    #
    # prepare interpolation equations of u, v, w, rho in "interpolation_exprs" 
    # e.g.)
    # interpolation_vel_expr['u'] = a0 + ax*x + ay*y + axy*x*y + ax2*x*x + ay2*y*y (2D case)
    #
    # compute first order derivatives of the interpolation functions
    # e.g.)
    # dudy is computed and stored in 
    # first_derivs['u']['y'] = ay + axy*x + 2*ay2*y (2D case)
    #
    # compute second order derivatives of the interpolation functions
    # e.g.)
    # d^2u/dy^2 is computed and stored in 
    # second_derivs['u']['yy'] = 2*ay2 (2D case)
    #

    # num of coeffs
    #  6 = dim**2 + 2
    # 11 = dim**2 + 2
    ncoeff = dim**2 + 2

    x, y, z = sp.symbols('x y z')
    x_sym_list = [x,y,z][:dim]
    terms = [1, x, y, x*y, x**2, y**2, z, x*z, y*z, x*y*z, z**2][:ncoeff]

    # compute parts for "laplacian rho" equation
    first_deriv_types = {
        'x': (x),
        'y': (y),
        'z': (z)
    }

    second_deriv_types = {
        'xx': (x, x),
        'yy': (y, y),
        'xy': (x, y),
        'zz': (z, z),
        'xz': (x, z),
        'yz': (y, z),
    }

    delta = sp.Rational(1,2)

    coords = {
        (0, 0, 0)[:dim]: (-delta, -delta, -delta)[:dim], # mmm
        (0, 1, 0)[:dim]: (-delta,  delta, -delta)[:dim], # mpm
        (1, 0, 0)[:dim]: ( delta, -delta, -delta)[:dim], # pmm
        (1, 1, 0)[:dim]: ( delta,  delta, -delta)[:dim], # ppm
        (0, 0, 1)[:dim]: (-delta, -delta,  delta)[:dim], # mmp
        (0, 1, 1)[:dim]: (-delta,  delta,  delta)[:dim], # mpp
        (1, 0, 1)[:dim]: ( delta, -delta,  delta)[:dim], # pmp
        (1, 1, 1)[:dim]: ( delta,  delta,  delta)[:dim]  # ppp
    }

    a0, ax, ay, axy, ax2, ay2, az, axz, ayz, axyz, az2 = sp.symbols('a0 ax ay axy ax2 ay2 az axz ayz axyz az2')
    b0, bx, by, bxy, bx2, by2, bz, bxz, byz, bxyz, bz2 = sp.symbols('b0 bx by bxy bx2 by2 bz bxz byz bxyz bz2')
    c0, cx, cy, cxy, cx2, cy2, cz, cxz, cyz, cxyz, cz2 = sp.symbols('c0 cx cy cxy cx2 cy2 cz cxz cyz cxyz cz2')
    d0, dx, dy, dxy, dx2, dy2, dz, dxz, dyz, dxyz, dz2 = sp.symbols('d0 dx dy dxy dx2 dy2 dz dxz dyz dxyz dz2')

    # # reconstruct interpolation exprs for export phase # # ---> dD in rho is replaced with x2 or y2
    coeffs_map     = ['0', 'x', 'y', 'xy', 'x2', 'y2', 'z', 'xz', 'yz', 'xyz', 'z2'][:ncoeff]
    coeffs_map_rho = ['0', 'x', 'y', 'xy',  'D',  'D', 'z', 'xz', 'yz', 'xyz',  'D'][:ncoeff]

    var_config = [
        ('u',   'a', coeffs_map),
        ('v',   'b', coeffs_map),
        ('w',   'c', coeffs_map),
        ('rho', 'd', coeffs_map), 
    ]#[:dim+1]

    var_config_vel = [
        ('u', 'a', coeffs_map),
        ('v', 'b', coeffs_map),
        ('w', 'c', coeffs_map)
    ]#[:dim]

    var_config_rho = [
        ('rho', 'd', coeffs_map_rho)
    ]

    interpolation_exprs = {}
    for var_name, prefix, suffix_list in var_config:
        c_names = [f"{prefix}{suffix}" for suffix in suffix_list]
        coeffs = sp.symbols(' '.join(c_names))    
        interpolation_exprs[var_name] = sum(c * term for c, term in zip(coeffs, terms))

    interpolation_vel_exprs = {}
    for var_name, prefix, suffix_list in var_config_vel:
        c_names = [f"{prefix}{suffix}" for suffix in suffix_list]
        coeffs = sp.symbols(' '.join(c_names))
        interpolation_vel_exprs[var_name] = sum(c * term for c, term in zip(coeffs, terms))

    interpolation_rho_exprs = {}
    for var_name, prefix, suffix_list in var_config_rho:
        c_names = [f"{prefix}{suffix}" for suffix in suffix_list]
        coeffs = sp.symbols(' '.join(c_names))    
        interpolation_rho_exprs[var_name] = sum(c * term for c, term in zip(coeffs, terms))

    # compute first and second order derivatives of velocity components
    first_derivs = {}
    for var_name, expr in interpolation_vel_exprs.items():
        first_derivs[var_name] = {}
        for d_type, var in first_deriv_types.items():
            first_derivs[var_name][d_type] = sp.diff(expr, var)

    second_derivs = {}
    for var_name, expr in interpolation_exprs.items():
        second_derivs[var_name] = {}
        for d_type, (var1, var2) in second_deriv_types.items():
            second_derivs[var_name][d_type] = sp.diff(expr, var1, var2)

    coord_names = ['x', 'y', 'z'][:dim]
    vel_map = {coord: interpolation_vel_exprs[vel] for coord, vel in zip(coord_names, vel_names)}

    # compute advection term for laplacian rho equation
    adv_terms = {
        var: {
            coord: vel_map[coord] * first_derivs[var][coord]
            for coord in coord_names
        }
        for var in vel_names
    }

    advection_terms = {
        var: sum(adv_terms[var].values())
        for var in vel_names
    }


    # - * - * - constraint for interpolation function at four/eight nodes - * - * - 
    def constraint_equations_at_nodes(target_vars, interpolation_eq, var_mats, coords, x_sym_list):
        equations = []

        for var_name in target_vars:
            mat = var_mats[var_name]
            expr = interpolation_eq[var_name]
            
            for coord, points in coords.items():
                sub_dict = dict(zip(x_sym_list, points))

                eq = expr.subs(sub_dict) - mat[coord]
                equations.append(eq)

        return equations



    # div u dot nabla u #
    div_u_dot_nabla_u = sum(
        sp.diff(advection_terms[vel], coord)
        for vel, coord in zip(vel_names, coord_names)
    )

    div_u_dot_nabla_u = sp.diff(advection_terms['u'], x) + sp.diff(advection_terms['v'], y)

    xsubs_map = {x: 0, y: 0, z: 0}
    div_adv_term_expr = 3 * div_u_dot_nabla_u.subs(xsubs_map)


    # laplacian rho = - 3 rho0 div u dot nabla u
    div_adv_term_name = 'div_adv_term'
    div_adv_term = sp.Symbol(div_adv_term_name)
    rho_expr = interpolation_rho_exprs['rho']
    laplacian_rho = sp.diff(rho_expr, x, 2) + sp.diff(rho_expr, y, 2)

    eq_laplace_rho = laplacian_rho + div_adv_term # laplacian rho = - 3 rho0 div u dot nabla u

    # ---> construct and solve rho equations
    equations_rho = constraint_equations_at_nodes(['rho'], interpolation_rho_exprs, var_mats, coords, x_sym_list)
    # set additional constraint for rho via div (NS equation)
    equations_rho.append(eq_laplace_rho)

    all_coeffs_rho = [] # list all rho coefficients to be solved for
    for var_name, prefix, suffix_list in var_config_rho:
        unique_suffixes = list(dict.fromkeys(suffix_list)) # eliminate duplication of 'D' 
        c_names = [f"{prefix}{suffix}" for suffix in unique_suffixes]
        all_coeffs_rho.extend(sp.symbols(' '.join(c_names)))

    solution_tuple = sp.linsolve(equations_rho, all_coeffs_rho)
    solution_dict  = dict(zip(all_coeffs_rho, next(iter(solution_tuple))))
    expr_list_rho  = list(solution_dict.values())

    replacements_coeffs_rho, reduced_coeffs_rho = sp.cse(expr_list_rho, symbols=sp.numbered_symbols('xr'))
    # <---


    # ---> construct and solve velocity equations
    # common part for 2D and 3D
    equations_vel = constraint_equations_at_nodes(vel_names, interpolation_vel_exprs, var_mats, coords, x_sym_list)

    def auxiliary_constraint_via_cumlant(equations, dim, var_mats, second_derivs, omega):
        if dim == 2:
            c20, c02, c11 = var_mats['c20'], var_mats['c02'], var_mats['c11']
            
            dx_c11 = ( ( c11[1,0] - c11[0,0] ) # x derivative of c11
                    + ( c11[1,1] - c11[0,1] ) ) * sp.Rational(1, 2)
            
            dy_c11 = ( ( c11[0,1] - c11[0,0] ) # y derivative of c11
                    + ( c11[1,1] - c11[1,0] ) ) * sp.Rational(1, 2)

            c20Mc02_xp = ( ( c20[1,1] - c02[1,1] ) + ( c20[1,0] - c02[1,0] ) ) * sp.Rational(1,2)
            c20Mc02_xm = ( ( c20[0,1] - c02[0,1] ) + ( c20[0,0] - c02[0,0] ) ) * sp.Rational(1,2)
            dx_c20Mc02 = sp.simplify( c20Mc02_xp - c20Mc02_xm ) # x derivative of c20 - c02

            c20Mc02_yp = ( ( c20[1,1] - c02[1,1] ) + ( c20[0,1] - c02[0,1] ) ) * sp.Rational(1,2)
            c20Mc02_ym = ( ( c20[1,0] - c02[1,0] ) + ( c20[0,0] - c02[0,0] ) ) * sp.Rational(1,2)        
            dy_c20Mc02 = sp.simplify( c20Mc02_yp - c20Mc02_ym ) # y derivative of c20 - c02

            # construct equations
            eq_c11x = dx_c11 * 3 * omega + ( second_derivs['v']['xx'] + second_derivs['u']['xy'] )
            eq_c11y = dy_c11 * 3 * omega + ( second_derivs['v']['xy'] + second_derivs['u']['yy'] )
            eq_c20x = dx_c20Mc02 * sp.Rational(3,2) * omega + ( second_derivs['u']['xx'] - second_derivs['v']['xy'] )
            eq_c20y = dy_c20Mc02 * sp.Rational(3,2) * omega + ( second_derivs['u']['xy'] - second_derivs['v']['yy'] )

            equations.append(eq_c11x) # supplementals via cumulants to close set of eqs
            equations.append(eq_c11y)
            equations.append(eq_c20x)
            equations.append(eq_c20y)

        else: # dim == 3
            c200, c020, c002, c110, c101, c011 = var_mats['c200'], var_mats['c020'], var_mats['c002'], var_mats['c110'], var_mats['c101'], var_mats['c011']

            dx_c110 = ( ( c110[1,0,0] - c110[0,0,0] ) # x derivative of c110
                    + ( c110[1,1,0] - c110[0,1,0] ) 
                    + ( c110[1,0,1] - c110[0,0,1] ) 
                    + ( c110[1,1,1] - c110[0,1,1] ) 
                    ) * sp.Rational(1, 4)
            
            dy_c110 = ( ( c110[0,1,0] - c110[0,0,0] ) # y derivative of c110
                    + ( c110[1,1,0] - c110[1,0,0] ) 
                    + ( c110[0,1,0] - c110[0,0,1] ) 
                    + ( c110[1,1,1] - c110[1,0,1] ) 
                    ) * sp.Rational(1, 4)
            
            dx_c101 = ( ( c101[1,0,0] - c101[0,0,0] ) # x derivative of c101
                    + ( c101[1,1,0] - c101[0,1,0] ) 
                    + ( c101[1,0,1] - c101[0,0,1] ) 
                    + ( c101[1,1,1] - c101[0,1,1] ) 
                    ) * sp.Rational(1, 4)
            
            dz_c101 = ( ( c101[0,0,1] - c101[0,0,0] ) # z derivative of c101
                    + ( c101[1,0,1] - c101[1,0,0] ) 
                    + ( c101[0,0,1] - c101[0,1,0] ) 
                    + ( c101[1,1,1] - c101[1,1,0] ) 
                    ) * sp.Rational(1, 4)
            
            dy_c011 = ( ( c011[0,1,0] - c011[0,0,0] ) # y derivative of c011
                    + ( c011[1,1,0] - c011[1,0,0] ) 
                    + ( c011[0,1,0] - c011[0,0,1] ) 
                    + ( c011[1,1,1] - c011[1,0,1] ) 
                    ) * sp.Rational(1, 4)
            
            dz_c011 = ( ( c011[0,0,1] - c011[0,0,0] ) # z derivative of c011
                    + ( c011[1,0,1] - c011[1,0,0] ) 
                    + ( c011[0,0,1] - c011[0,1,0] ) 
                    + ( c011[1,1,1] - c011[1,1,0] ) 
                    ) * sp.Rational(1, 4)

            c200Mc020 = var_mats['c200Mc020']
            c200Mc002 = var_mats['c200Mc002']

            #   d/dx [ ( c200 - c002 ) + ( c200 - c020 ) ]
            # = d/dx [ 2*c200 - c020 - c002 ]
            c200Mc020_xp = sp.Symbol('c200Mc020_xp')
            c200Mc020_xm = sp.Symbol('c200Mc020_xm')
            c200Mc002_xp = sp.Symbol('c200Mc002_xp')
            c200Mc002_xm = sp.Symbol('c200Mc002_xm')
            c200Mc020_xp = (c200Mc020[1,0,0] + c200Mc020[1,1,0] + c200Mc020[1,0,1] + c200Mc020[1,1,1]) / 4
            c200Mc020_xm = (c200Mc020[0,0,0] + c200Mc020[0,1,0] + c200Mc020[0,0,1] + c200Mc020[0,1,1]) / 4
            c200Mc002_xp = (c200Mc002[1,0,0] + c200Mc002[1,1,0] + c200Mc002[1,0,1] + c200Mc002[1,1,1]) / 4
            c200Mc002_xm = (c200Mc002[0,0,0] + c200Mc002[0,1,0] + c200Mc002[0,0,1] + c200Mc002[0,1,1]) / 4
            dx_2c200Mc020Mc002 = ( (c200Mc020_xp + c200Mc002_xp) - (c200Mc020_xm + c200Mc002_xm) )

            #   d/dy [ ( c200 - c002 ) - ( c200 - c020 ) ]
            # = d/dy [ c020 - c002 ]
            c200Mc020_yp = sp.Symbol('c200Mc020_yp')
            c200Mc020_ym = sp.Symbol('c200Mc020_ym')
            c200Mc002_yp = sp.Symbol('c200Mc002_yp')
            c200Mc002_ym = sp.Symbol('c200Mc002_ym')
            c200Mc020_yp = (c200Mc020[0,1,0] + c200Mc020[1,1,0] + c200Mc020[0,1,1] + c200Mc020[1,1,1]) / 4
            c200Mc020_ym = (c200Mc020[0,0,0] + c200Mc020[1,0,0] + c200Mc020[0,0,1] + c200Mc020[1,0,1]) / 4
            c200Mc002_yp = (c200Mc002[0,1,0] + c200Mc002[1,1,0] + c200Mc002[0,1,1] + c200Mc002[1,1,1]) / 4
            c200Mc002_ym = (c200Mc002[0,0,0] + c200Mc002[1,0,0] + c200Mc002[0,0,1] + c200Mc002[1,0,1]) / 4
            dy_c020Mc002 = ( (c200Mc002_yp - c200Mc020_yp) - (c200Mc002_ym - c200Mc020_ym) )

            #   d/dz [ ( c200 - c020 ) - ( c200 - c002 ) ]
            # = d/dz [ c002 - c020 ]
            c200Mc020_zp = sp.Symbol('c200Mc020_zp')
            c200Mc020_zm = sp.Symbol('c200Mc020_zm')
            c200Mc002_zp = sp.Symbol('c200Mc002_zp')
            c200Mc002_zm = sp.Symbol('c200Mc002_zm')
            c200Mc020_zp = (c200Mc020[0,0,1] + c200Mc020[1,0,1] + c200Mc020[0,1,1] + c200Mc020[1,1,1]) / 4
            c200Mc020_zm = (c200Mc020[0,0,0] + c200Mc020[1,0,0] + c200Mc020[0,1,0] + c200Mc020[1,1,0]) / 4
            c200Mc002_zp = (c200Mc002[0,0,1] + c200Mc002[1,0,1] + c200Mc002[0,1,1] + c200Mc002[1,1,1]) / 4
            c200Mc002_zm = (c200Mc002[0,0,0] + c200Mc002[1,0,0] + c200Mc002[0,1,0] + c200Mc002[1,1,0]) / 4
            dz_c002Mc020 = ( (c200Mc020_zp - c200Mc002_zp) - (c200Mc020_zm - c200Mc002_zm) )

            # d/dx (c110); d/dy (c110)
            eq_c110x = dx_c110 * 3 * omega + ( second_derivs['v']['xx'] + second_derivs['u']['xy'])
            eq_c110y = dy_c110 * 3 * omega + ( second_derivs['v']['xy'] + second_derivs['u']['yy'])

            # d/dx (c101); d/dz (c101)
            eq_c101x = dx_c101 * 3 * omega + ( second_derivs['w']['xx'] + second_derivs['u']['xz'])
            eq_c101z = dz_c101 * 3 * omega + ( second_derivs['w']['xz'] + second_derivs['u']['zz'])

            # d/dy (c010); d/dz (c010)
            eq_c011y = dy_c011 * 3 * omega + ( second_derivs['w']['yy'] + second_derivs['v']['yz'])
            eq_c011z = dz_c011 * 3 * omega + ( second_derivs['w']['yz'] + second_derivs['v']['zz'])

            # 
            eq_c200x = dx_2c200Mc020Mc002 * sp.Rational(3,2) * omega + ( 2 * second_derivs['u']['xx'] - second_derivs['v']['xy'] - second_derivs['w']['xz']) 
            eq_c020y = dy_c020Mc002 * sp.Rational(3,2) * omega + ( second_derivs['v']['yy'] - second_derivs['w']['yz']) 
            eq_c020z = dz_c002Mc020 * sp.Rational(3,2) * omega + ( second_derivs['w']['zz'] - second_derivs['v']['yz']) 

            equations.append(eq_c110x.subs({x:0, y:0, z:0}))
            equations.append(eq_c110y.subs({x:0, y:0, z:0}))
            equations.append(eq_c101x.subs({x:0, y:0, z:0}))
            equations.append(eq_c101z.subs({x:0, y:0, z:0}))
            equations.append(eq_c011y.subs({x:0, y:0, z:0}))
            equations.append(eq_c011z.subs({x:0, y:0, z:0}))
            equations.append(eq_c200x.subs({x:0, y:0, z:0}))
            equations.append(eq_c020y.subs({x:0, y:0, z:0}))
            equations.append(eq_c020z.subs({x:0, y:0, z:0}))

        return equations


    # set additional constraints using cumulants
    equations_vel = auxiliary_constraint_via_cumlant(equations_vel, dim, var_mats, second_derivs, omega)

    all_coeffs_vel = [] # list all velocity coefficients to be solved for
    for var_name, prefix, suffix_list in var_config_vel:
        c_names = [f"{prefix}{suffix}" for suffix in suffix_list]
        all_coeffs_vel.extend(sp.symbols(' '.join(c_names)))

    solution_tuple = sp.linsolve(equations_vel, all_coeffs_vel)
    solution_dict  = dict(zip(all_coeffs_vel, next(iter(solution_tuple))))
    expr_list_vel  = list(solution_dict.values())

    replacements_coeffs_vel, reduced_coeffs_vel = sp.cse(expr_list_vel)
    # <---



    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - - - - - - - -        backward transformation from c to f       - - - - - - - - ->
    #
    pipe_exprs = {} # store expressions in backward transformation
    # dummy call chimera_moment to obtain v_map, which will be used in backward transformation from moment to f
    first_chimera, second_chimera, v_map, pipe_exprs = chimera_moment(dim, vectors, pipe_exprs) 
    pipe_exprs = {} # reset pipe_exprs overwritten in chimera_moment

    # cumulant expressions
    cumulants_gen = CumulantGenerator(dim=dim)
    all_orders = list(itertools.product((0, 1, 2), repeat=dim))
    cumulants_eq = {}
    for order in all_orders:
        eq = cumulants_gen(order, density_scaling=False)    
        clean_lhs = clean_symbol_name(eq.lhs)
        
        cumulants_eq[order] = {
            'lhs': clean_lhs,
            'rhs': eq.rhs
        }

    #for o in all_orders:
    #    print(f"{cumulants_eq[o]}")

    kappa_expr = {}
    for o in all_orders:
        if sum(o) >= 2:
            cumulant = cumulants_eq[o]
            equation = ( cumulant['lhs'] - cumulant['rhs'] ) * rho
            kappa_expr[o] = sp.solve(equation, K_cen[o])[0]
            #print(f"{K_cen[o]} = {kappa_expr[o]}" )

    def lowercase_first_char(symbol_dict):
        lowercase_dict = {}
        for o, name_sym in zip(symbol_dict.keys(), symbol_dict.values()):
            name = name_sym.name
            new_name = name[0].lower() + name[1:]
            lowercase_dict[o] = sp.Symbol(new_name)

        return lowercase_dict

    c_cum = lowercase_first_char(C_cum) # cumulant symbols in c000 format (lowercase for non-scaled)

    high_orders = [o for o in all_orders if sum(o) >= 3]

    zero_subs = {c_cum[o]: 0 for o in high_orders}
    for o in high_orders: # eliminate high order cumulants assuming equilibrium
        kappa_expr[o] = kappa_expr[o].xreplace(zero_subs).simplify()
        #print(f"{o}: {kappa_expr[o]}")

    for _ in range(5): # loop for safely eliminate 0 moments from exprs
        zero_kappa_dict = {}
        for o in high_orders:
            if kappa_expr[o] == 0:
                zero_kappa_dict.update({K_cen[o]: 0})

        for o in high_orders:
            kappa_expr[o] = kappa_expr[o].xreplace(zero_kappa_dict).simplify()

    for o in all_orders:
        if sum(o) >= 2:
            pipe_exprs[K_cen[o]] = kappa_expr[o]
            #print(f"{o} {pipe_exprs[K_cen[o]]}")

    # backward transformation from kappa to raw moment
    pipe_exprs = back_trans_kappa_to_raw(dim, moment_orders, vel_syms, K_cen, M_post, pipe_exprs) # backward transform: kappa to moment

    # collect zero kappa [to eliminate trivial 0 in export phase]
    zero_kappa_dict = {}
    for o in high_orders:
        if kappa_expr[o] == 0:
            zero_kappa_dict.update({K_cen[o]: 0})
    # also, some moment chimera may be 0; so collect them 
    for key, expr in zip(pipe_exprs.keys(), pipe_exprs.values()):
        if expr.xreplace(zero_kappa_dict) == 0:
            zero_kappa_dict.update({key: 0})

    # shift post-collision raw moment to "shifted" raw moment before transforming back to f
    # this process does do nothing if drho_mode is 'rho'
    for o in moment_orders:
        if M_post[o] in pipe_exprs:
                pipe_exprs[M_post[o]] -= order_to_weight[o]

    # backward Transformation from m_post to f_post
    pipe_exprs, f_post_exprs = back_trans_raw_to_f(dim, v_map, M_post, pipe_exprs) # backward transform: moment to f


    # re-order allsignments as 
    # from macro to post moment, (stored in asignments_other)
    # then, post f in oder of 0, 1, 2, ... (stored in f_post)
    # convert direction in variable name to q index, like '1_1_1' -> 26
    def _convert_direction_to_idx(dim, var_name):
        parts = var_name.split("_")
        def parse_v(s):
            if s == "m1": return -1
            return int(s)
        if dim == 2:
            return (parse_v(parts[3]), parse_v(parts[4])) # (i, j)
        else:
            return (parse_v(parts[3]), parse_v(parts[4]), parse_v(parts[5])) # (i, j, k)

    f_post_map = {}
    assignments_other = []
    for var_sym, expr in zip(pipe_exprs.keys(), pipe_exprs.values()):
        var_name = var_sym.name
        if var_name.startswith("f_post_idx_"):
            f_idx = vectors.index(_convert_direction_to_idx(dim, var_name))
            f_post_map[f_idx] = expr # write f_new last. for this, we escape them into f_post_map
        else:
            assignments_other.append((var_name, expr))                    





    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - - - - - - - - - - - -    interpolation [common part]     - - - - - - - - - - - ->
    #
    if dim == 2:
        c11_expr = -sp.Rational(1,3)/omega*(first_derivs['v']['x'] + first_derivs['u']['y'])
        c20_expr = -sp.Rational(2,3)/omega*(first_derivs['u']['x'])
        c02_expr = -sp.Rational(2,3)/omega*(first_derivs['v']['y'])
    else:
        c200_expr = -sp.Rational(2,3)/omega*(first_derivs['u']['x'])
        c020_expr = -sp.Rational(2,3)/omega*(first_derivs['v']['y'])
        c002_expr = -sp.Rational(2,3)/omega*(first_derivs['w']['z'])
        c110_expr = -sp.Rational(1,3)/omega*(first_derivs['v']['x'] + first_derivs['u']['y'])
        c101_expr = -sp.Rational(1,3)/omega*(first_derivs['w']['x'] + first_derivs['u']['z'])
        c011_expr = -sp.Rational(1,3)/omega*(first_derivs['w']['y'] + first_derivs['v']['z'])


    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - - - - - - - - - - - -        interpolation F -> C        - - - - - - - - - - - ->
    #
    # Fine to Coarse (x,y) = (0,0) at target coarse node
    #
    pipe_FtoC = {}

    coord_dict = {'x': 0, 'y': 0, 'z': 0} 
    values = {k: coord_dict[k] for k in coord_names}

    for vel_name in vel_names:
        pipe_FtoC[vel_name]   = interpolation_exprs[vel_name].subs(values)

    pipe_FtoC['rho'] = interpolation_exprs['rho'].subs(values)

    if dim == 2:
        pipe_FtoC['c11'] = c11_expr.subs(values)
        pipe_FtoC['c20'] = c20_expr.subs(values)
        pipe_FtoC['c02'] = c02_expr.subs(values)
    else:
        pipe_FtoC['c200'] = c200_expr.subs(values)
        pipe_FtoC['c020'] = c020_expr.subs(values)
        pipe_FtoC['c002'] = c002_expr.subs(values)
        pipe_FtoC['c110'] = c110_expr.subs(values)
        pipe_FtoC['c101'] = c101_expr.subs(values)
        pipe_FtoC['c011'] = c011_expr.subs(values)


    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - - - - - - - - - - - -        interpolation C -> F        - - - - - - - - - - - ->
    #
    # Coarse to Fine @ target fine nodes
    #   (m,m,m) = (-1/4,-1/4,-1/4) 
    #   (p,m,m) = ( 1/4,-1/4,-1/4) 
    #   (p,p,m) = ( 1/4, 1/4,-1/4) 
    #   (m,p,m) = (-1/4, 1/4,-1/4) 
    #   (m,m,p) = (-1/4,-1/4, 1/4) 
    #   (p,m,p) = ( 1/4,-1/4, 1/4) 
    #   (p,p,p) = ( 1/4, 1/4, 1/4) 
    #   (m,p,p) = (-1/4, 1/4, 1/4) 
    pipe_CtoF = {}

    for vel_name in vel_names:
        pipe_CtoF[vel_name]   = interpolation_exprs[vel_name]

    pipe_CtoF['rho'] = interpolation_exprs['rho']

    if dim == 2:
        pipe_CtoF['c11'] = c11_expr
        pipe_CtoF['c20'] = c20_expr
        pipe_CtoF['c02'] = c02_expr
    else:
        pipe_CtoF['c200'] = c200_expr
        pipe_CtoF['c020'] = c020_expr
        pipe_CtoF['c002'] = c002_expr
        pipe_CtoF['c110'] = c110_expr
        pipe_CtoF['c101'] = c101_expr
        pipe_CtoF['c011'] = c011_expr



    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    # - - - - - - - - - - - -        export functions        - - - - - - - - - - - - - ->
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #
    #
    # define "struct Coeffs"
    #
    Macrovars_name = 'macrovars'
    Cumulants_name = 'cumulants'

    struct_members = f"{rho}=float, " + ", ".join([f"{suffix}=float" for suffix in vel_names])
    buffer.write(f"{idt[0]}{Macrovars_name.capitalize()} = ti.types.struct({struct_members})\n")

    struct_members = ", ".join([f"{suffix}=float" for suffix in cumulant_list])
    buffer.write(f"{idt[0]}{Cumulants_name.capitalize()} = ti.types.struct({struct_members})\n")

    struct_members = ", ".join([f"C{suffix}=float" for suffix in coeffs_map])
    buffer.write(f"{idt[0]}Coeffs = ti.types.struct({struct_members})\n")

    coeffs_names = ["rho_coeffs", "u_coeffs", "v_coeffs", "w_coeffs"][:(dim+1)]
    struct_members = ", ".join([f"{suffix}=Coeffs" for suffix in coeffs_names])
    buffer.write(f"{idt[0]}SCoeffs = ti.types.struct({struct_members})\n\n")

    struct_members = ", ".join([f"{suffix}={suffix}" for suffix in coeffs_names])
    return_coeffs = f"{idt[0]}SCoeffs({struct_members})\n\n"

    #
    # function "compute_cumulants"
    #
    buffer.write(f"{idt[0]}@ti.func\n")
    buffer.write(f"{idt[0]}def compute_cumulants(f: ti.template(), I): # f[I] is source\n")

    for idx, vec in enumerate(vectors):
        buffer.write(f"{idt[1]}f{idx} = f[I][{idx}]\n")

    for var, expr in replacements_mom:
        buffer.write(f"{idt[1]}{var} = {expr}\n")

    for key, expr in zip(cse_target_keys, reduced_mom):
        buffer.write(f"{idt[1]}{key} = {expr}\n")

    buffer.write(f"{idt[1]}{rho} = {M_raw[(0,0,0)[:dim]]}\n") # density expr
    buffer.write(f"{idt[1]}inv_rho = 1/{rho}\n")
    for i, v_sym in enumerate(vel_syms): # velocity expr
        order_tuple = [0] * dim
        order_tuple[i] = 1
        buffer.write(f"{idt[1]}{v_sym} = {clean_div_terms( used_inverses, str(M_raw[tuple(order_tuple)] / rho) ) }\n")

    for key, expr in zip(cumulant_pipe.keys(), cumulant_pipe.values()): # cumulant expr
        buffer.write(f"{idt[1]}{key} = {clean_div_terms( used_inverses, str(sp.expand(expr)) )}\n")

    cumulant_names = ", ".join(cumulant_list)

    if dim == 2:
        buffer.write(f"{idt[1]}return {rho}, {return_vel_str}, {cumulant_names}\n")
    else:
        buffer.write(f"{idt[1]}return {rho}, {return_vel_str}, {cumulant_names}, {c_cum[(2,0,0)]-c_cum[(0,2,0)]}, {c_cum[(2,0,0)]-c_cum[(0,0,2)]}\n")

    buffer.write(f"\n")

    #
    # function "compute_interpolation_coeffs"
    #
    buffer.write(f"{idt[0]}@ti.func\n")
    buffer.write(f"{idt[0]}def compute_interpolation_coeffs(f: ti.template(), I, omega):\n")

    if dim == 2:
        for (dx, dy), suffix in grid_map.items():
            vec_code = f"{idt[1]}I{suffix} = ti.Vector([I[0]{dx:+d}, I[1]{dy:+d}])"
            buffer.write(vec_code.replace('+0', '  ') + "\n")

        for (x, y), suffix in grid_map.items():
            lhs_vars = ", ".join([f"{v}_{suffix}" for v in vars_list])
            buffer.write(f"    {lhs_vars} = compute_cumulants(f, I{suffix})\n")

    else:
        for (dx, dy, dz), suffix in grid_map.items():
            vec_code = f"{idt[1]}I{suffix} = ti.Vector([I[0]{dx:+d}, I[1]{dy:+d}, I[2]{dz:+d}])"
            buffer.write(vec_code.replace('+0', '  ') + "\n")

        for (x, y, z), suffix in grid_map.items():
            lhs_vars = ", ".join([f"{v}_{suffix}" for v in vars_list])
            buffer.write(f"    {lhs_vars} = compute_cumulants(f, I{suffix})\n")


    for var, expr in replacements_coeffs_vel:
        buffer.write(f"{idt[1]}{var} = { clean_div_terms(used_inverses, str(expr) ) }\n")

    for var, expr in replacements_coeffs_rho:
        buffer.write(f"{idt[1]}{var} = { clean_div_terms(used_inverses, str(expr) ) }\n")

    field_mapping_vel = {
        'C0':   '0', 
        'Cx':   'x', 
        'Cy':   'y', 
        'Cxy':  'xy', 
        'Cx2':  'x2', 
        'Cy2':  'y2',
        'Cz':   'z', 
        'Cxz':  'xz', 
        'Cyz':  'yz', 
        'Cxyz': 'xyz', 
        'Cz2':  'z2'
    }

    field_mapping_rho = {
        'C0':   '0', 
        'Cx':   'x', 
        'Cy':   'y', 
        'Cxy':  'xy', 
        'Cx2':  'D', 
        'Cy2':  'D',
        'Cz':   'z', 
        'Cxz':  'xz', 
        'Cyz':  'yz', 
        'Cxyz': 'xyz',  
        'Cz2':  'D'
    }

    coeff_map_vel = {coeff: expr for coeff, expr in zip(all_coeffs_vel, reduced_coeffs_vel)}

    for var_name, prefix, suffix_list in var_config_vel[:dim]:
        r_name = f"{var_name.lower()}_coeffs"
        buffer.write(f"{idt[1]}{r_name} = Coeffs(\n")
        
        for field_name, suffix in field_mapping_vel.items():
            if suffix in suffix_list:
                sym_name = f"{prefix}{suffix}"
                expr = coeff_map_vel[sp.Symbol(sym_name)]
                buffer.write(f"{idt[2]}{field_name} = { clean_div_terms(used_inverses, str(expr) ) },\n")
                
        buffer.write(f"{idt[1]})\n")

    # prepare subs map for replace a wity u_coeff in div (u dot nabla u) term
    prefix_map = {'u': 'a', 'v': 'b', 'w': 'c'}
    coeff_subs_map = {}
    for v_name in vel_names:
        prefix = prefix_map[v_name]
        for c_type in coeffs_map:
            sym_key = sp.Symbol(f"{prefix}{c_type}")
            val_name = f"{v_name}_coeffs.C{c_type}"
            val_sym = sp.Symbol(val_name)
            coeff_subs_map[sym_key] = val_sym

    buffer.write(f"{idt[1]}{div_adv_term_name} = {div_adv_term_expr.xreplace(coeff_subs_map)}\n")

    coeff_map_rho = {coeff: expr for coeff, expr in zip(all_coeffs_rho, reduced_coeffs_rho)}

    for var_name, prefix, suffix_list in var_config_rho:
        r_name = f"{var_name.lower()}_coeffs"
        buffer.write(f"{idt[1]}{r_name} = Coeffs(\n")
        
        for field_name, suffix in field_mapping_rho.items():
            if suffix in suffix_list:
                sym_name = f"{prefix}{suffix}"
                expr = coeff_map_rho[sp.Symbol(sym_name)]
                buffer.write(f"{idt[2]}{field_name} = { clean_div_terms( used_inverses, str(expr) ) },\n")
                
        buffer.write(f"{idt[1]})\n")

    return_names = [f"{var_name}_coeffs" for var_name, prefix, suffix_list in (var_config_vel[:dim] + var_config_rho)]

    #buffer.write(f"{idt[1]}return {', '.join(return_names)}\n")
    buffer.write(f"{idt[1]}return {return_coeffs}")


    #
    # function "backtrans_c_to_f"
    #
    buffer.write(f"{idt[0]}@ti.func\n")
    #buffer.write(f"{idt[0]}def backtrans_c_to_f(f: ti.template(), I, rho, {return_vel_str}, {cumulant_names}): # f[I] is injection target: F->C or C->F\n")
    buffer.write(f"{idt[0]}def backtrans_c_to_f(f: ti.template(), I, {Macrovars_name}, {Cumulants_name}): # f[I] is injection target: F->C or C->F\n")
    buffer.write(f"{idt[1]}{rho} = {Macrovars_name}.{rho}\n")
    for vel_name in vel_names:
        buffer.write(f"{idt[1]}{vel_name} = {Macrovars_name}.{vel_name}\n")
    for c_name in cumulant_list:
        buffer.write(f"{idt[1]}{c_name} = {Cumulants_name}.{c_name}\n")

    buffer.write(f"{idt[1]}inv_rho = 1.0/{rho}\n")

    # export chimera transformation
    skip_moments = ['m00', 'm10', 'm01'] if dim == 2 else ['m000', 'm100', 'm010', 'm001']
    for var_name, expr in assignments_other:
        if var_name in skip_moments:
            pass
        else:
            if sp.Symbol(var_name) in zero_kappa_dict:
                pass
            else:
                buffer.write(f"{idt[1]}{var_name} = { clean_div_terms(used_inverses, str( expr.xreplace(zero_kappa_dict) ) ) }\n")

    # export f
    for f_idx in sorted(f_post_map.keys()):
        expr = f_post_map[f_idx]
        buffer.write(f"{idt[1]}f[I][{f_idx}] = { clean_div_terms( used_inverses, str(expr) ) }\n")


    #
    # [preparation of variable name replacements for FtoC CtoF functions]
    #
    replacements = {}

    for var_name, prefix, suffix_list in var_config:
        if var_name == 'rho':
            struct_name = 'RC'
        else:
            struct_name = f"{var_name.upper()}C"
        
        for suffix in suffix_list:
            old_sym = sp.Symbol(f"{prefix}{suffix}")
            new_str = f"{struct_name}.C{suffix}"
            replacements[old_sym] = new_str


    def generate_code_string(expr, replacements):
        subs_dict = {
            sp.Symbol(str(k)): sp.Symbol(str(v)) 
            for k, v in replacements.items()
        }    
        new_expr = expr.subs(subs_dict)    
        return str(new_expr) 


    #
    # function "interpolation_FtoC"
    #
    buffer.write(f"\n")
    buffer.write(f"{idt[0]}@ti.func\n")
    buffer.write(f"{idt[0]}def interpolation_FtoC(coeffs, omega):\n")
    #buffer.write(f"{idt[0]}def interpolation_FtoC({args_C_str}, RC, omega):\n")

    Coeffs_names = [name[0].upper() + "C" for name in coeffs_names]    
    for Coeffs_name, coeffs_name in zip(Coeffs_names, coeffs_names):
        buffer.write(f"{idt[1]}{Coeffs_name} = coeffs.{coeffs_name}\n")

    buffer.write(f"{idt[1]}INV_3omega = 1/(3*omega)\n")
    buffer.write(f"{idt[1]}UpScaling=2 # reconstructed gradient at F becomes twice when C observes it (chain rule in x_F <-> x_C)\n")
    for lhs, rhs in zip(pipe_FtoC.keys(), pipe_FtoC.values()):
        expr = generate_code_string(rhs, replacements)
        expr = expr.replace("/(3*omega)", " * INV_3omega")
        expr = expr.replace("*x**2", "*x*x")
        expr = expr.replace("*y**2", "*y*y")
        expr = expr.replace("*z**2", "*z*z")
        if 'c' in lhs:
            if '2' in lhs:
                buffer.write(f"{idt[1]}{lhs} = {expr}" + clean_div_terms(used_inverses, f" * UpScaling + {cs2}") + "\n")
            else:
                buffer.write(f"{idt[1]}{lhs} = {expr} * UpScaling\n")
        else:
            buffer.write(f"{idt[1]}{lhs} = {expr}\n")

    struct_members = f"{rho}={rho}, " + ", ".join([f"{suffix}={suffix}" for suffix in vel_names])
    buffer.write(f"{idt[1]}{Macrovars_name} = {Macrovars_name.capitalize()}({struct_members})\n")

    struct_members = ", ".join([f"{suffix}={suffix}" for suffix in cumulant_list])
    buffer.write(f"{idt[1]}cumulants = Cumulants({struct_members})\n")

    buffer.write(f"{idt[1]}return {Macrovars_name}, {Cumulants_name}\n")

    #
    # function "interpolation_CtoF"
    #
    buffer.write(f"\n")
    buffer.write(f"{idt[0]}@ti.func\n")
    buffer.write(f"{idt[0]}def interpolation_CtoF(coeffs, omega, coords):\n")
    #buffer.write(f"{idt[0]}def interpolation_CtoF({args_C_str}, RC, omega, {args_x_str}):\n")

    Coeffs_names = [name[0].upper() + "C" for name in coeffs_names]    
    for Coeffs_name, coeffs_name in zip(Coeffs_names, coeffs_names):
        buffer.write(f"{idt[1]}{Coeffs_name} = coeffs.{coeffs_name}\n")

    for i, coord in enumerate(x_sym_list):
        buffer.write(f"{idt[1]}{coord} = coords[{i}]\n")


    buffer.write(f"{idt[1]}INV_3omega = 1/(3*omega)\n")
    buffer.write(f"{idt[1]}DownScaling=0.5 # reconstructed gradient at C becomes half  when F observes it (chain rule in x_C <-> x_F)\n")

    for lhs, rhs in zip(pipe_CtoF.keys(), pipe_CtoF.values()):
        expr = generate_code_string(rhs, replacements)
        expr = expr.replace("/(3*omega)", " * INV_3omega")
        expr = expr.replace("*x**2", "*x*x")
        expr = expr.replace("*y**2", "*y*y")
        expr = expr.replace("*z**2", "*z*z")
        if 'c' in lhs:
            if '2' in lhs:
                buffer.write(f"{idt[1]}{lhs} = {expr}" + clean_div_terms(used_inverses, f" * DownScaling + {cs2}") + "\n")
            else:
                buffer.write(f"{idt[1]}{lhs} = {expr} * DownScaling\n")
        else:
            buffer.write(f"{idt[1]}{lhs} = {expr}\n")

    struct_members = f"{rho}={rho}, " + ", ".join([f"{suffix}={suffix}" for suffix in vel_names])
    buffer.write(f"{idt[1]}{Macrovars_name} = {Macrovars_name.capitalize()}({struct_members})\n")

    struct_members = ", ".join([f"{suffix}={suffix}" for suffix in cumulant_list])
    buffer.write(f"{idt[1]}cumulants = Cumulants({struct_members})\n")

    buffer.write(f"{idt[1]}return {Macrovars_name}, {Cumulants_name}\n")


    # export to file 
    all_content = buffer.getvalue()

    with open(file_abs, 'w', encoding="utf-8") as f:
        f.write(f"# {filename}\n\n")
        f.write(f"{idt[0]}import taichi as ti\n")
        f.write(f"{idt[0]}import taichi.math as tm\n\n")

        for i in used_inverses:
            f.write(f"{idt[0]}INV_{i} = 1.0/{i}.0\n")

        f.write(f"\n")

        f.write(all_content)

    buffer.close()

