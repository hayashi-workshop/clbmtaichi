# BGK

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
The Chapman-Enskog expansion drives that the pressure in LBM is $p = c_{s}^{2} \rho$ which is consistent with the definition of speed of sound $c_{s}^{2} = \left. \partial p / \partial \rho \right|_{s}$ for idela gas.

```


## Equilibrium distribution function

The equilibrium distribution function in LBM is given by 

```{math}
:label: eq:eq_f_eq

f_{i}^{eq} = w_{i} \rho \left( 1 + \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ (\mathbf{u} \cdot \mathbf{u})^{2} }{2 c_{s}^{2}} \right)
```

This is a discrete expression of Maxwelian {cite:p}`Seta2021` and can be [derived from the Hermite generating function](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/common_utils.py#L59) {cite:p}`Kruger2017`

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
vectors = create_vectors(dim=dim)
weights = [calculate_weight(v) for v in vectors]
weights

[4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36]
```




## Density-fluctuation mode

In LBM, the density at $\mathbf{u} = 0$ is scaled as $\rho_{0} = 1$. The density fluctuation is expected to be small in incompressible flows, so that the density fluctuation $\delta \rho = \rho - \rho_{0}$ around $\rho_{0}$ may be small. It is therefore reasonable to shift distribution as 

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

\widetilde{f}_{i}^{eq} = f_{i}^{eq} - w_{i} = w_{i} \left( \delta \rho + \rho \left[ \frac{\mathbf{c} \cdot \mathbf{u}}{c_{s}^{2}} + \frac{( \mathbf{c} \cdot \mathbf{u} )^{2}}{2 c_{s}^{4}} - \frac{ (\mathbf{u} \cdot \mathbf{u})^{2} }{2 c_{s}^{2}} \right] \right)
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
