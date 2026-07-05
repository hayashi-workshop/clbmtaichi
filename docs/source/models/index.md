# LB models

```{admonition} @github
[`lb_solver/lbm_lib.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/lbm_lib.py)
```

## Lattice Boltzmann equation
Lattice Boltzmann solvers are based on the following lattice Boltzmann equation: 

```{math}
:label: eq:eq_LBE

f_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = f_{i} ( t, \mathbf{x} ) + \Omega(f)
```

where $\Delta x = \Delta t = 1$ in lattice unit, and the lattice speed is defined by $c = \Delta x / \Delta t = 1$. The algorithm of LBM consists of the streaming and collision steps and is much simpler than Navier-Stokes based solvers. A variety of the LB models comes from the treatment of the collision operator $\Omega (f)$. [`clbmtaichi`](https://github.com/hayashi-workshop/clbmtaichi/) provides implementation examples of BGK, TRT, MRT and cumulants. 


```{toctree}
:maxdepth: 1

velocity
streaming
bgk
trt
mrt
cumulant
omega
bc
```


```{seealso}
For cumulants and moments, see also [Jupynoter Notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) provided in `generator` directory. 
```

```{seealso}
{cite:p}`Kruger2017` is a comprehensive reference from fundamentals of physics, math and numerics to practice covering `cuda` coding. Readers, those who are new for LBM, {cite:p}`Seta2021` is highly recommended, but Japanese language edition only! 
```