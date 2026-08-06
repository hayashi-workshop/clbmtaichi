# Relaxation rates

```{seealso} 
[`lb_solver/lbm_lib.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_solver/lbm_lib.py)
```

## BGK

- `omega[1]` for $\omega$

## TRT

- `omega[1]` and `omega[2]` for $\omega_{+}$ and $\omega_{-}$

The value of $\omega_{-}$ will be initially set to one if you do not specify the value. 

## MRT

In 2D, 

- `omega[1]` for shear $\omega_{1}$
- `omega[2]` for bulk viscosity $\omega_{2}$
- `omega[3]` for third order moments $\omega_{3}$
- `omega[6]` for fourth order moments $\omega_{6}$

In 3D, in addition to the 2D case, 

- `omega[4]` for $m_{120} - m_{102}$...
- `omega[5]` for $m_{111}$
- `omega[7]` for fourth order moments like $m_{220}$
- `omega[8]` for fourth order moments like $m_{211}$
- `omega[9]` for fifth order moments
- `omega[10]` for sixth order moments

The values of $\omega$ except $\omega_{1}$ will be initially set to one if you do not specify the value. 

## Cumulant

- Similar to those in MRT

The values of $\omega$ except $\omega_{1}$ will be initially set to one if you do not specify the value. 
