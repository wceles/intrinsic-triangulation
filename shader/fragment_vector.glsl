#version 410

uniform vec4 ldif;

in data {
  vec3 n;
  vec3 l;
  vec3 v;
  vec4 color;
} f;

out vec4 color;

void main (void)
{
  float ndotl = dot(normalize(f.n),normalize(f.l));
  color = f.color * (0.1 + 0.9 * max(0,ndotl)); 
}