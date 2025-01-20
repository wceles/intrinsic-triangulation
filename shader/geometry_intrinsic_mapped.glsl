#version 410

layout (triangles) in;
layout (triangle_strip, max_vertices=3) out;

uniform vec4 lpos;  // light pos in lighting space
uniform vec4 cpos;  // camera pos in lighting space
uniform mat4 Mv; 
uniform mat4 Mn; 
uniform mat4 Mvp;


out data {
  vec3 s;       // wireframe texture coordinates
  vec3 normal;
  vec3 view;
  vec3 light;
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
    vec3 p = vec3(Mv*gl_in[i].gl_Position);
    if (lpos.w == 0) 
      vtx.light = normalize(vec3(lpos));
    else 
      vtx.light = normalize(vec3(lpos)-p); 
    vtx.view = normalize(vec3(cpos)-p);
    vtx.normal = normal;
    gl_Position = Mvp*gl_in[i].gl_Position; 
    EmitVertex();
  }
  EndPrimitive();
}

