#version 330

out vec4 color;
uniform sampler2D Texture;
uniform float time;
uniform int wave_number = 8;
uniform float speed = 1.;
uniform int amplitude = 800;

in vec2 uv0;
vec4 buff;

void main() {
    float offset = 2 * sin(2*3.14 * ((uv0[1] + (time * speed)) * wave_number)) / amplitude * distance(vec2(0, 0), uv0);
    vec2 uv1 = vec2(uv0[0] + offset, uv0[1]);
    buff = texture(Texture, uv1);

    color[0] = buff.b;
    color[1] = buff.g;
    color[2] = buff.r;
    color[3] = buff.a;
}


