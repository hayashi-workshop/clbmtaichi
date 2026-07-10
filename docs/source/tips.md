# Coding tips

## New to Taichi? 

Visit [Taichi Lang official](https://www.taichi-lang.org/) to get started! Key decorators are 

- `@ti.kernel`       (like `__global__` in `cuda`)
- `@ti.func`         (like `__device__` in `cuda`)
- `ti.static`        (unroll `if`/`for`)
- `ti.ndrange`       (efficient `for` loop) 
- `ti.grouped`       (efficient `for` loop)
- `ti.data_oriented` (for object-oriented programming with `class`)

If you are new to GPU computing (e.g. CUDA), pay close attention to the descriptions of *Python scope* and *Taichi scope* in `Kernels & Functions` section. 


## SoA (Structure of Array)

The memory layout of the distribution function is [f0[], f0[], ..., f0[] | f1[], f1[], ..., f1[] | ...] (SoA), not [ f0[], f1[], ..., f8[] | f0[], f1[], ..., f8[]] (AoS). The former is the field-based, and the latter is the node-based layout. 

```python
            block_old = ti.root.dense(self.ti_axes, self.nd)
            for q in range(self.Q): 
                block_old.place(self.f_old.get_scalar_field(q))

            block_new = ti.root.dense(self.ti_axes, self.nd)
            for q in range(self.Q): # allocation must be done with another for loop
                block_new.place(self.f_new.get_scalar_field(q))
```


## Pull-type streaming

The distributions are fetched from the neighbor lattice nodes before collision. 

```python
        for I in ti.grouped(lbm.rho):
            # Streaming & Fetch (pull algorithm)
            f0 = f_pre[I - self.c[0]][0]
            f1 = f_pre[I - self.c[1]][1]
            f2 = f_pre[I - self.c[2]][2]
            f3 = f_pre[I - self.c[3]][3]
            f4 = f_pre[I - self.c[4]][4]
            f5 = f_pre[I - self.c[5]][5]
            f6 = f_pre[I - self.c[6]][6]
            f7 = f_pre[I - self.c[7]][7]
            f8 = f_pre[I - self.c[8]][8]
```


## Update macroscopic variables in kernel

The macroscopic variables $\rho$ and $\mathbf{u}$ are computed in the collision kernel. They are used to construct the equilibrium distributions and moments. Then, the field values are updated with the computed values, by which there is no need to launch another kernel to update the macros only (launching kernels are costly!). It should be noted that $\rho$ and $\rho \mathbf{u}$ are conservative quantities, so that their values do no change during the collision process; justfying the algorithm.

```python
        for I in ti.grouped(lbm.rho):
            ...

            # CSE expressions of macroscopic variables and f_eq
            x0 = f1 + f8
            x1 = f2 + f6
            x2 = f0 + f3 + f4 + f5 + f7 + x0 + x1
            x3 = 1/x2
            x4 = f5 - f7
            x5 = -f3 - f6 + x0 + x4
            x6 = x3*x5
            x7 = -f4 - f8 + x1 + x4
            x8 = x3*x7
            ...

            lbm.rho[I] = x2 # <- note: actual value stored here is rho - density_shift
            lbm.vel[I][0] = x6
            lbm.vel[I][1] = x8
```


## Pseudo distribution variable swapping

The speed of a LB simulation is mainly dominated by memory access. Launching kernels and fetching/writing $f$ (27 $f$s in 3D!) should be minimized to prevant deterioration of computation speed. After the collision, the pre-collision distribution is fetched from $f_{pre}$, and the post-collision distribution is stored into $f_{post}$. By switching the roles of the arrays for these fields step by step, a data copy between them as preparation for the next time step is not required. 

```python
    def swap(self, step):
        f_post = self.f_new if step % 2 == 0 else self.f_old
        f_pre  = self.f_old if step % 2 == 0 else self.f_new
        return f_pre, f_post
```

In C++, the pointer swap may be the easiest way to implement the procedure. 


## Index polymorphism

The node index is (i,j) and (i,j,k) in 2D and 3D. The data access is therefore like this: self.rho[i,j] in 2D, but self.rho[i,j,k] in 3D. In order to make the code flexible for both dimensions, hard-coding of the indexes is not efficient. Taichi-lang allows `self.rho[I]` with tuple `I` of indixes and the kernel loop can be written for `I` using `ti.grouped`, with which `i,j,k` is hindered and codes can be the same for both dimensions. 

```python
    @ti.kernel
    def col_stream_core(self, lbm: ti.template(), f_pre: ti.template(), f_post: ti.template()):
        ...
        for I in ti.grouped(lbm.rho):
            ...

            self.rho[I] = rho

            # this is equivalent to self.rho[i,j]   = rho in 2D
            #                    to self.rho[i,j,k] = rho in 3D
            # each index can be accessed as i = I[0], j = I[1], k = I[2]
```



