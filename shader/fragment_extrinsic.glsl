#version 410

uniform vec4 lpos;  // light pos in lighting space
uniform vec4 cpos;  // camera pos in lighting space

uniform vec4 lamb;
uniform vec4 ldif;
uniform vec4 lspe;

uniform samplerBuffer colormap;
uniform isamplerBuffer colorcode;
uniform sampler1D colorscale;
uniform sampler1D wireframe;

uniform int colorscale_flag;

in data {
  float prop;
  vec3 s;
  vec3 pos;
} f;

uniform int wireframe_flag;

out vec4 color;

void main (void) 
{
  vec4 mdif = texture(colorscale,f.prop);
  vec3 normal = normalize(cross(dFdx(f.pos),dFdy(f.pos)));
  vec3 light = normalize(vec3(lpos)-f.pos);
  vec3 view = normalize(vec3(cpos)-f.pos);
  float ndotl = dot(normal,light);
  color = mdif * (0.1 + 0.9*ldif * max(0,ndotl)); 

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



