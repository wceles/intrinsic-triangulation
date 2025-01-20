from OpenGL.GL import *
from .shape import Shape
import array

class Screen (Shape):
  def __init__ (self):
    coords = array("f",[
      # back face: counter clockwise 
      -1.0,-1.0,
       1.0,-1.0,
       1.0, 1.0,
      -1.0, 1.0
    ])
    index = array("L",[
      0,1,2,3
    ])
    # create VAO
    self.vao = glGenVertexArrays(1)
    glBindVertexArray(self.vao)
    # create coord buffer
    self.coord_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glBufferData(GL_ARRAY_BUFFER,4*len(coords),coords.tobytes(),GL_STATIC_DRAW)
    glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,0,0)
    # create index buffer
    index_id = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,index_id)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER,4*len(index),index.tobytes(),GL_STATIC_DRAW)

  def Draw (self, st):
    glBindVertexArray(self.vao)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glEnableVertexAttribArray(0) 
    glDrawElements(GL_TRIANGLES,36,GL_UNSIGNED_INT,None)
    glBindBuffer(GL_ARRAY_BUFFER,self.coord_buffer)
    glDisableVertexAttribArray(0) 