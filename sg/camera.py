import math
import glm
from OpenGL.GL import *
from .arcball import Arcball

class Camera:
  def __init__(self, x, y, z):
    self.ortho = False
    self.fovy = 45
    self.znear = 0.1
    self.zfar = 1000
    self.center = glm.vec3(0,0,0)
    self.eye = glm.vec3(x,y,z)
    self.up = glm.vec3(0,1,0)
    self.arcball = None
    self.reference = None

  def SetAngle (self, fovy):
    self.fovy = fovy

  def GetAngle (self):
    return self.fovy

  def SetZPlanes (self, znear, zfar):
    self.znear = znear
    self.zfar = zfar
  
  def SetCenter (self, x, y, z):
    self.center = glm.vec3(x,y,z)

  def GetCenter (self):
    return self.center

  def SetEye (self, x, y, z):
    self.eye = glm.vec3(x,y,z)

  def GetEye (self):
    return self.eye

  def SetUpDir (self, x, y, z):
    self.up = glm.vec3(x,y,z)

  def SetOrtho (self, flag):
    self.ortho = flag

  def CreateArcball (self):
    d = glm.length(self.eye-self.center)
    self.arcball = Arcball(d)
    return self.arcball

  def GetArcball (self):
    return self.arcball

  def SetReference (self, ref):
    self.reference = ref

  def GetProjMatrix (self):
    vp = glGetIntegerv(GL_VIEWPORT)
    ratio = vp[2]/vp[3]
    if not self.ortho:
      return glm.perspective(glm.radians(self.fovy),ratio,self.znear,self.zfar)
    else:
      dist = glm.distance(self.eye,self.center)
      height = dist * math.tan(glm.radians(self.fovy)/2)
      width = height / vp[3] * vp[2]
      return glm.ortho(-width,width,-height,height,self.znear,self.zfar)

  def GetViewMatrix (self):
    view = glm.mat4(1.0)
    if self.arcball: 
      view = view * self.arcball.GetMatrix()
    view = view * glm.lookAt(self.eye,self.center,self.up)
    if (self.reference):
        view = view * glm.inverse(self.reference.get_modelmatrix())
    return view

  def Load (self, st):
    shd = st.GetShader()
    cpos = glm.vec4(0,0,0,1)
    if shd.GetLightingSpace() == "world":
      mat = glm.inverse(self.GetViewMatrix())
      cpos = mat * cpos
    shd.SetUniform("cpos",cpos)