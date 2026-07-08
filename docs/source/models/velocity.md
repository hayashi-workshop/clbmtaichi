# Discrete velocity model

```{admonition} @github : velocity c defined as ti.Vector in kernel files
[`lb_solver/`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/)
```

```{important} 

Preparation of jupyter notebook for Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

If you have already clonee the repository, 
- `cd generator/`
- launch notebook by `jupyter notebook cumulant_moment_exprs.ipynb`
- Then, from notebook menu, `Kernel` > `Restart Kernel and Run All Cells` to load modules on your notebook. 
```

Particles belonging to $f_{i}$ move with the lattice velocity $\mathbf{c}_{i}$. In physics $\mathbf{c}$ is continuous in velocity space, and therefore infinite possibilities are considered. In numerics, we use a finite set of $\mathbf{c}$; discrete velocity set $\mathbf{c}_{i}$. D2Q9 ($f_{0}$, ..., $f_{8}$) and D3Q27 ($f_{0}$, ..., $f_{26}$) [velocity models](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/common_utils.py#L14) are supported in [`clbmtaichi`](https://github.com/hayashi-workshop/clbmtaichi/).

[The macroscopic variables](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L119), the density and momentum, are the 0th and 1st-order moments of the velocity distribution function $f$: 

```{math}
:label: eq:eq_macro_density

\rho = \sum_{i=0}^{Q-1} f_{i}
```

```{math}
:label: eq:eq_macro_momentum

\rho \mathbf{u} = \sum_{i=0}^{Q-1} \mathbf{c}_{i} f_{i}
```

where $Q = 9$ and $27$ in D2Q9 and D3Q27, respectively. 

## Velocity sets 

### D2Q9

```
#     6  2  5
#      \ | /
#     3- 0 -1
#      / | \
#     7  4  8 
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python
vector = create_vectors(dim=2)
display(vector) # result : [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (-1, -1), (1, -1)]
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

Compute Eq. {eq}`eq:eq_macro_density`

```python
dim = 2 # dimension
vectors = create_vectors(dim=dim)
f = sp.symbols(f'f0:{len(vectors)}') # f0, f1, ..., fn
display(f)
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

Compute Eq. {eq}`eq:eq_macro_momentum`

```python
def compute_moment_expr(order): # order is tuple
    dim = len(order) # get dimension from order tuple
    vectors = create_vectors(dim) # create lattice velocity
    u = sp.symbols(['u', 'v', 'w'][:dim]) # velocity symbols
    f = sp.symbols(f'f0:{len(vectors)}') # f0, f1, ..., fn

    moment_expr = 0 # sum (f_{i} * c_{ix}^alpha * c_{iy}^beta * c_{iz}^gamma)
    for i, v in enumerate(vectors):
        term = f[i] * sp.prod([ ( v[j] )**order[j] for j in range(dim) ])
        moment_expr += term

    return moment_expr

m00 = compute_moment_expr( (0,0) ) # m00 = rho
m10 = compute_moment_expr( (1,0) ) # m10 = rho u
m01 = compute_moment_expr( (0,1) ) # m01 = rho v
display(m10/m00, m01/m00) # u, v
```


### D3Q27

In D3Q27, the order of the lattice velocities is defined as 1st velocity, oppsite to 1st velocity is put on the second place, 3rd velocity, oppsite to 3rd velocity is put on the 4th place ... We show several exapmles below: 

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

```python 
vector = create_vectors(dim=3)
display(vector)
    # result
    #[(0, 0, 0),
    # (1, 0, 0),
    # (-1, 0, 0),
    # (0, 1, 0),
    # (0, -1, 0),
    # (0, 0, 1),
    # (0, 0, -1),
    # (1, 1, 0),
    # (-1, -1, 0),
    # (1, -1, 0),
    # (-1, 1, 0), ...
```

```
On $x-y$ plane, 

#    10  3  7
#      \ | /
#     2- 0 -1
#      / | \
#     8  4  9 
```

```{admonition} need help
Is it possible to draw 27 directions by ascii-art?
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

Function `compute_moment_expr` made above also works for 3D. Compute Eq. {eq}`eq:eq_macro_momentum`

```python
m000 = compute_moment_expr( (0,0,0) )
m100 = compute_moment_expr( (1,0,0) )
display(m100/m000)
```