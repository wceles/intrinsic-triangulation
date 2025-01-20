import glm

class Transform:
  def __init__ (self):
    self.mat = glm.mat4(1.0)

  def LoadIdentity (self):
    self.mat = glm.mat4(1.0)
  
  def MultMatrix (self, mat):
    self.mat *= mat
  
  def Translate (self, x, y, z):
    self.mat = glm.translate(self.mat,glm.vec3(x,y,z))
  
  def Scale (self, x, y, z):
    self.mat = glm.scale(self.mat,glm.vec3(x,y,z))
  
  def Rotate (self, angle, x, y, z):
    self.mat = glm.rotate(self.mat,glm.radians(angle),glm.vec3(x,y,z))
  
  def GetMatrix (self):
    return self.mat
  
  def Load (self, st):
    st.PushMatrix()
    st.MultMatrix(self.mat)

  def Unload (self, st):
    st.PopMatrix()
