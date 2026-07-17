# MRT

```{admonition} @github
[`lb_solver/d2q9_MRT_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_MRT_kernel.py)
[`lb_solver/d2q9_MRT_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_MRT_drho_kernel.py)
[`lb_solver/d3q27_MRT_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_MRT_kernel.py)
[`lb_solver/d3q27_MRT_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_MRT_drho_kernel.py)
```

## Multi-relaxation time model

[The collision proceeds in the moment space](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L251) rather than the $f$ space:

```{math}
:label: eq:eq_moment_transformation
m = M f
```

where $f$ is the vector of distribution function ($f_{q}$), $M$ is the transformation matrix, and $m$ is the moment vector. Therefore,

```{math}
:label: eq:eq_collision_mrt

\Omega = - S ( m - m^{eq} )
```

and 

```{math}
:label: eq:eq_LBE_mrt_collision

m^{*} = m - S ( m - m^{eq} )
```

where $m^{*}$ denotes the post-collision moment, and $S$ is the diagonal matrix whose components are the relaxation rates for each moment. The streaming process is applied to $f_{i}$; that is, 

```{math}
:label: eq:eq_LBE_mrt

f_{i}^{*}(t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = f_{i} (t, \mathbf{x}) - M^{-1} m^{*}
```

The non-orthogonal (raw) moments of orders $(\alpha, \beta, \gamma)$ in each direction are defined by 

```{math}
:label: eq:eq_raw_moment_definition

m_{\alpha \beta \gamma} = \sum_{i=0}^{Q-1} c_{ix}^{\alpha} c_{iy}^{\beta} c_{iz}^{\gamma} f_{i}
```


```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
$$
m_{00} = \sum_{i=0}^{Q-1} c_{ix}^{0} c_{iy}^{0} f_{i} = \sum_{i=0}^{Q-1} f_{i} =  f_{0} + f_{1} + f_{2} + f_{3} + f_{4} + f_{5} + f_{6} + f_{7} + f_{8}
$$

$$
m_{20} = \sum_{i=0}^{Q-1} c_{ix}^{2} c_{iy}^{0} f_{i} = f_{1} + f_{3} + f_{5} + f_{6} + f_{7} + f_{8}
$$

```python
moment_d2q9 = MomentGenerator(vectors=create_vectors(dim=2), is_central_moment=False)
m00 = moment_d2q9((0,0))
print(m00.rhs)
m20 = moment_d2q9((2,0))
print(m20.rhs)
```

```{note}
The MRT introduced here differs from the well-known DHumieres's implementation {cite:p}`DHumieres`, in which Gram-Schmidt orthogonalization is the key idea to connecting each moment to physical quantities. See discussion in {cite:p}`Geier2015`.
```

## Equilibrium moment $m_{eq}$

The equilibrium distribution function $f_{i}^{eq}$ in the BGK section was obtained by the second-order approximation. The equilibrium moments $m^{eq}$ up to second order can be obtained by directly transforming $f_{i}^{eq}$ with $M$ as 
```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
```python
dim = 3

vectors = create_vectors(dim) 
weights = [calculate_weight(v) for v in vectors]

rho = sp.Symbol('rho')
u   = sp.symbols(['u', 'v', 'w'][:dim]) 

cs2 = sp.Rational(1, 3)
u_sq_sum = sum(u_i**2 for u_i in u)

feq_list = []
for idx, vec in enumerate(vectors):
    c_dot_u = sum(cx * u_i for cx, u_i in zip(vec, u))
    feq = weights[idx] * rho * (1 + c_dot_u/cs2 + (c_dot_u**2)/(2 * cs2**2) - u_sq_sum/(2 * cs2))
    feq_list.append( feq ) 
    
M = moment_d3q27.M

meq = sp.simplify( M@sp.Matrix(feq_list) )
display(meq) # result: rho, rho u, rho w, rho v, rho (u^2 + 1/3), ...
```


The conserved quantities (density and momentum): 
```{math} 
:label: eq:eq_conserved_moments

m_{000}^{eq} = \rho,~~m_{100}^{eq} = \rho u,~~m_{010}^{eq} = \rho v,~~m_{001}^{eq} = \rho w
```

The second-order moments: 
```{math}
:label: eq:eq_2nd_order_moments

m_{200}^{eq} = \rho u^{2} + \rho c_{s}^{2},~~
m_{020}^{eq} = \rho v^{2} + \rho c_{s}^{2},~~
m_{002}^{eq} = \rho w^{2} + \rho c_{s}^{2}
```

The other second-order moments: 
```{math} 
:label: eq:eq_2nd_order_moments_others

m_{110}^{eq} = \rho u v,~~
m_{101}^{eq} = \rho u w,~~
m_{011}^{eq} = \rho v w,~~
```


For the 3rd-order moment, we shall confirm the central moment: 
```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
```python
moment_d3q27.derive_central_moment_from_moment((2,1,0))
```
This code shows you that 
```{math}
\kappa_{210} = m_{210} - \frac{m_{010} m_{200}}{m_{000}} - \frac{2 m_{100} m_{110}}{m_{000}} + \frac{2 m_{010} m_{100}^{2}}{m_{000}^{2}}
```

In equilibrium, the third and fourth terms cancel out, and $C_{210}^{eq} = \kappa_{210}^{eq} = 0$, where $C_{210}$ is the density-scaled cumulant (see {ref}`cumulant`). Therefore, 
```{math}
m_{210}^{eq} = \frac{m_{010}^{eq} m_{200}^{eq}}{m_{000}^{eq}}
```

The third-order moments:
```{math} 
:label: eq:eq_3rd_order_moments

m_{210}^{eq} = \frac{m_{200}^{eq} m_{010}^{eq}}{m_{000}^{eq}},~~
m_{201}^{eq} = \frac{m_{200}^{eq} m_{001}^{eq}}{m_{000}^{eq}},~~
m_{120}^{eq} = \frac{m_{100}^{eq} m_{020}^{eq}}{m_{000}^{eq}},~~
m_{102}^{eq} = \frac{m_{100}^{eq} m_{002}^{eq}}{m_{000}^{eq}},~~
m_{021}^{eq} = \frac{m_{020}^{eq} m_{001}^{eq}}{m_{000}^{eq}},~~
m_{012}^{eq} = \frac{m_{010}^{eq} m_{002}^{eq}}{m_{000}^{eq}},~~
m_{111}^{eq} = \frac{m_{100}^{eq} m_{010}^{eq} m_{001}^{eq}}{m_{000}^{eq} m_{000}^{eq}}
```

We then consider $m_{211}$. 
```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
```python
C = cumulants_d3q27((2,1,1), density_scaling=True).rhs

kappa_subs_dict = {
    'kappa011': moment_d3q27.derive_central_moment_from_moment((0,1,1)).rhs,
    'kappa200': moment_d3q27.derive_central_moment_from_moment((2,0,0)).rhs,
    'kappa101': moment_d3q27.derive_central_moment_from_moment((1,0,1)).rhs,
    'kappa110': moment_d3q27.derive_central_moment_from_moment((1,1,0)).rhs,
    'kappa211': moment_d3q27.derive_central_moment_from_moment((2,1,1)).rhs,
}

C = sp.simplify(C.subs(kappa_subs_dict))

rho = sp.Symbol('rho')
u, v, w = sp.symbols(['u', 'v', 'w'])
cs2 = sp.Rational(1,3)
moment_subs_dict = {
    'm000': rho,
    'm100': rho*u,
    'm010': rho*v,
    'm001': rho*w,
    'm110': rho*u*v,
    'm101': rho*u*w,
    'm011': rho*v*w,
    'm111': rho*u*v*w,
    'm200': rho*(u**2+cs2),
    'm020': rho*(v**2+cs2),
    'm002': rho*(w**2+cs2),
    'm210': rho*(u**2+cs2)*v,
    'm201': rho*(u**2+cs2)*w,
    'm120': rho*(v**2+cs2)*u,
    'm021': rho*(v**2+cs2)*w,
    'm102': rho*(w**2+cs2)*u,
    'm012': rho*(w**2+cs2)*v, 
}

C = sp.simplify(C.subs(moment_subs_dict))

display(C)
```
We recognize that 
```{math}
C_{211}^{eq} = m_{211}^{eq} - \rho u^{2} v w - \frac{\rho v w}{3}
```
However, $C_{211}^{eq} = 0$, and thereofre 
```{math}
m_{211}^{eq} = \left( \rho u^{2} + \frac{\rho}{3} \right) v w 
```

The fourth-order moments:
```{math} 
:label: eq:eq_4th_order_moments

m_{220}^{eq} = \frac{m_{200}^{eq} m_{020}^{eq}}{m_{000}^{eq}},~~
m_{202}^{eq} = \frac{m_{200}^{eq} m_{002}^{eq}}{m_{000}^{eq}},~~
m_{022}^{eq} = \frac{m_{020}^{eq} m_{002}^{eq}}{m_{000}^{eq}},~~
m_{211}^{eq} = \frac{m_{200}^{eq} m_{010}^{eq} m_{001}^{eq}}{m_{000}^{eq} m_{000}^{eq}},~~
m_{121}^{eq} = \frac{m_{100}^{eq} m_{020}^{eq} m_{001}^{eq}}{m_{000}^{eq} m_{000}^{eq}},~~
m_{112}^{eq} = \frac{m_{100}^{eq} m_{010}^{eq} m_{002}^{eq}}{m_{000}^{eq} m_{000}^{eq}}
```

The fifth-order moments:
```{math} 
:label: eq:eq_5th_order_moments

m_{221}^{eq} = \frac{m_{200}^{eq} m_{020}^{eq} m_{001}^{eq}}{m_{000}^{eq} m_{000}^{eq}},~~
m_{212}^{eq} = \frac{m_{200}^{eq} m_{010}^{eq} m_{002}^{eq}}{m_{000}^{eq} m_{000}^{eq}},~~
m_{122}^{eq} = \frac{m_{100}^{eq} m_{020}^{eq} m_{002}^{eq}}{m_{000}^{eq} m_{000}^{eq}}
```

Before considering the highest order, we define the moment subs dict: 
```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
```python
import itertools

moment_orders = itertools.product(range(3), repeat=3)

kappa_subs_dict = {} # for central moment
for XYZ in moment_orders:
    key_name = f"kappa{XYZ[0]}{XYZ[1]}{XYZ[2]}"
    kappa_subs_dict[key_name] = moment_d3q27.derive_central_moment_from_moment(XYZ).rhs

moment_subs_dict.update( # update moment_subs_dict up to 5th order
    {
        'm220': rho*(u**2+cs2)*(v**2+cs2),
        'm202': rho*(u**2+cs2)*(w**2+cs2),
        'm022': rho*(v**2+cs2)*(w**2+cs2),
        'm211': rho*(u**2+cs2)*v*w,
        'm121': rho*(v**2+cs2)*u*w,
        'm112': rho*(w**2+cs2)*u*v,
        'm122': rho*(v**2+cs2)*(w**2+cs2)*u,
        'm212': rho*(u**2+cs2)*(w**2+cs2)*v,
        'm221': rho*(u**2+cs2)*(v**2+cs2)*w,
    }
)
```

Then, 
```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)
```python
C = cumulants_d3q27((2,2,2), density_scaling=True).rhs
C = sp.simplify(C.subs(kappa_subs_dict))
C = sp.simplify(C.subs(moment_subs_dict))
m222 = sp.solve(Eq(sp.Symbol('C222'), C), sp.Symbol('m222'))[0]
m222 = sp.factor(m222.subs({'C222': 0}))
```
You would find 
```{math}
m_{222}^{eq} = \rho \left( u^{2} + \frac{1}{3} \right) \left( v^{2} + \frac{1}{3} \right) \left( w^{2} + \frac{1}{3} \right)
```
where $C_{222}^{eq} = 0$ was used. 

Thus, the sixth-order moment: 
```{math} 
:label: eq:eq_6th_order_moment

m_{222}^{eq} = \frac{m_{200}^{eq} m_{020}^{eq} m_{002}^{eq}}{m_{000}^{eq} m_{000}^{eq}}
```

## Collision in moment space

The formulation 
```{math}
m^{*} = (1 - \omega) m + m^{eq}
```
is applied to $110$, $101$, $011$, $211$, $121$, $112$, $221$, $212$, $122$, $222$. $m_{110}$, $m_{101}$, $m_{011}$ are relaxed with $\omega_{1}$ for shear viscosity. 

With $200$s, for shear 
```{math} 
:label: eq:eq_MRT_col_shear

\begin{split}
m_{200}^{*} - m_{020}^{*} = (1 - \omega_{1}) (m_{200} - m_{020}) + (m_{200}^{eq} - m_{020}^{eq}) \\
m_{200}^{*} - m_{002}^{*} = (1 - \omega_{1}) (m_{200} - m_{002}) + (m_{200}^{eq} - m_{002}^{eq}) \\
\end{split}
```
and for bulk 
```{math} 
:label: eq:eq_MRT_col_bulk

m_{200}^{*} + m_{020}^{*} + m_{002}^{*}
 = (1 - \omega_{2})(m_{200} + m_{020} + m_{002}) + (m_{200}^{eq} + m_{020}^{eq} + m_{002}^{eq}) 
```
Then, the other moments are relaxed as 
```{math} 
:label: eq:eq_MRT_col_dev

\begin{split}
&m_{120}^{*} + m_{102}^{*} = (1-\omega_{3})(m_{120} + m_{102}) + (m_{120}^{eq} + m_{102}^{eq}) \\
&m_{120}^{*} - m_{102}^{*} = (1-\omega_{4})(m_{120} - m_{102}) + (m_{120}^{eq} - m_{102}^{eq}) \\
&m_{210}^{*} + m_{012}^{*} = (1-\omega_{3})(m_{210} + m_{012}) + (m_{210}^{eq} + m_{012}^{eq}) \\
&m_{210}^{*} - m_{012}^{*} = (1-\omega_{4})(m_{210} - m_{012}) + (m_{210}^{eq} - m_{012}^{eq}) \\
&m_{201}^{*} + m_{021}^{*} = (1-\omega_{3})(m_{201} + m_{021}) + (m_{201}^{eq} + m_{021}^{eq}) \\
&m_{201}^{*} - m_{021}^{*} = (1-\omega_{4})(m_{201} - m_{021}) + (m_{201}^{eq} - m_{021}^{eq}) 
\end{split}
```
and 
```{math} 
:label: eq:eq_MRT_col_devdev

\begin{split}
&m_{220}^{*} - 2 m_{202}^{*} + m_{022}^{*} = (1-\omega_{6}) (m_{220} - 2 m_{202} + m_{022}) + (m_{220}^{eq} - 2 m_{202}^{eq} + m_{022}^{eq}) \\
&m_{220}^{*} + m_{202}^{*} - 2 m_{022}^{*} = (1-\omega_{6}) (m_{220} + m_{202} - 2 m_{022}) + (m_{220}^{eq} + m_{202}^{eq} - m_{022}^{eq}) \\
&m_{220}^{*} + m_{202}^{*} + m_{022}^{*} = (1-\omega_{7}) (m_{220} + m_{202} + m_{022}) + (m_{220}^{eq} + m_{202}^{eq} + m_{022}^{eq}) 
\end{split}
```


## Back transformation from $m$ to $f$

The back transformation is given simply by 

```{math}
:label: eq:eq_backtransformation_f_m

f^{*} = M^{-1} m^{*}
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

$$
f_{1} = \frac{m_{10}}{2} - \frac{m_{12}}{2} + \frac{m_{20}}{2} - \frac{m_{22}}{2}
$$

```python
moment_d2q9 = MomentGenerator(vectors=create_vectors(dim=2), is_central_moment=False)
f_exprs, f_list = moment_d2q9.express_f_in_terms_of_moments()
print(f_exprs[1])
```


However, since each moment appears multiple times in the $f$ expression, naive computation by definition is not efficient. [An efficient backward transformation from $m$ to $f$](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/cumulant_utils.py#L304) is given by (Eq. (B.89)-(B.97) in {cite:p}`Geier2015`)

```{math}
:label: eq:eq_chimera_backtransformation_m_f

\begin{aligned}
&m_{0|\beta\gamma} = m_{0\beta\gamma} - m_{2\beta\gamma} \\
&m_{\bar{1}|\beta\gamma} = (-m_{1\beta\gamma} + m_{2\beta\gamma}) / 2 \\
&m_{1|\beta\gamma} = (m_{1\beta\gamma} + m_{2\beta\gamma}) / 2 \\
&m_{i0|\gamma} = m_{i0\gamma} - m_{i2\gamma} \\
&m_{i\bar{1}|\gamma} = (-m_{i1\gamma} + m_{i2\gamma}) / 2 \\
&m_{i1|\gamma} = (m_{i1\gamma} + m_{i2\gamma}) / 2 \\
&f_{ i j 0} = m_{ij|0} - m_{ij|2} \\
&f_{ i j-1} = \frac{ -m_{ij|1} + m_{ij|2} }{2} \\
&f_{ i j 1} = \frac{  m_{ij|1} + m_{ij|2} }{2} 
\end{aligned}
```

## Stability control

`examples/JCprob_bb.py` (push+bb) with $Re$ increased to 10,000,000 can be a challenge for numerical stability. All one for $\omega_{i>1}$ could not reach 1000000 steps, while the simulation got stable with $\omega_{i>2} = 1.4$, which dumped high order noises; where $\omega_{2}$ for bulk viscosity was kept at unity. 

<div style="max-width: 100%">
    <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/JCprob1_bb_MRT-10000000.png"></img>
</div>


`examples/nested.py` of Re=1,000,000 using MRT. The large $u$ (0.1) can be a challenge for stable simulation. High dumping for $\omega_{2}$ and over relaxation for higher orders are required to prevent simulation failure and noisy velocity distributions; $\omega_{2} = 1.8$ and $\omega_{i>2} = 1.9$ for all (four) grid levels in this example. The figure below shows the predicted velocity field at 50,000 step. 

<div style="max-width: 100%">
    <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/nested_MRT-50000.png"></img>
</div>


## Density-fluctuation mode

The shifted moment is defined by 

```{math}
:label: eq:eq_moment_transformation_shifted

\widetilde{m} = M \widetilde{f} = M ( f - w ) = m - M w
```

where $w$ is the vector of weights, and the non-zero components of $M w$, for example in D2Q9, are $(0,0): 1$, $(2,0), (0,2): 1/3$ and $(2,2): 1/9$. 

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python
vectors = create_vectors(dim=2)
weights = [calculate_weight(v) for v in vectors]
moment_d2q9.M@sp.Matrix(weights)
```

One additional pattern $1/27$ at the order $(0,0,0)$ appers in D3Q27. 


## Transformation matrix

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python
import itertools

dim = 2
vectors = create_vectors(dim=dim)

all_orders = list(itertools.product((0, 1, 2), repeat=dim))
moment_orders = sorted(all_orders, key=lambda x: (sum(x), -x[0]))
M, M_inv = create_trans_matrix(moment_orders, vectors) 
```

$$
M = 
\left[\begin{matrix}1 & 1 & 1 & 1 & 1 & 1 & 1 & 1 & 1\\0 & 1 & 0 & -1 & 0 & 1 & -1 & -1 & 1\\0 & 0 & 1 & 0 & -1 & 1 & 1 & -1 & -1\\0 & 1 & 0 & 1 & 0 & 1 & 1 & 1 & 1\\0 & 0 & 0 & 0 & 0 & 1 & -1 & 1 & -1\\0 & 0 & 1 & 0 & 1 & 1 & 1 & 1 & 1\\0 & 0 & 0 & 0 & 0 & 1 & 1 & -1 & -1\\0 & 0 & 0 & 0 & 0 & 1 & -1 & -1 & 1\\0 & 0 & 0 & 0 & 0 & 1 & 1 & 1 & 1\end{matrix}\right]
$$

$$
M^{-1}
=
\left[\begin{matrix}1 & 0 & 0 & -1 & 0 & -1 & 0 & 0 & 1\\0 & \frac{1}{2} & 0 & \frac{1}{2} & 0 & 0 & 0 & - \frac{1}{2} & - \frac{1}{2}\\0 & 0 & \frac{1}{2} & 0 & 0 & \frac{1}{2} & - \frac{1}{2} & 0 & - \frac{1}{2}\\0 & - \frac{1}{2} & 0 & \frac{1}{2} & 0 & 0 & 0 & \frac{1}{2} & - \frac{1}{2}\\0 & 0 & - \frac{1}{2} & 0 & 0 & \frac{1}{2} & \frac{1}{2} & 0 & - \frac{1}{2}\\0 & 0 & 0 & 0 & \frac{1}{4} & 0 & \frac{1}{4} & \frac{1}{4} & \frac{1}{4}\\0 & 0 & 0 & 0 & - \frac{1}{4} & 0 & \frac{1}{4} & - \frac{1}{4} & \frac{1}{4}\\0 & 0 & 0 & 0 & \frac{1}{4} & 0 & - \frac{1}{4} & - \frac{1}{4} & \frac{1}{4}\\0 & 0 & 0 & 0 & - \frac{1}{4} & 0 & - \frac{1}{4} & \frac{1}{4} & \frac{1}{4}\end{matrix}\right]
$$

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

See that $M M^{-1} = I$: 

```python
moment_d3q27.M@moment_d3q27.M_inv
```
