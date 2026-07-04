# Cumulant

## Generating functions 

The cumulant collision operator was proposed in {cite:p}`Geier2015`, the milestone paper. See also {cite:p}`Yamamoto2025` which discusses a role of trancated terms in SGS viscosity. 

Take a glance at [lbmpy tutorial 04](https://pycodegen.pages.i10git.cs.fau.de/lbmpy/notebooks/04_tutorial_cumulant_LBM.html), which is very easy to follow the relationships between the statistics. [Jupyter Notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) was developed based on the cumulant-moment transformation described in `lbmpy`. [The moment generating function](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/generating_functions.py#L92) is defined by 

```{math}
:label: eq:eq_moment_generating_function

M( \mathbf{X} ) = \sum_{q} f_{q} \exp ( \mathbf{c} \cdot \mathbf{X} )  
```

where $\mathbf{X} = (X, Y, Z)$. The (raw) moments are derived from $M$ as 

```{math}
:label: eq:eq_raw_moment_derived_from_M

m_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} M( \mathbf{X} ) \right]_{\mathbf{X}=0}
```

The central moment is obtained by the shift with the macroscipic fluid velocity $\mathbf{u}$; therefore, 

```{math}
:label: eq:eq_central_moment_generating_function

K ( \mathbf{X} ) = \exp( - \mathbf{X} \cdot \mathbf{u} ) M( \mathbf{X} )
```

and 

```{math}
:label: eq:eq_central_moment_derived_from_K

\kappa_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} K( \mathbf{X} ) \right]_{\mathbf{X}=0}
```

[The cumulant generating function](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/generating_functions.py#L17) is defined by 

```{math}
:label: eq:eq_cumulant_generating_function

C ( \mathbf{X} ) = \log M( \mathbf{X} ) 
```

and the cumulants are derived by 

```{math}
:label: eq:eq_cumulant_derived_from_C

c_{\alpha \beta \gamma} = \left[ \partial_{X}^{\alpha} \partial_{Y}^{\beta} \partial_{Z}^{\gamma} C( \mathbf{X} ) \right]_{\mathbf{X}=0}
```

However, according to the definition of $K$, we have 

```{math}
:label: eq:eq_C_as_function_of_K

C ( \mathbf{X} ) = \mathbf{X} \cdot \mathbf{u} + \log K( \mathbf{X} )
```

[This relationship gives transformation from $\kappa$ to $c$.](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/generating_functions.py#L50) For example, 

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

```{note}
$C_{201}$ is the density scaled cumulant $\rho c_{201}$, not the generating function. 
```

The fourth and higher are different. Use [notebook](https://github.com/hayashi-workshop/clbmtaichi/blob/main/generator/cumulant_moment_exprs.ipynb) to confirm transformation results. 


## Algorithm 

The implementation of the cumulant collision process in `clbmtaichi` is as follows: 
- Forward transformation from $f$ to $m$ (When $\widetilde{f}$ is used, the moment shift is applied here ($m \rightarrow \widetilde{m}$))
- Forward transformation from $m$ to $\kappa$
- Forward transformation from $\kappa$ to $C$
- Collision in cumulant space ($C \rightarrow C^{*}$)
- Backward transformation from $C^{*}$ to $\kappa^{*}$
- Backward transformation from $\kappa^{*}$ to $m^{*}$ (the moment shift is applied ($\widetilde{m}^{*} \rightarrow m^{*}$))
- Backward transformation from $m^{*}$ to $f^{*}$ 

Here, $\kappa$ is the central moment defined by

```{math}
:label: eq:eq_central_moment_definition

\kappa_{\alpha \beta \gamma} = \sum_{i=0}^{Q-1} (c_{ix}-u_{x})^{\alpha} (c_{iy}-u_{y})^{\beta} (c_{iz}-u_{z})^{\gamma} f_{i}
```


[The chimera fast moment transformation](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/cumulant_utils.py#L10) is given by {cite:p}`Geier2015`

```{math}
:label: eq:eq_chimera_transformation_f_m

\begin{aligned}
&m_{ij|\gamma} = \sum_{k=-1,0,1} k^{\gamma} f_{ijk} \\
&m_{i|\beta \gamma} = \sum_{j=-1,0,1} j^{\beta} m_{ij|\beta} \\
&m_{\alpha \beta \gamma}  = \sum_{i=-1,0,1} i^{\alpha} m_{i|\beta \gamma}
\end{aligned}
```

It should be noted that this equation suppose the condition $0! = 1$. By definition (Eq. {eq}`eq:eq_central_moment_definition`), $\kappa$ can be derived from $m$, e.g., 

$$
\kappa_{110} = m_{110} - \rho u v
$$

The cumulants ($\times \rho$) are the same as $\kappa$ up to the third order. For the higher orders, those cumulants are dervied from lower order $\kappa$. [The fast-backward transformation](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/generator_utils/cumulant_utils.py#L226) from $\kappa^{*}$ to $m^{*}$ is given by

```{math}
:label: eq:eq_chimera_transformation_k_m

\begin{aligned}
&m^{*}_{ij|\gamma} = \sum_{k=0}^{\gamma} \left(\begin{array}{c}
        \gamma \\
        k 
    \end{array} \right) w^{\gamma-k} \kappa^{*}_{ijk} \\
&m^{*}_{i|\beta \gamma} = \sum_{j=0}^{\beta} \left(\begin{array}{c}
        \beta \\
        j 
    \end{array} \right)  v^{\beta-j} m^{*}_{ij|\gamma} \\
&m^{*}_{\alpha \beta \gamma}  = \sum_{i=0}^{\alpha} \left(\begin{array}{c}
        \alpha \\
        i 
    \end{array} \right) u^{\alpha-k} m^{*}_{i|\beta \gamma} 
\end{aligned}
```

where 

```{math}
:label: eq:eq_binomial
    \left(\begin{array}{c}
        \alpha \\
        i 
    \end{array} \right)
    = \frac{\alpha!}{i! (\alpha - i)!}
```

The fast-backward transformation from $m^{*}$ to $f^{*}$ is given by Eq. {eq}`eq:eq_chimera_backtransformation_m_f`


## Collision 

[The collision step](https://github.com/hayashi-workshop/clbmtaichi/blob/0f27d15c04fe9697c33d4774e892adc08ce0ca10/generator/cumulant_generator.py#L439) is for the following set of density-scaled cumulants: 

|                                                              | $C^{\text{eq}}$              | $\omega$     |                |
| ------------------------------------------------------------ | ---------------------------- | ------------ | -------------- |
| $C_{000}$                                                    | $\rho \ln \rho$              |              |                | 
| $C_{100}, C_{010}, C_{001}$                                  | $\rho u$, $\rho v$, $\rho w$ |              |                |
| $C_{110}, C_{101}, C_{011}$                                  | $0$, $0$, $0$                | $\omega_{1}$ | shear          |
| $C_{200} - C_{020}$, $C_{200} - C_{002}$                     | $0$, $0$                     | $\omega_{1}$ | shear          | 
| $C_{200} + C_{020} + C_{002}$                                | $\rho$                       | $\omega_{2}$ | trace/pressure |
| $C_{120} + C_{102}$,$C_{210} + C_{012}$,$C_{201} + C_{021}$  | $0$, $0$, $0$                | $\omega_{3}$ |                |
| $C_{120} - C_{102}$,$C_{210} - C_{012}$,$C_{201} - C_{021}$  | $0$, $0$, $0$                | $\omega_{4}$ |                |
| $C_{111}$                                                    | $0$                          | $\omega_{5}$ |                | 
| $C_{220} -2C_{202} + C_{022}$                                | $0$                          | $\omega_{6}$ |                |
| $C_{220} + C_{202} -2C_{022}$                                | $0$                          | $\omega_{6}$ |                |
| $C_{220} + C_{202} + C_{022}$                                | $0$                          | $\omega_{7}$ |                |
| $C_{211}, C_{121}, C_{112}$                                  | $0$, $0$, $0$                | $\omega_{8}$ |                |
| $C_{221}, C_{212}, C_{122}$                                  | $0$, $0$, $0$                | $\omega_{9}$ |                |
| $C_{222}$                                                    | $0$                          | $\omega_{10}$|                | 

```{note}
The implementation here does not include the velocity gradients for high-order error correction {cite:p}`Geier2015`
```