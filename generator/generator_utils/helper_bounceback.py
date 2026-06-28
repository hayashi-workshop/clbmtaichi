# helper_bounceback_.py

# run this script from root as 
# PYTHONPATH=. python generator/generator_utils/helper_bounceback.py

#
# this script is neither simulator nor generator
# helper to show bounce back core part to facilitate coding bback_kernel.py
#

import sys
import os
import sympy as sp
import itertools
import math

from generator.generator_utils.common_utils import calculate_weight, create_vectors

def indent(level):
    base = "    "
    idt = ""
    for i in range(level):
        idt = idt + base
    return idt

idt = [indent(i) for i in range(10)]


def generate_inv_indices_taichi(opp_map):
    max_idx = max(opp_map.keys())
    indices = [opp_map[i] for i in range(max_idx + 1)]
    
    indices_str = ", ".join(map(str, indices))
    
    q = len(opp_map)
    dim = round(int(math.log(q, 3)))
    return f"{idt[2]}inv_idx_d{dim}q{q} = ti.Vector([{indices_str}])"


def get_boundary_code(normal_vector):
    pipeline = []

    dim = len(normal_vector)
    vectors = create_vectors(dim) # lattice vector c
    weights = [calculate_weight(v) for v in vectors] # weights w
    num_pops = len(vectors)                          # Q (9 or 27)

    rho_name = 'rho'
    vel_names = ['u', 'v', 'w'][:dim]
    rho = sp.Symbol(rho_name) # sympy symbol
    vel_syms = sp.symbols(vel_names) # sympy symbol
    cs2 = sp.Rational(1, 3) # sound speed square [not used]

    opp_map = {} # search opposite (-) direction
    for i, v in enumerate(vectors):
        opp_v = tuple(-c for c in v)
        opp_map[i] = vectors.index(opp_v)

    u_vec     = sp.Matrix(vel_syms)
    c_vectors = [sp.Matrix(c) for c in vectors]
    c_dot_u   = [c.dot(u_vec) for c in c_vectors]

    num_zeros = normal_vector.count(0) # count 0 in tuple to detect wall type (face, edge, corner)

    axes = ["i", "j", "k"]

    conditions = []    
    for idx, val in enumerate(normal_vector):
        if val == 1:
            conditions.append(f"{axes[idx]} == 0")
        elif val == -1:
            conditions.append(f"{axes[idx]} == lbm.nd[{idx}] - 1")
    
    evaluate = " and ".join(conditions)
    pipeline.append(evaluate)

    target_dot = dim - num_zeros

    n = sp.Matrix(normal_vector)

    lines = []
    
    for i, v in enumerate(vectors):
        c_i = sp.Matrix(v)
        dot = c_i.dot(n)
        
        if dot == target_dot: 
            inv_q = vectors.index(tuple(-c for c in v))
            coeff = weights[i] * 2 / cs2
            if target_dot == 1:
                code = f"{idt[5]}f_post[x_bc + self.c[{i}]][{i}] = f_pre[x_bc][{inv_q}] + {coeff} * ( {c_dot_u[i]} )"
            else:
                code = f"{idt[5]}f_post[x_bc + self.c[{i}]][{i}] = f_pre[x_bc][{inv_q}]"
            pipeline.append(code)

    return pipeline, opp_map


def export_rational():
    for i in used_inverses:
        print(f"{idt[2]}self.INV_{i} = 1.0/{i}.0")


def process_expression(expr_str):
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
                expr_str = expr_str.replace(pattern, f" * self.INV_{i}")
                used_inverses.add(i)

    # delete 1 * if the expression is 1 * INV_
    expr_str = expr_str.replace(" + 1 * ", " + ") 
    expr_str = expr_str.replace(" - 1 * ", " - ")

    return expr_str


def bc_id3():
    print(f"{idt[4]}else: # bc_id == 3")
    print(f"{idt[5]}for q in ti.static(range(lbm.Q)):")
    print(f"{idt[6]}inv_q = self.inv_idx[q]")
    print(f"{idt[6]}f_post[x_bc + self.c[q]][q] = f_pre[x_bc][ inv_q ]")

# - * - * - * - * - * - * - * - * - * - * - * - * - * - * - #


used_inverses = set() # dict for INV_ list

# D2Q9
wall_normals_d2q9 = [
    ( 1,  1), #"left_bottom"),
    ( 1, -1), #"left_top"),
    (-1,  1), #"right_bottom"),
    (-1, -1), #"right_top")
    ( 1,  0), #"left"),
    (-1,  0), #"right"),
    ( 0,  1), #"bottom"),
    ( 0, -1), #"top"),
]

count = 0
for n in wall_normals_d2q9:
    ev = f"{idt[4]}if " if count == 0 else f"{idt[4]}elif "
    codes, opp_map_dim2 = get_boundary_code(n)
    for i in range(len(codes)):
        if i == 0:
            print(ev + codes[i] + ":")
        else:
            print(process_expression(codes[i]))
    count += 1

bc_id3()

print(f"\n")

# D3Q27
wall_normals_d3q27 = [
    ( 1,  1,  1), #"left_bottom_back"),
    ( 1, -1,  1), #"left_top_back"),
    ( 1,  1, -1), #"left_bottom_front"),
    ( 1, -1, -1), #"left_top_front"),
    (-1,  1,  1), #"right_bottom_back"),
    (-1, -1,  1), #"right_top_back"),
    (-1,  1, -1), #"right_bottom_front"),
    (-1, -1, -1), #"right_top_front")
    ( 1,  0,  1), #"left_back"),
    ( 1,  0, -1), #"left_front"),
    (-1,  0,  1), #"right_back"),
    (-1,  0, -1), #"right_front"),
    ( 0,  1,  1), #"bottom_back"),
    ( 0,  1, -1), #"bottom_front"),
    ( 0, -1,  1), #"top_back"),
    ( 0, -1, -1), #"top_front")
    ( 1,  0,  0), #"left"),
    (-1,  0,  0), #"right"),
    ( 0,  1,  0), #"bottom"),
    ( 0, -1,  0), #"top"),
    ( 0,  0,  1), #"back"),
    ( 0,  0, -1), #"front"),
]

count = 0
for n in wall_normals_d3q27:
    ev = f"{idt[4]}if " if count == 0 else f"{idt[4]}elif "
    codes, opp_map_dim3 = get_boundary_code(n)
    for i in range(len(codes)):
        if i == 0:
            print(ev + codes[i] + ":")
        else:
            print(process_expression(codes[i]))
    count += 1

bc_id3()


print(f"\n")

opp_taichi = generate_inv_indices_taichi(opp_map_dim2)
print(opp_taichi)

opp_taichi = generate_inv_indices_taichi(opp_map_dim3)
print(opp_taichi + "\n")


export_rational()