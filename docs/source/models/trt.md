# TRT

## Two-relaxation time model

[The two-relaxation time collision model](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L188) {cite:p}`Ginzburg2008` attempts to reduce errors by introducing an additional relaxation rate. The LBE of TRT is similar to that of BGK, while the relaxation is applied in a different manner, that is, 

```{math}
:label: eq:eq_LBE_trt

f_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = f_{i} (t, \mathbf{x}) - \omega^{+} ( f_{i}^{+} - f_{i}^{eq+} ) - \omega^{-} ( f_{i}^{-} - f_{i}^{eq-} )
```

where $\bar{i}$ represents the index of the direction opposite to $i$. 

```{math}
:label: eq:eq_f_trt

f_{i}^{+} = \frac{f_{i} + f_{\bar{i}}}{2},~~~~f_{i}^{-} = \frac{f_{i} - f_{\bar{i}}}{2}
```

```{seealso}
{cite:p}`Seta2014` Theoretical study on removal of boundary error (velocity slip) using TRT
```

For density-fluctuation mode, 

```{math}
:label: eq:eq_LBE_trt_shifted

\widetilde{f}_{i} (t + \Delta t, \mathbf{x} + \mathbf{c}_{i} \Delta t) = \widetilde{f}_{i} (t, \mathbf{x}) - \omega^{+} ( \widetilde{f}_{i}^{+} - \widetilde{f}_{i}^{eq+} ) - \omega^{-} ( \widetilde{f}_{i}^{-} - \widetilde{f}_{i}^{eq-} )
```

the functional form of which is the same as for the standard $\rho$ mode since the density shift $f_{i} - w_{i}$ for the $i$ and $\bar{i}$ terms cancel out in $f - f^{eq}$ calculation. 
