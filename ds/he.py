# HE: HalfEdge Data Structure
# Waldemar Celes
# Tecgraf Institute of PUC-Rio
# celes@tecgraf.puc-rio.br

# Index-based implementation of a halfedge datastructure for triangle mesh
# An edge on the border has its second halfedge set to -1

import math
import numpy as np
import random as rd
from . import utl

def CreateGrid (nx, ny, lx=1, ly=1):
  # create a grid triangulation
  # add vertices
  V = []
  dx = lx / nx
  dy = ly / ny
  for j in range(0,ny+1):
    for i in range(0,nx+1):
      V.append([i*dx,j*dy,0]) 
    # add triangle
  F = []
  for j in range(0,ny):
    for i in range(0,nx):
      ii = j*(nx+1) + i
      ij = ii+1
      ji = (j+1)*(nx+1) + i
      jj = ji + 1
      F.append([ii,ij,ji])
      F.append([ij,jj,ji])
  return V, F
    
# create a sphere model
def CreateSphere (nx, ny):
  V, F = CreateGrid(nx,ny)
  for c in V:
    theta = c[0]*math.pi
    phi = c[1]*2*math.pi
    c[0] = math.sin(theta) * math.cos(phi)
    c[1] = math.sin(theta) * math.sin(phi)
    c[2] = math.cos(theta)
  return V, F

# create a torus model
def CreateTorus (R, r, nx, ny):
  V, F = CreateGrid(nx,ny)
  for c in V:
    theta = c[0]*2*math.pi
    phi = c[1]*2*math.pi
    c[0] = (R + r * math.cos(theta)) * math.cos(phi)
    c[1] = (R + r * math.cos(theta)) * math.sin(phi)
    c[2] = r * math.sin(theta)
  for f in F:
    j = f[1]
    k = f[2]
    f[1] = k
    f[2] = j
  return V, F

class Mesh:
  '''Halfedge data structure for triangle meshes'''
  def __init__ (self, C=[], I=[]):
    self.C = []  # vertex coordinates: [x,y,z]
    self.V = []  # one halfedge index associated to vertex: he
    self.E = []  # the two halfedge indices that form the edge: [he0,he1]
    self.T = []  # one halfedge index associated to the triangle: he
    self.H = []  # vertex, edge, triangle, and next halfedge associated to halfedge: [v,e,t,he]
    for c in C:
      self.addvertex(c[0],c[1],c[2])
    if len(I) > 0:
      self.sew(I)

  # add a new isolated vertex; return its id
  def addvertex (self, x, y, z=0.0, D=None):
    if D:
      prec = 1e7
      h = str(int(prec*x)) + "|" + str(int(prec*y)) + "|" + str(int(prec*z))
      if h in D:
        v = D[h]
        D['ind'].append(v)
      else:
        v = len(self.V)
        self.C.append([x,y,z])
        self.V.append(-1)
        D[h] = v
        D['ind'].append(v)
    else:
      v = len(self.V)
      self.C.append([x,y,z])
      self.V.append(-1)

  # sew the data structure considering all the triangles at once
  def sew (self, I):
    T = [] # temporary list of edges
    # create halfedges (still, without edges)
    for i,t in enumerate(I):
      h = len(self.H)
      self.H.append([t[0],None,i,h+1])
      self.H.append([t[1],None,i,h+2])
      self.H.append([t[2],None,i,h])
      self.V[t[0]] = h
      self.V[t[1]] = h+1
      self.V[t[2]] = h+2
      self.T.append(h)
      appendedge(T,t[0],t[1],h,i)
      appendedge(T,t[1],t[2],h+1,i)
      appendedge(T,t[2],t[0],h+2,i)
    T.sort(key = lambda x : (x[0],x[1]))
    i = 0
    while i < len(T):
      if i+1 < len(T) and T[i][0] == T[i+1][0] and T[i][1] == T[i+1][1]:
        e = len(self.E)
        self.E.append([T[i][2],T[i+1][2]])
        self.H[T[i][2]][1] = e
        self.H[T[i+1][2]][1] = e
        if i+2 < len(T) and T[i][0] == T[i+2][0] and T[i][1] == T[i+2][1]:
          raise("More than two uses per edge")
        i += 2
      else:
        e = len(self.E)
        self.E.append([T[i][2],-1])
        self.H[T[i][2]][1] = e
        i += 1

  # add a triangle; it should result in a manifold mesh
  def addtriangle (self, v0, v1, v2):
    t = len(self.T)  # index of to-be-created triangle
    inc = [v0,v1,v2]
    # collect mate he of existing edges
    m = []
    for i in range(0,3):
      m.append(self.find_vv(inc[(i+1)%3],inc[i]))
    for i in range(0,3):
      h = len(self.H)  # index of to-be-created he
      if m[i] == -1:      # create new edge
        e = len(self.E)   
        self.E.append([h,-1])
      else:               # update existing edge
        e = self.H[m[i]][1]
        self.E[e][1] = h 
      self.H.append([inc[i],e,t,h-2 if i==2 else h+1])  # create he
      self.V[inc[i]] = h         # set vertex he
    self.T.append(h)             # create triangle
    return t

  # return the incidence table of the triangulation
  def get_incidence_table (self):
    I = []
    for t in range(0,len(self.T)):
      I.append(self.t_get_inc(t))
    return I

  # return a triangle incidence
  def t_get_inc (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    return [
      self.H[h0][0],
      self.H[h1][0],
      self.H[h2][0],
    ]

  # get min edge length
  def get_lmin (self):
    lmin = 1e10
    for e in range(len(self.E)):
      h0 = self.E[e][0]
      h1 = self.next(h0)
      l = self.distance(self.H[h0][0],self.H[h1][0])
      if l < lmin:
        lmin = l
    return lmin

  # get min angle
  def get_angle_min (self):
    amin = 2*math.pi
    for i in range(len(self.T)):
      a = self.t_get_angles(i)
      for j in range(0,3):
        if a[j] < amin:
          amin = a[j]
    return amin

  # get the angles of a triangle
  def t_get_angles (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    assert(h0 == self.next(h2))
    return [self.h_angle(h0),self.h_angle(h1),self.h_angle(h2)]

  # get triangle angle at halfedge vertex
  def h_angle (self, h0):
    h1 = self.next(h0)
    h2 = self.next(h1)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0]
    v2 = self.H[h2][0]
    c0 = self.C[v0]
    c1 = self.C[v1]
    c2 = self.C[v2]
    l0 = utl.distance(c0,c1)
    l1 = utl.distance(c1,c2)
    l2 = utl.distance(c2,c0)
    c = utl.clamp((l0*l0+l2*l2-l1*l1)/(2*l0*l2),-1,1)
    return math.acos(c)

  # find vi in the star of v; return the halfedge from vi to v
  def find_vv (self, v, vi):
    l = self.adj_vh(v)
    for he in l:
      nt = self.next(he)
      if self.H[nt][0] == vi:
        return he
    return -1

  # collect the halfedges of a vertex
  def adj_vh (self, v):
    l = []
    h0 = he = self.V[v]
    if he != -1:
      while True:
        l.append(he)
        he = self.mate(he)
        if he == -1:
          break
        he = self.next(he)
        if he==h0:
          return l
      he = self.mate(self.previous(h0))
      while he != -1:
        l.insert(0,he)
        he = self.mate(self.previous(he))
    return l

  # return the border he associated to the vertex; return -1 if v is not at border or is isolated
  def border_h (self, v):
    h0 = he = self.V[v]
    if he == -1:
      return -1
    while not self.h_isborder(he):
      he = self.next(self.mate(he))
      if he==h0:
        return -1;
    return he

  # return the next he on border
  def h_nextborder (self, he):
    he = self.next(he)
    while not self.h_isborder(he):
      he = self.next(self.mate(he))
    return he

  # return the previous he on border
  def h_prevborder (self, he):
    he = self.previous(he)
    while not self.h_isborder(he):
      he = self.previous(self.mate(he))
    return he

  # check if he is on a border edge
  def h_isborder (self,he):
    return self.E[self.H[he][1]][1] == -1

  # check if e is a border edge
  def e_isborder (self,e):
    return self.E[e][1] == -1

  # return the mate he
  def mate (self, he):
    e = self.H[he][1]
    if self.E[e][0] == he:
      return self.E[e][1]
    else:
      return self.E[e][0]

  # return the next he in a triangle
  def next (self, he):
    return self.H[he][3]

  # return the previous he in a triangle
  def previous (self, he):
    return self.H[self.H[he][3]][3] # two nexts (triangle!)
  
  # swap edge
  def swapedge (self, e):
    if self.E[e][1] == -1:
      return False        # cannot swap border edge
    h0 = self.E[e][0]
    h1 = self.E[e][1]
    n0 = self.next(h0)
    n1 = self.next(h1)
    p0 = self.next(n0)
    p1 = self.next(n1)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0]
    w0 = self.H[p1][0]
    w1 = self.H[p0][0]
    t0 = self.H[h0][2]
    t1 = self.H[h1][2]
    l = self.distance(w0,w1)
    d0 = self.orient(w0,w1,v0) / l / 2
    d1 = self.orient(w0,w1,v1) / l / 2
    tol = 1e-5
    if (d0 > tol and d1 < -tol) or (d0 < -tol and d1 > tol):
      self.H[h0] = [w0,e,t0,p0]
      self.H[h1] = [w1,e,t1,p1]
      self.H[n0] = [v1,self.H[n0][1],t1,h1]
      self.H[n1] = [v0,self.H[n1][1],t0,h0]
      self.H[p0] = [w1,self.H[p0][1],t0,n1]
      self.H[p1] = [w0,self.H[p1][1],t1,n0]
      self.V[v0] = n1
      self.V[v1] = n0
      self.V[w0] = h0
      self.V[w1] = h1
      self.T[t0] = h0
      self.T[t1] = h1
      return True
    else:
      return False
  
  # return if the triple vertices are counter clockwise oriented
  def ccw (self, v0, v1, v2):
    a = self.C[v0]
    b = self.C[v1]
    c = self.C[v2]
    m = np.array([[1,a[0],a[1]],[1,b[0],b[1]],[1,c[0],c[1]]])
    return np.linalg.det(m) > 0

  def orient (self, v0, v1, v2):
    a = self.C[v0]
    b = self.C[v1]
    c = self.C[v2]
    m = np.array([[1,a[0],a[1]],[1,b[0],b[1]],[1,c[0],c[1]]])
    return np.linalg.det(m)

  # check if vertex v is in the circle formed by v0v1v2
  def incircle (self, v0, v1, v2, v):
    a = self.C[v0]
    b = self.C[v1]
    c = self.C[v2]
    d = self.C[v]
    m = np.array([
                  [a[0],a[1],a[0]*a[0]+a[1]*a[1],1],
                  [b[0],b[1],b[0]*b[0]+b[1]*b[1],1],
                  [c[0],c[1],c[0]*c[0]+c[1]*c[1],1],
                  [d[0],d[1],d[0]*d[0]+d[1]*d[1],1]
                  ])
    return np.linalg.det(m) > 0

  # check if the edge is legal
  def e_legal (self, e):
    if self.e_isborder(e):
      return True
    h0 = self.E[e][0]
    h1 = self.E[e][1]
    n0 = self.next(h0)
    n1 = self.next(h1)
    p0 = self.next(n0)
    p1 = self.next(n1)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0]
    w0 = self.H[p1][0]
    w1 = self.H[p0][0]
    return (not self.incircle(v0,v1,w1,w0)) and (not self.incircle(v0,w0,v1,w1))
  
  def delaunay (self):
    done = False
    while not done:
      done = True
      for e in range(0,len(self.E)):
        if not self.e_legal(e):
          self.swapedge(e)
          done = False

  # return if the two vertex of the associated he edge forms a ccw triangle with given vertex
  def h_ccw (self, he, v):
    return self.ccw(self.H[he][0],v,self.H[self.next(he)][0])

  # return a triangulation of points (X,Y) using the incremental algorithm
  def triangulate (self, X, Y):
    for (x,y) in zip(X,Y):
      self.addvertex(x,y)
    I = np.argsort(X)
    if self.ccw(I[0],I[1],I[2]):
      self.addtriangle(I[0],I[1],I[2]) 
    else:
      self.addtriangle(I[0],I[2],I[1])
    bt = 0   # bottom border vertex
    # for each remaining vertex to be included in triangulation
    for i in I[3:len(X)]:  
      hbt = self.border_h(bt)
      if self.h_ccw(hbt,i): 
        he = self.h_prevborder(hbt)
        while self.h_ccw(he,i):     # try to move bt backward
          hbt = he
          he = self.h_prevborder(he)
      else:
        hbt = self.h_nextborder(hbt)
        while not self.h_ccw(hbt,i): # try to move bt forward
          hbt = self.h_nextborder(hbt)
      bt = self.H[hbt][0] # update bottom vertex accordingly
      self.addtriangle(self.H[hbt][0],i,self.H[self.next(hbt)][0])  # add first triangle
      he = self.h_nextborder(hbt)
      while self.h_ccw(he,i):     # add remaining triangle fan
        self.addtriangle(self.H[he][0],i,self.H[self.next(he)][0])  # add first triangle
        he = self.h_nextborder(he)

  # compute distance between two vertices
  def distance (self, v0, v1):
    c0 = self.C[v0]
    c1 = self.C[v1]
    return utl.distance(c0,c1)

  # compute triangle area
  def t_area (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    e0 = self.edgevector(h0)
    e1 = self.edgevector(h1)
    return utl.length(utl.cross(e0,e1))

  # compute the unit normal vector of a triangle
  def t_normal (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    e0 = self.edgevector(h0)
    e1 = self.edgevector(h1)
    return utl.normalize(utl.cross(e0,e1))

  # compute the smooth normal at a vertex
  def v_smooth_normal (self, v):
    s = [0,0,0]
    h0 = h = self.V[v]
    while True:
      a = self.h_angle(h)
      n = self.t_normal(self.H[h][2])
      s = utl.add(s,utl.scalar_mult(n,a)) 
      h = self.mate(self.previous(h))
      if h == -1 or h == h0:  
        break
    if h == -1:
      h = self.next(self.mate(h0))
      while h != -1:
        a = self.h_angle(h)
        n = self.t_normal(self.H[h][3])
        s = utl.add(s,utl.scalar_mult(n,a)) 
        h = self.next(self.mate(h0))
    return utl.normalize(s)

  # return the edge vector associated to he of a triangle
  def edgevector (self, h0):
    h1 = self.next(h0)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0] 
    c0 = self.C[v0]
    c1 = self.C[v1]
    return utl.sub(c1,c0)

  def generate_baricentric_points (self, n):
    points = []
    for i in range(0,len(self.T)):
      points.append((i,[1/3,1/3,1/3]))
    return points

  # randomly generate n points on the triangulation
  def generate_random_points (self, n):
    # compute probability to choose each triangle
    points = []
    area = 0
    pi = []
    for i in range(len(self.T)):
      a = self.t_area(i)
      pi.append(a)  
      area += a
    for i in range(len(self.T)):
      pi[i] /= area
    # generate the points for each triangle
    for i in range(len(self.T)):
      ni = int(round(pi[i]*n,0))
      for j in range(ni):
        # sample the triangle uniformly
        e1 = rd.random()
        e2 = rd.random()
        s1 = math.sqrt(e1)
        u = 1 - s1
        v = e2 * s1
        points.append((i,[u,v,1-u-v]))
    return points

  # return the coordinates of a point in the triangle, provided the baricentric coordinates
  def t_getcoord (self, t, uvw):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0]
    v2 = self.H[h2][0]
    assert(v0 < len(self.C) and v1 < len(self.C) and v2 < len(self.C))
    c0 = self.C[v0]
    c1 = self.C[v1]
    c2 = self.C[v2]
    return [
      c0[0]*uvw[0] + c1[0]*uvw[1] + c2[0]*uvw[2],
      c0[1]*uvw[0] + c1[1]*uvw[1] + c2[1]*uvw[2],
      c0[2]*uvw[0] + c1[2]*uvw[1] + c2[2]*uvw[2],
    ]


##################################################################3
# add an edge to the list: v0, v1, t; with v0<v1       
def appendedge (E, v0, v1, he, t):
  if (v0 < v1):
    E.append([v0,v1,he,t])
  else:
    E.append([v1,v0,he,t])