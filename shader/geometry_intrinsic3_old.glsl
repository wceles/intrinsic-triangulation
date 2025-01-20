#version 410

layout (triangles) in;
layout (triangle_strip, max_vertices=3) out;

uniform mat4 Mv; 
uniform mat4 Mn; 
uniform mat4 Mvp;

uniform samplerBuffer N;
uniform samplerBuffer P;

in float angle[];

const vec2 barycentric[3] = vec2[3](vec2(1,0),vec2(0,1),vec2(0,0));

out data {
  vec2 b, c;     // 2d position of second and third triangle vertices
  vec2 p;        // 2d position of current vertex
  vec2 s;        // baricentric coordinate (for wireframe rendering)
  vec3 pos;      // 3d position of current vertex
} vtx;

void compute_geometry (out vec2 p[3])
{
  vec3 u = vec3(gl_in[1].gl_Position - gl_in[0].gl_Position);
  vec3 v = vec3(gl_in[2].gl_Position - gl_in[0].gl_Position);
  vec3 n = normalize(cross(u,v));
  vec3 t = normalize(u);
  vec3 b = cross(n,t);
  mat3 B = transpose(mat3(t,b,n));
  p[0] = vec2(0,0);
  p[1] = vec2(length(u),0); 
  p[2] = vec2(B * v); 
}

void main (void) 
{
  vec2 p[3];
  compute_geometry(p);
  for (int i=0; i<3; ++i) {
    vtx.b = p[1];
    vtx.c = p[2];
    vtx.p = p[i];
    vtx.s = barycentric[i];
    vtx.pos = vec3(Mv*gl_in[i].gl_Position);
    gl_Position = Mvp*gl_in[i].gl_Position; 
    EmitVertex();
  }
  EndPrimitive();
}

