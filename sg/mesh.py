from OpenGL.GL import *
from .shape import Shape
import numpy as np

class Mesh (Shape):
  def __init__ (self, V, F):
    coords = np.array(V,dtype='float32')
    index = np.array(F,dtype='uint32')
    self.nindex = index.size
    self.min = np.min(coords,0)
    self.max = np.max(coords,0)
    '''
    # normalizing
    delta = self.max - self.min
    coords = (coords-self.min)/(delta)
    self.min = np.min(coords,0)
    self.max = np.max(coords,0)
    '''

    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    # create coord buffer
    coord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,coord_buffer)
    glBufferData(GL_ARRAY_BUFFER,coords.nbytes,coords,GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,None)
    glEnableVertexAttribArray(0)
    # create index buffer
    index_id = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,index_id)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,index.nbytes,index,GL_STATIC_DRAW)

  def Min (self):
    return self.min

  def Max (self):
    return self.max

  def Draw (self, st):
    glBindVertexArray(self.vao)
    glDrawElements(GL_TRIANGLES,self.nindex,GL_UNSIGNED_INT,None)
