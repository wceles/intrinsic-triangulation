import glm

class Node:
  def __init__ (self, shader=None, trf=None, apps=[], shps=[], nodes=[]):
    self.parent = None
    self.shader = shader
    self.trf = trf
    self.apps = apps
    self.shps = shps
    self.nodes = nodes

  def SetShader (self, shader):
    self.shader = shader

  def GetShader (self):
    return self.shader
  
  def SetTransform (self, trf):
    self.trf = trf
  
  def AddAppearance (self, app):
    self.apps.append(app)
  
  def AddShape (self, shp):
    self.shps.append(shp)
  
  def AddNode (self, node):
    self.nodes.append(node)
    node.SetParent(self)
  
  def SetParent (self, parent):
    self.parent = parent
  
  def GetParent (self):
    return self.parent
  
  def GetMatrix (self):
    if self.trf:
      return self.trf
    else:
      return glm.mat4(1.0)
  
  def GetModelMatrix (self):
    mat = self.GetMatrix()
    node = self.GetParent()
    while node:
      mat = node.GetMatrix() * mat
      node = node.GetParent()
    return mat
  
  def Render (self, st):
    # load
    if self.shader:
      self.shader.Load(st)
    if self.trf:
      self.trf.Load(st)
    for app in self.apps:
      app.Load(st)
    # draw
    if len(self.shps) > 0:
      st.LoadMatrices()
      for shp in self.shps:
        shp.Draw(st)
    for node in self.nodes:
      node.Render(st)
    # unload in reverse order
    for app in self.apps:
      app.Unload(st)
    if self.trf:
      self.trf.Unload(st)
    if self.shader:
      self.shader.Unload(st)
