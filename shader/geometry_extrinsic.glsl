#version 410

layout (triangles) in;
layout (triangle_strip, max_vertices=3) out;

uniform mat4 Mv; 
uniform mat4 Mn; 
uniform mat4 Mvp;

in float prop[];

out data {
  float prop;
  vec3 s;       // wireframe texture coordinates
  vec3 pos;
} vtx;

void main (void) 
{
  vec3 v0 = vec3(gl_in[0].gl_Position); 
  vec3 v1 = vec3(gl_in[1].gl_Position); 
  vec3 v2 = vec3(gl_in[2].gl_Position); 
  vec3 u = v1 - v0;
  vec3 v = v2 - v0;
  vec3 normal = normalize(cross(u,v));

  for (int i=0; i<3; ++i) {
    vtx.s = vec3(1,1,1);
    vtx.s[i] = 0;
    vtx.pos = vec3(Mv*gl_in[i].gl_Position);
    vtx.prop = prop[i];
    gl_Position = Mvp*gl_in[i].gl_Position; 
    EmitVertex();
  }
  EndPrimitive();
}

