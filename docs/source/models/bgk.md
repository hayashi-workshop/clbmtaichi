# BGK

```{admonition} @github
[`lb_solver/d2q9_BGK_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_BGK_kernel.py)
[`lb_solver/d2q9_BGK_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_BGK_drho_kernel.py)
[`lb_solver/d3q27_BGK_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_BGK_kernel.py)
[`lb_solver/d3q27_BGK_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_BGK_drho_kernel.py)
```

## Single-relaxation time model

BGK is abbreviation of the authors' names, Bhatnagar, Gross and Krook {cite:p}`Bhatnagar1954`. [This model assumes that all $f$ relaxes toward equilibrium at the same rate denoted by $\omega$.](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L158) Therefore, 

```{math}
:label: eq:eq_LBE_bgk

f_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q} (t, \mathbf{x}) - \omega ( f_{q} - f_{q}^{eq} )
```

where $\omega$ is defined by 

```{math}
:label: eq:eq_omega_definition

\omega = 1 / \tau
```

and $\tau$ is the relaxation time. The kinematic viscosity is given as a function of $\tau$ as 

```{math}
:label: eq:eq_viscosity_definition

\nu = c_{s}^{2} \left( \tau - \frac{1}{2} \right)
```

where $c_{s}$ is the speed of sound, and $c_{s}^{2} = 1/3$ for D2Q9 and D3Q27 velocity models. 

```{note}
The Chapman-Enskog expansion derives that the pressure in LBM is $p = c_{s}^{2} \rho$ which is consistent with the definition of speed of sound $c_{s}^{2} = \left. \partial p / \partial \rho \right|_{s}$ for idela gas.

```


## Equilibrium distribution function

[The equilibrium distribution function](https://github.com/hayashi-workshop/clbmtaichi/blob/c9e6d53609b93901daaef06c0d13dccf0fb81319/generator/generator_utils/common_utils.py#L59) in LBM is given by 

```{math}
:label: eq:eq_f_eq

f_{i}^{eq} = w_{i} \rho \left( 1 + \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ \mathbf{u} \cdot \mathbf{u} }{2 c_{s}^{2}} \right)
```

This is a discrete expression of Maxwelian {cite:p}`Seta2021` and can be derived from the Hermite generating function {cite:p}`Kruger2017`. 


The values of [weights $w_{i}$](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/common_utils.py#L7) are determined by the parity symmetry (the Hermite generating function is symmetric) and constrains required to recover the Navier-Stokes equation. For example, the condition $\sum f^{eq} = \rho$ imposes 

```{math}
:label: eq:eq_sum_w

\sum_{i=0}^{Q-1} w_{i} = 1
```

```{math}
:label: eq:eq_sum_cw

\sum_{i=0}^{Q-1} c_{i\alpha} w_{i} = 0
```

```{math}
:label: eq:eq_sum_ccw

\sum_{i=0}^{Q-1} c_{i\alpha} c_{i\beta} w_{i} = c_{s}^{2} \delta_{\alpha \beta}
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python 
dim = 2 # set dimension
vectors = create_vectors(dim=dim)
weights = [calculate_weight(v) for v in vectors]
display(weights)
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python 
dim = 2

vectors = create_vectors(dim) 
weights = [calculate_weight(v) for v in vectors]

rho = sp.Symbol('rho')
u   = sp.symbols(['u', 'v', 'w'][:dim]) 

cs2 = sp.Rational(1, 3)
u_sq_sum = sum(u_i**2 for u_i in u)
    
for idx, vec in enumerate(vectors):
    c_dot_u = sum(cx * u_i for cx, u_i in zip(vec, u))
    display( Eq( sp.Symbol(f"f_eq{idx}"), weights[idx] * rho * (1 + c_dot_u/cs2 + (c_dot_u**2)/(2 * cs2**2) - u_sq_sum/(2 * cs2)) ) )
```


## Density-fluctuation mode

In LBM, the density at $\mathbf{u} = 0$ is scaled as $\rho_{0} = 1$. The density fluctuation is expected to be small in incompressible flows, so that the density fluctuation $\delta \rho = \rho - \rho_{0}$ around $\rho_{0}$ may be small. It is therefore reasonable to [shift distribution](https://github.com/hayashi-workshop/clbmtaichi/blob/c9e6d53609b93901daaef06c0d13dccf0fb81319/generator/cumulant_generator.py#L75) as 

```{math}
:label: eq:eq_shifted_f

\widetilde{f}_{i} = f_{i} - w_{i}
```

to capture $\delta \rho$. With $\widetilde{f}_{i}$, 

```{math}
:label: eq:eq_density_fluctuation

\delta \rho = \sum_{i=0}^{Q-1} \widetilde{f}_{i}
```

The density-fluctuation mode may also advantageous from a point of view of preventing round-off errors in single-precision computing on gpu (this statement needs validation). 

The momentum is unchanged under the density shift due to the parity symmetry of the lattice velocity: 

```{math}
:label: eq:eq_momentum_shifted

\rho \mathbf{u} = \sum_{i=0}^{Q-1} \mathbf{c}_{i} f_{i} = \sum_{i=0}^{Q-1} \mathbf{c}_{i} \widetilde{f}_{i}
```

The shifted equilibrium disribution function is also defined as

```{math}
:label: eq:eq_shifted_f_eq

\widetilde{f}_{i}^{eq} = f_{i}^{eq} - w_{i} = w_{i} \left( \delta \rho + \rho \left[ \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ \mathbf{u} \cdot \mathbf{u} }{2 c_{s}^{2}} \right] \right)
```

where 

$$
\sum_{i=0}^{Q-1} \widetilde{f}_{i}^{eq} = \sum_{i=0}^{Q-1} \left( {f}_{i}^{eq} - w_{i} \right) = \rho - \rho_{0} = \delta \rho
$$

The LB functional form is unchangd under the density shift: 

```{math}
:label: eq:eq_LBE_bgk_shifted

\widetilde{f}_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = \widetilde{f}_{i} (t, \mathbf{x}) - \omega ( \widetilde{f}_{i} - \widetilde{f}_{i}^{eq} )
```

```{note}
Further approximation? $\rho = \rho_{0} + \delta \rho$. Products of $\delta \rho$ and $u$ are expected to be small, and therefore $\rho \rightarrow \rho_{0}$ in the second term. This approximation however made simulations unstable in our experience. 
```{math}
\widetilde{f}_{i}^{eq} = w_{i} \left( \delta \rho + \rho_{0} \left[ \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ \mathbf{u} \cdot \mathbf{u} }{2 c_{s}^{2}} \right] \right)
```


## Constraints for weights

In addition to Eqs. {eq}`eq:eq_sum_w`, {eq}`eq:eq_sum_cw` and {eq}`eq:eq_sum_ccw`, we have the following to recover the N-S equation:

```{math}
:label: eq:eq_eq_sum_cccw

\sum_{i=0}^{Q-1} c_{i\alpha} c_{i\beta} c_{i\gamma} w_{i} = 0
```
```{math}
:label: eq:eq_eq_sum_ccccw

\sum_{i=0}^{Q-1} c_{i\alpha} c_{i\beta} c_{i\gamma} c_{i\delta} w_{i} = c_{s}^{4} ( 
    \delta_{\alpha\beta} \delta_{\gamma\delta}
    +\delta_{\alpha\gamma} \delta_{\beta\delta}
    +\delta_{\alpha\delta} \delta_{\beta\gamma}
    )
```
```{math}
:label: eq:eq_eq_sum_cccccw

\sum_{i=0}^{Q-1} c_{i\alpha} c_{i\beta} c_{i\gamma} c_{i\delta} c_{i\sigma} w_{i} = 0
```

We shall check the constraints are fullfilled with our weights. First, we define the following function in [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb): 

```python 
from collections.abc import Iterable

def compute_weight_tensor(suffix=None, dim=2): # suffix is tuple
    vectors = create_vectors(dim) # create lattice velocity
    weights = [calculate_weight(v) for v in vectors]

    if suffix == None:
        return sum(weights)
    elif not isinstance(suffix, Iterable):
        suffix = (suffix,)

    w_tensor_expr = 0 # sum ( w_{i} * c_{i alpha} * c_{i beta} * c_{i gamma} ...)
    for i, v in enumerate(vectors):
        cprod = weights[i] # set w_{i}
        for s in suffix:
            ss = s - 1 # shift: physics uses x=1, but code uses x=0
            cprod *= v[ss] # multiply w_{i} * c_{i alpha} * c_{i beta} * c_{i gamma} ...
        w_tensor_expr += cprod

    return w_tensor_expr
```

Then, for the 0th-order (scalar), 
```python
dim = 3
W0 = compute_weight_tensor(dim=dim)
display(W0)
```

The 1st-order (vector), 
```python
import numpy as np

wt = []
for i in range(dim):
    wt.append(compute_weight_tensor(suffix=(i), dim=dim))
W1 = sp.Matrix( np.array(wt) )
display(W1)
```

The 2nd-order tensor, 
```python
wt = []
for j in range(dim):
    for i in range(dim):
        suffix = (i, j)
        wt.append( compute_weight_tensor(suffix=suffix, dim=dim) )
W2 = sp.Matrix( np.array(wt).reshape(dim, dim) )
display(W2)
```

For the higher orders, let me leave an example, 
```python
display(compute_weight_tensor(suffix=(1,1,2,2), dim=dim)) # 4th-order (result: 1/9)
```