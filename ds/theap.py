# theap: triangle heap for mesh refinment
# Waldemar Celes
# Tecgraf Institute of PUC-Rio
# celes@tecgraf.puc-rio.br

# This is an auxiliary class that implements a simple triangle heap to support greedy algorithms

import heapq
import math

class THeap:
  def __init__ (self, mesh, amin):
    self.amin = amin
    self.mesh = mesh
    self.heap = []                  # priority list sorted by area (decreasing order)
    self.ts = [0] * len(mesh.T)     # triangle timestamp table 
    for t in range(len(mesh.T)):
      self.insert_if(t)

  # update heap datastructure for the triangle in the set
  def update (self, tset):
    self.ts += [0] * (len(self.mesh.T)-len(self.ts))
    while tset:
      t, _ = tset.popitem()
      self.insert_if(t)
  
  # pop the triangle in heap with largest area
  # return triangle id, area, and angle
  def pop (self):
    while self.heap:
      _, area, t, angle, ts = heapq.heappop(self.heap)
      if self.ts[t] ==  ts:
        return t, -area, angle
    return None, None, None

  # insert a triangle in the heap if its min angle is less than the limit
  def insert_if (self, t):
    if not self.mesh.t_narrow(t):
      angle = min(self.mesh.t_get_angles(t))
      self.ts[t] += 1
      if angle < self.amin:
        area = self.mesh.h_area(self.mesh.T[t])
        heapq.heappush(self.heap,(angle,-area,t,angle,self.ts[t]))
  