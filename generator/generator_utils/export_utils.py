# export_utils.py

import sympy as sp
import itertools
import math
import re # used in clean_div_terms
import os

class TypeWriter:
    def __init__(self, filename, collision_model, drho_mode, default_pack, misc_pack, code_bundle, f_eq_pack):
        self.buffer = [] # buffer for code lines
        self.used_inverses = set() # dict for INV_ list
        self.filename = filename
        self.collision_model = collision_model
        self.drho_mode = drho_mode
        self.default_pack = default_pack
        self.misc_pack = misc_pack
        self.code_bundle = code_bundle
        self.f_eq_pack = f_eq_pack # for f_eq function

        def indent(level):
            base = "    "
            idt = ""
            for i in range(level):
                idt = idt + base
            return idt
        self.idt = [indent(i) for i in range(5)]

        # base indent level
        # 0: global function
        # 1: class member
        self.bi = 1 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.filename, "w", encoding="utf-8") as f:
            self._export_common_header(f)
            f.writelines(self.buffer)
            self._export_common_closer(f)

            f.flush()
            os.fsync(f.fileno())

    def write(self):
        if self.collision_model == "BGK":
            self._export_bgk_code()
        elif self.collision_model == "TRT":
            self._export_trt_code()
        elif self.collision_model == "MRT":
            self._export_mrt_code()
        elif self.collision_model == "Cumulant":
            self._export_cumulant_code()

    def process_expression(self, expr_str):
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
                    self.used_inverses.add(i)

        # delete 1 * if the expression is 1 * INV_
        expr_str = expr_str.replace(" + 1 * ", " + ") 
        expr_str = expr_str.replace(" - 1 * ", " - ")

        return expr_str

    def _clean_div_terms(self, expr_str):
        expr_str = expr_str.replace("log(", "ti.log(")
        expr_str = re.sub(r'\b1/inv_rho\b', 'rho', expr_str)    
        expr_str = re.sub(r'/inv_rho\*\*2', ' * rho**2', expr_str)
        expr_str = re.sub(r'/inv_rho', ' * rho', expr_str)
        expr_str = re.sub(r'/rho\*\*2', ' * inv_rho**2', expr_str)
        expr_str = re.sub(r'/rho', ' * inv_rho', expr_str)
        expr_str = self.process_expression(expr_str)
        
        return expr_str

    def _export_common_header(self, f):
        idt, bi = self.idt, self.bi

        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        f.write(f"# -*- coding: utf-8 -*-\n")
        f.write(f"# ======================================================================================\n")
        f.write(f"# This code was generated with SymPy CSE code generator\n")
        f.write(f"# Discr: D{dim}Q{num_pops}\n")
        f.write(f"# Model: {collision_model}\n")
        if self.collision_model == "Cumulant":
            f.write(f"# Some intermediate variable names are inspired by the naming conventions used in lbmpy.\n")
        f.write(f"# ======================================================================================\n\n")
        f.write(f"import taichi as ti\n")
        f.write(f"import taichi.math as tm\n\n")

        weight_strs = [f"{float(w)}" if w.is_Integer else f"{w.as_numer_denom()[0]}.0 / {w.as_numer_denom()[1]}.0" for w in weights]
        vec_strs = [f"[{', '.join(map(str, v))}]" for v in vectors]
        vec_idx_strs = [f"ti.Vector([{', '.join(map(str, v))}])" for v in vectors]
        f.write(f"{idt[0]}#weights = ti.types.vector({num_pops}, float)([{', '.join(weight_strs)}])\n") # - #
        f.write(f"{idt[0]}c = ({', '.join(vec_idx_strs)})\n\n") # - #

        f.write(f"{idt[0]}@ti.data_oriented\n")
        f.write(f"{idt[0]}class ModelConfig:\n")
        f.write(f"{idt[1]}def __init__(self, mode=\"pull\"):\n")

        density_shift = 0.0 if self.drho_mode == 'rho' else 1.0
        f.write(f"{idt[2]}self.density_shift = {density_shift}\n")

        f.write(f"{idt[2]}self._set_rational()\n")

        f.write(f"{idt[2]}self.pop = 1 if mode == \"push\" else 0 # pull or push\n") # - #
        f.write(f"{idt[2]}print(f\"mode: {{mode}} - pop {{self.pop}}\")\n") # - #


        f.write(f"\n\n{idt[bi]}@ti.kernel\n")
        f.write(f"{idt[bi]}def col_stream_core(self, {class_name}: ti.template(), f_pre: ti.template(), f_post: ti.template()):\n") # function begins

        #f.write(f"{idt[bi+1]}for I in ti.grouped({class_name}.rho):\n")
        #f.write(f"{idt[bi+2]}# Streaming & Fetch (pull algorithm)\n")

        if dim == 2:
            f.write(f"{idt[bi+1]}for i, j in ti.ndrange((ti.static(self.pop), ti.static(lbm.nd[0] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[1] - self.pop))):")
            f.write(f"\n{idt[bi+2]}I = ti.Vector([i, j])\n")
        else: # dim == 3
            f.write(f"{idt[bi+1]}for i, j, k in ti.ndrange((ti.static(self.pop), ti.static(lbm.nd[0] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[1] - self.pop)), (ti.static(self.pop), ti.static(lbm.nd[2] - self.pop))):")
            f.write(f"\n{idt[bi+2]}I = ti.Vector([i, j, k])\n")

        f.write(f"{idt[bi+2]}# Fetch f\n") # - #
        for idx, vec in enumerate(vectors):
#            f.write(f"{idt[bi+2]}f{idx} = {old_name}[I - self.c[{idx}]][{idx}]\n")
            f.write(f"{idt[bi+2]}f{idx} = {old_name}[I + c[{idx}]*ti.static(self.pop-1)][{idx}]\n")
        f.write("\n")

    def _export_common_closer(self, f):
        f.write(f"\n")
        self._taichi_CSE_feq_generator(f) # CSE optimized f_eq function #
        self._export_rational(f) # INV_

    def _export_rational(self, f):
        idt, bi = self.idt, self.bi
        f.write(f"{idt[bi]}def _set_rational(self):\n")
        for i in self.used_inverses:
            f.write(f"{idt[bi+1]}self.INV_{i} = 1.0/{i}.0\n")

    def _taichi_CSE_feq_generator(self, f):
        idt, bi = self.idt, self.bi
        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        replacements_eq, reduced_eq = self.f_eq_pack

        f.write(f"{idt[bi]}@ti.func\n")
        f.write(f"{idt[bi]}def f_eq(self, {class_name}, I):\n")
        f.write(f"{idt[bi+1]}rho = lbm.rho[I] # <- note: actual value stored here is rho - density_shift\n")
        vel_names = ['u', 'v', 'w'][:dim]
        for d in range(dim):
            f.write(f"{idt[bi+1]}{vel_names[d]} = lbm.vel[I][{d}]\n") 
        f.write("\n")
        
        for sym, expr in replacements_eq:
            f.write(f"{idt[bi+1]}{sym} = {self._clean_div_terms(str(expr))}\n")
        f.write("\n")
        
        f.write(f"{idt[bi+1]}return ti.Vector([\n")
        for red_expr in reduced_eq:
            f.write(f"{idt[bi+2]}{self._clean_div_terms(str(red_expr))},\n")
        f.write(f"{idt[bi+1]}])\n\n")


    def _export_macrovars(self, rho_ex, vel_ex, class_name):
        idt, bi = self.idt, self.bi
        self.buffer.append(f"{idt[bi+2]}{class_name}.rho[I] = {rho_ex} # <- note: actual value stored here is rho - density_shift\n")
        for d in range(len(vel_ex)):
            self.buffer.append(f"{idt[bi+2]}{class_name}.vel[I][{d}] = {vel_ex[d]}\n")

    def _export_f_new_list(self, f, class_name, new_name):
        idt, bi = self.idt, self.bi
        for idx in range(len(f)):
#            self.buffer.append(f"{idt[bi+2]}{new_name}[I][{idx}] = {f[idx]}\n")
            self.buffer.append(f"{idt[bi+2]}{new_name}[I + c[{idx}]*ti.static(self.pop)][{idx}] = {f[idx]}\n")

    def _export_bgk_code(self):
        idt, bi = self.idt, self.bi
        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        replacements, reduced_exprs = self.code_bundle

        self.buffer.append(f"{idt[bi+2]}# CSE expressions of macroscopic variables and f_eq\n")
        for var_sym, expr_sym in replacements:
            expr_str = self._clean_div_terms(str(sp.expand(expr_sym)))
            self.buffer.append(f"{idt[bi+2]}{var_sym} = {expr_str}\n")

        self.buffer.append(f"{idt[bi+2]}# Collision/relaxation\n")
        
        shift= 0 
        f_final = []
        for idx in range(num_pops):
            # stored later than rho and vel, so dim + 1 + idx
            # when drho mode is used, macro vars are [drho, rho, vels] so we need to set shift = 1
            f_final.append( self._clean_div_terms(str(reduced_exprs[(dim+1)+idx+shift])) ) 
        self._export_f_new_list(f_final, class_name, new_name)

        rho_ex = self._clean_div_terms(str(reduced_exprs[0]))
        vel_ex = []
        for d in range(dim):
            vel_ex.append(self._clean_div_terms(str(reduced_exprs[d+1])))
        self._export_macrovars(rho_ex, vel_ex, class_name)


    def _export_trt_code(self):
        idt, bi = self.idt, self.bi
        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        rr_macro, rr_feq  , rr_f_new, macro_ex = self.code_bundle # expand args
        replacements_macro, reduced_macro      = rr_macro
        replacements_feq  , reduced_feq        = rr_feq
        f_keys            , f_new_list         = rr_f_new
        macro_keys        , macro_exprs        = macro_ex

        self.buffer.append(f"{idt[bi+2]}# CSE expressions of macroscopic variables and f_eq\n")
        for sym, expr in replacements_macro: # macrovars parts
            self.buffer.append(f"{idt[bi+2]}{sym} = {self._clean_div_terms(str(expr))}\n")

        for name, red_expr in zip(macro_exprs.keys(), reduced_macro): # rho = , u = ...
            self.buffer.append(f"{idt[bi+2]}{name} = {self._clean_div_terms(str(red_expr))}\n")

        for sym, expr in replacements_feq: # feq parts
            self.buffer.append(f"{idt[bi+2]}{sym} = {self._clean_div_terms(str(expr))}\n")

        for q, red_expr in enumerate(reduced_feq): # feq = ...
            self.buffer.append(f"{idt[bi+2]}feq{q} = {self._clean_div_terms(str(red_expr))}\n")

        self.buffer.append(f"{idt[bi+2]}# Collision/relaxation\n")
        for q in range(num_pops):
#            self.buffer.append(f"{idt[bi+2]}{new_name}[I][{q}] = {self._clean_div_terms(str(f_new_list[f_keys[q]]))}\n")
            self.buffer.append(f"{idt[bi+2]}{new_name}[I + c[{q}]*ti.static(self.pop)][{q}] = {self._clean_div_terms(str(f_new_list[f_keys[q]]))}\n")

        self.buffer.append(f"\n{idt[bi+2]}# Update arrays of macroscopic vars\n")
        self._export_macrovars(macro_keys[0], macro_keys[1:dim+1], class_name)


    def _export_mrt_code(self):
        idt, bi = self.idt, self.bi
        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        rr, meq_rr, inv_rr, vel_names, moment_set = self.code_bundle # <--- updated from rr, inv_rr, vel_names, moment_set = self.code_bundle
        replacements    , reduced     = rr
        meq_replacements, meq_reduced = meq_rr # <--- updated 
        inv_replacements, inv_reduced = inv_rr
        m_eq_dict, moment_orders, mom_names, M_post = moment_set

        self.buffer.append(f"{idt[bi+2]}# 1) Forward transformation from f to raw moment\n")
        for var, expr in replacements: self.buffer.append(f"{idt[bi+2]}{var} = {self._clean_div_terms(str(expr))}\n")
        for name, expr in zip(mom_names, reduced): self.buffer.append(f"{idt[bi+2]}{name} = {self._clean_div_terms(str(expr))}\n")
        
        self.buffer.append(f"\n{idt[bi+2]}rho = m" + "0"*dim)
        rho_full = 'rho' if self.drho_mode=='rho' else '(rho + 1)'
        self.buffer.append(f"\n{idt[bi+2]}inv_rho = 1.0 / {rho_full}\n")
        for d_idx, d_name in enumerate(vel_names):
            mom_code = ["0"] * dim; mom_code[d_idx] = "1"
            self.buffer.append(f"{idt[bi+2]}{d_name} = m{''.join(mom_code)} * inv_rho\n")
            
        self.buffer.append(f"\n{idt[bi+2]}# Equilibrium moments (m_eq)\n")
        '''
        skip_eq_moms = {"m20", "m02", "m200", "m020", "m002"}
        for name, expr in m_eq_dict.items():
            if name in skip_eq_moms: 
                continue
            if name[1:].isdigit():
                if sum(int(c) for c in name[1:]) <= 1: 
                    continue
            self.buffer.append(f"{idt[bi+2]}{name}_eq = {self._clean_div_terms(str(expr))}\n")
        '''
        # ---> updated
        for var_sym, expr_sym in meq_replacements:
            self.buffer.append(f"{idt[bi+2]}{var_sym} = {self._clean_div_terms(str(expr_sym))}\n")

        for name, expr in zip(m_eq_dict.keys(), meq_reduced):
            self.buffer.append(f"{idt[bi+2]}{name}_eq = {self._clean_div_terms(str(expr))}\n")
        # <--- updated

        self.buffer.append(f"\n{idt[bi+2]}# 2) Collision/relaxation in moment space\n")
        for o in moment_orders:
            o_name = "".join(map(str, o))
            self.buffer.append(f"{idt[bi+2]}m{o_name}_post = {self._clean_div_terms(str(M_post[o]))}\n")
        
        self.buffer.append(f"\n{idt[bi+2]}# 3) Backward transformation from m to f\n")
        for var_sym, expr_sym in inv_replacements:
            safe_var = str(var_sym).replace("x", "inv_x")
            expr_str = self._clean_div_terms(str(sp.factor(expr_sym)))
            if "/4" in expr_str:  expr_str = "0.25 * (" + expr_str.replace("/4", "") + ")"
            elif "/2" in expr_str: expr_str = "0.5 * (" + expr_str.replace("/2", "") + ")"
            self.buffer.append(f"{idt[bi+2]}{safe_var} = {expr_str.replace('x', 'inv_x')}\n")
            
        for idx, final_expr in enumerate(inv_reduced):
#            self.buffer.append(f"{idt[bi+2]}{new_name}[I][{idx}] = {self._clean_div_terms(str(final_expr)).replace('x', 'inv_x')}\n")
            self.buffer.append(f"{idt[bi+2]}{new_name}[I + c[{idx}]*ti.static(self.pop)][{idx}] = {self._clean_div_terms(str(final_expr)).replace('x', 'inv_x')}\n")

        self.buffer.append(f"\n{idt[bi+2]}# 4) Update arrays of macroscopic vars\n")
        self.buffer.append(f"{idt[bi+2]}lbm.rho[I] = rho # <- note: actual value stored here is rho - density_shift\n")
        for d_idx, d_name in enumerate(vel_names):
            self.buffer.append(f"{idt[bi+2]}lbm.vel[I][{d_idx}] = {d_name}\n")


    def _export_cumulant_code(self):
        idt, bi = self.idt, self.bi
        dim, num_pops, collision_model, vectors, weights = self.default_pack
        class_name, old_name, new_name                   = self.misc_pack

        all_assignments, rr_macro, macro_keys, vel_names = self.code_bundle
        replacements_macro, reduced_macro                = rr_macro

        for var, expr in replacements_macro: self.buffer.append(f"{idt[bi+2]}{var} = {self._clean_div_terms(str(expr))}\n")
        for name, expr in zip(macro_keys, reduced_macro): 
            if name =='rho':
                rho_expr = expr
                density_shift = sp.Integer(1) if self.drho_mode == 'drho' else sp.Integer(0)
                self.buffer.append(f"{idt[bi+2]}{name} = {self._clean_div_terms(str(expr + density_shift))} # real (un-shifted) density\n")
            else:
                self.buffer.append(f"{idt[bi+2]}{name} = {self._clean_div_terms(str(expr))}\n")
        self.buffer.append(f"{idt[bi+2]}inv_rho = 1.0 / rho\n")

        self.buffer.append(f"{idt[bi+2]}# forward chimera transform & macroscopic quantities\n")

        # re-order allsignments as 
        # from macro to post moment, (stored in asignments_other)
        # then, post f in oder of 0, 1, 2, ... (stored in f_post)
        f_post_map = {}
        assignments_other = []
        for var_sym, expr in all_assignments:
            var_name = var_sym.name
            if var_name.startswith("f_post_idx_"):
                f_idx = vectors.index(self._convert_direction_to_idx(dim, var_name))
                f_post_map[f_idx] = expr # write f_new last. for this, we escape them into f_post_map
            else:
                assignments_other.append((var_name, expr))                    
        
        skip_moments = ['m00', 'm10', 'm01'] if dim==2 else ['m000', 'm100', 'm010', 'm001']
        for var_name, expr in assignments_other:
            if var_name in skip_moments:
                pass
            else:
                self.buffer.append(self._clean_div_terms(f"{idt[bi+2]}{var_name} = {expr}\n"))

        for f_idx in sorted(f_post_map.keys()):
            expr = f_post_map[f_idx]
#            self.buffer.append(self._clean_div_terms(f"{idt[bi+2]}{new_name}[I][{f_idx}] = {expr}\n"))
            self.buffer.append(self._clean_div_terms(f"{idt[bi+2]}{new_name}[I + c[{f_idx}]*ti.static(self.pop)][{f_idx}] = {expr}\n"))

        self.buffer.append(f"\n{idt[bi+2]}# update arrays of macroscopic vars\n")
        self.buffer.append(f"{idt[bi+2]}{class_name}.rho[I] = {self._clean_div_terms(str(rho_expr))}\n")
        for d_idx, d_name in enumerate(vel_names):
            self.buffer.append(f"{idt[bi+2]}{class_name}.vel[I][{d_idx}] = {d_name}\n")


    # convert direction in variable name to q index, like '1_1_1' -> 26
    def _convert_direction_to_idx(self, dim, var_name):
        parts = var_name.split("_")
        def parse_v(s):
            if s == "m1": return -1
            return int(s)
        if dim == 2:
            return (parse_v(parts[3]), parse_v(parts[4])) # (i, j)
        else:
            return (parse_v(parts[3]), parse_v(parts[4]), parse_v(parts[5])) # (i, j, k)
        
