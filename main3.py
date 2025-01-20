# Testing Extended Supporting HalfEdge Data Structure
# Waldemar Celes
# Tecgraf Institute of PUC-Rio
# celes@tecgraf.puc-rio.br

from ds import he
from ds import she3 as she
from ds import utl
import numpy as np
import math
import time
import sys

import glfw
from OpenGL.GL import *
import potpourri3d as pp3d

from sg import *

intrinsic_mode = True
scene_mode = True

clist = False
solution = None

NC = 6       # number of colors
AMIN = 25    # target minimum angle for refinement

def load_mesh (filename):
  V, F = pp3d.read_mesh(filename)
  m = he.Mesh(V,F)
  im = she.IntrinsicMesh(m, 1e-10)
  im.print_info()
  return m,im

def main():
  if len(sys.argv) != 2:
    print("usage: python main.py mesh_filename")
    exit()

  # Initialize gui library
  if not glfw.init():
      return
  # Create a windowed mode window and its OpenGL context
  glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
  glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
  glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
  glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
  win = glfw.create_window(800, 800, "", None, None)
  if intrinsic_mode:
    glfw.set_window_title(win,"Intrinsic Mesh")
  else:
    glfw.set_window_title(win,"Extrinsic Mesh")
  if not win:
      glfw.terminate()
      return
  glfw.set_key_callback(win,keyboard)

  # Make the window's context current
  glfw.make_context_current(win)
  print("OpenGL version: ",glGetString(GL_VERSION))

  # Initialize application
  initialize(win, sys.argv[1])

  # Loop until the user closes the window
  t0 = time.perf_counter()
  count = 0
  while not glfw.window_should_close(win):
    t = time.perf_counter()
    if t-t0 > 5.0:
      fps = count/(t-t0)
      glfw.set_window_title(win,"fps: " + str(round(fps,2)))
      t0 = time.perf_counter()
      count = 0
    # Render here, e.g. using pyOpenGL
    display(win)
    count += 1
    # Swap front and back buffers
    glfw.swap_buffers(win)
    # Poll for and process events
    glfw.poll_events()


def initialize (win, filename):
  glClearColor(1,1,1,1)
  # enable depth test 
  glEnable(GL_DEPTH_TEST)
  # cull back faces
  glEnable(GL_CULL_FACE)  

  # create objects
  light = EyeLight(0.0,0.0,0.0)
  global colorscale_flag
  colorscale_flag = Variable("colorscale_flag",0)
  global wireframe_var 
  wireframe_var = Variable("wireframe_flag",0)
  global im, m 
  m, im = load_mesh(filename)
  # create extrinsic mesh for rendering
  inc = m.get_incidence_table()
  mesh = Mesh(m.C,inc)
  min = mesh.Min()
  max = mesh.Max()
  print("BBmin:",min)
  print("BBmax:",max)
  med = (min + max) / 2

  global diag
  diag = utl.distance(min, max)

  # load intrinsic mesh to GPU
  global TE, E, T, H, L, S, A, PROP, PROP_E, colorscale, colorcode
  TE = TexBuffer("TE",np.array(m.T,dtype='int32'))
  E = TexBuffer("E",np.array(im.E,dtype='int32'))
  H = TexBuffer("H",np.array(im.H,dtype='int32'))
  T = TexBuffer("T",np.array(im.T,dtype='int32'))
  L = TexBuffer("L",np.array(im.L,dtype='float32'))
  S = TexBuffer("S",np.array(im.S,dtype='int32'))
  A = TexBuffer("A",np.array(im.A,dtype='float32'))
  PROP = TexBuffer("PROP",np.zeros(1,dtype='float32'))
  PROP_E = TexBuffer("PROP_E",np.zeros(len(m.V),dtype='float32'))
  colorcode = TexBuffer("colorcode",np.array(set_colorcode(im,NC),dtype='int32'))
  wireframe = TexWireframe('wireframe',2.0,color=[0.1,0.1,0.1],nmax=9*1024)

  colorscale = Texture1D("colorscale")
  colorscale.SetWrap(GL_CLAMP_TO_EDGE)
  set_colormap_scale(0)
  colormap = colormap_random_pastel(NC)

  DS = [TE,E,H,T,L,S,A,PROP,PROP_E,colormap,colorscale,wireframe,colorcode]

  global camera
  camera = Camera(med[0],med[1],med[2]+1.5*diag)
  camera.SetCenter(med[0],med[1],med[2])
  global arcball
  arcball = camera.CreateArcball()
  arcball.Attach(win)

  global shader_intrinsic
  global shader_extrinsic
  global shader_pick
  shader_intrinsic = Shader(light,"world")
  shader_intrinsic.AttachVertexShader("shader/vertex_intrinsic.glsl")
  shader_intrinsic.AttachGeometryShader("shader/geometry_intrinsic.glsl")
  shader_intrinsic.AttachFragmentShader("shader/fragment_intrinsic3.glsl")
  shader_intrinsic.Link()
  shader_extrinsic = Shader(light,"world")
  shader_extrinsic.AttachVertexShader("shader/vertex_extrinsic.glsl")
  shader_extrinsic.AttachGeometryShader("shader/geometry_extrinsic.glsl")
  shader_extrinsic.AttachFragmentShader("shader/fragment_extrinsic.glsl")
  shader_extrinsic.Link()
  shader_pick = Shader(light,"world")
  shader_pick.AttachVertexShader("shader/vertex_pick.glsl")
  shader_pick.AttachFragmentShader("shader/fragment_pick.glsl")
  shader_pick.Link()

  # build scene
  global root
  root = Node(shader_intrinsic, 
              apps = [colorscale_flag,wireframe_var],
              nodes = [
                        Node(None,None,DS,[mesh])
                      ]
              )
  global scene, scene1 
  scene1 = Scene(root)
  scene = scene1
  
  # prepare scene for mapped mesh
  global meshlist, applist
  meshlist = []
  applist = [colormap,colorcode,wireframe]
  shader_intrinsic_mapped = Shader(light,"world")
  shader_intrinsic_mapped.AttachVertexShader("shader/vertex_intrinsic_mapped.glsl")
  shader_intrinsic_mapped.AttachGeometryShader("shader/geometry_intrinsic_mapped.glsl")
  shader_intrinsic_mapped.AttachFragmentShader("shader/fragment_intrinsic_mapped.glsl")
  shader_intrinsic_mapped.Link()
  root2 = Node(shader_intrinsic_mapped, 
              apps = [wireframe_var],
              nodes = [
                        Node(None,None,applist,meshlist)
                      ]
          )
  global scene2 
  scene2 = Scene(root2)

# build scene with mapped intrinsic mesh
def create_mapped_scene ():
  global clist
  print("begin mapped intrinsic")
  t0 = glfw.get_time()
  elist, ilist, clist = im.generate_common_subdivision()
  print("end mapped intrinsic: ", glfw.get_time()-t0,"s")
  global meshlist, applist
  inc = [i for i in range(0,3*len(clist))]
  applist.append(TexBuffer("M",np.array(ilist,dtype='int32')))
  print("#triangles (mapped intrinsic)",len(elist),len(ilist),len(clist))
  meshlist.append(Mesh(clist,inc))

def pick_triangle (x, y):
  global scene
  global camera
  global root
  global shader_pick
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
  curr_shader = root.GetShader()
  root.SetShader(shader_pick)
  scene.Render(camera)
  glFinish()
  color = glReadPixels(x,y,1,1,GL_RGB,GL_FLOAT)
  id = (int)(((color[0][0][0] * 255 + color[0][0][1]) * 255 + color[0][0][2]) * 255)
  root.SetShader(curr_shader)
  print("id:",id,len(m.T))
  if id < len(m.T):
    return id
  else:
    return None

def display (win):
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
  scene.Render(camera)


def keyboard (win, key, scancode, action, mods):
   global arcball
   global im

   # pan window up
   if key == glfw.KEY_UP and action != glfw.RELEASE:
    if(glfw.get_key(win, glfw.KEY_LEFT_SHIFT) == glfw.PRESS):
      arcball.Translate(0.0,0.01,0.0)
    else:
      arcball.Translate(0.0,0.1,0.0)

   # pan window down
   elif key == glfw.KEY_DOWN and action != glfw.RELEASE:
    if(glfw.get_key(win, glfw.KEY_LEFT_SHIFT) == glfw.PRESS):
      arcball.Translate(0.0,-0.01,0.0)
    else:
      arcball.Translate(0.0,-0.1,0.0)

   # pan window right
   elif key == glfw.KEY_RIGHT and action != glfw.RELEASE:
    if(glfw.get_key(win, glfw.KEY_LEFT_SHIFT) == glfw.PRESS):
      arcball.Translate(0.01,0.0,0.0)
    else:
      arcball.Translate(0.1,0.0,0.0)

   # pan window left
   elif key == glfw.KEY_LEFT and action != glfw.RELEASE:
    if(glfw.get_key(win, glfw.KEY_LEFT_SHIFT) == glfw.PRESS):
      arcball.Translate(-0.01,0.0,0.0)
    else:
      arcball.Translate(-0.1,0.0,0.0)

   # zoom in
   elif key == glfw.KEY_W and action != glfw.RELEASE:
    camera.SetAngle(camera.GetAngle()/1.05)

   # zoom out
   elif key == glfw.KEY_S and action != glfw.RELEASE:
    camera.SetAngle(camera.GetAngle()*1.05)

   # quit app
   elif key == glfw.KEY_Q and action == glfw.PRESS:
    glfw.set_window_should_close(win,glfw.TRUE)

   # switch intrinsic/extrinsic mesh rendering
   elif key == glfw.KEY_I and action == glfw.PRESS:
    global intrinsic_mode
    intrinsic_mode = not intrinsic_mode
    if intrinsic_mode:
      glfw.set_window_title(win,"Intrinsic Mesh")
      root.SetShader(shader_intrinsic)
    else:
      glfw.set_window_title(win,"Extrinsic Mesh")
      root.SetShader(shader_extrinsic)

   # set, cyclically, wireframe rendering
   elif key == glfw.KEY_L and action == glfw.PRESS:
    wireframe_var.SetValue((wireframe_var.GetValue()+1)%3)

   # switch colorscale/colorcode palette
   elif key == glfw.KEY_M and action == glfw.PRESS:
    global colorscale_flag
    colorscale_flag.SetValue(colorscale_flag.GetValue()^1)

   # create/render common subdivision
   elif key == glfw.KEY_X and action == glfw.PRESS:
    if not clist:
      create_mapped_scene()
    global scene
    global scene_mode
    scene_mode = not scene_mode
    if scene_mode:
      if intrinsic_mode:
        glfw.set_window_title(win,"Intrinsic Mesh")
      else:
        glfw.set_window_title(win,"Extrinsic Mesh")
      scene = scene1
    else:
      glfw.set_window_title(win,"Common Subdivision")
      scene = scene2
    
   # refine mesh 
   elif key == glfw.KEY_R and action == glfw.PRESS:
    print("begin chew93")
    im.delaunay()
    t0 = glfw.get_time()
    im.chew93(AMIN*math.pi/180)  # set minimun angle goal
    print("end chew93:", glfw.get_time() - t0)
    im.check_consistency()
    im.print_info()
    E.SetData(np.array(im.E,dtype='int32'))
    H.SetData(np.array(im.H,dtype='int32'))
    T.SetData(np.array(im.T,dtype='int32'))
    L.SetData(np.array(im.L,dtype='float32'))
    S.SetData(np.array(im.S,dtype='int32'))
    A.SetData(np.array(im.A,dtype='float32'))
    PROP.SetData(np.zeros(len(im.V)))
    colorcode.SetData(np.array(set_colorcode(im,NC),dtype='int32'))

   # build Delaunay mesh
   elif key == glfw.KEY_D and action == glfw.PRESS:
    print("begin delaunay")
    t0 = glfw.get_time()
    im.delaunay()
    print("end delaunay:", glfw.get_time() - t0)
    im.check_consistency()
    im.print_info()
    E.SetData(np.array(im.E,dtype='int32'))
    H.SetData(np.array(im.H,dtype='int32'))
    T.SetData(np.array(im.T,dtype='int32'))
    L.SetData(np.array(im.L,dtype='float32'))
    S.SetData(np.array(im.S,dtype='int32'))
    A.SetData(np.array(im.A,dtype='float32'))
    PROP.SetData(np.zeros(len(im.V)))
    colorcode.SetData(np.array(set_colorcode(im,NC),dtype='int32'))

   # simulate heat diffusion (source indicated by the cursor position)
   elif key == glfw.KEY_H and action == glfw.PRESS:
    x, y = glfw.get_cursor_pos(win)
    wn_w, wn_h = glfw.get_window_size(win)
    fb_w, fb_h = glfw.get_framebuffer_size(win)
    x = x * fb_w / wn_w
    y = (wn_h - y) * fb_h / wn_h
    id = pick_triangle(x,y)
    if id:
      print("begin heat diffusion")
      t0 = glfw.get_time()
      vid = im.HE.H[im.HE.T[id]][0]
      print("VID:",vid)
      Ti = {}
      Ti[vid] = 1
      solution = im.HeatDiffusion(Ti,1e4/im.l_average()**4)
      print("minmax:",vid,np.min(solution),np.max(solution))
      print("end heat diffusion:", glfw.get_time()-t0)
      min = np.min(solution)
      max = np.max(solution)
      solution = (solution-min) / (max-min)
      PROP.SetData(solution)
      transf_solution = im.data_transfer(solution)
      PROP_E.SetData(transf_solution)
      colorscale_flag.SetValue(1)
      set_colormap_scale(0)

def colormap_random_pastel (n):
  import colorsys
  cm = [
    [0xff,0xda,0xdf],
    [0xfe,0xc9,0xc3],
    [0xdc,0xc2,0xe0],
    [0xc4,0xe9,0xe6],
    [0xf9,0xf3,0xaa],
    [0xc9,0xea,0xd8],
  ]
  cm = [[239, 230, 69], [233, 53, 161], [0, 227, 255], [225, 86, 44], [83, 126, 255], [0, 203, 133]]
  for i, c in enumerate(cm):
    c[0] /= 255
    c[1] /= 255
    c[2] /= 255
    c = colorsys.rgb_to_hsv(*c)
    cm[i] = colorsys.hsv_to_rgb(c[0],c[1]-0.2,1)
  return TexBuffer("colormap",np.array(cm,dtype='float32'))

def set_colormap_scale (kind):
  if kind==0: 
    cm = [[0,0,1],[0,1,1],[0,1,0],[1,1,0],[1,0,0]]
  else:
    cm = ([[1,1,1]]*16 + [[0.7,0.7,0.7]]*4) * 40
  colorscale.SetData(np.array(cm,dtype='float32'))

# get triangle color code from [0,c)
def set_colorcode (mesh,c):
  label = 0   # next preferrable label to be assign
  colorcode = []
  print(len(colorcode),len(mesh.T))
  for t in range(len(mesh.T)):
    h0 = mesh.T[t]
    h1 = mesh.next(h0)
    h2 = mesh.next(h1)
    t0 = mesh.H[mesh.mate(h0)][2]
    t1 = mesh.H[mesh.mate(h1)][2]
    t2 = mesh.H[mesh.mate(h2)][2]
    taken = []
    if t0 < t:
      taken.append(colorcode[t0])
    if t1 < t:
      taken.append(colorcode[t1])
    if t2 < t:
      taken.append(colorcode[t2])
    while label in taken:
      label = (label + 1) % c
    colorcode.append(label)
  return colorcode

if __name__ == "__main__":
    main()

