import glm
from OpenGL.GL import *

class State:
  def __init__ (self, camera):
    self.camera = camera
    self.shader = []
    self.stack = [glm.mat4(1.0)]
    glUseProgram(0) # compatibility profile as default

  def PushShader (self, shd):
    self.shader.append(shd)
    shd.UseProgram()

  def PopShader (self):
    self.shader.pop()
    if not self.shader:
      glUseProgram(0)
    else:
      self.shader[-1].UseProgram()
  
  def GetShader (self):
    if not self.shader:
      raise SystemExit("Shader not defined")
    return self.shader[-1]

  def GetCamera (self):
    return self.camera

  def PushMatrix (self):
    self.stack.append(self.GetCurrentMatrix())

  def PopMatrix (self):
    self.stack.pop()

  def LoadMatrix (self, mat):
    self.stack[-1] = mat

  def MultMatrix (self, mat):
    self.stack[-1] = self.stack[-1] * mat

  def GetCurrentMatrix (self):
    return self.stack[-1]

  def LoadMatrices (self):
    # set matrices
    shd = self.GetShader()
    mvp = self.camera.GetProjMatrix() * self.camera.GetViewMatrix() * self.GetCurrentMatrix()
    mv = self.GetCurrentMatrix()      # to global space
    if shd.GetLightingSpace() == "camera":
      mv = self.camera.GetViewMatrix() * mv  # to camera space
    mn = glm.transpose(glm.inverse(mv))
    shd.SetUniform("Mvp",mvp)
    shd.SetUniform("Mv",mv)
    shd.SetUniform("Mn",mn)
    # load camera
    self.camera.Load(self)