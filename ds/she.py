# SHE: Supporting HalfEdge Data Structure
# Waldemar Celes
# Tecgraf Institute of PUC-Rio
# celes@tecgraf.puc-rio.br

# Index-based implementation of the Supporitng Halfedge Datastructure for intrinsic triangulation
# An edge on the border has its second halfedge set to -1

import copy
import numpy as np
import scipy
import math
from . import utl
from .theap import THeap

L_MIN = 1e-10

class IntrinsicMesh:
  '''Supporting Halfedge Data Structure for intrinsic triangulations'''

  # create a intrinsic triangulation based on the extrinsic one provided
  def __init__ (self, HE, mollification_factor=None):
    self.HE = HE # supporting extrinsic mesh
    self.V = copy.deepcopy(HE.V)  # one halfedge index associated to vertex: he
    self.E = copy.deepcopy(HE.E)  # the two halfedge indices that form the edge: [he0,he1]
    self.T = copy.deepcopy(HE.T)  # one halfedge index associated to the triangle: he
    self.H = copy.deepcopy(HE.H)  # vertex, edge, triangle, and next halfedge associated to halfedge: [v,e,t,he]
    self.L = []  # edge length: l
    self.S = []  # supporting he associated to extrinsic triangle: [h]
    self.A = []  # supporting he angle associated to extrinsic triangle: [phi]

    # compute edge lengths
    for e in HE.E:
      h0 = e[0] 
      h1 = HE.next(h0)
      v0 = HE.H[h0][0]  # first vertex
      v1 = HE.H[h1][0]  # second vertex
      self.L.append(HE.distance(v0,v1))
    self.lmin = min(self.L)

    # compute mollification
    if mollification_factor:
      self.mollification(mollification_factor)
    # mark narrow vertices
    self.mark_narrow_vertices(60/180*math.pi)

    # set supporting halfedge information
    # both triangulation are equal in the beginning
    for he in HE.T:
      self.S.append(he)  # assign the intrinsic he associated to the extrinsic triangle 
      self.A.append(0.0) # assign the intrinsic he angle w.r.t. the extrinsic triangle halfedge
    self.check_consistency()

  # ensure li >= lj + lk + delta
  def mollification (self, delta):
    epsilon = 0
    for t in range(len(self.T)):
      l = self.t_get_lens(t)
      for i in range(3):
        j = (i+1) % 3
        k = (j+1) % 3
        d = delta + l[i] - l[j] - l[k]
        if d > epsilon:
          epsilon = d
    if epsilon == 0:
      return False
    for e in range(len(self.L)):
      self.L[e] += epsilon
    return True
  
  # mark extrinsic vertices with angle less than a limit
  def mark_narrow_vertices (self, limit):
    self.narrow = []
    for v in range(len(self.V)):
      self.narrow.append(False)
      if self.v_angle(v) < limit:
        self.narrow[v] = True
  
  # check if a triangle has a narrow vertex
  def t_narrow (self, t):
    inc = self.t_get_inc(t)
    for v in inc:
      if v < len(self.HE.V) and self.narrow[v]:
        return True
    return False

  # get min edge length
  def get_lmin (self):
    return min(self.L)

  # get vertex angle
  def v_angle (self, v):
    h0 = h = self.V[v]
    a = 0
    while True:
      a += self.h_angle(h)
      h = self.mate(self.previous(h))
      if h == -1 or h == h0:  
        break
    if h == -1:
      m = self.mate(h0)
      while m != -1:
        h = self.next(m)
        a += self.h_angle(h)
        m = self.mate(h)
    return a

  # return triangle incidence
  def t_get_inc (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    return [
      self.H[h0][0],
      self.H[h1][0],
      self.H[h2][0],
    ]
  
  def print_info (self):
    # edges on border
    count = 0
    for e in self.E:
      if e[1] == -1:
        count += 1
    # vertex on border
    vcount = 0
    for v in range(0,len(self.V)):
      if self.border_h(v) != -1:
        vcount += 1
    # isolated vertex
    dangling_verts = 0
    for h in self.V:
      if h == -1:
        dangling_verts += 1

    print("# verts: ", len(self.V))
    print("# edges: ", len(self.E))
    print("# tris:  ", len(self.T))
    print("# genus: ", (2 - (len(self.V)-len(self.E)+len(self.T)))//2)
    print("# boders:",count)
    print("# v on boders:",vcount)
    print("# dangling verts:",dangling_verts)
    print('lmin_0:',self.lmin)
    print("amin:",self.get_angle_min()*180/math.pi)
    print("amax:",self.get_angle_max()*180/math.pi)
    print("lmin:",min(self.L))
    
  # check consistency of intrinsic triangles
  def check_consistency (self):
    for t, h0 in enumerate(self.T):
      h1 = self.next(h0)
      h2 = self.next(h1)
      assert(h0 == self.next(h2))
      l0 = self.L[self.H[h0][1]]
      l1 = self.L[self.H[h1][1]]
      l2 = self.L[self.H[h2][1]]
      assert(l0 + l1 > l2)
      assert(l1 + l2 > l0)
      assert(l2 + l0 > l1)
      a0 = math.acos((l0*l0 + l2*l2 - l1*l1)/(2*l0*l2))
      a1 = math.acos((l1*l1 + l0*l0 - l2*l2)/(2*l1*l0))
      a2 = math.acos((l2*l2 + l1*l1 - l0*l0)/(2*l2*l1))
      assert(l0*l0 + l2*l2 - 2*l0*l2 * math.cos(a0) > 0)
      assert(l1*l1 + l0*l0 - 2*l1*l0 * math.cos(a1) > 0)
      assert(l2*l2 + l1*l1 - 2*l2*l1 * math.cos(a2) > 0)
      s = (l0 + l1 + l2) / 2
      assert(s*(s-l0)*(s-l1)*(s-l2) > 0)
    for a in self.A:
      assert a <=0 and a > -math.pi
    
  # check if halfedge vertex is on border
  def t_on_border (self, h0):
    h1 = self.next(h0)
    h2 = self.next(h1)
    return (self.border_h(self.H[h0][0]) != -1 or 
            self.border_h(self.H[h1][0]) != -1 or 
            self.border_h(self.H[h2][0]) != -1
           )

  # compute average value of edge length
  def l_average (self):
    return sum(self.L) / len(self.L)
  
  # compute maximum value of edge length
  def l_max (self):
    lmax = 0
    for l in self.L:
      if l > lmax:
        lmax = l
    return l

  # compute center of 3d triangle layout
  # the circumcenter of internal triangles or 
  # the barycenter for triangles on border 
  # the function also receive the triangle 2d layout
  def t_center (self, h0, v):
    if self.t_on_border(h0):
      return utl.barycenter(v[0],v[1],v[2])
    else:
      return utl.circumcenter(v[0],v[1],v[2])

  # displace vertex to weighted average of the circumcenter positions 
  def vertex_displacement (self, v, tset=None):
    if v < len(self.HE.V):
      return False # extrinsic vertex cannot be displaced
    if self.border_h(v) != -1:
      return False # vertex on border cannot be displace
    # collect incident halfedge in ccw order
    hlist = [self.V[v]]
    h = hlist[0]
    while True:
      h = self.mate(self.previous(h))
      if h == hlist[0]:
        break
      hlist.append(h)
    # compute layout position of star, assuming v at (0,0)
    plist = []
    phi = 0
    for h in hlist:
      e = self.H[h][1]
      l = self.L[e]
      plist.append([l*math.cos(phi),l*math.sin(phi)])
      phi += self.h_angle(h)
    # compute coordinates of incident triangles
    vlist = []   
    n = len(plist)
    for i in range(0,n):
      vlist.append([[0,0],plist[i],plist[(i+1)%n]])
    v0 = [0,0]
    atotal = 0
    for i in range(0,n):
      c = self.t_center(hlist[i],vlist[i])
      a = utl.area(*vlist[i])
      v0[0] += c[0]*a
      v0[1] += c[1]*a
      atotal += a
    v0[0] /= atotal
    v0[1] /= atotal
    flist = self.move_all_images(v,hlist,v0,plist)
    # check consistency: no triangle flip
    done = False
    while not done:
      done = True
      for i in range(0,n):
        if utl.orient(flist[i],flist[(i+1)%n],v0)/2/utl.distance(flist[i],flist[(i+1)%n]) <= 1e-5:
          return
    # simulate removing halfedges to update sign
    for h0 in hlist:
      m = self.mate(h0)
      self.update_removal(m)
    # adjust edge lengths
    for i, h in enumerate(hlist):
      e = self.H[h][1]
      self.L[e] = utl.distance(v0,flist[i])
    # simulate inserting halfedges to update sign
    for h in hlist:
      m = self.mate(h)
      self.update_insertion(m)
    # mark modified triangles, if asked
    if tset:
      for h in hlist:
        tset[self.H[h][2]] = True
    return True

  # move all image of the same vertex on the plane
  def move_all_images (self, v, hlist, v0, plist):
    flist = []  # fixed positions
    for i, h in enumerate(hlist):
      w = self.H[self.mate(h)][0]
      if v == w:
        flist.append([plist[i][0] + v0[0], plist[i][1] + v0[1]])
      else:
        flist.append(plist[i])
    return flist

  # atomic operation: update supporting information due to removal of an hafedge from vertex
  def update_removal (self, h):
    v = self.H[h][0]
    if v < len(self.HE.V):   # check if vertex correspond to a extrinsic one
      helist = self.HE.adj_vh(v)
      # check for update in all incident extrinsic triangles
      for he in helist:
        te = self.HE.H[he][2]
        if self.S[te] == h:
          ref = self.next(self.mate(h))  # next of mate
          self.S[te] = ref
          self.A[te] -= self.h_angle(ref)

  # atomic operation: update supporting information due to insertion of an hafedge to vertex
  def update_insertion (self, h):
    v = self.H[h][0]
    if v < len(self.HE.V):   # check if vertex correspond to a extrinsic one
      helist = self.HE.adj_vh(v)
      # check for update in all incident extrinsic triangles
      for he in helist:
        te = self.HE.H[he][2]
        ref = self.S[te]
        if self.mate(self.previous(ref)) == h:
          theta = self.h_angle(ref)
          if (self.A[te] + theta) <= 0:
            self.S[te] = h 
            self.A[te] += theta
            assert self.A[te] <= 0 and self.A[te] > -math.pi
  
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
  
  # conditional swapedge (does not allow triangle flip)
  def conditional_swapedge (self, e):
    if self.e_isborder(e):
      return
    h = self.E[e]
    a0 = self.h_angle(h[0]) 
    b0 = self.h_angle(self.next(h[0]))
    b1 = self.h_angle(h[1]) 
    a1 = self.h_angle(self.next(h[1]))
    if (a0+a1 < 0.95*math.pi and b0+b1 < 0.95*math.pi):
      self.swapedge(e)
  
  # swap edge
  def swapedge (self, e):
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

    self.update_removal(h0)
    self.update_removal(h1)

    # compute new edge length
    a0 = self.t_opposite_angle(n0)
    a1 = self.t_opposite_angle(p1)
    l0 = self.L[self.H[p0][1]]
    l1 = self.L[self.H[n1][1]]
    self.L[e] = math.sqrt(l0*l0 + l1*l1 - 2*l0*l1*math.cos(a0+a1))

    # update topological info
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

    self.update_insertion(h0)
    self.update_insertion(h1)

    return True
  
  # get triangle angle opposite to a given the halfedge he
  def t_opposite_angle (self, he):
    h0 = he
    h1 = self.next(h0)
    h2 = self.next(h1)
    l0 = self.L[self.H[h0][1]]
    l1 = self.L[self.H[h1][1]]
    l2 = self.L[self.H[h2][1]]
    c = utl.clamp((l1*l1+l2*l2-l0*l0)/(2*l1*l2),-1,1)
    return math.acos(c)

  # get triangle angle at halfedge vertex
  def h_angle (self, h0):
    h1 = self.next(h0)
    h2 = self.next(h1)
    l0 = self.L[self.H[h0][1]]
    l1 = self.L[self.H[h1][1]]
    l2 = self.L[self.H[h2][1]]
    c = utl.clamp((l0*l0+l2*l2-l1*l1)/(2*l0*l2),-1,1)
    return math.acos(c)

  # check if the edge is legal
  def e_legal (self, e):
    if self.e_isborder(e):
      return True
    h0 = self.E[e][0]
    h1 = self.E[e][1]

    #if self.H[self.previous(h0)][0] == self.H[self.previous(h1)][0]:
    #  return True

    a = self.t_opposite_angle(h0)
    b = self.t_opposite_angle(h1)
    return a + b <= math.pi + 1e-5
  
  # convert triangution into Delaunay 
  # return number of edge flips
  def delaunay (self):
    n = 0
    eset = {}
    for i in range(0,len(self.E)):
      eset[i] = True
    n += self.delaunay_flip(eset)
    return n

  # check Delaunay condition for the queued edges
  # if triangle set is provided, collect all affected triangles
  # return number of performed flips
  def delaunay_flip (self, eset, tset=None): 
    n = 0 
    while eset:
      e,_ = eset.popitem() 
      if not self.e_legal(e):
        self.swapedge(e)
        n += 1
        h0 = self.E[e][0]
        h1 = self.E[e][1]
        if tset:
          tset[self.H[h0][2]] = True
          tset[self.H[h1][2]] = True
        eset[self.H[self.next(h0)][1]] = True
        eset[self.H[self.previous(h0)][1]] = True
        eset[self.H[self.next(h1)][1]] = True
        eset[self.H[self.previous(h1)][1]] = True
    return n

  # displace all intrinsic vertices and perform delaunay
  def displace_delaunay (self):
    for v in range(len(self.HE.V),len(self.V)):
      self.vertex_displacement(v)
    self.delaunay()

  # displace all intrinsic vertices n times
  def displace_all (self, n=1):
    for i in range(n):
      for v in range(len(self.HE.V),len(self.V)):
        self.vertex_displacement(v)
  
  # get the angles of a triangle
  def t_get_angles (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    assert(h0 == self.next(h2))
    return [self.h_angle(h0),self.h_angle(h1),self.h_angle(h2)]
  
  # get triangle edges
  def t_get_edges (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    return [self.H[h0][1],self.H[h1][1],self.H[h2][1]]

  # get the edge lens of a triangle
  def t_get_lens (self, t):
    e = self.t_get_edges(t)
    return [self.L[e[0]], self.L[e[1]], self.L[e[2]]]

  # get triangle edges
  def t_edges (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    return [self.H[h0][1], self.H[h1][1], self.H[h2][1]]

  # get triangle edges
  def t_halfedges (self, t):
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    return [h0,h1,h2]
    
  # return a list of triangle angles
  def get_angle_table (self):
    A = []
    for i in range(0,len(self.T)):
      A.append(self.t_get_angles(i))
    return A

  # compute min angle per vertex
  def compute_angle_min (self):
    result = [2*math.pi for i in range(0,len(self.V))]
    for t in range(0,len(self.T)):
      h = self.T[t]
      for i in range(0,3):
        v = self.H[h][0]
        a = self.h_angle(h)
        if a < result[v]:
          result[v] = a
        h = self.next(h)
    return result

  # compute surface curvatures at vertices
  def v_curvatures (self):
    result = [2*math.pi for i in range(0,len(self.V))]
    for t in range(0,len(self.T)):
      h = self.T[t]
      for i in range(0,3):
        v = self.H[h][0]
        result[v] -= self.h_angle(h)
        h = self.next(h)
    n = 0
    limit = 2*math.pi/100
    for c in result:
      if abs(c) < limit:
        n += 1
    return result
  
  # get min angle
  def get_angle_min (self):
    amin = 2*math.pi
    for i in range(0,len(self.T)):
      if not self.t_narrow(i):
        a = self.t_get_angles(i)
        for j in range(0,3):
          if a[j] < amin:
            amin = a[j]
    return amin

  # get min angle, discarding constrained angles
  def get_free_angle_min (self):
    amin = 2*math.pi
    for h0 in self.T:
      h1 = self.next(h0)
      h2 = self.next(h1)
      v0 = self.H[h0][0]
      v1 = self.H[h1][0]
      v2 = self.H[h2][0]
      if v0 < len(self.HE.V):
        a = self.h_angle(h0)
        if a < amin:
          amin = a
      if v1 < len(self.HE.V):
        a = self.h_angle(h1)
        if a < amin:
          amin = a
      if v2 < len(self.HE.V):
        a = self.h_angle(h2)
        if a < amin:
          amin = a
    return amin

  # get max angle
  def get_angle_max (self):
    amax = 0
    for i in range(0,len(self.T)):
      if not self.t_narrow(i):
        a = self.t_get_angles(i)
        for j in range(0,3):
          if a[j] > amax:
            amax = a[j]
    return amax
  
  # return corresponding edge length, given a halfedge
  def h_edge_len (self, he):
    return self.L[self.H[he][1]]

  # transform set of coordinates to barycentric coordinate of a triangle
  def to_baricentric (self, v, coord):
    t_area = utl.area(v[0],v[1],v[2])
    uv = []
    for q in coord:
      uv.append(
        [
          utl.area(v[1],v[2],q)/t_area,
          utl.area(v[2],v[0],q)/t_area,
        ]
      ) 
    return uv
  
  # return the area of the triangle associated to the give he
  def h_area (self, h0):
    h1 = self.next(h0)
    h2 = self.next(h1)
    e0 = self.H[h0][1]
    e1 = self.H[h1][1]
    e2 = self.H[h2][1]
    l0 = self.L[e0]
    l1 = self.L[e1]
    l2 = self.L[e2]
    s = (l0 + l1 + l2) / 2
    return math.sqrt(s*(s-l0)*(s-l1)*(s-l2))
  
  # return list of 3d triangles: [[x,y,z],[x,y,z],[x,y,z],...]
  def to_3d_triangles (self, te, uv):
    h0 = self.HE.T[te]
    h1 = self.HE.next(h0)
    h2 = self.HE.next(h1)
    v = [  # extrinsic triangle 3d coordinate
      self.HE.C[self.HE.H[h0][0]],
      self.HE.C[self.HE.H[h1][0]],
      self.HE.C[self.HE.H[h2][0]]
    ]
    tcoord = []  
    v0 = [v[0][0]*uv[0][0] + v[1][0]*uv[0][1] + v[2][0]*(1-uv[0][0]-uv[0][1]),
          v[0][1]*uv[0][0] + v[1][1]*uv[0][1] + v[2][1]*(1-uv[0][0]-uv[0][1]),
          v[0][2]*uv[0][0] + v[1][2]*uv[0][1] + v[2][2]*(1-uv[0][0]-uv[0][1]),
         ]
    v1 = [v[0][0]*uv[1][0] + v[1][0]*uv[1][1] + v[2][0]*(1-uv[1][0]-uv[1][1]),
          v[0][1]*uv[1][0] + v[1][1]*uv[1][1] + v[2][1]*(1-uv[1][0]-uv[1][1]),
          v[0][2]*uv[1][0] + v[1][2]*uv[1][1] + v[2][2]*(1-uv[1][0]-uv[1][1]),
         ]
    for i in range(2,len(uv)):
      v2 = [v[0][0]*uv[i][0] + v[1][0]*uv[i][1] + v[2][0]*(1-uv[i][0]-uv[i][1]),
            v[0][1]*uv[i][0] + v[1][1]*uv[i][1] + v[2][1]*(1-uv[i][0]-uv[i][1]),
            v[0][2]*uv[i][0] + v[1][2]*uv[i][1] + v[2][2]*(1-uv[i][0]-uv[i][1]),
          ]
      tcoord.append([v0,v1,v2])
      v1 = v2
    return tcoord

  # generate the common subdivision of the two meshes (extrinsic and intrinsic)
  # return three lists: 
  #   elist = [te_id, ...]  -- list of extrinsic triangle ids
  #   ilist = [ti_id, ...]  -- list of intrinsic triangle ids
  #   clist = [[[x,y,z],[x,y,z],[x,y,z]],...]  -- list of triangle coordinates in 3d
  def generate_common_subdivision2 (self):
    elist = []
    ilist = []
    clist = []  
    for te in range(0,len(self.HE.T)):
      p = self.te_flatten(te)
      il, cl = self.get_overlapping_triangles(te,p,True)
      elist += [te] * len(il)
      ilist += il
      clist += cl
    return elist, ilist, clist

  # get list of overlapping triangles in 2D
  # given a extrinsic 2d triangle, get the list of overlapping intrisic triangles
  # return two lists: tlist = [t_id,...], clist = [[[x,y,z],[x,y,z],[x,y,z]],...]
  # if flag_3d is False, the coordiantes are in 2d, clist = [[[x,y],[x,y],[x,y]],...]
  def get_overlapping_triangles (self, te, p, flag_3d):
    h0 = self.S[te]
    phi0 = self.A[te]
    visited = {}
    tlist = []
    clist = []
    self.search_overlapping_triangles(visited,tlist,clist,te,p,[0,0],h0,phi0,flag_3d)
    return tlist, clist

  def search_overlapping_triangles (self, visited, tlist, clist, te, p, v0, h0, phi0, flag_3d):
    t = self.H[h0][2]
    if t in visited:
      return
    visited[t] = True  # mark as visited
    h1 = self.next(h0)
    h2 = self.next(h1)
    e0 = self.H[h0][1]
    e1 = self.H[h1][1]
    phi1 = phi0 + math.pi - self.h_angle(h1)
    phi2 = phi1 + math.pi - self.h_angle(h2)

    v1 = [
      v0[0] + self.L[e0] * math.cos(phi0),
      v0[1] + self.L[e0] * math.sin(phi0),
    ]
    v2 = [
      v1[0] + self.L[e1] * math.cos(phi1),
      v1[1] + self.L[e1] * math.sin(phi1),
    ]

    v = [v0,v1,v2]
    out = utl.clip(p,v)   # get intersection between the two triangles
    if out:
      if flag_3d:
        uv = self.to_baricentric(p,out)
        tcoord = self.to_3d_triangles(te,uv)
      else:
        tcoord = [[v0,v1,v2]]
      tlist += [t] * len(tcoord)
      clist += tcoord
      m1 = self.mate(h1)
      if m1 != -1:
        self.search_overlapping_triangles(visited,tlist,clist,te,p,v2,m1,phi1+math.pi,flag_3d)
      m2 = self.mate(h2)
      if m2 != -1:
        self.search_overlapping_triangles(visited,tlist,clist,te,p,v0,m2,phi2+math.pi,flag_3d)

 # generate the common subdivision of the two meshes (extrinsic and intrinsic)
  # return three lists: 
  #   elist = [te_id, ...]  -- list of extrinsic triangle ids
  #   ilist = [ti_id, ...]  -- list of intrinsic triangle ids
  #   clist = [[[x,y,z],[x,y,z],[x,y,z]],...]  -- list of triangle coordinates in 3d
  def generate_common_subdivision (self, feedback=False):
    elist = []
    ilist = []
    clist = []  
    mark = [-1 for i in range(0,len(self.T))]
    for te in range(0,len(self.HE.T)):
      if feedback:
        print(te)
      ce = self.te_flatten(te)
      trace = self.collect_overlapping_triangles(te,ce,mark)
      for t, v in trace:
        out = utl.clip(ce,v)   # get intersection between the two triangles
        if out:
          uv = self.to_baricentric(ce,out)
          tcoord = self.to_3d_triangles(te,uv)
          elist += [te] * len(tcoord)
          ilist += [t] * len(tcoord)
          clist += tcoord
    return elist, ilist, clist

  # collect all overlapping triangles
  def collect_overlapping_triangles (self, te, ce, mark):
    trace, front = self.trace_perimeter(te,ce,mark)
    while front:
      v0, h0, phi0 = front.pop()
      t = self.H[h0][2]
      if mark[t] != te:
        v1, v2, phi1, phi2 = self.compute_flattern(v0,h0,phi0)
        h1 = self.next(h0)
        h2 = self.next(h1)
        m1 = self.mate(h1)
        m2 = self.mate(h2)
        gc = [
          (v0[0]+v1[0]+v2[0])/3,
          (v0[1]+v1[1]+v2[1])/3,
        ]
        if utl.in_triangle(ce,gc):
          trace.append((t,[v0,v1,v2]))
          mark[t] = te
          front.append((v2,m1,phi1+math.pi))
          front.append((v0,m2,phi2+math.pi))
    return trace

  # compute the flatten coordiantes of a triangle
  def compute_flattern (self, v0, h0, phi0, v1=None):
    e0 = self.H[h0][1]
    l0 = self.L[e0]
    if v1 == None:
      v1 = [v0[0] + l0*math.cos(phi0) ,v0[1] + l0*math.sin(phi0)]
    h1 = self.next(h0)
    h2 = self.next(h1)
    # compute v2
    e1 = self.H[h1][1]
    e2 = self.H[h2][1]
    l1 = self.L[e1]
    l2 = self.L[e2]
    alpha = math.acos((l0*l0+l1*l1-l2*l2)/(2*l0*l1))
    phi1 = phi0 + math.pi - alpha
    v2 = [v1[0] + l1*math.cos(phi1),
          v1[1] + l1*math.sin(phi1)
        ]
    beta = math.acos((l0*l0+l2*l2-l1*l1)/(2*l0*l2))
    phi2 = phi0 + beta + math.pi
    return v1,v2,phi1,phi2

  # trace triangle perimeter,
  # while collecting halfedge to an advancing front procedure
  # returns two dictionary:
  #  traced triangles: [t] = [v0,v1,v2]
  #  front triangles: [h0] = (v0,phi0)
  def trace_perimeter (self, te, ce, mark):  # <-- trace, front
    trace = []                # collect all visited triangles (without duplication)
    front = []                # collect all advancing-front triangles (without duplication)
    h0e = self.HE.T[te]
    h1e = self.HE.next(h0e)
    h2e = self.HE.next(h1e)
    ve = [self.HE.H[h0e][0],self.HE.H[h1e][0],self.HE.H[h2e][0]] # vertex indices
    phie = [                  # extrinsic triangle angles
      self.HE.h_angle(h0e),
      self.HE.h_angle(h1e),
      self.HE.h_angle(h2e),
    ]
    theta = 0       # extrinsic triangle edge aligned to x axis
    # perform trace along each edge
    h0 = self.S[te]
    phi0 = self.A[te]
    for i in range(0,3):
      to = ce[i]          # origin
      tp = ce[(i+1)%3]    # target position
      tv = ve[(i+1)%3]    # target index
      v0 = ce[i]
      v1 = None
      N = 0
      while True:
        N += 1
        if N == 200:
          print("no convergence: te =",te)
          break
        v1, v2, phi1, phi2 = self.compute_flattern(v0,h0,phi0,v1)
        # mark triangle as traced
        t = self.H[h0][2]
        trace.append((t,[v0,v1,v2]))
        mark[t] = te
        # check if target was reached
        h1 = self.next(h0)
        h2 = self.next(h1)
        if self.H[h1][0] == tv or self.H[h2][0] == tv:
          break
        # check if it crosses edge v1-v2
        m1 = self.mate(h1)
        m2 = self.mate(h2)
        if utl.orient(to,tp,v0) <= 0 or utl.orient(to,tp,v1) >= 0 or utl.orient(to,tp,v2) >= 0:
          assert(m1 != -1)
          # check if neighbor should belongs to search front
          if (m2 != -1 and 
              mark[self.H[m2][2]] != te and
              utl.in_triangle(ce,v0) and
              utl.in_triangle(ce,v2)
             ):
            front.append((v0,m2,phi2+math.pi))
          v0 = v2  # v1 remains the same
          h0 = m1
          phi0 = phi1 + math.pi
          continue 
        elif utl.orient(v2,v0,tp) <= 0:
          assert(m2 != -1)
          v1 = v2  # v0 remains the same
          h0 = m2
          phi0 = phi2 + math.pi
          continue; 

      # update h0 and phi0 to the trace the next extrinsic edge
      if self.H[h1][0] == tv:
        h0 = h1
        phi0 = phi1
      else:
        h0 = h2
        phi0 = phi2
      theta = theta + math.pi - phie[(i+1)%3]
      phi0 = phi0 % (2*math.pi)
      v0 = tp
      while phi0 > theta:
        # check if neighbor should belongs to search front
        v1, v2, phi1, phi2 = self.compute_flattern(v0,h0,phi0)
        m1 = self.mate(self.next(h0))
        if (m1 != -1 and 
            mark[self.H[m1][2]] != te and
            utl.orient(ce[(i+0)%3],ce[(i+1)%3],v1) >= 0 and
            utl.orient(ce[(i+1)%3],ce[(i+2)%3],v1) >= 0 and 
            utl.orient(ce[(i+2)%3],ce[(i+0)%3],v1) >= 0 and
            utl.orient(ce[(i+0)%3],ce[(i+1)%3],v2) >= 0 and 
            utl.orient(ce[(i+1)%3],ce[(i+2)%3],v2) >= 0 and 
            utl.orient(ce[(i+2)%3],ce[(i+0)%3],v2) >= 0
            ):
          front.append((v2,m1,phi1+math.pi))
        m = self.mate(h0)
        if m == -1:
          break
        h0 = self.next(m) 
        phi0 = phi0 - self.h_angle(h0)
        v1,v2,phi1,phi2 = self.compute_flattern(v0,h0,phi0)
        t = self.H[h0][2]
        if mark[t] != te:
          trace.append((t,[v0,v1,v2]))
          mark[t] = te
    return trace, front
  
  # procedure to locate point at the intrinsic mesh inside a extrinsic triangle given its baricentric coordinate
  def te_point_location (self, te, uvw):   #  <-- he, uvw_i
    v = self.te_flatten(te)
    p = utl.from_baricentric(v[0],v[1],v[2],uvw)
    h0 = self.S[te]
    phi0 = self.A[te]
    return self.point_location(p,h0,phi0)

  # procedure to locate point p in 2d space.
  # point p is expressed in a 2d system with origin at (0,0). 
  # h0 is the halfedge anchored at the origin with angle
  # equal to phi0 wrt the x axis. 
  def point_location (self, p, h0, phi0):  # <-- h0, uvw
    e0 = self.H[h0][1]
    l0 = self.L[e0]
    v0 = [0, 0]
    v1 = [l0*math.cos(phi0) ,l0*math.sin(phi0)];
    while True:
      # compute v2
      h1 = self.next(h0)
      h2 = self.next(h1)
      e1 = self.H[h1][1]
      e2 = self.H[h2][1]
      l1 = self.L[e1]
      l2 = self.L[e2]
      alpha = math.acos((l0*l0+l1*l1-l2*l2)/(2*l0*l1))
      phi1 = phi0 + math.pi - alpha
      v2 = [v1[0] + l1*math.cos(phi1),
            v1[1] + l1*math.sin(phi1)
           ]
      # check if needs to cross edge v1-v2
      if not utl.ccw(v1,v2,p) and (utl.ccw(v2,v0,p) or utl.crossing(v1,v2,p)):
        m1 = self.mate(h1)
        if (m1!=-1):    # check if border is crossed unexpectedely
          v0 = v2  # v1 remains the same
          l0 = l1
          h0 = m1
          phi0 = phi1 + math.pi
          continue 
      elif (not utl.ccw(v2,v0,p)):
        m2 = self.mate(h2)
        if (m2!=-1):   # check if border is crossed unexpectedely
          beta = math.acos((l0*l0+l2*l2-l1*l1)/(2*l0*l2))
          v1 = v2  # v0 remains the same
          l0 = l2
          h0 = m2
          phi0 = phi0 + beta
          continue; 
      a = utl.area(v0,v1,v2)
      uvw = [0,0,0]
      uvw[0] = utl.area(p,v1,v2) / a
      uvw[1] = utl.area(p,v2,v0) / a
      uvw[2] = 1 - uvw[0] - uvw[1]
      return h0, uvw
  
  def te_flatten (self, t):
    h0 = self.HE.T[t]
    h1 = self.HE.next(h0)
    h2 = self.HE.next(h1)
    v0 = np.array(self.HE.C[self.HE.H[h0][0]])
    v1 = np.array(self.HE.C[self.HE.H[h1][0]])
    v2 = np.array(self.HE.C[self.HE.H[h2][0]])
    u = v1 - v0
    v = v2 - v0
    n = np.cross(u,v)
    t = u / np.linalg.norm(u)
    n = n / np.linalg.norm(n)
    b = np.cross(n,t)
    B = np.array([t,b,n])
    p1 = B.dot(u)
    p2 = B.dot(v)
    return [[0,0],p1[0:2].tolist(),p2[0:2].tolist()]

  # compute flatten v2
  def compute_v2 (self, v0, h0, phi0):
    p = self.previous(h0)
    e2 = self.H[p][1]
    l2 = self.L[e2]
    a0 = self.h_angle(h0) 
    phi1 = phi0 + a0
    return [v0[0] + l2*math.cos(phi1),
            v0[1] + l2*math.sin(phi1)
           ]
   
  # flatten triangle given one of its halfedges
  def t_flatten (self, h0):
    e0 = self.H[h0][1]
    l0 = self.L[e0]
    v0 = [0,0]
    v1 = [l0,0]
    v2 = self.compute_v2(v0,h0,0)
    return [v0,v1,v2]

  # refine triangle if it minimun angle is less than amin,
  # maintaing the delaunay property
  def t_refine_if (self, t, amin, eset, tset):
    TOL = 1e-4
    a = self.t_get_angles(t)
    if min(a) >= amin:
      return
    h0 = self.T[t]
    v = self.t_flatten(h0)
    c = utl.circumcenter(v[0],v[1],v[2])
    h0, uvw = self.point_location(c,h0,0)
    if min(uvw) < TOL:
      if max(uvw) > 1-TOL:
        return # point at a vertex; nothing to do (unexpected)
      # refine edge
      h = h0
      for i in range(0,3):
        if uvw[i] < TOL:
          # vertex on opposite edge
          n = self.next(h)
          self.e_refine(n,uvw[(i+1)%3],eset,tset)
          break
        h = self.next(h)
    else:
      # refine triangle
      self.t_refine(h0,uvw,eset,tset)

  # refine a triangle
  # insert the point at uvw in the triangle, forming two new triangles
  # automatically apply delanay criterion at the original triangle edges
  # return the new inserted vertex id
  def t_refine (self, h0, uvw, eset, tset):
    # access existing entities
    t = self.H[h0][2]
    h1 = self.next(h0)
    h2 = self.next(h1)
    v0 = self.H[h0][0]
    v1 = self.H[h1][0]
    v2 = self.H[h2][0]
    # compute local geometry to perform insertion
    c = self.t_flatten(h0)
    p = utl.from_baricentric(c[0],c[1],c[2],uvw)
    # indices of new triangles
    t0 = len(self.T)
    t1 = t0 + 1
    # indices of new halfedges
    h00 = len(self.H)
    h01 = h00 + 1
    h10 = h00 + 2
    h11 = h00 + 3
    h20 = h00 + 4
    h21 = h00 + 5
    # indices of new edges
    e0 = len(self.E)
    e1 = e0 + 1
    e2 = e0 + 2
    # index of new vertex
    v = len(self.V)
    # update existing entities
    self.T[t] = h2
    self.H[h0][2:] = [t0, h11]
    self.H[h1][2:] = [t1, h21]
    self.H[h2][2:] = [t,h01]
    # insert new entities
    self.T.append(h0)  # t0
    self.T.append(h1)  # t1
    self.H.append([v, e0, t0, h0])    # h00
    self.H.append([v0, e0, t, h20])   # h01
    self.H.append([v, e1, t1, h1])    # h10
    self.H.append([v1, e1, t0, h00])  # h11
    self.H.append([v, e2, t, h2])     # h20
    self.H.append([v2, e2, t1, h10])  # h21
    self.E.append([h00,h01])  # e0
    self.E.append([h10,h11])  # e1
    self.E.append([h20,h21])  # e2
    self.L.append(utl.distance(c[0],p)) # e0
    self.L.append(utl.distance(c[1],p)) # e1
    self.L.append(utl.distance(c[2],p)) # e2
    self.V.append(h00)   # v
    self.update_insertion(h01)
    self.update_insertion(h11)
    self.update_insertion(h21)
    #self.vertex_displacement(v) # TODO: was commented
    tset[t] = True
    tset[t0] = True
    tset[t1] = True
    eset[self.H[h0][1]] = True
    eset[self.H[h1][1]] = True
    eset[self.H[h2][1]] = True
    return v
    
  # split edge
  # insert a vertex on the edge at t (parametric coordinate)
  # automatically apply delanay criterion at the original triangle edges
  # return the new inserte vertex id
  def e_refine (self, h0, s, eset, tset):
    # access existing entities
    e = self.H[h0][1]
    # TODO
    if self.L[e] < L_MIN:
      #print("cannot split edge")
      return None
    n0 = self.next(h0)
    p0 = self.previous(h0)
    t0 = self.H[h0][2]
    v2 = self.H[p0][0]
    h1 = self.mate(h0)
    if h1 != -1:
      n1 = self.next(h1)
      p1 = self.previous(h1)
      t1 = self.H[h1][2]
      v3 = self.H[p1][0]
    
    # compute local geometry to perform insertion
    c = self.t_flatten(h0)
    if h1 != -1:
      c.append(self.compute_v2(c[1],h1,-math.pi))  # complete quadrilateral coordinates
    p = [(1-s)*c[0][0] + s*c[1][0],   # point to be inserted
         (1-s)*c[0][1] + s*c[1][1],
        ]

    # indices of new entities 
    t0l = len(self.T)
    h00 = len(self.H)
    h01 = h00 + 1
    m1 = h00 + 2
    m0 = -1
    el = len(self.E)
    e0 = el + 1
    v = len(self.V)
    if h1 != -1:
      t1l = t0l + 1
      h10 = h00 + 3
      h11 = h00 + 4
      m0 = h00 + 5
      e1 = el + 2
    # update existing entities
    self.T[t0] = h0
    self.H[h0][3] = h00
    self.H[n0][2:] = [t0l, h01]
    if h1 != -1:
      self.T[t1] = h1
      self.H[h1][1] = el
      self.H[h1][3] = h10
      self.H[n1][2:] = [t1l, h11]
    self.E[e] = [h0,m0]
    self.L[e] = utl.distance(c[0],p)
    # insert new entities
    self.T.append(n0)  # t0l
    self.H.append([v, e0, t0, p0])    # h00
    self.H.append([v2, e0, t0l, m1])  # h01
    self.H.append([v, el, t0l, n0])   # m1
    self.E.append([m1, h1])    # el
    self.E.append([h00, h01])  # e0
    self.L.append(utl.distance(c[1],p)) # el
    self.L.append(utl.distance(c[2],p)) # e0
    self.V.append(h00)   # v
    if h1 != -1:
      self.T.append(n1)  # t1l
      self.H.append([v, e1, t1, p1])    # h10
      self.H.append([v3, e1, t1l, m0])  # h11
      self.H.append([v, e, t1l, n1])    # m0
      self.E.append([h10, h11])  # e1
      self.L.append(utl.distance(c[3],p)) # e1
    if h1 != -1:
      self.update_insertion(h01)
      self.update_insertion(h11)
      #self.vertex_displacement(v) # TODO: was commented
      tset[t0] = True
      tset[t0l] = True
      tset[t1] = True
      tset[t1l] = True
      eset[self.H[n0][1]] = True
      eset[self.H[n1][1]] = True
      eset[self.H[p0][1]] = True
      eset[self.H[p1][1]] = True
    else:
      self.update_insertion(h01)
      #self.vertex_displacement(v) # TODO: was commented
      tset[t0] = True
      tset[t0l] = True
      eset[self.H[n0][1]] = True
      eset[self.H[p0][1]] = True
    return v

  # refine triangulation maintaining delaunay property
  # eliminate all angles less than amin
  def refine_mesh (self, amin):
    tset = {}
    eset = {}
    for i in range(0,len(self.T)):
      tset[i] = True
    self.delaunay_refine(amin, eset,tset)

  # refine keeping Delaunay condition
  def delaunay_refine (self, amin, eset, tset):
    while tset:
      t,_ = tset.popitem()
      self.t_refine_if(t,amin,eset,tset)
      self.delaunay_flip(eset,tset)

  # compute the area of influence of a vertex for Laplacian matrix,
  # given the ring of he
  def cot_area (self, ring):
    area = 0
    for he in ring:
      area += self.h_area(he)
    return area/3

  # compute cotangent wij for Laplacian matrix
  def cot_wij (self, h):
    hb = self.next(h)
    p = self.previous(h)
    m = self.mate(p)
    ha = self.previous(m)
    alpha = self.h_angle(ha)
    beta = self.h_angle(hb)
    return 1/math.tan(alpha) + 1/math.tan(beta)

  # return sparse  Laplacian matrix in lil format
  # (multiplied by -1)
  def LaplacianMatrix (self):
    n = len(self.V)
    mat = scipy.sparse.lil_matrix((n,n),dtype='float')
    for i in range(0,len(self.V)):
      ring = self.v_ring1_he(i)
      wi = 1/(2*self.cot_area(ring))
      wii = 0
      for he in ring:
        j = self.H[he][0]
        wij = self.cot_wij(he)
        wii += wij
        mat[i,j] = wij * wi
      mat[i,i] = -wii * wi
    return mat

  # return sparse Diffusion matrix in lil format
  # M = (I - gamma h L), assuming gamma = 1
  def DiffusionMatrix (self, t=1):
    n = len(self.V)
    mat = scipy.sparse.lil_matrix((n,n),dtype='float64')
    for i in range(0,len(self.V)):
      ring = self.v_ring1_he(i)
      wi = 1/(2*self.cot_area(ring))
      wii = 0
      for he in ring:
        j = self.H[he][0]
        wij = self.cot_wij(he)
        wii += wij
        mat[i,j] = - t * wij * wi
      mat[i,i] = 1 + t * wii * wi
    return mat

  # simulate heat diffusion
  # Ti is a dictionary (v, T) represent initial temperatures at vertices
  def HeatDiffusion (self, Ti, t=1):
    A = self.DiffusionMatrix(t)
    b = np.zeros(len(self.V),dtype="float64")
    for i, T in Ti.items():
      col = A[:,i].toarray()[:,0]
      b -= col * T
    for i, T in Ti.items():
      A[:,i] = 0
      A[i,:] = 0
      A[i,i] = 1
      b[i] = T
    return scipy.sparse.linalg.spsolve(A.tocsr(),b)

  # solve the poisson equation, where b is the independent vector value
  # c is the boundary condition: a dictionary with key=vertex_index and value=pre-defined_value
  def Poisson (self, b, c):
    L = self.LaplacianMatrix()
    bn = np.array(b)
    # multiply the system by -1 to be positive
    L *= -1
    bn *= -1
    for k, v in c.items():
      col = L[:,k].toarray()[:,0]
      bn -= col * v
      bn[k] = v
      L[:,k] = 0
      L[k,:] = 0
      L[k,k] = 1
    return scipy.sparse.linalg.spsolve(L.tocsr(),bn)

  # return the list of halfedges that delimits the N1 ring around vertex v
  def v_ring1_he (self, i):
    he = self.adj_vh(i)
    for j in range(len(he)):
      he[j] = self.next(he[j])
    return he

  # transfer data
  # apply least square for minimizing the reconstruction error on randomly generated points
  # the function returns the solution mapped to extrinsic vertices
  # the factor f indicates how many points will be considered in the optimization: n = f * |V| 
  # the use_v flag indicates if the results at shared vertices should be include or
  # if only random points will be considered
  def data_transfer (self, solution, f=2.0, use_v=True):
    nv = len(self.V)
    ne = len(self.HE.V)
    n = f * nv
    if use_v:
      nr = n - ne  # number of random points
      points = self.HE.generate_random_points(nr)
      n = (ne + len(points))  # may be a bit more or less
    else:
      points = self.HE.generate_random_points(n)
    # build incosistent system for least square
    mat = scipy.sparse.lil_matrix((n,ne),dtype='float')
    b = np.zeros(n)
    if use_v:
      # fill vertex points in the system
      for i in range(ne):
        mat[i,i] = 1
        b[i] = solution[i]
    else:
      i = -1
    # fill random points in the system
    for p in points:
      i += 1
      te, uvw = p
      he0 = self.HE.T[te]
      he1 = self.HE.next(he0)
      he2 = self.HE.next(he1)
      ve0 = self.HE.H[he0][0]
      ve1 = self.HE.H[he1][0]
      ve2 = self.HE.H[he2][0]
      mat[i,ve0] = uvw[0]
      mat[i,ve1] = uvw[1]
      mat[i,ve2] = uvw[2]

      # compute numerical value on intrinsic mesh
      h0, uvw_i = self.te_point_location(te,uvw)
      h1 = self.next(h0)
      h2 = self.next(h1)
      v0 = self.H[h0][0]
      v1 = self.H[h1][0]
      v2 = self.H[h2][0]
      b[i] = uvw_i[0]*solution[v0] + uvw_i[1]*solution[v1] + uvw_i[2]*solution[v2] 

    # solve the system with least square
    x = scipy.sparse.linalg.lsqr(mat,b)[0]
    return x

  def find_largest_ungraded_triangle (self, min_angle):
    area_max = None
    t_max = None
    t_angle_min = None
    for t, h0 in enumerate(self.T):
      angle = min(self.t_get_angles(t))
      if angle < min_angle:
        a = self.h_area(h0)
        if area_max == None or a > area_max:
          area_max = a
          t_max = t
          t_angle_min = angle
        #if t_angle_min == None or angle < t_angle_min:
          #t_angle_min = angle
    return t_max, area_max, t_angle_min

  def find_min_angle_triangle (self, min_angle):
    t_min = None
    t_angle_min = None
    for t, h0 in enumerate(self.T):
      angle = min(self.t_get_angles(t))
      if angle < min_angle:
        if t_angle_min == None or angle < t_angle_min:
          t_angle_min = angle
          t_min = t
    return t_min, t_angle_min

  # improve triangulation according to Chew's algorithm
  def chew93 (self, min_angle):
    #n_none = 0
    v = None
    hp = THeap(self,min_angle)
    n = 0
    while True:
      t, area, angle = hp.pop()
      if t==None:
        break
      n += 1
      if n % 1000 == 0:
        print(">",self.get_angle_min()*180/math.pi)
      v, tset = self.t_add_vertex(t)
      if not v:
        break
      hp.update(tset)
  
  # add vertex at triangle circumcenter
  # return queue of updated triangles
  def t_add_vertex (self, t):
    TOL = 1e-5
    h0 = self.T[t]
    h1 = self.next(h0)
    h2 = self.next(h1)
    hlist = [h0,h1,h2]
    imax = utl.imax(self.t_get_angles(t))
    v = self.t_flatten(hlist[imax])
    c = utl.circumcenter(v[0],v[1],v[2])
    h0, uvw = self.point_location(c,hlist[imax],0)
    #utl.vclamp(uvw,TOL,1-TOL)
    eset = {}  # to collect updated halfedges
    tset = {}  # to collect updated triangles 
    '''
    if min(uvw) < TOL:
      #if max(uvw) > 1-TOL:
      #  print("UNEXPECTED: point at a vertex; nothing to do")
      #  return 
      # refine edge
      h = h0
      for i in range(0,3):
        if uvw[i] < TOL:
          # vertex on opposite edge
          n = self.next(h)
          s = uvw[(i+1)%3]
          if s < 0.2:
            s = 0.2
          elif s > 0.8:
            s = 0.8
          v = self.e_refine(n,s,eset,tset)
          #self.e_refine(n,uvw[(i+1)%3],eset,tset)
          #self.e_refine(n,0.5,eset,tset)
          break
        h = self.next(h)
    else:
      # refine triangle
      v = self.t_refine(h0,uvw,eset,tset)
    '''
    v = self.t_refine(h0,uvw,eset,tset)
    for e in eset:
      l = self.L[e] 
    if v:
      self.delaunay_flip(eset,tset)
    return v, tset
    




