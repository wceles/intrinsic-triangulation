#version 410

layout(location = 0) in vec4 pos;

// change PROP_E to PROP to visualize the result on the extrinsic mesh 
// directy copying data at shared vertices. 
// Note how the optimization procedure (using PROP_E) improves the mapping.

uniform samplerBuffer PROP_E;

out float prop;

void main (void) 
{
  prop = texelFetch(PROP_E,gl_VertexID)[0];
  gl_Position = pos; 
}

