from .appearance import Appearance

class Variable(Appearance):
  def __init__ (self, name, value):
    self.name = name
    self.value = value

  def SetValue (self, value):
    self.value = value

  def GetValue (self):
    return self.value
  
  def Load (self, st):
    shd = st.GetShader()
    shd.SetUniform(self.name,self.value)
