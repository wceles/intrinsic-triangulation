import math
import glm
from OpenGL.GL import *
import glfw

class Arcball:
  def __init__ (self, distance):
    self.distance = distance
    self.x0 = 0
    self.y0 = 0
    self.mat = glm.mat4(1)
  def Attach (self, win):
    def cursorpos (win, x, y):
      wn_w, wn_h = glfw.get_window_size(win)
      fb_w, fb_h = glfw.get_framebuffer_size(win)
      x = x * fb_w / wn_w
      y = (wn_h - y) * fb_h / wn_h
      self.AccumulateMouseMotion(x,y)
    def cursorinit (win, x, y):
      wn_w, wn_h = glfw.get_window_size(win)
      fb_w, fb_h = glfw.get_framebuffer_size(win)
      x = x * fb_w / wn_w
      y = (wn_h - y) * fb_h / wn_h
      self.InitMouseMotion(x,y)
      glfw.set_cursor_pos_callback(win,cursorpos)
    def dummy (win, x, y):
      pass
    def mousebutton (win, button, action, mods):
      if action == glfw.PRESS:
        glfw.set_cursor_pos_callback(win,cursorinit)  # cursor position callback
      else:
        glfw.set_cursor_pos_callback(win,dummy)        # callback disabled
    glfw.set_mouse_button_callback(win,mousebutton)

  def InitMouseMotion (self, x0, y0):
    self.x0 = x0
    self.y0 = y0

  def AccumulateMouseMotion (self, x, y):
    vp = glGetIntegerv(GL_VIEWPORT)  
    if x==self.x0 and y==self.y0:
      return
    ux, uy, uz = Map(vp[2],vp[3],self.x0,self.y0)
    vx, vy, vz = Map(vp[2],vp[3],x,y)
    self.x0 = x
    self.y0 = y
    ax = uy*vz - uz*vy
    ay = uz*vx - ux*vz
    az = ux*vy - uy*vx
    theta = 2*math.asin(math.sqrt(ax*ax+ay*ay+az*az)) 
    # self.mat = T * R * T
    m = glm.mat4(1)
    m = glm.translate(m,glm.vec3(0,0,-self.distance))
    m = glm.rotate(m,theta,glm.vec3(ax,ay,az))
    m = glm.translate(m,glm.vec3(0,0,self.distance))
    self.mat = m * self.mat

  def GetMatrix (self):
    return self.mat

  def Translate (self, dx, dy, dz):
    m = glm.mat4(1)
    m = glm.translate(m,glm.vec3(dx*self.distance,dy*self.distance,dz*self.distance))
    self.mat = m * self.mat

# Map function: from screen (x,y) to unit sphere (px,py,pz)
def Map (width, height, x, y):
  if width < height:
    r = width/2
  else:
    r = height/2
  X = (x - width/2) / r
  Y = (y - height/2) / r
  l = math.sqrt(X*X + Y*Y)
  if l <= 1:
    Z = math.sqrt(1 - l*l)
  else:
    X /= l
    Y /= l
    Z = 0
  return (X,Y,Z)