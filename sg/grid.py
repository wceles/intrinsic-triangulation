import numpy as np

class Grid:
  def __init__ (self, nx, ny):
    self.nx = nx
    self.ny = ny
    # fill coordinates
    self.coords = np.empty(2*self.VertexCount(), dtype = 'float32')
    dx = 1 / nx
    dy = 1 / ny
    nc = 0
    for j in range(0,ny+1):
      for i in range(0,nx+1):
        self.coords[nc+0] = i*dx
        self.coords[nc+1] = j*dy
        nc += 2
    
    # fill indices
    def findex (i, j, nx):
      return j*(nx+1) + i

    self.indices = np.empty(self.IndexCount(), dtype = 'int32')
    ni = 0
    for j in range(0,ny):
      for i in range(0,nx):
        self.indices[ni+0] = findex(i,j,nx)
        self.indices[ni+1] = findex(i+1,j,nx)
        self.indices[ni+2] = findex(i+1,j+1,nx)
        self.indices[ni+3] = findex(i,j,nx)
        self.indices[ni+4] = findex(i+1,j+1,nx)
        self.indices[ni+5] = findex(i,j+1,nx)
        ni += 6

  def GetNx (self):
    return self.nx

  def GetNy (self):
    return self.ny

  def VertexCount (self):
    return (self.nx+1)*(self.ny+1)

  def GetCoords (self):
    return self.coords

  def IndexCount (self):
    return 6*self.nx*self.ny

  def GetIndices (self):
    return self.indices
