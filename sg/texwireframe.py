
from OpenGL.GL import *
from PIL import Image
import numpy as np
import math
from .appearance import Appearance

class TexWireframe(Appearance):
  def __init__ (self, varname, thickness = 3, color = [0,0,0], nmax=4096):
    self.varname = varname
    self.tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_1D,self.tex)
    level = int(math.log2(nmax))
    rgba = color + [0]
    # build mipmapping of alpha texture
    for l in range(0,level+1):
      n = int(2**(level-l))
      # limit level wireframe thickness to 1/3 of texture dimension
      if thickness < n/3:
        lthick = thickness
      else:
        lthick = n / 3
      ithick = int(lthick // 2)  # half thickness at each face
      fthick = lthick % 2
      array = np.array([rgba]*n,dtype='float32')
      for i in range(0,ithick):
        array[i][3] = 1.0
        array[n-1-i][3] = 1.0
      if fthick > 0.0:
        array[ithick][3] = fthick
        array[n-1-ithick][3] = fthick
      glTexImage1D(GL_TEXTURE_1D,l,GL_RGBA,n,0,GL_RGBA,GL_FLOAT,array)
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)	
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_1D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
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

