# SHE: Supporting Halfedge Data Structure for Intrinsic Triangulation

This repository contains the implementation of **SHE (Supporting Halfedge Data Structure)**, a novel data structure proposed to represent intrinsic triangulations. This data structure supports advanced research in computational geometry and intrinsic mesh processing. The research behind this work was published as:

**"Direct Rendering of Intrinsic Triangulations"**  
*ACM Transactions on Graphics (TOG)*

## Features
- **Halfedge Data Structure (HE):** Standard implementation for extrinsic mesh representation.
- **Supporting Halfedge Data Structure (SHE):** A new approach for intrinsic triangulation.
- **Extended Supporting Halfedge Data Structure (SHE3):** Extended implementation with support for directional data.

## Repository Structure
The codebase includes the following components:

- `ds/he.py`: Halfedge data structure implementation for extrinsic mesh representation.
- `ds/she.py`: Proposed supporting halfedge data structure implementation for intrinsic mesh representation.
- `ds/she3.py`: Extended supporting halfedge data structure implementation for intrinsic mesh representation.
- `ds/utl.py`: Utility functions.
- `ds/theap.py`: Auxiliary list of priorities.
- `sg/*`: Scene graph implementation for mesh visualization.
- `shader/*`: Shaders used for visualizing extrinsic, intrinsic, and common subdivision meshes.
- `main.py`: Example application using the SHE data structure.
- `main3.py`: Example application using the extended SHE data structure.
- `data/*`: Sample meshes.

## Dependencies
The code requires the following Python modules:

- **[OpenGL](https://www.opengl.org/):** Graphics rendering library.
- **[glfw](https://github.com/glfw/glfw):** Graphical user interface library.
- **[potpourri3d](https://github.com/nmwsharp/potpourri3d):** Mesh loader for Python.
- **[numpy](https://numpy.org/):** Numerical array manipulation.
- **[scipy](https://scipy.org/):** Scientific computation.

Install dependencies using `pip`:
```bash
pip install glfw PyOpenGL potpourri3d numpy scipy
```

# Running the Examples

The example applications demonstrate the usage of SHE and SHE3. Pass a mesh filename as an argument to run the interactive visualizations:
```bash
python main.py data/pegaus.obj
python main3.py data/rocketship.ply
```


## Interactive Controls
	•	Mouse: Manipulate the object (arcball interface).
	•	Arrow Keys (UP, DOWN, LEFT, RIGHT): Pan the view.
	•	W/S Keys: Zoom in/out.
	•	I Key: Switch between viewing intrinsic and extrinsic meshes.
	•	L Key: Cycle through wireframe rendering modes (extrinsic → intrinsic → off).
	•	X Key: Create/visualize common subdivisions (press again to return).
	•	D Key: Build a Delaunay triangulation (without introducing new topological entities).
	•	R Key: Refine the mesh, targeting a minimum angle of 25 degrees (result is Delaunay).
	•	H Key: Simulate heat diffusion using the intrinsic triangulation (result mapped back to extrinsic vertices using an optimization procedure).
	•	Q Key: Quit the application.

## Sample Meshes

The data/ directory contains sample meshes for testing the applications.

# Citation
If you use this code for your research, please cite the original publication:

```latex
@article{intrinsic_triangulation_2025,
  title={Direct Rendering of Intrinsic Triangulations},
  author={Waldemar Celes},
  journal={ACM Transactions on Graphics (TOG)},
  year={2025}
}
```
