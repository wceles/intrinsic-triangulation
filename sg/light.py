import glm
from OpenGL.GL import *

class Light:
    def __init__ (self): 
      self.amb = glm.vec4(0.2,0.2,0.2,1.0)
      self.dif = glm.vec4(0.8,0.8,0.8,1.0)
      self.spe = glm.vec4(1.0,1.0,1.0,1.0)
      self.reference = None

    def SetAmbient (self, r, g, b):
      self.amb[0] = r
      self.amb[1] = g
      self.amb[2] = b

    def SetDiffuse (self, r, g, b):
      self.dif[0] = r
      self.dif[1] = g
      self.dif[2] = b

    def SetSpecular (self, r, g, b):
      self.spe[0] = r
      self.spe[1] = g
      self.spe[2] = b

    def SetReference (self, reference):
      self.reference = reference

    def GetReference (self):
      return self.reference

    def Load (self, st):
      shd = st.GetShader()
      shd.SetUniform("lamb",self.amb)
      shd.SetUniform("ldif",self.dif)
      shd.SetUniform("lspe",self.spe)