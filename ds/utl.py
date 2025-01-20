# Utility functions
# Waldemar Celes
# Tecgraf Institute of PUC-Rio
# celes@tecgraf.puc-rio.br

import math

def add (a, b):
  c = a.copy()
  for i, x in enumerate(b):
    c[i] += x
  return c

def sub (a, b):
  c = a.copy()
  for i, x in enumerate(b):
    c[i] -= x
  return c

def scalar_mult (a, x):
  c = a.copy()
  for i in range(len(c)):
    c[i] *= x
  return c

def length (v):
  s = 0
  for x in v:
    s += x*x
  return math.sqrt(s)

def normalize (v):
  l = length(v)
  if l == 0:
    return v
  else:
    n = []
    for x in v:
      n.append(x/l)
    return n

def distance (a, b):
  s = 0
  for x, y in zip(a,b):
    s += (x-y)*(x-y)
  return math.sqrt(s)

# scalar product
def dot (u, v):
  a = 0
  for x, y in zip(u,v):
    a += x * y
  return a 

# cross product 
def cross (u, v):
  return [
    u[1]*v[2] - u[2]*v[1],
    u[2]*v[0] - u[0]*v[2],
    u[0]*v[1] - u[1]*v[0]
  ]

def tri_valid (a, b, c, tol):
  l0 = distance(a,b)
  l1 = distance(b,c)
  l2 = distance(c,a)
  return tri_valid_len(l0,l1,l2,tol)

def tri_valid_len (l0, l1, l2, tol):
  return l0+l1 > l2+tol and l1+l2 > l0+tol and l2+l0 > l1+tol

# check if all polygon vertices are ccw wrt the given edge v0-v1
def separateline (v0, v1, p):
  for i in range(0,len(p)):
    if not ccw(v0,v1,p[i]):
      return False
  return True

# return if the triple vertices are counter clockwise oriented
def ccw (a, b, c):
  return orient(a,b,c) >= 0
  return (b[0]*c[1] + a[0]*b[1] + a[1]*c[0]) - (a[1]*b[0] + b[1]*c[0] + a[0]*c[1]) >= 0

# return the relative orientation of the three given points (positive (ccw), negative (cw), or zero)
def orient (a, b, c):
  return ((a[0]-c[0])*(b[1]-c[1])-(a[1]-c[1])*(b[0]-c[0]))
  return (b[0]*c[1] + a[0]*b[1] + a[1]*c[0]) - (a[1]*b[0] + b[1]*c[0] + a[0]*c[1])

# return the distance from an edge (a,b) to a point c
def edge_point_distance (a, b, c):
  return orient(a,b,c)/2/distance(a,b)

def in_triangle (v, p):
  return (orient(v[0],v[1],p) >= 0 and
          orient(v[1],v[2],p) >= 0 and
          orient(v[2],v[0],p) >= 0
         )

def crossing (v0, v1, p, o=[0,0]):
  t0 = ccw(o,p,v0)
  t1 = ccw(o,p,v1)
  u0 = ccw(v0,v1,o)
  u1 = ccw(v0,v1,p)
  return ((t0 and not t1) or (t1 and not t0)) and ((u0 and not u1) or (u1 and not u0))

# clamp values
def vclamp (v, xmin, xmax):
  for i in range(len(v)):
    if v[i] < xmin:
      v[i] = xmin
    elif v[i] > xmax:
      v[i] = xmax

def clamp (x, xmin, xmax):
  if x < xmin:
    x = xmin
  elif x > xmax:
    x = xmax
  return x

def clamp_angle (a):
  p2 = 2 * math.pi
  a = a % p2
  if a < 0:
    a += p2
  return a

# check if convex polygon overlap
# two convex polygons do not overlap if one of the edge is a separating line
def overlap (p,q):
  n = len(p)
  for i in range(0,n):
    j = (i+1) % n 
    if separateline(p[j],p[i],q):
      return False
  n = len(q)
  for i in range(0,n):
    j = (i+1) % n 
    if separateline(q[j],q[i],p):
      return False
  return True

def area (a, b, c):
  return ((b[0]*c[1] + a[0]*b[1] + a[1]*c[0]) - (a[1]*b[0] + b[1]*c[0] + a[0]*c[1])) / 2

def clip (v, p):
  inp = p.copy()
  for i in range(0,3):
    a = []
    for j in range(0,len(inp)):
      a.append(area(v[i],v[(i+1)%3],inp[j]))
    out = []
    for j in range(0,len(inp)):
      k = (j+1) % len(inp)
      if a[j] >= 0:
        out.append(inp[j])
      if a[j]*a[k] < 0:
        s = abs(a[j]) + abs(a[k])
        if s > 0:
          t = abs(a[j]) / s
          out.append(
            [
              (1-t)*inp[j][0]+t*inp[k][0],
              (1-t)*inp[j][1]+t*inp[k][1]
            ]
          )
    inp = out
  if len(out) < 3:
    return []
  return out
  '''
  if not out:
    return []
  out2 = [out[0]]
  for i in range(1,len(out)):
    if distance(out2[-1],out[i]) > 1e-10:
      out2.append(out[i])
  if distance(out2[0],out2[-1]) <= 1e-10:
    out2.pop()
  if len(out2) < 3:
    return []
  return out2
  '''

# compute the circumcenter of a triangle
def circumcenter(a, b, c):
  A = [0,0]
  B = [b[0]-a[0],b[1]-a[1]]
  C = [c[0]-a[0],c[1]-a[1]]
  D = 2 * (B[0]*C[1] - B[1]*C[0])
  if D == 0:
    print(a,b,c)
  return [
    (C[1]*(B[0]*B[0]+B[1]*B[1]) - B[1]*(C[0]*C[0]+C[1]*C[1]))/D + a[0],
    (B[0]*(C[0]*C[0]+C[1]*C[1]) - C[0]*(B[0]*B[0]+B[1]*B[1]))/D + a[1],
  ]

# compute the barycenter of a triangle
def barycenter(a, b, c):
  return [
    (a[0]+b[0]+c[0])/3,
    (a[1]+b[1]+c[1])/3
  ]

# return index of maximum element in list
def imax (v):
  xmax = v[0]
  imax = 0
  for i in range(1,len(v)):
    if v[i] > xmax:
      xmax = v[i]
      imax = i
  return imax

# compute the barycentric coordinates of a given point
def barycentric (a, b, c, p):
  A = area(a,b,c)
  u = area(b,c,p)/A
  v = area(c,a,p)/A
  return [u,v,1-u-v]

# compute point given the barycentric coordinates
def from_baricentric (a, b, c, uvw):
  return [
    a[0]*uvw[0] + b[0]*uvw[1] + c[0]*uvw[2],
    a[1]*uvw[0] + b[1]*uvw[1] + c[1]*uvw[2],
  ]

# testing
if __name__ == "__main__":
  a = -2
  print(a,clamp_angle(a))
  a = -4
  print(a,clamp_angle(a))
  a = 2 
  print(a,clamp_angle(a))
  a = 4
  print(a,clamp_angle(a))
  a = -8 
  print(a,clamp_angle(a))
  a = 34
  print(a,clamp_angle(a))
