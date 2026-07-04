# Boundary condition

The boundary condition implemented here is the same as in [LBM_Taichi](https://github.com/hietwll/LBM_Taichi), that is, Guo's extrapolation method{cite:p}`Guo2002`{cite:p}`Cheng2022` (`lb_utils/bc_kernel.py`): 

```{math}
:label: eq:eq_guo_bc

f_{bc} = f_{bc}^{eq} + f_{neighbor} - f_{neibor}^{eq}
```

where $f_{bc}^{eq}$ is calculated for the boundary values of the macroscopic variables. 

```python
        f_post[x_bc] = config.f_eq(lbm, x_bc) + f_post[x_nb] - config.f_eq(lbm, x_nb) 
```


The bounce-back boundary condition is also available in `lb_utils/bback_kernel.py`. 

```{math}
:label: eq:eq_momentum_correction_bc

f_{\bar{i}} = f_{i} + 2 \frac{w_{i}}{c_{s}^{2}} \mathbf{c}_{i} \cdot \mathbf{u}_{bc} 
```

where $\bar{i}$ is the direction opposite to {i} and $\mathbf{u}_{bc}$ is the velocity of boundary. See `generator/generator_utils/helper_bounceback.py` for `sympy` construction of bounce-back code. 

The former and latter bcs are compatible with pull and push streaming scheme, respectively. Different combination may cause numerical oscillations. 


```{note}
The current code sweep all mask nodes, thereby deteriorating the overall speed of simulation when the masked region is large. Possible remedies:

- Skip masked nodes surrounding other masked nodes.
- If mask is static, store sweep index list. 
- Taichi SNode (Unfortunately, Metal not supported)
```