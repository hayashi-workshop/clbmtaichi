# obstacle_stanford_bunny.py

# this class uses trimesh to handle mesh data
# install the following if not yet inplemented
#
#pip install 'trimesh[easy]'
#pip install networkx
#
# See https://github.com/mikedh/trimesh

import taichi as ti

import numpy as np
import trimesh

@ti.data_oriented
class ObstacleManager:
    def __init__(self, nd, offset, length_scale, export_dir='./'):
        self.mesh_src = 'https://raw.githubusercontent.com/mikedh/trimesh/master/models/bunny.ply'
        self.export_dir = export_dir
        self.length_scale = length_scale
        self.nd  = nd
        self.dim = len(self.nd)
        self.nx = self.nd[0]
        self.ny = self.nd[1]
        self.nz = self.nd[2] 

        # offset of mask region in LBM field
        self.offset = ti.Vector(offset)
        self.offset_np = np.array(offset)

        self.ti_axes = ti.ijk
        self.n = ti.Vector.field(self.dim, float) # unit normal
        for d in range(self.dim):
            ti.root.dense(self.ti_axes, nd).place(self.n.get_scalar_field(d))

        self.generate_mask()

    
    def generate_mask(self):
        self._load_model()
        self._generate_mask_np()
        self._convert_to_lattice_scale()
        self._send_model_to_Taichi()


    def _load_model(self):
        print("[StanfordBunny] Loading Stanford bunny model from github")
        loaded = trimesh.load_remote(self.mesh_src)

        if isinstance(loaded, trimesh.Scene): # if Scene, extract geometry 
            mesh = next(iter(loaded.geometry.values()))
        else:
            mesh = loaded # use scene as it is 

        if not mesh.is_watertight:
            mesh.fill_holes() # fill holes potentially present inside

        print("[StanfordBunny] Succesfully loaded")

        min_corner = mesh.bounds[0]
        mesh.vertices -= min_corner
        mesh.vertices /= np.max(mesh.extents)       # normalization

        self.mesh = mesh

    def _generate_mask_np(self): # LBM mask
        print("[StanfordBunny] Preparing contiguous grid to generate mask")
        x = np.linspace(0.0, 1.0, self.length_scale)
        y = np.linspace(0.0, 1.0, self.length_scale)
        z = np.linspace(0.0, 1.0, self.length_scale)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        grid_points = np.vstack([X.ravel(), Y.ravel(), Z.ravel()]).T

        print("[StanfordBunny] Generating mask for LBM")
        inside_mask = self.mesh.contains(grid_points) # mask data from mesh: in -> 1, out -> 0
        self.mask_3d_np = inside_mask.reshape((self.length_scale, self.length_scale, self.length_scale)) # reshape mask in shape of (nx, ny, nz)
        self.mask_3d_center = ti.Vector([len(self.mask_3d_np[0]) // 2, len(self.mask_3d_np[1]) // 2, len(self.mask_3d_np[2]) // 2], dt=ti.i32)

        self.voxel_centers_np = grid_points[inside_mask].astype(np.float32) # mask points for Taichi GUI visualization
        self.num_voxels       = len(self.voxel_centers_np)

    def _convert_to_lattice_scale(self):
        self.mesh.vertices    *= self.length_scale
        self.voxel_centers_np *= self.length_scale

    def _send_model_to_Taichi(self):
        num_vertices  = len(self.mesh.vertices)
        num_triangles = len(self.mesh.faces)

        self.vertices = ti.Vector.field(3, dtype=ti.f32, shape=num_vertices)
        self.indices  = ti.field(dtype=ti.i32, shape=num_triangles * 3)

        self.vertices.from_numpy(self.mesh.vertices.astype(np.float32))
        self.indices.from_numpy(self.mesh.faces.flatten().astype(np.int32))

        self.voxel_centers = ti.Vector.field(3, dtype=ti.f32, shape=self.num_voxels)
        self.voxel_centers.from_numpy(self.voxel_centers_np)

        self.mask_field = ti.field(dtype=ti.i32, shape=(self.length_scale, self.length_scale, self.length_scale))
        self.mask_field.from_numpy(self.mask_3d_np)

        print("[StanfordBunny] Voxel model has been sent to Taichi scope")


    def apply_to_mask(self, lbm): # wrapper function for private kernel _generate_mask_kernel
        self.mesh.vertices += self.offset_np
        self.mesh.export(self.export_dir + 'stanford_bunny.ply')
        self._generate_mask_kernel(lbm.mask)
        self._compute_normal(lbm.mask)

    @ti.kernel
    def _generate_mask_kernel(self, mask: ti.template()):
        mask.fill(0)
        for I in ti.grouped(self.mask_field):
            target_I = I + self.offset

            is_inside = True
            for d in ti.static(range(self.dim)):
                if target_I[d] < 0 or target_I[d] >= mask.shape[d]:
                    is_inside = False
            
            if is_inside:
                mask[target_I] = self.mask_field[I]

    @ti.kernel
    def _compute_normal(self, mask: ti.template()):
        center = self.mask_3d_center + self.offset # center of mask3d
        for I in ti.grouped(mask):
            grad = ti.Vector([0.0, 0.0, 0.0]) # grad(mask)
            is_set = False
            max_stencil = 5 # maybe enough
            for d in ti.static(range(self.dim)): # search for all direction x, y, z
                for s in range(1,max_stencil+1): # search non zero gradient value from narrow stencil
                    if is_set: # if gradient is already found, pass
                        continue

                    e = ti.Vector([1 if i == d else 0 for i in range(self.dim)]) # unit vector in d direction
                    grad[d] = (self._get_mask(mask, I + s*e) - self._get_mask(mask, I - s*e)) / (2 * s) # compute gradient of mask

                    if ti.abs(grad[d]) > 1e-6: # if grad is non zero, 
                        self.n[I][d] = grad[d] # current stencil is emplyed
                        is_set = True          # lock 

                if is_set == False: # safe guard for model internal
                    self.n[I][d] = (I[d] - center[d] + 1e-6)/(self.length_scale*0.5)

            self.n[I] = self.n[I].normalized()

    @ti.func
    def _get_mask(self, mask, I): # avoid index out of scope
        clamped_I = ti.Vector([
            ti.max(0, ti.min(I[0], self.nx - 1)),
            ti.max(0, ti.min(I[1], self.ny - 1)),
            ti.max(0, ti.min(I[2], self.nz - 1))
        ])
        return mask[clamped_I]
