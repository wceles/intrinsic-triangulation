#version 410

uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform vec4 lpos;  // light pos in lighting space
uniform vec4 cpos;  // camera pos in lighting space

//uniform isamplerBuffer V;  // vertex set: not needed
uniform isamplerBuffer E;    // edge set
uniform isamplerBuffer H;    // halfedge set
uniform isamplerBuffer T;    // triangle set
uniform samplerBuffer L;     // edge length set
uniform isamplerBuffer S;    // supporting halfedge set
uniform samplerBuffer A;     // supporting halfedge angle set

uniform isamplerBuffer colorcode; // triangle color code texture  (index to colormap)
uniform samplerBuffer colormap;   // triangle color palette 
uniform sampler1D colorscale;     // property color palette
uniform samplerBuffer PROP;       // property texture
uniform sampler1D wireframe;      // wireframe texture 

uniform int colorscale_flag;      // property map rendering flag
uniform int wireframe_flag;       // wireframe rendering flag

in data {
  vec2 s;
  vec2 p;
  vec3 pos;
} f;

out vec4 color;

#define PI 3.1415926535898
#define IMAX 200

bool ccw (vec2 p, vec2 q, vec2 r) 
{
  float det = (p[0]-r[0])*(q[1]-r[1])-(p[1]-r[1])*(q[0]-r[0]);
  return det >= 0; 
}

float area (vec2 p, vec2 q, vec2 r) 
{
  float det = (q.x*r.y + p.x*q.y + p.y*r.x) -
              (q.x*p.y + r.x*q.y + r.y*p.x);
  return det / 2;
}

int mate (int he)
{
  int e = texelFetch(H,he)[1];
  ivec4 edge = texelFetch(E,e);
  return (edge[0] == he) ? edge[1] : edge[0];
}

bool separateline (vec2 v0, vec2 v1, vec2 p[3])
{
  return ccw(v1,v0,p[0]) && ccw(v1,v0,p[1]) && ccw(v1,v0,p[2]);
}

bool crossing (vec2 v0, vec2 v1, vec2 p)
{
  vec2 o = vec2(0,0);
  bool t0 = ccw(o,p,v0);
  bool t1 = ccw(o,p,v1);
  bool u0 = ccw(v0,v1,o);
  bool u1 = ccw(v0,v1,p);
  return ((t0 && !t1) || (t1 && !t0)) && ((u0 && !u1) || (u1 && !u0));
}
  
int find_triangle (int te, out vec3 uvw, out vec3 duvwdx, out vec3 duvwdy)
{
  int h0 = texelFetch(S,te)[0];
  float phi0 = texelFetch(A,te)[0];
  int e0 = texelFetch(H,h0)[1];
  float l0 = texelFetch(L,e0)[0];
  vec2 v0 = vec2(0,0);
  vec2 v1 = vec2(l0*cos(phi0) ,l0*sin(phi0));
  for (int niter=0; niter<IMAX; ++niter) {
    // compute v2
    int t = texelFetch(H,h0)[2];
    int h1 = texelFetch(H,h0)[3];  // next
    int h2 = texelFetch(H,h1)[3];  // next
    int e1 = texelFetch(H,h1)[1];
    int e2 = texelFetch(H,h2)[1];
    float l1 = texelFetch(L,e1)[0];
    float l2 = texelFetch(L,e2)[0];
    float alpha = acos((l0*l0+l1*l1-l2*l2)/(2*l0*l1));
    //float alpha = get_angle(t,h1);
    float phi1 = phi0 + PI - alpha;
    vec2 v2 = vec2(v1[0] + l1*cos(phi1), v1[1] + l1*sin(phi1));
    // check which triangle edge crosses line segment 0-p
    bool out_v1v2 = !ccw(v1,v2,f.p);
    if (out_v1v2 && crossing(v1,v2,f.p)) {
      int m1 = mate(h1);
      if (m1!=-1) {   // check if border is crossed unexpectedely
        v0 = v2;  // v1 remains the same
        l0 = l1;
        h0 = m1;
        phi0 = phi1 + PI;
        continue; 
      }
    }
    else if (out_v1v2 || !ccw(v2,v0,f.p)) {
      int m2 = mate(h2);
      if (m2!=-1) {   // check if border is crossed unexpectedely
        float beta = acos((l0*l0+l2*l2-l1*l1)/(2*l0*l2));
        //float beta = get_angle(t,h0);
        v1 = v2;  // v0 remains the same
        l0 = l2;
        h0 = m2;
        phi0 = phi0 + beta;
        continue; 
      }
    } 
    vec2 p = f.p;
    vec2 px = f.p + dFdx(f.p);
    vec2 py = f.p + dFdy(f.p);
    float a = area(v0,v1,v2);
    float a12 = area(v1,v2,p);
    float a20 = area(v2,v0,p);
    float a01 = a - a12 - a20;
    float a12x = area(v1,v2,px);
    float a20x = area(v2,v0,px);
    float a01x = a - a12x - a20x;
    float a12y = area(v1,v2,py);
    float a20y = area(v2,v0,py);
    float a01y = a - a12y - a20y;
    int href = texelFetch(T,t)[0];
    vec3 uvwx, uvwy;
    if (href == h0) {
      uvw.x = a12 / a;
      uvw.y = a20 / a;
      uvwx.x = a12x / a;
      uvwx.y = a20x / a;
      uvwy.x = a12y / a;
      uvwy.y = a20y / a;
    }
    else if (href == h1) {
      uvw.x = a20 / a;
      uvw.y = a01 / a;
      uvwx.x = a20x / a;
      uvwx.y = a01x / a;
      uvwy.x = a20y / a;
      uvwy.y = a01y / a;
    }
    else {
      uvw.x = a01 / a;
      uvw.y = a12 / a;
      uvwx.x = a01x / a;
      uvwx.y = a12x / a;
      uvwy.x = a01y / a;
      uvwy.y = a12y / a;
    }
    uvw.z = 1 - uvw.x - uvw.y;
    uvwx.z = 1 - uvwx.x - uvwx.y;
    uvwy.z = 1 - uvwy.x - uvwy.y;
    duvwdx = uvwx - uvw;
    duvwdy = uvwy - uvw;
    return t;
  }
  uvw = vec3(1,0,0);
  return -1;
}

float get_property (int t, vec3 uvw)
{
  int h0 = texelFetch(T,t)[0];
  int h1 = texelFetch(H,h0)[3];  // next
  int h2 = texelFetch(H,h1)[3];  // next
  int v0 = texelFetch(H,h0)[0];
  int v1 = texelFetch(H,h1)[0];
  int v2 = texelFetch(H,h2)[0];
  float p0 = texelFetch(PROP,v0)[0];
  float p1 = texelFetch(PROP,v1)[0];
  float p2 = texelFetch(PROP,v2)[0];
  return p0*uvw.x + p1*uvw.y + p2*uvw.z;
}

vec4 find_color (int te, out int tout, out vec3 uvw, out vec3 duvwdx, out vec3 duvwdy)
{
  int t = find_triangle(te,uvw,duvwdx,duvwdy);
  tout = t;
  if (colorscale_flag==1) {
    float s = get_property(t,uvw);
    return texture(colorscale,s);
  }
  else {
    return texelFetch(colormap,texelFetch(colorcode,t)[0]);
  }
}

void main (void) 
{
  int t;
  vec3 uvw, duvwdx, duvwdy;  // baricentric coordinate and its derivatives
  vec4 mdif = find_color(gl_PrimitiveID,t,uvw,duvwdx,duvwdy);
  vec3 normal = normalize(cross(dFdx(f.pos),dFdy(f.pos)));
  vec3 light = normalize(vec3(lpos)-f.pos);
  vec3 view = normalize(vec3(cpos)-f.pos);
  float ndotl = dot(normal,light);
  color = mdif * (0.1 + 0.9 * ldif * max(0,ndotl)); 

  if (wireframe_flag==1) {
    // render extrinsic wireframe
    vec4 wcolor = texture(wireframe,f.s.x);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = texture(wireframe,f.s.y);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = texture(wireframe,1-f.s.x-f.s.y);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
  }
  else if (wireframe_flag==2) {
    // draw intrinsic wireframe
    vec3 fx = duvwdx;
    vec3 fy = duvwdy;
    vec4 wcolor = textureGrad(wireframe,uvw.x,fx.x,fy.x);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = textureGrad(wireframe,uvw.y,fx.y,fy.y);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = textureGrad(wireframe,uvw.z,fx.z,fy.z);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
  }
  /*
  if (ndotl > 0) {
    vec3 refl = normalize(reflect(-light,normal));
    color += vec4(1,1,1,1) * lspe * pow(max(0,dot(refl,view)),64); 
  }
  */
}



