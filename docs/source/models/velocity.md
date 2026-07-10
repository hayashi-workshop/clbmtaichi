# Discrete velocity model

```{admonition} @github : velocity c defined as ti.Vector in kernel files
[`lb_solver/`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/)
```

```{important} 

Preparation of jupyter notebook for Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

If you have already clone the repository, 
- `cd generator/`
- launch notebook by `jupyter notebook cumulant_moment_exprs.ipynb`
- Then, from notebook menu, `Kernel` > `Restart Kernel and Run All Cells` to load modules on your notebook. 
```


```
# <--- micro          |           meso           | ---> macro 
# (Newton's e.o.m.)            (Boltzmann)             (NS eq)
#    ^                                                   
#    |     o                        o                  ---> 
#    o     |       o    f(c=-1) <- ooo -> f(c=1)       ---> 
#          v      /                 o                  --->
#  o ->          L                                        
```
From a microscopic view, fluid molecles are moving as particles and their motion is governed by Newton's equation of motion. We can label each particle: particle 1, particle 2, particle 3... In contrast we have a bunch of particles in a macroscopic system and cannot see the motion of each particle; instead we are able to define the *density* (()/m<sup>3</sup>) of physical quantities as continuous function of space $\mathbf{x}$, e.g., the mass density $\rho (t, \mathbf{x})$ (kg/m<sup>3</sup>), the momentum density $\rho \mathbf{u}$ ((kg m/s)/m<sup>3</sup>). In the macrpscopic sense, even at a point $\mathbf{x}$, we assume that there are numerous particles and the densities are statistically meaningfull. The velocity $\mathbf{u}$ means the baricentric velocity of the particles at $\mathbf{x}$. A mesoscopic model deals with particles, but they are grouped in terms of the population $f$; the probability of particles moving at velocity $\mathbf{c}$. Interestigly, $f$ is cosindered as continuous function of $\mathbf{x}$ although we consider particles. Thus, the probability of particles of $\mathbf{c}$ at $t$ and $\mathbf{x}$ is $f(t, \mathbf{x}, \mathbf{c})$, and by assigning the particle mass to $f$ the mass density is given by  
```{math}
:label: eq:eq_density_from_f
\rho (t, \mathbf{x}) = \iiint_{-\infty}^{\infty} f (t, \mathbf{x}, \mathbf{c}) d\mathbf{c} 
```
$\mathbf{c}$ is continuous in velocity space, and therefore infinite possibilities are considered. In numerics, we use a finite set of $\mathbf{c}$; discrete velocity set $\mathbf{c}_{i}$. Particles belonging to $f_{i}$ move with the lattice velocity $\mathbf{c}_{i}$. D2Q9 ($f_{0}$, ..., $f_{8}$) and D3Q27 ($f_{0}$, ..., $f_{26}$) [velocity models](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/common_utils.py#L14) are supported in [`clbmtaichi`](https://github.com/hayashi-workshop/clbmtaichi/).

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


## Discretization 

The Boltzmann equation is given by 
```{math}
:label: eq:eq_Boltzamann_discretized
\frac{\partial f}{\partial t} + \mathbf{c} \cdot \nabla f = \Omega (f)
```
We have discretized $\mathbf{c}$ as $\mathbf{c}_{i}$; thus 
```{math}
:label: eq:eq_lattice_Boltzamann_discretized
\frac{\partial f_{i}}{\partial t} + \mathbf{c}_{i} \cdot \nabla f_{i} = \Omega (f)
```
Applying the first-order upwind scheme yields
```{math} 
:label: eq:eq_lattice_Boltzamann_discretized_upwind
f_{i} (t + \Delta t, \mathbf{x}) = f_{i} ( t, \mathbf{x} ) + \left( - \frac{|\mathbf{c}_{i}| \Delta t}{| \Delta \mathbf{x} |} \left\{ f_{i} ( t, \mathbf{x} ) - f_{i} \left( t, \mathbf{x} - \frac{\mathbf{c}_{i}}{|\mathbf{c}_{i}|} \cdot \Delta \mathbf{x} \right) \right\} + \Delta t \Omega(f) \right)
```
where $\Delta \mathbf{x} = (\Delta x, \Delta y, \Delta z)$ and the components are distances between neighborting grid points (nodes). We usually take $\Delta t = \Delta x = \Delta y = \Delta z = 1$, and the lattice speed is given by $c = \Delta x / \Delta t = 1$. D2Q9 and D3Q27 consists of $\mathbf{c}_{i}$ whose components are $0$ or $\pm c$. Hence, 
```{math} 
:label: eq:eq_lattice_Boltzamann_equation
f_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = f_{i} ( t, \mathbf{x} ) + \Omega(f)
```
where the node coordinate was shifted: $\mathbf{x} \rightarrow \mathbf{x} + \mathbf{c}_{i} \Delta t$.

```{note}
Why can LBE mimic macroscopic flow behavior? See {cite:p}`Kruger2017`/{cite:p}`Seta2021`, or [Prof. Kruger's online lecture](https://www.youtube.com/watch?v=jfk4feD7rFQ). 
```

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
