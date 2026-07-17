# TRT

```{admonition} @github
[`lb_solver/d2q9_TRT_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_TRT_kernel.py)
[`lb_solver/d2q9_TRT_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d2q9_TRT_drho_kernel.py)
[`lb_solver/d3q27_TRT_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_TRT_kernel.py)
[`lb_solver/d3q27_TRT_drho_kernel.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/d3q27_TRT_drho_kernel.py)
```

## Two-relaxation time model

[The two-relaxation time collision model](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L188) {cite:p}`Ginzburg2008` attempts to reduce errors by introducing an additional relaxation rate. The LBE of TRT is similar to that of BGK, while the relaxation is applied in a different manner, that is, 

```{math}
:label: eq:eq_LBE_trt

f_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = f_{i} (t, \mathbf{x}) - \omega^{+} ( f_{i}^{+} - f_{i}^{eq+} ) - \omega^{-} ( f_{i}^{-} - f_{i}^{eq-} )
```

where $\bar{i}$ represents the index of [the direction opposite to $i$](https://github.com/hayashi-workshop/clbmtaichi/blob/c9e6d53609b93901daaef06c0d13dccf0fb81319/generator/cumulant_generator.py#L209). 

```{math}
:label: eq:eq_f_trt

f_{i}^{+} = \frac{f_{i} + f_{\bar{i}}}{2},~~~~f_{i}^{-} = \frac{f_{i} - f_{\bar{i}}}{2}
```

```{seealso}
{cite:p}`Seta2014` Theoretical study on removal of boundary error (velocity slip) using TRT
```

```{admonition} Example with [cumulant_moment_exprs.ipynb](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb)

Find $\bar{i}$ for $i$: 

```python 
opp_map = {} # search opposite (-) direction
for i, v in enumerate(create_vectors(dim=2)):
    opp_v = tuple(-c for c in v) # c -> -c
    opp_map[i] = vectors.index(opp_v) # get index for -c

print(opp_map)
```


## Density-fluctuation mode 

```{math}
:label: eq:eq_LBE_trt_shifted

\widetilde{f}_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = \widetilde{f}_{i} (t, \mathbf{x}) - \omega^{+} ( \widetilde{f}_{i}^{+} - \widetilde{f}_{i}^{eq+} ) - \omega^{-} ( \widetilde{f}_{i}^{-} - \widetilde{f}_{i}^{eq-} )
```

the functional form of which is the same as for the standard $\rho$ mode since the density shift $f_{i} - w_{i}$ for the $i$ and $\bar{i}$ terms cancel out in $f - f^{eq}$ calculation. 


## Stability control 

TRT application example: `cavity2d.py` with Re=38000, where $\omega_{2} = 1.99999$. BGK breaks at this $Re$. However, the improvement is not remarkable, i.e., even with BGK Re=35000 can be stable for the present condition. 

<div style="max-width: 100%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline>
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d_TRT-38000.mp4" type="video/mp4">
  </video>
</div>
