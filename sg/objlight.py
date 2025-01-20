print(__name__)
from .light import Light
import glm

class ObjLight(Light):
    def __init__ (self, x, y, z, w=1):
      Light.__init__(self)
      self.pos = glm.vec4(x,y,z,w)

    def SetPosition (self, x, y, z, w):
      self.pos[0] = x
      self.pos[1] = y
      self.pos[2] = z
      self.pos[3] = w

    def Load (self, st):
      Light.Load(self,st)
      # Set position in lighting space
      shd = st.GetShader()
      mat = glm.mat4(1.0)
      if shd.GetLightingSpace() == "camera":
        mat = st.GetCamera().GetViewMatrix()
      if self.GetReference():
        mat = mat * self.GetReference().GetModelMatrix()
      pos = mat * self.pos  # to lighting space
      shd.SetUniform("lpos",pos)