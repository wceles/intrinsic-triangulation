from .light import Light
import glm

class EyeLight(Light):
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
      pos = self.pos
      if shd.GetLightingSpace() == "world":
        pos = glm.inverse(st.GetCamera().GetViewMatrix())*pos
      shd.SetUniform("lpos",pos)