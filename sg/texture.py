
from OpenGL.GL import *
from PIL import Image
import numpy as np
import glm
from .appearance import Appearance

class Texture(Appearance):
  def __init__ (self, varname, filename, texel=None, width=1, height=1):
    self.varname = varname
    self.tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D,self.tex)
    if filename:
      img = Image.open(filename)
      data = np.array(img)
      width, height = img.size
      if (img.mode == 'RGB'):
        mode = GL_RGB
      elif (img.mode == 'RGBA'):
        mode = GL_RGBA
      else:
        raise RuntimeError("Unsupported image mode: " + img.mode)
      if (data.dtype == 'uint8'):
        type = GL_UNSIGNED_BYTE
      else:
        raise RuntimeError("Unsupported image component type: " + data.dtype)
      glTexImage2D(GL_TEXTURE_2D,0,mode,width,height,0,mode,type,data)
      glGenerateMipmap(GL_TEXTURE_2D)
    elif texel == None:
      glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,width,height,0,GL_RGB,GL_UNSIGNED_BYTE,None)
    elif type(texel) == "<class 'glm.vec3'>":
      glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,1,1,0,GL_RGB,GL_UNSIGNED_BYTE,glm.value_ptr(texel))
    elif type(texel) == "<class 'glm.vec4'>":
      glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,1,1,0,GL_RGBA,GL_UNSIGNED_BYTE,glm.value_ptr(texel))
    else:
      raise RuntimeError("Invalid Texture parameters")
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)	
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
    glBindTexture(GL_TEXTURE_2D,0)

  def GetTexId (self):
    return self.tex

  def Load (self, st):
    shd = st.GetShader()
    shd.ActiveTexture(self.varname)
    glBindTexture(GL_TEXTURE_2D,self.tex)

  def Unload (self, st):
    shd = st.GetShader()
    shd.DeactiveTexture()

