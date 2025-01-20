from OpenGL.GL import *
from shape import *
import numpy as np

class Cube (Shape):
  def __init__ (self):
    coords = np.array([
      # back face: counter clockwise 
      -0.5, 0.0,-0.5,
      -0.5, 1.0,-0.5,
      0.5, 1.0,-0.5,
      0.5, 0.0,-0.5,
      # front face: counter clockwise 
      -0.5, 0.0, 0.5,
      0.5, 0.0, 0.5,
      0.5, 1.0, 0.5,
      -0.5, 1.0, 0.5,
      # letf face: counter clockwise
      -0.5, 0.0,-0.5,
      -0.5, 0.0, 0.5,
      -0.5, 1.0, 0.5,
      -0.5, 1.0,-0.5,
      # right face: counter clockwise
      0.5, 0.0,-0.5,
      0.5, 1.0,-0.5,
      0.5, 1.0, 0.5,
      0.5, 0.0, 0.5,
      # botton face: counter clockwise 
      -0.5, 0.0,-0.5,
      0.5, 0.0,-0.5,
      0.5, 0.0, 0.5,
      -0.5, 0.0, 0.5,
      # top face: counter clockwise
      -0.5, 1.0,-0.5,
      -0.5, 1.0, 0.5,
      0.5, 1.0, 0.5,
      0.5, 1.0,-0.5
    ], dtype = 'float32')
    normals = np.array([
      # back face: counter clockwise 
      0.0, 0.0,-1.0,
      0.0, 0.0,-1.0,
      0.0, 0.0,-1.0,
      0.0, 0.0,-1.0,
      # front face: counter clockwise 
      0.0, 0.0, 1.0,
      0.0, 0.0, 1.0,
      0.0, 0.0, 1.0,
      0.0, 0.0, 1.0,
      # left face: counter clockwise
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      # right face: counter clockwise
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      # botton face: counter clockwise 
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      # top face: counter clockwise
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
    ], dtype = 'float32')
    texcoords = np.array([
      # back face: counter clockwise 
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
      # front face: counter clockwise 
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
      # left face: counter clockwise
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
      # right face: counter clockwise
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
      # botton face: counter clockwise 
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
      # top face: counter clockwise
      0.0, 0.0,
      1.0, 0.0,
      1.0, 1.0,
      0.0, 1.0,
    ], dtype = 'float32')
    tangents = np.array([
      # back face: counter clockwise 
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      # front face: counter clockwise 
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      # left face: counter clockwise
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
      0.0, 1.0, 0.0,
      # right face: counter clockwise
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      0.0,-1.0, 0.0,
      # botton face: counter clockwise 
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      -1.0, 0.0, 0.0,
      # top face: counter clockwise
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
      1.0, 0.0, 0.0,
    ], dtype = 'float32')
    index = np.array([
      0,1,2,0,2,3,
      4,5,6,4,6,7,
      8,9,10,8,10,11,
      12,13,14,12,14,15,
      16,17,18,16,18,19,
      20,21,22,20,22,23
    ], dtype = 'uint32')
    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    # create coord buffer
    self.coord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glBufferData(GL_ARRAY_BUFFER,coords.nbytes,coords,GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(0) 
    # create normal buffer
    self.normal_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.normal_buffer)
    glBufferData(GL_ARRAY_BUFFER,normals.nbytes,normals,GL_STATIC_DRAW)
    glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(1) 
    # create tangent buffer
    self.tangent_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.tangent_buffer)
    glBufferData(GL_ARRAY_BUFFER,tangents.nbytes,tangents,GL_STATIC_DRAW)
    glVertexAttribPointer(2,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(2) 
    # create tex coord buffer
    self.texcoord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.texcoord_buffer)
    glBufferData(GL_ARRAY_BUFFER,texcoords.nbytes,texcoords,GL_STATIC_DRAW)
    glVertexAttribPointer(3,2,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(3) 
    # create index buffer
    index_id = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,index_id)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,index.nbytes,index,GL_STATIC_DRAW)

  def Draw (self, st):
    glBindVertexArray(self.vao)
    glDrawElements(GL_TRIANGLES,36,GL_UNSIGNED_INT,None)