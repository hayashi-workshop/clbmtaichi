# Boundary condition

The boundary condition implemented here is the same as in [LBM_Taichi](https://github.com/hietwll/LBM_Taichi), that is, Guo's extrapolation method{cite:p}`Guo2002`{cite:p}`Cheng2022` (`lb_utils/bc_kernel.py`): 

```{math}
:label: eq:eq_guo_bc

f_{\text{bc}} = f_{\text{bc}}^{eq} + f_{\text{neighbor}} - f_{\text{neighbor}}^{eq}
```

where $f_{bc}^{eq}$ is calculated for the boundary values of the macroscopic variables. 

```python
        f_post[x_bc] = config.f_eq(lbm, x_bc) + f_post[x_nb] - config.f_eq(lbm, x_nb) 
```

```
# Guo's bc example
# - wet-node (nodes are exactly on wall)
# - with pull streaming
#
#             -suppose f are initially known at all nodes
# @t = step  : (i,j)=(3,1) pulls f5 from (4,0)
#              collision@(3,1) changes f5 > f5*
#              @(4,0), rho and v are specified by BC and compute f^{eq} for those rho and u. 
#                      f*@(4,1) (highlighted as (o)) are known. f^(1) = f - f^{eq} @(4,1) is extrapolated to (4,0) to set 
#                                     f_{\text{bc}} = f_{\text{bc}}^{eq} + f_{\text{neighbor}} - f_{\text{neighbor}}^{eq}
# @t = step+1: (i,j)=(3,1) pulls f5 from (4,0)
#              collision@ ...
#              
# j=2 o - - - - o - - - - o - - - - o - - - - o
#     |         |         |         |         |
#     |         |         |         |         |
#     |         |         |         |         |
#     |         |         |         |         |    
# j=1 o - - - - o - - - -(o)- - - - o - - - - o
#     |         | \       ||        |         |
#     |         |   \     ||f-f^{eq}|         |
#     |         |     \   ||        |         |
#     |         |  f5   \ |v        |         |    
# j=0 o - - - - o - - - -[o]- - - - o - - - - o
#   i=2       i=3       i=4       i=5       i=6...
```


The bounce-back boundary condition is also available in `lb_utils/bback_kernel.py`. 

```{math}
:label: eq:eq_momentum_correction_bc

f_{\bar{i}} = f_{i} + 2 \frac{w_{i}}{c_{s}^{2}} \mathbf{c}_{i} \cdot \mathbf{u}_{bc} 
```

where $\bar{i}$ is the direction opposite to ${i}$ and $\mathbf{u}_{bc}$ is the velocity of boundary. See `generator/generator_utils/helper_bounceback.py` for `sympy` construction of bounce-back code. 

The former and latter bcs are compatible with pull and push streaming scheme, respectively. Different combination may cause numerical oscillations. 


```
# Bounce back example
# - wet-node (nodes are exactly on wall)
# - delayed bounce-back with push streaming
#
# @t = step  : collition f > f* (suppose step % 2 == 0; f_old > f_new)
#              post-collision distribution f_{7}^{*} is pushed from (i,j)=(3,1) to (4,0). this value is stored in f_new(4,0). 
# @t = step+1: collision f > f* (step % 2 == 1, so f_new > f_old)
#              f7*(4,0) stored@(i,j)=(4,0) [in f_new] is pushed back to (3,1). 
#
# j=2 o - - - - o - - - - o - - - - o - - - - o
#     |         |         |         |         |
#     |         |         |         |         |
#     |         |         |         |         |
#     |         |         |         |         |    
# j=1 o - - - - o - - - - o - - - - o - - - - o
#     |         |\ \      |         |         |
#     |         |  \ \f7* |         |         |
#     |         |    \ \  |         |         |
#     |         |  f5* \ \|         |         |    
# j=0 o - - - - o - - - -[o]- - - - o - - - - o
#   i=2       i=3       i=4       i=5       i=6...
```


```{note}
The current code sweep all mask nodes, thereby deteriorating the overall speed of simulation when the masked region is large. Possible remedies:

- Skip masked nodes surrounding other masked nodes.
- If mask is static, store sweep index list. 
- Taichi SNode (Unfortunately, Metal not supported)
```