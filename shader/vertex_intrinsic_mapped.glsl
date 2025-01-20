#version 410

layout(location = 0) in vec4 pos;

uniform isamplerBuffer M;

out int t_id;

void main (void) 
{
  t_id = texelFetch(M,gl_VertexID)[0];
  gl_Position = pos; 
}

