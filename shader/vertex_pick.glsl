#version 410

layout(location = 0) in vec4 pos;

uniform mat4 Mvp;

void main (void) 
{
  gl_Position = Mvp * pos; 
}

