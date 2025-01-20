from OpenGL.GL import *
from .appearance import Appearance

class TexBuffer(Appearance):
  def __init__ (self, varname, array):
    self.varname = varname
    self.buffer = glGenBuffers(1)
    self.tex = glGenTextures(1)
    self.SetData(array)

  def SetData (self, array):
    dtype = array.dtype
    shape = array.shape
    if dtype == 'int32':
      if len(shape) == 1:
        self.format = GL_R32I
      elif shape[1] == 2:
        self.format = GL_RG32I
      elif shape[1] == 3:
        self.format = GL_RGB32I
      elif shape[1] == 4:
        self.format = GL_RGBA32I
      else:
        raise RuntimeError("Invalid shape for texture buffer")
    elif dtype == 'uint32':
      if len(shape) == 1:
        self.format = GL_R32UI
      elif shape[1] == 2:
        self.format = GL_RG32I
      elif shape[1] == 3:
        self.format = GL_RGB32UI
      elif shape[1] == 4:
        self.format = GL_RGBA32UI
      else:
        raise RuntimeError("Invalid shape for texture buffer")
    elif dtype == 'float32' or dtype == 'float64':
      if dtype == 'float64':
        array = array.astype('float32')
      if len(shape) == 1:
        self.format = GL_R32F
      elif shape[1] == 2:
        self.format = GL_RG32F
      elif shape[1] == 3:
        self.format = GL_RGB32F
      elif shape[1] == 4:
        self.format = GL_RGBA32F
      else:
        raise RuntimeError("Invalid shape for texture buffer")
    else:
      raise RuntimeError("Invalid type for texture buffer:",dtype)
    glBindTexture(GL_TEXTURE_BUFFER,self.tex)
    glBindBuffer(GL_TEXTURE_BUFFER,self.buffer)
    glBufferData(GL_TEXTURE_BUFFER,array.nbytes,array,GL_STATIC_DRAW)
    glTexBuffer(GL_TEXTURE_BUFFER,self.format,self.buffer)


  def GetTexId (self):
    return self.tex

  def Load (self, st):
    shd = st.GetShader()
    shd.ActiveTexture(self.varname)
    glBindTexture(GL_TEXTURE_BUFFER,self.tex)

  def Unload (self, st):
    shd = st.GetShader()
    shd.DeactiveTexture()