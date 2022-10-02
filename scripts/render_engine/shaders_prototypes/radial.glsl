#version 330


precision mediump float;
uniform sampler2D Texture;

out vec4 color;
uniform float time;
in vec2 v_text;
const int samples = 12;
const float power = 0.0001;
vec4 buff;

mat2 rotate2d(float angle) {
    vec2 sc = vec2(sin(angle), cos(angle));
    return mat2( sc.y, -sc.x, sc.x, sc.y );
}

void main() {
    vec2 uv = v_text.xy;
    float amount = distance(uv, vec2(0.5, 0.5)) * 0.00251;
    vec2 m = vec2(0.5, 0.66);
    color = vec4(0, 0, 0, 0);
    for (int i = 0; i < samples; i ++)
    {
        uv -= m;
        uv *= rotate2d( power * float(i) );
        uv += m;
        buff.r = texture(Texture, vec2(uv.x+amount,uv.y)).r;
        buff.g = texture(Texture, uv).g;
        buff.b = texture(Texture, vec2(uv.x-amount,uv.y)).b;
        color += buff / samples;
    }

    color /= float(samples);
    color = pow(color, vec4(1./2.2));
    color.r*= (time/ time);
}