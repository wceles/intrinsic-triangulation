
from OpenGL.GL import *
from .appearance import Appearance

class Texture1D(Appearance):
  def __init__ (self, varname, array=None):
    self.varname = varname
    self.tex = glGenTextures(1)
    if array:
      self.SetData(array)
  
  def SetData (self, array):
    glBindTexture(GL_TEXTURE_1D,self.tex)
    width = array.shape[0]
    if array.ndim == 1:
      mode = GL_R
    elif array.shape[1] == 3:
      mode = GL_RGB
    elif array.shape[1] == 4:
      mode = GL_RGBA
    else:
      raise RuntimeError("Unsupported array shape: " + array.shape)
    if (array.dtype == 'uint8'):
      type = GL_UNSIGNED_BYTE
    elif (array.dtype == 'uint64'):
      type = GL_UNSIGNED_INT
    elif (array.dtype == 'float32'):
      type = GL_FLOAT
    elif (array.dtype == 'float64'):
      type = GL_FLOAT
      array = array.astype('float32')
    else:
      raise RuntimeError("Unsupported image component type: " + array.dtype)
    glTexImage1D(GL_TEXTURE_1D,0,mode,width,0,mode,type,array)
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)	
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glGenerateMipmap(GL_TEXTURE_1D)
    glBindTexture(GL_TEXTURE_1D,0)

  def GetTexId (self):
    return self.tex
  
  def SetWrap (self,wrap):
    glBindTexture(GL_TEXTURE_1D,self.tex)
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,wrap)	
    glBindTexture(GL_TEXTURE_1D,0)

  def Load (self, st):
    shd = st.GetShader()
    shd.ActiveTexture(self.varname)
    glBindTexture(GL_TEXTURE_1D,self.tex)

  def Unload (self, st):
    shd = st.GetShader()
    shd.DeactiveTexture()

