#version 410

layout (triangles) in;
layout (triangle_strip, max_vertices=9) out;

uniform vec4 lpos;  // light pos in lighting space
uniform vec4 cpos;  // camera pos in lighting space

uniform mat4 Mv;
uniform mat4 Mvp;

uniform samplerBuffer VECTOR;

out data {
  vec3 n;
  vec3 l;
  vec3 v;
  vec4 color;
} v;

vec3 normal ()
{
  vec3 u = vec3(gl_in[1].gl_Position - gl_in[0].gl_Position);
  vec3 v = vec3(gl_in[2].gl_Position - gl_in[0].gl_Position);
  vec3 n = normalize(cross(u,v));
  return n;
}

const float factor = 1;

void main (void) 
{
  vec3 n = normal();
  for (int i=0; i<3; ++i) {
    vec3 e = vec3(texelFetch(VECTOR,3*gl_PrimitiveIDIn+i));
    vec3 t = normalize(cross(n,e));
    float w = length(e)/5/factor;
    vec4 p = gl_in[i].gl_Position + vec4(w*t,0); 
    v.n = n;
    v.l = vec3(lpos-Mv*p);
    v.v = vec3(cpos-Mv*p);
    v.color = vec4(1,0,0,1);
    gl_Position = Mvp*p;
    EmitVertex();
    p = gl_in[i].gl_Position - vec4(w*t,0); 
    v.n = n;
    v.l = vec3(lpos-Mv*p);
    v.v = vec3(cpos-Mv*p);
    v.color = vec4(1,0,0,1);
    gl_Position = Mvp*p;
    EmitVertex();
    p = gl_in[i].gl_Position+vec4(e/factor,0);
    v.n = n;
    v.l = vec3(lpos-Mv*p);
    v.v = vec3(cpos-Mv*p);
    v.color = vec4(1,0.8,0.8,1);
    gl_Position = Mvp*p;
    EmitVertex();
    EndPrimitive();
  }
}

