#version 410

out vec4 color;

void main (void) 
{
  int id = gl_PrimitiveID;
  color.r = floor(id / (255*255)) / 255.0;
  id = id % (255*255);
  color.g = floor(id / 255) / 255.0;
  id = id % 255;
  color.b = id / 255.0;
  color.a = 1.0;
}



