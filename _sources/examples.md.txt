# Examples

```{admonition} @github
[`examples/`](https://github.com/hayashi-workshop/clbmtaichi/tree/main/examples)
```

## Flow past a cylinder

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/object2d.py
```

Use `PYTHONPATH=.` to solve the library paths for examples/*.py launched from root dir. 

<div style="max-width: 100%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/object2d.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/object2d.mp4" type="video/mp4">
  </video>
</div>


## Flow past a sphere

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/object3d.py
```

<div style="max-width: 50%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/object3d.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/object3d.mp4" type="video/mp4">
  </video>
</div>


## Lid-driven catity

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/cavity2d.py
```

<div style="max-width: 50%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d.mp4" type="video/mp4">
  </video>
</div>


```bash
cd $REPO_PATH
PYTHONPATH=. python examples/cavity3d.py
```

## Change domain size

Let us try the standard square cavity flow. Copy the cavity flow example as [`cavity2d_std.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/cavity2d_std.py)

```bash
cp examples/cavity2d.py examples/cavity2d_std.py
```

Open the copied file to change some conditions: 

```bash
nano examples/cavity2d_std.py
```

- Cavity size (201, 201)
- Re=5000
- some rendering conditions to draw velocity magnitude contour
- MRT kernel

```python
nd = (201, 201)
u, Re = 0.01, 5000.0
...

from lb_solver.d2q9_MRT_kernel import ModelConfig
...

renderer = FluidRenderer(lbm, vmin=0., vmax=u*0.5) # Taichi realtime rendering #
...

    renderer.render(lbm, mode="velocity")
```

Save the file; then, 

```bash
PYTHONPATH=. python examples/cavity2d_std.py
```

<div style="max-width: 30%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d_std.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d_std.mp4" type="video/mp4">
  </video>
</div>


## Change boundary condition

```bash
cp examples/cavity2d_std.py examples/cavity2d_std_bc.py
nano examples/cavity2d_std_bc.py
```

Change the following:
- Domain size
- u and Re
- Cumulant $\delta \rho$ mode
- Boundary velocities
- Rendering params `vmin` `vmax`
- Rendering mode: set back to "vorticity".

```python
nd = (301, 301)
u, Re = 0.1, 50000.0
...
from lb_solver.d2q9_Cumulant_drho_kernel import ModelConfig
...
bc_manager = BoundaryManager(nd, [2, 2, 2, 2], [ [0, -u*0.5], [0,u*0.5], [-u,0], [u,0] ])

renderer = FluidRenderer(lbm, vmin=-u*0.5, vmax=u*0.5) # Taichi realtime rendering #

while renderer.window.running and step < step_end:
    for _ in range(500):
    ...
    renderer.render(lbm, mode="vorticity")
```

<img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d_std_bc.png" width=301><img>


## MLUPS monitoring

MLUPS is (total number of lattice units updated per seond)/10^6. `PerformanceMonitor` class in `lb_utils/lbm_utils.py` provides a simple MLUPS measure. As implemented in [`examples/object2d.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/object2d.py), instantiate a class object (`mlups_monitor`) and add one line `mlpus_monitor.update(step)` in the time loop. 

```python
from lb_utils.lbm_utils import PerformanceMonitor
...

mlups_monitor = PerformanceMonitor(nd)
...
while renderer.window.running and step < step_end:
    for _ in range(100):
        ...
        step += 1

    mlups_monitor.update(step)
```


## GPU vs CPU

One of the attractive features of [Taichi](https://www.taichi-lang.org/) is its portability. No need to modify the code to migrate from a gpu to a cpu environment. Apple Silicon M2 used in the code development possesses 8 cpu cores (4 efficient, 4 performance) and 8 gpu cores. `examples/mlups_main.py` compares MLUPS with the M2 gpu and cpu for 100x100x100 (1M lattice) and 256x256x256 (16.8M lattice) cavity flow simulation. 

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/mlups_main.py
```

<div style="max-width: 100%; display: flex; gap: 10px;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups.png" style="max-width: 50%; height: auto; object-fit: contain;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups_256.png" style="max-width: 50%; height: auto; object-fit: contain;">
</div>



## Bumpy channel (trick with cylinders)

[`examples/bumpy.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/bumpy.py) shows a multiple object case. Three cylinders are set on the channel wall to mimic bumpy channel geometry. For this purpose, `ObjectManager` classs is rewritten in `examples/object_bump.py`. 

1201x201; Re=5000; u=0.01, Cumulant ($\delta \rho$ mode)

<div style="max-width: 100%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/bumpy.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/bumpy.mp4" type="video/mp4">
  </video>
</div>

## Using Paraview

`pyevtk` allows you to dump simulation results in `vtk`/`vtr` for Paraview visualiation. Find an example how to dump field data with `pyevtk` in [`main.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/main.py): 

```python
from lb_utils.lbm_utils import save_vtk

...

    while renderer.window.running and step < step_end:
        ...

        if step % output_step and output_flag:
            save_vtk(lbm, step, output_dir)
```


## Irregular shape

### Johansen-Collela

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/JCprob1.py
```

A star-like shape in [JC1998] as embedded solid boundary. See [examples/JCprob1.py](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/JCprob1.py). 

The narrow gaps between the object and the wall causes strong vortical motion, for which the naive outlet boundary treatment can be dangerous and simulations may face a challenge for stability! 

[JC1998] Johansen and Colella. Journal of Computational Physics, 147(1):60–85, 1998.

<div style="max-width: 100%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/JCprob1.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/JCprob1.mp4" type="video/mp4">
  </video>
</div>

### Stanford bunny

[Stanford bunny](https://graphics.stanford.edu/data/3Dscanrep/) in a duct. 

Polygon model@[trimesh repo](https://github.com/mikedh/trimesh) is used to set mask field (see [`examples/obstacle_stanford_bunny.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/obstacle_stanford_bunny.py)). In order to use trimesh, install the following packages to your virtual environment: 

```bash
pip install 'trimesh[easy]'
pip install networkx
```

Then, 

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/stanford_bunny.py
```

(241, 121, 121); length_scale = 60; offset = (50, 0, 30) (corner edige of model bounding box); (u, Re) = (0.1, 40000)

<img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/stanford_bunny_vtk.png" width=600></img>

Here, the isosurfaces represent Q-criterion, $Q = (|\Omega|^2 - |S|^2)/2$. In paraview, 

- Load vtr file
- Apply `Gradient` filter
- Turn on `Compute Q criterion` in the filter panel
- Apply `Contour` filter to the `Gradient` filter


## Extracting isosurfaces

### Marching cube

- MarchingCube class: [`lb_utils/marching_cube.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/lb_utils/marching_cube.py)
- Surface extraction example [`examples/mcube_extra_surface.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/mcube_extract_surface.py)

<img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/extract_surface.png" width=300></img>

Marching cube extracts isosurface as a set of triangles. The cubic cells consisting of the eight LB nodes are scanned to detect edges at which (S - isovalue) changes is sign where $S$ is a given field variable. This is actually done by using a look up table of 256 patterns for the state of the eight nodes (bit info of S - isovalue at eight nodes). Then, the intersection is calculated by linear interpolation. 

This example extracts 10 isosurfaces from a singed distance field of sphere. On-Taichi implementation and on-cpu (serial) implementation are compared to check the validity of the former. 

[!NOTE] `trimesh` is used same as the example above. 

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/mcube_extract_surface.py
```

### Extract Q-criterion isosurfaces using marching cube

Compute and export Q-criterion [`examples/mcube_stanford_bunny.py`](https://github.com/hayashi-workshop/clbmtaichi/blob/main/examples/mcube_stanford_bunny.py)

<video src="https://github.com/user-attachments/assets/7befea58-1075-4156-aa99-1c69275f05b4" width="350" autoplay loop muted playsinline></video>

Frequent export of velocity data may occupy a large disk space. In this example, the marching cube method is used to extract two isosurfaces of Q-criterion to dump the surface (mesh) data rather than velocity volume data. The isosurface extraction is not so slow, but the data transfer from Taichi to Python scope (`to_numpy`) can be the bottole neck. 


## Bounce-back boundary condition

The above examples are all for the combination of pull streaming/Guo's boundary condition. Applications of push streaming with the (delayed) bounce-back scheme can be found in examples named `_bb.py`

`cavity2d_bb.py` with Re=10000000 demonstrates the stability of cumulant lbm. nd=(801, 401) and u=0.1. 
<div style="max-width: 100%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline>
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/cavity2d_bb-10000000_comp.mp4" type="video/mp4">
  </video>
</div>

## Nested grid (tentative)

```{caution}
Only push/bounce-back combination is allowed for the nested grid algorithm implemented. Push is slower than pull. Further study is required. 
```

### 2D nested grids

```bash
cd $REPO_PATH
PYTHONPATH=. python examples/nested.py
```

<div style="max-width: 80%; margin: 1em auto;">
  <video class="responsive-video" controls playsinline poster="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/nested_vtk_poster.png">
    <source src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/nested_vtk.mp4" type="video/mp4">
  </video>
</div>

4 level nested grids surrounding a cylindrical object. Tthe vorticity magnitude is visualized using ParaView. The numbers of nodes are `nd0 = (801, 201)`, `nd1 = (400, 280)`, `nd2 = (440, 320)`, `nd3 = (580, 480)` from level 0 to 3, and the grid boundaries are represented with the white boxes. 20 nodes are adopted to the cylinder raidus at level 0, while 160 nodes at level 3. Communication between grids at different levels is based on the bubble function proposed in {cite:p}`Geier2009`. In 2D, Taichi GGUI is run for level 0; higher level grids inject their values into the canvas at level 0. 



### 3D nested grids

```{danger}
3D simulation with nested grids could be heavy, inducing high memory pressure. Please try a small grid setting (maybe begin with onyl 2 levels) while considering your environment. 
```

<img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/nested3d_vtk.png" width=600></img>

3 levels are used to simulate a flow about a sphere. The domain sizes are `nd0 = (361, 121, 121)`, `nd1 = (240, 160, 160)`, and `nd2 = (300, 220, 220)`: 26M nodes in total. The sphere radius at level 0 is 15, while it is 60 at level 3. 

This example was actually run on A100@Google Colab although M2 can also work. 

[!NOTE] On Macbook Pro M2 16GB, adding the next level `nd3 = (400, 320, 320)` failed with `segmentation fault`. 

Taichi GGUI is currently not supported for 3D nested grid. The result should be dumped via `pyevtk` to visualize it with Paraview. Or, you can put single grid to `FluidRenderer`, which can be used to render single 3D grid as in `examples/cavity3d.py`. 


## Google Colab Workflow

- Open new colab notebook `ipynb`.
- Choose a GPU runtime. 
- Copy and paste the following command line in the first cell. 

```bash
!git clone https://github.com/hayashi-workshop/clbmtaichi.git
%cd clbmtaichi/
!pip install -r requirements.txt
!pip install 'trimesh[easy]'
!pip install networkx
!mkdir -p output
```

- Open `File` in the side menu. 
- Go down the directory tree to `example/`.
- (file editing below can be replaced with file upload from your local file)
- Double click an example you want to run. It will be open on the right side of the browser. 
- Comment out Taichi GGUI related lines in the example script (search by `render`). The time loop usually have `while running`, but this should also be `while step < step_end:`. 
- Add `save_vtk` in or end of the time loop to dump the results. 
- Run! `!PYTHONPATH=. python examples/yourfile.py`


- The following code will compress `output/` to facilitate downloading the results. 

```python
import shutil
from google.colab import files

directory_name = 'output/nested' # change the directory name for your case
zip_filename = 'nested_result.zip'

shutil.make_archive(zip_filename.replace('.zip', ''), 'zip', directory_name)
```

- Then, 

```python
files.download(zip_filename)
```

Cloned and dumped files will be deleted when sessions are terminated. Consider to mount google drive to keep them. 


### MLUPS bench with Colab

`examples/mlups_main.py` does not use GGUI; therefore it runs on Colab without any changes. 

CPU (Xeon 6cores/12threads cores (2.20 GHz)) vs. GPU (NVIDIA A100-SXM4-40GB) 

<div style="max-width: 100%; display: flex; gap: 10px;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups_A100.png" style="max-width: 50%; height: auto; object-fit: contain;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups_256_A100.png" style="max-width: 50%; height: auto; object-fit: contain;">
</div>

CPU (EPYC 9B45 24cores/48threads) vs. G4 GPU (NVIDIA RTX Pro 6000 Blackwell Server Edition) 

<div style="max-width: 100%; display: flex; gap: 10px;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups_G4.png" style="max-width: 50%; height: auto; object-fit: contain;">
  <img src="https://www.lab.kobe-u.ac.jp/eng-mfd/clbmtaichi/benchmark_mlups_256_G4.png" style="max-width: 50%; height: auto; object-fit: contain;">
</div>

