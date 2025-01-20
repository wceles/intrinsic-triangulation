from OpenGL.GL import *
from .shape import Shape
import numpy as np
import math

class Strip (Shape):
  def __init__ (self, n=64):
    coord = []
    normal = []
    for i in range(0,n+1):
      theta = 2*math.pi*i/n
      coord.append([math.cos(theta),math.sin(theta),-1])
      coord.append([math.cos(theta),math.sin(theta), 1])
      normal.append([math.cos(theta),math.sin(theta), 0])
      normal.append([math.cos(theta),math.sin(theta), 0])
    bcoord = np.array(coord,dtype='float32')
    bnormal = np.array(normal,dtype='float32')
    self.vao = glGenVertexArrays(1)
    self.ninc = 2*(n+1)
    glBindVertexArray(self.vao)
    id = glGenBuffers(2)
    self.coord_buffer = id[0]
    glBindBuffer(GL_ARRAY_BUFFER,id[0])
    glBufferData(GL_ARRAY_BUFFER,bcoord.nbytes,bcoord,GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    self.normal_buffer = id[1]
    glBindBuffer(GL_ARRAY_BUFFER,id[1])
    glBufferData(GL_ARRAY_BUFFER,bnormal.nbytes,bnormal,GL_STATIC_DRAW)
    glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)

  def Draw (self, st):
    glBindVertexArray(self.vao)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glEnableVertexAttribArray(0) 
    glBindBuffer(GL_ARRAY_BUFFER,self.normal_buffer)
    glEnableVertexAttribArray(1) 
    glDrawArrays(GL_TRIANGLE_STRIP,0,self.ninc)
    glBindBuffer(GL_ARRAY_BUFFER,self.normal_buffer)
    glDisableVertexAttribArray(1) 
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glDisableVertexAttribArray(0) 