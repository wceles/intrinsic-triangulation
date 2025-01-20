from OpenGL.GL import *
from .shape import Shape
from .grid import Grid
import numpy as np
import math

class Sphere(Shape):
  def __init__(self, nstack=64, nslice=64):
    grid = Grid(nstack,nslice)
    self.nind = grid.IndexCount()
    coord = np.empty(3*grid.VertexCount(), dtype = 'float32')
    tangent = np.empty(3*grid.VertexCount(), dtype = 'float32')
    texcoord = grid.GetCoords()
    nc = 0
    for i in range(0,2*grid.VertexCount(),2):
      theta = texcoord[i+0]*2*math.pi
      phi = texcoord[i+1]*math.pi
      coord[nc+0] = math.sin(theta) * math.sin(math.pi-phi)
      coord[nc+1] = math.cos(math.pi-phi)
      coord[nc+2] = math.cos(theta) * math.sin(math.pi-phi)
      tangent[nc+0] = math.cos(theta)
      tangent[nc+1] = 0
      tangent[nc+2] = -math.sin(theta)
      nc += 3
    
    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    # create coord buffer
    self.coord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glBufferData(GL_ARRAY_BUFFER,coord.nbytes,coord,GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)
    self.tangent_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.tangent_buffer)
    glBufferData(GL_ARRAY_BUFFER,tangent.nbytes,tangent,GL_STATIC_DRAW)
    glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,0,None)
    self.texcoord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.texcoord_buffer)
    glBufferData(GL_ARRAY_BUFFER,texcoord.nbytes,texcoord,GL_STATIC_DRAW)
    glVertexAttribPointer(3,2,GL_FLOAT,GL_FALSE,0,None) 
    # create index buffer
    indices = grid.GetIndices()
    index = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,index)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,indices.nbytes,indices,GL_STATIC_DRAW)

  def Draw (self, st):
    glBindVertexArray(self.vao)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.tangent_buffer)
    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER,self.texcoord_buffer)
    glEnableVertexAttribArray(3)
    glDrawElements(GL_TRIANGLES,self.nind,GL_UNSIGNED_INT,None)
    glBindBuffer(GL_ARRAY_BUFFER,self.texcoord_buffer)
    glDisableVertexAttribArray(3) 
    glBindBuffer(GL_ARRAY_BUFFER,self.tangent_buffer)
    glDisableVertexAttribArray(2) 
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glDisableVertexAttribArray(0) 
    glDisableVertexAttribArray(1) 
