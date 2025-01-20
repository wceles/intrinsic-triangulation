import glm
from .appearance import Appearance

class Material(Appearance):
    def __init__ (self, r, g, b, a=1):
      Appearance.__init__(self)
      self.amb = glm.vec4(r,g,b,a)
      self.dif = glm.vec4(r,g,b,0.0)
      self.spe = glm.vec4(1.0,1.0,1.0,0.0)
      self.shi = 32.0

    def SetAmbient (self, r, g, b, a=1):
      self.amb[0] = r
      self.amb[1] = g
      self.amb[2] = b
      self.amb[3] = a
    
    def SetDiffuse (self, r, g, b, a=1):
      self.dif[0] = r
      self.dif[1] = g
      self.dif[2] = b
      self.dif[3] = a
    
    def SetSpecular (self, r, g, b, a=1):
      self.spe[0] = r
      self.spe[1] = g
      self.spe[2] = b
      self.spe[3] = a 
    
    def SetShininess (self, shi):
      self.shi = shi
    
    def Load (self, st):
      shd = st.GetShader()
      shd.SetUniform("mamb",self.amb)
      shd.SetUniform("mdif",self.dif)
      shd.SetUniform("mspe",self.spe)
      shd.SetUniform("mshi",self.shi)
