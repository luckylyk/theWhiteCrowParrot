#version 330

out vec4 color;
uniform sampler2D Texture;
uniform vec2 window_size;
uniform vec2 resolution;
uniform float amount;
uniform int time;
float final_amount;
in vec2 uv0;
vec4 buff;
float noise_amount = 0.15;


vec4 noiseIt(vec4 buff) {
    float noise = (fract(sin(dot(uv0, vec2(12.9898,78.233)*time)) * 43758.5453));
    vec4 result = buff - noise * (noise_amount * (1 - ((buff.x + buff.y + buff.z) / 3)));
    return result;
}


void main() {
    final_amount = amount * (resolution.x / window_size.x);
    final_amount *= abs(0.5 - uv0.x);
    final_amount /= 150;
    buff.r = texture(Texture, vec2(uv0.x + final_amount, uv0.y)).r;
    buff.g = texture(Texture, uv0).g;
    buff.b = texture(Texture, vec2(uv0.x + (final_amount * 2), uv0.y)).b;
    buff.a = texture(Texture, uv0).a;
    buff = noiseIt(buff);
    color[0] = buff.b;
    color[1] = buff.g;
    color[2] = buff.r;
    color[3] = buff.a;
}


