# Streaming step

```{admonition} @github : see fetch and write steps of $f$ in kernel files
[`lb_solver/`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/)
```

## Operator splitting

The collision and streaming are split as 

```{math}
:label: eq:eq_LBE_collision

\begin{aligned}
&f_{q}^{*} ( t, \mathbf{x} ) = f_{q} ( t, \mathbf{x} ) + \Omega (f) \\
&f_{q}^{*} (t + \Delta t, \mathbf{x} + \mathbf{c}_{q} \Delta t) = f_{q}^{*} ( t, \mathbf{x} ) 
\end{aligned}
```

The $*$ decoration denotes the post-collision distribution. 


## Pull/Push scheme

```{important}
The pull (push) scheme should be used with Guo's (bounce-back) boundary condition. These boundary conditions are defined, respectively, in  

- `lb_utils/bc_kernel.py` (Guo's bc)
- `lb_utils/bback_kernel.py` ((delayed) bounce-back)
```

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
