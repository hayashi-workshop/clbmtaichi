# Collision-streaming kernel

## Static

The kernel files in [`lb_solver/`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/):

|                               | Model    | Dimension | Velocity | Mode          |  
| ----------------------------- | -------- | --------- | -------- | ------------- |
| d2q9_BGK_drho_kernel.py       | BGK      | 2         | 9        | $\delta \rho$ | 
| d2q9_BGK_kernel.py            | BGK      | 2         | 9        |               |
| d2q9_TRT_drho_kernel.py       | TRT      | 2         | 9        | $\delta \rho$ | 
| d2q9_TRT_kernel.py            | TRT      | 2         | 9        |               |
| d2q9_MRT_drho_kernel.py       | MRT      | 2         | 9        | $\delta \rho$ | 
| d2q9_MRT_kernel.py            | MRT      | 2         | 9        |               |
| d2q9_Cumulant_drho_kernel.py  | Cumulant | 2         | 9        | $\delta \rho$ |
| d2q9_Cumulant_kernel.py       | Cumulant | 2         | 9        |               |
| d3q27_BGK_drho_kernel.py      | BGK      | 3         | 27       | $\delta \rho$ | 
| d3q27_BGK_kernel.py           | BGK      | 3         | 27       |               |
| d3q27_TRT_drho_kernel.py      | TRT      | 3         | 27       | $\delta \rho$ | 
| d3q27_TRT_kernel.py           | TRT      | 3         | 27       |               |
| d3q27_MRT_drho_kernel.py      | MRT      | 3         | 27       | $\delta \rho$ | 
| d3q27_MRT_kernel.py           | MRT      | 3         | 27       |               |
| d3q27_Cumulant_drho_kernel.py | Cumulant | 3         | 27       | $\delta \rho$ | 
| d3q27_Cumulant_kernel.py      | Cumulant | 3         | 27       |               |


## On-demand

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/kernel_sample.py
less examples/generated_kernel.py
```

The collision process can be confirmed in the console message when `run_generator()` is run with `silient=False`. Run the following commend: 

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/kernel_sample.py > examples/mrt_algorith.txt
less examples/mrt_algorithm.txt
```

This sample shows the derivation of MRT collision kernel:

```
# distributions: 
 [f0, f1, f2, f3, f4, f5, f6, f7, f8]

# orders of moments: 
 [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (2, 1), (1, 2), (2, 2)]
feq4th0 = 4*rho*(-3*u**2/2 - 3*v**2/2 + 1)/9
...
M = Matrix([[1, 1, 1, 1, 1, 1, 1, 1, 1],
M_inv = Matrix([[1, 0, 0, -1, 0, -1, 0, 0, 1], 
m00 = rho
m10 = rho*u
...
(0, 0) = m00
(1, 0) = m10
...
f0 = m00_post - m02_post - m20_post + m22_post
f1 = m10_post/2 - m12_post/2 + m20_post/2 - m22_post/2
```

- The discrete set of $f$ is first displayed. Then, 
- The corresponding orders of moments, like $m_{00}$
- The equilibrium distributions for computing equilibrium moments.
- The transformation matrix $M$ and its inverse $M^{-1}$.
- The equilibrium moments, $m^{eq}_{00}$.
- The post-collision moments
- The post-collision distributions as function of the moments (backward transformation)


Change the settings in `kernel_sample.py` to check the other models and dimensions. For example, 

```python
# kernel_sample.py

from generator.cumulant_generator import run_generator

collision_model = "TRT"
dimension       = 3
omega           = [1.8, 1.1]

run_generator(collision_model=collision_model, dimension=dimension, omega_config_input=omega, output_filename="examples/generated_kernel.py", target_directory="./")
```

Then, 

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/kernel_sample.py > examples/trt_algorith.txt
less examples/trt_algorithm.txt
```


## Static
[!NOTE] Running the following script with `gen` (generate mode) will rewrite the static kernel files in `lb_solver/`. 

The following command will generate the collision-streaming kernels:

```bash
cd $REPO_PATH
python main.py gen
less lb_solver/d2q9_BGK_kernel.py
```

This invokes `allrun()` defined in `generator/cumulant_generator.py` for all models available with the generator. 



## JIT: simplify collision eqs with given relaxation rates

`lb_solver/generated_kernel.py`


save the equations constructed in the generator by running the generator with `silent=False`


The values of the relaxation parameters $\omega_{i}$ are *embedded* in the collision equations; it may look like, for $\omega_{5} = 1.02$, 

```python
            kappa111_post = -0.02*kappa111
```

This is 

```
            kappa111_post = -kappa111*lbm.omega[5] + kappa111
```

in `d3q27_Cumulant_kernel.py`. In the cumulant collision process, high order cumulants have the form of $C^{*} = (1 - \omega) C$. Therefore, if you choose $\omega = 1$ for cumulants of those orders, the code gerator gives simply $C^{*} = 0$.



## Hashed equations: Sympy CSE 

The above example generates `examples/generated_kernel.py`. The first part may look like

```python
            # 1) Forward transformation from f to raw moment
            x0 = f5 + f8
            x1 = f6 + f7 + x0
            x2 = f1 + f3 + x1
            x3 = f2 + f4
            x4 = -f6
            x5 = -f7
            x6 = x0 + x4 + x5
            x7 = f5 - f8
            x8 = f6 + x5 + x7
            m00 = f0 + x2 + x3
            m10 = f1 - f3 + x6
            m01 = f2 - f4 + x8
            m20 = x2
            m11 = f7 + x4 + x7
            m02 = x1 + x3
            m21 = x8
            m12 = x6
            m22 = x1
```

This is the forward transformation from $f$ to $m$, e.g,  

$$
m_{00} = f_{0} + f_{1} + f_{2} + f_{3} + f_{4} + f_{5} + f_{6} + f_{7} + f_{8}
$$

The generated code looks different from this equation. However, by substituting `x1` and `x2` into `m00 = f0 + x2 + x3` recovers the definition. The benefit of this hashed representation becomes clear when checking the simplicity of the following moments, e.g., `m20 = x2`: the combination of `f` for `x2` is used not only for `m00` but also for `m20`.  
