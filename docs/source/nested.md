# Nested grid

```{admonition} @github
[`lb_utils/nested_grid.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_utils/nested_grid.py)
[`lb_utils/nested_utils/`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_utils/nested_utils/)
```

This page introduces the bubble-fucntion{cite:p}`Geier2009` based nested grid implementation. The interpolation code in `clbmtaichi` is generated using `sympy` script `generator/nested_bubble_generator.py`, which is linked from the key equations given below. 

## Grid overlapping and time marching

The distribution functions are exchanged between grids of neighboring levels. The coarse grid fill fine nodes `[+]`, while the fine grid correct the coarse node value `(o)`; see the following ascii art: 

```
# The following ascii art shows a case of
#     o : Coarse (15, 11)
#     + : Fine   (18, 14)
#         Offset ( 3,  2)#
#   One halo line of Fines (+) is required to prevent push streaming in delayed Bounce Back scheme#
# 10o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#  9o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |13 + | + + | + + | + + | + + | + + | + + | + + | + + | +   |     |     |
#  8o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |12 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#   |     |     |11 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#  7o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |10 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 9 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  6o - - o - - o - - o - - o - -(o)- -(o)- -(o)- -(o)- -(o)- - o - - o - - o - - o - - o
#   |     |     | 8 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 7 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  5o - - o - - o - - o - - o - -(o)- - o - - o - - o - -(o)- - o - - o - - o - - o - - o
#   |     |     | 6 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 5 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  4o - - o - - o - - o - - o - -(o)- -(o)- -(o)- -(o)- -(o)- - o - - o - - o - - o - - o
#   |     |     | 4 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#   |     |     | 3 + |[+ +]| + + | + + | + + | + + | + + | + + |[+ +]| +   |     |     |
#  3o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     | 2 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     | 
#   |     |     | 1 + |[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]|[+ +]| +   |     |     |
#  2o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     | 0 + | + + | + + | + + | + + | + + | + + | + + | + + | +   |     |     |
#   |     |     |   0 | 1 2 | 3 4 | 5 6 | 7 8 | 9 10|11 12|13 14|15 16|17   |     |     |
#  1o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#   |     |     |     |     |     |     |     |     |     |     |     |     |     |     |
#  0o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o - - o
#   0     1     2     3     4     5     6     7     8     9     10    11    12    13    14
```

The coase grid proceeds onece, the fince grid proceeds twice, and then the coarse-fine interpolation is conducted. The algorithm is as follows: 

```
#   Level 0: proceed dt_{Coarse} x 1
#   - Collision (1)
#   - Push (streaming) (1)
#   - Boundary condition (1)
#     ---> Call Level 1
#          Level 1: proceed dt_{Fine} x 2 (= dt_{Coarse})
#        - Collision (1)
#        - Push (streaming) (1)
#        - [Boundary condition (1)] <- (can be skipped)
#        - Collision (2)
#        - Push (streaming) (2)
#        - [Boundary condition (2)] <- (can be skipped)
#     <--- Back to Level 0
#   - interpolation between neighboring level grids (0 <-> 1)
```

## Interpolation function

### 2D case 

Four `o` nodes reconstruct the profiles of the macroscopic variables and cumulants within the nodes, and then $f$ of four `[+]` surrounded by the `o`s are updated by making use of the reconstructed profiles. Four `+` reconstruct the profiles of the variables, and then $f$ of one `(o)` are updated. 

The velocity componensts and density are interpolated using the following [quadratic functions](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L379) {cite:p}`Geier2009``Geier2025`: 

```{math}
:label: eq:eq_nested_interpolation2d

\begin{aligned}
&u = a_{0} + a_{x} x + a_{y} y + a_{xy} x y + a_{x2} x^{2} + a_{y2} y^{2} \\
&v = b_{0} + b_{x} x + b_{y} y + b_{xy} x y + b_{x2} x^{2} + b_{y2} y^{2} \\
&\rho = d_{0} + d_{x} x + d_{y} y + d_{xy} x y + ( x^{2} + y^{2} ) d_{\Delta}
\end{aligned}
```

The profile reconstruction is carried out for a square of the size $1 \times 1$, and the coordinates of each vertices (nodes) are `(-1/2, -1/2)`, `(1/2, -1/2)`, `(1/2, 1/2)` and `(-1/2, 1/2)` (`mm`, `pm`, `pp`, `mp` in the code). 

The density has five coefficients while we have only four `o`/`+` nodes for interpolation. {cite:p}`Geier2025` proposed using the approximated Navier-Stokes equation to close the set of equations: 

```{math}
:label: eq:eq_laplace_p
\nabla^{2} p = - \nabla \cdot \left( \rho \mathbf{u} \cdot \nabla \mathbf{u} \right)
```

Since $p = \rho c_{s}^{2}$, 

```{math}
:label: eq:eq_laplace_rho
\nabla \rho = - c_{s}^{-2} \nabla \cdot \left( \mathbf{u} \cdot \nabla \mathbf{u} \right)
```

where the density on the right-hand side was appriximated as $\rho \sim \rho_{0} = 1$. The left-hand side is 

```{math}
:label: eq:eq_laplace_rho_dD
\begin{aligned}
\partial^{2} \rho / \partial x^{2} + \partial^{2} \rho / \partial y^{2} = 4 d_{\Delta}
\end{aligned}
```

Thus, $d_{\Delta}$ is given as [a function of the interpolation coefficients for velocity](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L458). The divergence of the advection term is evaluated by differentiating the velocity interpolation equations at $(x, y) = (0, 0)$. Therefore, the interpolation coefficients on the right-hand side are known by reconstructing the velocity first. 

The two velocity componens have 12 coefficients in total. The number of [constraints by the velocity values at four vertices](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L429) is however eight. Therefore, we need four additional conditions to close the set of equations. As {cite:p}`Geier2009` proposed, this can be done with the compact $2 \times 2$ stencial (bubble?) by making use of the moments at each vertices. 

The perturbation moment 

```{math}
:label: eq:eq_PI1_definition
\Pi_{\alpha \beta}^{(1)} = \sum_{i} c_{i\alpha} c_{i\beta} f_{i}^{(1)}
```

is given by 

```{math}
:label: eq:eq_PI1_stress
\Pi_{\alpha \beta}^{(1)} \sim - \frac{\rho c_{s}^{2}}{\omega} \left( \partial^{(1)}_{\beta} u_{\alpha} + \partial^{(1)}_{\alpha} u_{\beta} \right)
```

See Eq. (4.15) in {cite:p}`Kruger2017`. Since $f_{i}^{(1)} \sim f_{i} - f_{i}^{eq}$, 

```{math}
:label: eq:eq_PI1_moment
\Pi_{\alpha \beta}^{(1)} \sim m_{\alpha \beta} - m_{\alpha \beta}^{eq}
```

Note that, for example, 

```{math}
:label: eq:eq_k_m_c
\kappa_{20} = m_{20} - \frac{u^{2}}{\rho} = \rho c_{20}
```

```{math}
:label: eq:eq_PI1_mm
\frac{\Pi_{\alpha \beta}^{(1)}}{\rho} \sim \frac{m_{\alpha \beta} - m_{\alpha \beta}^{eq}}{\rho}
```

is equivalent to an approximation of the non-equilibrium component of cumulant $c_{20}$, so we write it as $c_{20}^{\text{neq}}$. We use the following set for 2D bubble function: 

```{math}
:label: eq:eq_cumulant_PI
\begin{aligned}
&c_{11}^{\text{neq}} = - \frac{c_{s}^{2}}{\omega} \left( \partial_{x} v + \partial_{y} u \right) \\
&c_{20}^{\text{neq}} - c_{02}^{\text{neq}} = - \frac{2 c_{s}^{2}}{\omega} \left( \partial_{x} u - \partial_{y} v \right) \\
\end{aligned}
```

By differentiating these equation with respect to $x$ and $y$, we obtain the following [four equations](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L489):

```{math}
:label: eq:eq_diff_cumulant_2d

\begin{aligned}
&\partial_{x} c_{11}^{\text{neq}} = - \frac{c_{s}^{2}}{\omega} \left( \partial_{x} \partial_{x} v + \partial_{x} \partial_{y} u \right) \\
&\partial_{y} c_{11}^{\text{neq}} = - \frac{c_{s}^{2}}{\omega} \left( \partial_{y} \partial_{x} v + \partial_{y} \partial_{y} u \right) \\
&\partial_{x} ( c_{20}^{\text{neq}} - c_{02}^{\text{neq}} ) = - \frac{2 c_{s}^{2}}{\omega} \left( \partial_{x} \partial_{x} u - \partial_{x} \partial_{y} v \right) \\
&\partial_{y} ( c_{20}^{\text{neq}} - c_{02}^{\text{neq}} ) = - \frac{2 c_{s}^{2}}{\omega} \left( \partial_{y} \partial_{x} u - \partial_{y} \partial_{y} v \right) \\
\end{aligned}
```

The derivatives of the velocity components are computed by differentiating the interpolation functions. Since the interpolation functions are quadratic, differentiating twice eliminates $x$ and $y$ on the right-hand side; only velocity coefficients remain. Therefore, [by computing the cumulants at the vertices from $f$](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L222), the equations are for the velocity foefficients and close the set of equations to determin 12 velocity coefficients. 

For [the fine-to-coarse interpolation](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L782), the target coarse node is located at $(x,y) = (0,0)$, so that 

```{math}
:label: eq:eq_bubble_function_FtoC_2d

\begin{aligned}
&u = a_{0} \\
&v = b_{0} \\
&\rho = d_{0} \\
&c_{11} = -\frac{1}{3 \omega_{C}} (a_{y} + b_{x}) J_{C} \\
&c_{20} = -\frac{2}{3 \omega_{C}} a_{x} J_{C} + \frac{1}{3} \\
&c_{02} = -\frac{2}{3 \omega_{C}} b_{y} J_{C} + \frac{1}{3} \\
\end{aligned}
```

where $J_{C}$ is the one-dimensional Jacobian

```{math}
:label: eq:eq_Jacobian_C

J_{C} = \frac{\partial x_{C}}{\partial x_{F}} = 2
```

which scales the velocity gradient computed at the fine grid to that at the coase grid. It should be noted that the cumulants here are not $\text{neq}$; the raw cumulants, and $1/3$ is the cumulant in equilibirum. 

[The coarse-to-fine interpolation](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L807) is conducted for four fine nodes, `(x, y) = (-1/4, -1/4)`, `(1/4, -1/4)`, `(1/4, 1/4)` and `(-1/4, 1/4)` with the local coodinates. The scaling factor for the velocity gradient in this case is 

```{math}
:label: eq:eq_Jacobian_F

J_{F} = \frac{\partial x_{F}}{\partial x_{C}} = \frac{1}{2}
```

[The backward transformation](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L708) from $c \rightarrow \kappa \rightarrow m \rightarrow f$ completes the procedure. 


### 3D case

```{note}
the implementation of auxiliary equations with cumulants has not been confirmed whether it is the same as in {cite:p}`Geier2025` or not. Is there any reference for the concrete expressions for the cumulant equations for 3D?
```

3D cases requires a modification in the cumulant reconstruction step since the number of constraints lacking in the system is different from the 2D case. The interpolation is also qudratic: 

```{math}
:label: eq:eq_nested_interpolation3d

\begin{aligned}
&u = a_{0} + a_{x} x + a_{y} y + a_{xy} x y + a_{x2} x^{2} + a_{y2} y^{2} + a_{z} z + a_{xz} x z + a_{yz} y z + a_{xyz} x yz + a_{z2} z^{2} \\
&v = b_{0} + b_{x} x + b_{y} y + b_{xy} x y + b_{x2} x^{2} + b_{y2} y^{2} + b_{z} z + b_{xz} x z + b_{yz} y z + b_{xyz} x yz + b_{z2} z^{2} \\
&w = c_{0} + c_{x} x + c_{y} y + c_{xy} x y + c_{x2} x^{2} + c_{y2} y^{2} + c_{z} z + c_{xz} x z + c_{yz} y z + c_{xyz} x yz + c_{z2} z^{2} \\
&\rho = d_{0} + d_{x} x + d_{y} y + d_{xy} x y + d_{x2} x^{2} + d_{y2} y^{2} + d_{z} z + d_{xz} x z + d_{yz} y z + d_{xyz} x y z + d_{z2} z^{2} \\
\end{aligned}
```

The number of coefficients in each expression is 11. We have eight constraints at the eight vertices for each (`mmm`, `pmm`, ...). Being similar to the 2D case, we set $d_{\Delta} = d_{x2} = d_{y2} = d_{z2}$ to reduce the unkowns in the density expression ($-2$). The lapalacian of $\rho$ derived from the approximate Navier-Stoke eq. is also used as auxilirary condition. Thus, the set of equations for the nine $\rho$-interpolation coefficients is closed, provided that the velocity interpolation coefficients are given. 

For the three velocity components, we have to determine $11 \times 3 = 33$ coefficients, but the constraints give by the vertex values are only $8 \times 3 = 24$. Therefore, we need [$9$ auxiliary conditions](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L519) to close the system. We employ $c_{110}, c_{101}, c_{011}$ for six equations, and $2 c_{200} - c_{020} - c_{002}, c_{020} - c_{002}$ for three equations, that is, 

```{math}
:label: eq:eq_diff_cumulant_3d

&\partial_{x} c_{110}^{\text{neq}},~\partial_{y} c_{110}^{\text{neq}} \\
&\partial_{x} c_{101}^{\text{neq}},~\partial_{z} c_{101}^{\text{neq}} \\
&\partial_{y} c_{011}^{\text{neq}},~\partial_{z} c_{011}^{\text{neq}} \\
&\partial_{x} ( 2 c_{200}^{\text{neq}} - c_{020}^{\text{neq}} - c_{002}^{\text{neq}} ) \\
&\partial_{y} ( c_{020}^{\text{neq}} - c_{002}^{\text{neq}} ) \\
&\partial_{z} ( c_{002}^{\text{neq}} - c_{020}^{\text{neq}} ) \\
```

In the actual implementation, we use $c_{200}^{\text{neq}} - c_{020}^{\text{neq}}$ and $c_{200}^{\text{neq}} - c_{002}^{\text{neq}}$ to express the latter three. 

```{admonition}{need help}
Inspired by Eqs. (55)-(57) ($C_{110}$ relaxed single) and (61) and (62) ($C_{200} - C_{020}$ and $C_{200} - C_{002}$ are combined to express deviation). However, $2 c_{200} - c_{020} - c_{002}$ does not. The present implementation seems bit lacking for symmetry. Any reference for 3D case? 
```

Solving the set of equations we obtain the velocity components and the second-order cumulants $c_{110}, c_{101}, c_{011}, c_{200}, c_{020}, c_{002}$. The cumulants of orders higher than 2 are assumed to be in equilibrium, meaning [that they are 0](https://github.com/hayashi-workshop/clbmtaichi/blob/002a5a6bb09900f84165c1ae5f0f06808e2adbff/generator/nested_bubble_generator.py#L689). 


```{seealso}
Another compact reconstruction strategy can be found in {cite:p}`Qi2019`. 
```

## Relaxation rates

The relaxation rates of the grids are in the following relationship: 

```{math}
:label: eq:eq_omega_F

\omega_{F} = \left[ \frac{2}{\omega_{C}} - \frac{1}{2} \right]^{-1}
```

which assures the same viscosity at the two levels

```{math}
:label: eq:eq_nested_acoustic_scaling
\nu = \frac{1}{3} \left( \frac{1}{\omega_{C}} - \frac{1}{2} \right) \frac{\Delta x_{C}^{2}}{\Delta t_{C}} = \frac{1}{3} \left( \frac{1}{\omega_{F}} - \frac{1}{2} \right) \frac{\Delta x_{F}^{2}}{\Delta t_{F}}
```

with the acoustic scaling $\Delta x_{C} / \Delta t_{C} = \Delta x_{F} / \Delta t_{F}$. 
