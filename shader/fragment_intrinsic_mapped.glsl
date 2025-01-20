#version 410

uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform isamplerBuffer M;
uniform samplerBuffer colormap;
uniform isamplerBuffer colorcode;
uniform sampler1D wireframe;

in data {
  vec3 s;
  vec3 normal;
  vec3 view;
  vec3 light;
} f;

uniform int wireframe_flag;

out vec4 color;

void main (void) 
{
  int t = texelFetch(M,gl_PrimitiveID)[0];
  vec4 mdif = texelFetch(colormap,texelFetch(colorcode,t)[0]);
  vec3 normal = normalize(f.normal);
  vec3 view = normalize(f.view);
  vec3 light = normalize(f.light);
  float ndotl = dot(normal,light);
  color = mdif * (0.1 + 0.9 * ldif * max(0,ndotl)); 
  if (wireframe_flag==1) {
    vec4 wcolor = texture(wireframe,f.s.x);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = texture(wireframe,f.s.y);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
    wcolor = texture(wireframe,f.s.z);
    color = (1-wcolor[3]) * color + wcolor[3] * wcolor;
  }
  /*
  if (ndotl > 0) {
    vec3 refl = normalize(reflect(-light,normal));
    color += vec4(1,1,1,1) * lspe * pow(max(0,dot(refl,view)),64); 
  }
  */
}



