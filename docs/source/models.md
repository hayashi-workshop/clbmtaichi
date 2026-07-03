# lattice Boltzmann method

For cumulants and moments, see also [Jupynoter Notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) provided in `generator` directory. 


## Discrete velocity

D2Q9 ($f_{0}$-$f_{8}$) and D3Q27 ($f_{0}$-$f_{26}$) models are supported.

The macroscopic variables, the density and momentum, are the 0th and 1st-order moments of the velocity distribution function $f$: 

$$
\rho = \sum_{q=0}^{Q-1} f_{q},~~~~\rho \mathbf{u} = \sum_{q=0}^{Q-1} \mathbf{c}_{q} f_{q}
$$

where $Q = 9$ or $Q = 27$. 

## LB equation
The code solves the following lattice Boltzmann equation: 

$$
f_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q} ( t, \mathbf{x} ) + \Omega(f)
$$

where $\Delta x = \Delta t = 1$ in lattice unit, and the lattice speed is defined by $c = \Delta x / \Delta t = 1$. 

## Operator splitting

The collision and streaming are split as 

$$
f_{q}^{*} ( t, \mathbf{x} ) = f_{q} ( t, \mathbf{x} ) + \Omega (f)
$$

$$
f_{q}^{*} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q}^{*} ( t, \mathbf{x} ) 
$$

The $*$ decoration denotes the post-collision distribution. 


### Pull/Push scheme

In collision-streaming kernel (Taichi kernel `col_stream_core`), streaming and collision are conducted in the same `for` loop since invoking Taichi kernel and fetching/writing distribution functions twice deteriorate simulation performce. 

The pull scheme is as follows: 
- fetch $f$s from negihbors (pull streaming), then
- perform collision and store $f$s at `(i,j,k)`.
- boundary condition is applied to the post-collision distributions. 

The push scheme is 
- fetch $f$s from `(i,j,k)` and do collision process, then
- push the post-collision $f$s to the neighbors.
- boundary condition is applied to the streamed distributions. 

The `ModelConfig` employs the pull scheme as default. You can choose the push by specifying the mode as 

```python
config = ModelConfig(mode="push")
```

[!NOTE]

The pull (push) scheme should be used with Guo's (bounce-back) boundary condition. These boundary conditions are defined, respectively, in  

- `lb_utils/bc_kernel.py` (Guo's bc)
- `lb_utils/bback_kernel.py` ((delayed) bounce-back)


## Equilibrium distribution function

The equilibrium distribution function in LBM is given by 

$$
f_{q}^{eq} = w_{q} \rho \left( 1 + \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ (\mathbf{u} \cdot \mathbf{u})^{2} }{2 c_{s}^{2}} \right)
$$

The shifted disribution function is also defined as

$$
\widetilde{f}_{q}^{eq} = f_{q}^{eq} - w_{q} = w_{q} \left( \delta \rho + \rho \left[ \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ (\mathbf{u} \cdot \mathbf{u})^{2} }{2 c_{s}^{2}} \right] \right)
$$

where 

$$
\delta \rho = \sum \widetilde{f}_{q}^{eq} = \rho - \rho_{0}
$$

and $\rho_{0} = 1$. In contrast, the momentum is unchanged under the density shift due to the parity symmetry of the lattice velocity: 

$$
\rho \mathbf{u} = \sum \mathbf{c}_{q} f_{q} = \sum \mathbf{c}_{q} \widetilde{f}_{q}
$$


### BGK

#### dDqQ_BGK_kernel

$$
f_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q} (t, \mathbf{x}) - \omega ( f_{q} - f_{q}^{eq} )
$$

where $\omega$ is the relaxation parameter defined by 

$$
\omega = 1 / \tau
$$

and $\tau$ is the relaxation time. 

#### dDqQ_BGK_drho_kernel

The shifted distribution $\widetilde{f}_{q} = {f}_{q} - w_{q}$ is used. The LB functional form is unchangd under the shift: 

$$
\widetilde{f}_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = \widetilde{f}_{q} (t, \mathbf{x}) - \omega ( \widetilde{f}_{q} - \widetilde{f}_{q}^{eq} )
$$

However, the shifted distribution function defined above is used for $\widetilde{f}_{i}^{eq}$.


### TRT

#### dDqQ_TRT_kernel

$$
f_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q} (t, \mathbf{x}) - \omega^{+} ( f_{q}^{+} - f_{q}^{eq+} ) - \omega^{-} ( f_{q}^{-} - f_{q}^{eq-} )
$$

where $\bar{q}$ represents the index of the direction opposite to $q$. 

$$
f_{q}^{+} = \frac{f_{q} + f_{\bar{q}}}{2},~~~~f_{q}^{-} = \frac{f_{q} - f_{\bar{q}}}{2}
$$


#### dDqQ_TRT_drho_kernel

$$
\widetilde{f}_{q} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = \widetilde{f}_{q} (t, \mathbf{x}) - \omega^{+} ( \widetilde{f}_{q}^{+} - \widetilde{f}_{q}^{eq+} ) - \omega^{-} ( \widetilde{f}_{q}^{-} - \widetilde{f}_{q}^{eq-} )
$$

### MRT

#### dDqQ_MRT_kernel

Collision process is computed in the moment space:

$$
m = M f
$$

where f is the vector of distribution function ($f_{q}$), $M$ is the transformation matrix, and $m$ is the moment vector. Therefore,

$$
\Omega = - S ( m - m^{eq} )
$$

where $S$ is the diagonal matrix whose components are the relaxation rates for each moment. The streaming process is conducted for $f_{q}$; that is, 

$$
\mathbf{f}(t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q} (t, \mathbf{x}) - M^{-1} m^{*}
$$

where $m^{*}$ denotes the post-collision moment. 

The non-orthogonal (raw) moments of orders $(\alpha, \beta, \gamma)$ in each direction are defined by 

$$
m_{\alpha \beta \gamma} = \sum_{q=0}^{Q-1} c_{qx}^{\alpha} c_{qy}^{\beta} c_{qz}^{\gamma} f_{q}
$$


#### dDqQ_MRT_drho_kernel

The shifted moment is defined by 

$$
\widetilde{m} = M ( f - w ) = m - M w
$$

where $w$ is the vector of weights, and the non-zero components of $M w$, for example in D2Q9, are $(0,0): 1$, $(2,0), (0,2): 1/3$ and $(2,2): 1/9$. 


### Cumulant

The cumulant collision operator was proposed in [Geier2015], the milestone paper. 

[Geier2015] Martin Geier et al., [Computers and Mathematics with Applications](https://doi.org/10.1016/j.camwa.2015.05.001). 70 (2015) 507–547.

See also [KY2025] which discusses a role of trancated terms in SGS viscosity. 

- Yamamoto, K. 2025. [Physics of Fluids](https://doi.org/10.1063/5.0294087) 37(11): 115148.

Take a glance at [lbmpy tutorial 04](https://pycodegen.pages.i10git.cs.fau.de/lbmpy/notebooks/04_tutorial_cumulant_LBM.html), which is very easy to follow the relationships between the statistics. [Jupyter Notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) was developed based on the cumulant-moment transformation described in `lbmpy`. The moment generating function is defined by 

$$
M( \mathbf{X} ) = \sum_{q} f_{q} \exp ( \mathbf{c} \cdot \mathbf{X} )  
$$

where $\mathbf{X} = (X, Y, Z)$. The (raw) moments are derived from $M$ as 

$$
m_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} M( \mathbf{X} ) \right]_{\mathbf{X}=0}
$$

The central moment is obtained by the shift with the macroscipic fluid velocity $\mathbf{u}$; therefore, 

$$
K ( \mathbf{X} ) = \exp( - \mathbf{X} \cdot \mathbf{u} ) M( \mathbf{X} )
$$

and 

$$
\kappa_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} K( \mathbf{X} ) \right]_{\mathbf{X}=0}
$$

The cumulant generating function is defined by 

$$
C ( \mathbf{X} ) = \log M( \mathbf{X} ) 
$$

and the cumulants are derived by 

$$
c_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} C( \mathbf{X} ) \right]_{\mathbf{X}=0}
$$

However, according to the definition of $K$, we have 

$$
C ( \mathbf{X} ) = \mathbf{X} \cdot \mathbf{u} + \log K( \mathbf{X} )
$$

This relationship gives transformation from $\kappa$ to $c$. For example, 

$$
\begin{aligned}
c_{000} 
&= \left[ \partial_{X}^{0} \partial_{Y}^{0} \partial_{Z}^{0} ( \mathbf{X} \cdot \mathbf{u} ) + \partial_{X}^{0} \partial_{Y}^{0} \partial_{Z}^{0} log K \right]_{\mathbf{X}=0} \\
&= \left[ Xu + Yv + Zw + \log K \right]_{\mathbf{X}=0} \\
&= \log \rho 
\end{aligned}
$$

$$
\begin{aligned}
c_{201} 
&=  \left[ \partial_{X}^{2} \partial_{Y}^{0} \partial_{Z}^{1} ( \mathbf{X} \cdot \mathbf{u} ) + \partial_{X}^{2} \partial_{Y}^{0} \partial_{Z}^{1} ( \log K( \mathbf{X} ) ) \right]_{\mathbf{X}=0} \\
&= \left[ \partial_{X}^{2} ( w ) + \partial_{X}^{2} \partial_{Z}^{1} ( \log K( \mathbf{X} ) ) \right]_{\mathbf{X}=0} \\
&= \left[ \partial_{X}^{2} \partial_{Z}^{1} ( \log K( \mathbf{X} ) ) \right]_{\mathbf{X}=0} \\
&= \left[ \partial_{X}^{2} \left( \frac{1}{K} \partial_{Z} K \right) \right]_{\mathbf{X}=0} \\
&= \left[ \partial_{X} \left( - \frac{1}{K^{2}} \partial_{X} K \partial_{Z} K + \frac{1}{K} \partial_{X} \partial_{Z} K \right) \right]_{\mathbf{X}=0} \\ 
&= \left[ \frac{2}{K^{3}} (\partial_{X} K)^{2} \partial_{Z} K - \frac{1}{K^{2}} \partial_{X}^{2} K \partial_{Z} K - \frac{1}{K^{2}} ( \partial_{X} K ) \partial_{X} \partial_{Z} K - \frac{1}{K^{2}} ( \partial_{X} K ) \partial_{X} \partial_{Z} K + \frac{1}{K} \partial_{X}^{2} \partial_{Z} K \right]_{\mathbf{X}=0} 
\end{aligned}
$$

Therefore, 

$$
c_{201} = \frac{2 \kappa_{100}^2 \kappa_{001}}{\rho^3} - \frac{\kappa_{200} \kappa_{001}}{\rho^2} - \frac{2\kappa_{100} \kappa_{101}}{\rho^2} + \frac{\kappa_{201}}{\rho}
$$

However, $\kappa_{100} = \kappa_{001} = 0$; thus, 

$$
C_{201} = \rho c_{201} = \kappa_{201}
$$

The forth and higher are different. Use [notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) to confirm transformation results. 


The implementation of the cumulant collision process here is as follows: 
- Forward transformation from $f$ to $m$ (When $\widetilde{f}$ is used, the moment shift is applied here ($m \rightarrow \widetilde{m}$))
- Forward transformation from $m$ to $\kappa$
- Forward transformation from $\kappa$ to $C$
- Collision in cumulant space ($C \rightarrow C^{*}$)
- Backward transformation from $C^{*}$ to $\kappa^{*}$
- Backward transformation from $\kappa^{*}$ to $m^{*}$ (the moment shift is applied ($\widetilde{m}^{*} \rightarrow m^{*}$))
- Backward transformation from $m^{*}$ to $f^{*}$ 

Here, $\kappa$ is the central moment defined by

$$
\kappa_{\alpha \beta \gamma} = \sum_{q}^{Q-1} (c_{qx}-u_{x})^{\alpha} (c_{qy}-u_{y})^{\beta} (c_{qz}-u_{z})^{\gamma} f_{q}
$$


The chimera-fast moment transformation is given by [Geier2015]

$$
m_{ij|\gamma} = \sum_{k=-1,0,1} k^{\gamma} f_{ijk} \rightarrow
m_{i|\beta \gamma} = \sum_{j=-1,0,1} j^{\beta} m_{ij|\beta} \rightarrow
m_{\alpha \beta \gamma}  = \sum_{i=-1,0,1} i^{\alpha} m_{i|\beta \gamma}
$$

It should be noted that this equation suppose the condition $0! = 1$. 

By definition, $\kappa$ can be derived from $m$, e.g., 

$$
\kappa_{110} = m_{110} - \rho u v
$$

The cumulants ($times \rho$) are the same as $\kappa$ up to the third order. For the higher orders, those cumulants are dervied from lower order $\kappa$. 

The fast-backward transformation from $\kappa^{*}$ to $m^{*}$ is given by

$$
m^{*}_{ij|\gamma} = \sum_{k=0}^{\gamma} \left(\begin{array}{c}
        \gamma \\
        k 
    \end{array} \right) w^{\gamma-k} \kappa^{*}_{ijk}
\rightarrow m^{*}_{i|\beta \gamma} = \sum_{j=0}^{\beta} \left(\begin{array}{c}
        \beta \\
        j 
    \end{array} \right)  v^{\beta-j} m^{*}_{ij|\gamma} \\
\rightarrow m^{*}_{\alpha \beta \gamma}  = \sum_{i=0}^{\alpha} \left(\begin{array}{c}
        \alpha \\
        i 
    \end{array} \right) u^{\alpha-k} m^{*}_{i|\beta \gamma} 
$$

where 

$$
    \left(\begin{array}{c}
        \alpha \\
        i 
    \end{array} \right)
    = \frac{\alpha!}{i! (\alpha - i)!}
$$

The fast-backward transformation from $m^{*} to f^{*}$ is given by (Eq. (B.89)-(B.97) in [Geier2015])

$$
f_{ i j 0}^{*} =   m_{ij|0}^{*} - m_{ij|2} ^{*}
\rightarrow f_{ i j-1}^{*} = \frac{ -m_{ij|1}^{*} + m_{ij|2}^{*} }{2}  
\rightarrow f_{ i j 1}^{*} = \frac{  m_{ij|1}^{*} + m_{ij|2}^{*} }{2} 
$$

## Relaxation parameters 

### BGK

- `omega[1]` for $\omega$

### TRT

- `omega[1]` and `omega[2]` for $\omega_{+}$ and $omega_{-}$

The value of $\omega_{-}$ will be initially set to one if you do not specify the value. 

### MRT

In 2D, 

- `omega[1]` for shear $\omega_{1}$
- `omega[2]` for bulk viscosity $\omega_{2}$
- `omega[3]` for third order moments $\omega_{3}$
- `omega[6]` for fourth order moments $\omega_{6}$

In 3D, in addition to the 2D case, 

- `omega[4]` for $m_{120} - m_{102}$...
- `omega[5]` for $m_{111}$
- `omega[7]` for fourth order moments like $m_{220}$
- `omega[8]` for fourth order moments like $m_{211}$
- `omega[9]` for fifth order moments
- `omega[10]` for sixth order moments

The values of $\omega$ except $\omega_{1}$ will be initially set to one if you do not specify the value. 

### Cumulant

- Similar to those in MRT

The values of $\omega$ except $\omega_{1}$ will be initially set to one if you do not specify the value. 


## Boundary condition

The boundary condition implemented here is the same as in [LBM_Taichi](https://github.com/hietwll/LBM_Taichi), that is, Guo's extrapolation method (`lb_utils/bc_kernel.py`): 

$$
f_{bc} = f_{bc}^{eq} + f_{neighbor} - f_{neibor}^{eq}
$$

where $f_{bc}^{eq}$ is calculated for the boundary values of the macroscopic variables. 

```python
        f_post[x_bc] = config.f_eq(lbm, x_bc) + f_post[x_nb] - config.f_eq(lbm, x_nb) 
```


The bounce-back boundary condition is also available in `lb_utils/bback_kernel.py`. 

$$
f_{\bar{i}} = f_{i} + 2 \frac{w_{i}}{c_{s}^{2}} \mathbf{c}_{i} \cdot \mathbf{u}_{bc} 
$$

where $\bar{i}$ is the direction opposite to {i} and $\mathbf{u}_{bc}$ is the velocity of boundary. See `generator/generator_utils/helper_bounceback.py` for `sympy` construction of bounce-back code. 

The former and latter bcs are compatible with pull and push streaming scheme, respectively. Different combination may cause numerical oscillations. 


[!MEMO] The current code sweep all mask nodes, thereby deteriorating the overall speed of simulation when the masked region is large. Possible remedies:

- Skip masked nodes surrounding other masked nodes.
- Taichi SNode (Unfortunately, Metal not supported)



[Guo2002] Guo et al. 2002. [Physics of Fluids](https://doi.org/10.1063/1.1471914) 14(6): 2007–10.

[CW2022] Cheng and Wachs. 2022. [Journal of Computational](https://doi.org/10.1016/j.jcp.2022.111669) Physics 471: 111669.

