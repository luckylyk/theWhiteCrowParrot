#version 330

#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_texcoord_0;
out vec2 uv0;

void main() {
    gl_Position = vec4(in_position, 1);
    uv0 = vec2(in_texcoord_0[0], -in_texcoord_0[1]);
}

#elif defined FRAGMENT_SHADER


out vec4 color;
uniform sampler2D Texture;
uniform int time;
in vec2 uv0;
vec4 buff;
float amount = 0.02;
float contrast = 1.02;


vec4 noiseIt(vec4 buff) {
    float noise = (fract(sin(dot(uv0, vec2(12.9898,78.233)*time)) * 43758.5453));
    vec4 result = buff - noise * (amount * (1 - ((buff.x + buff.y + buff.z) / 3)));
    return result;
}


void main() {
    color = texture(Texture, uv0);
    buff = noiseIt(vec4(color.b, color.g, color.r, color.a));
    buff -= .5;
    buff *= contrast;
    buff += .5;
    // buff[1] =- .5
    // buff[2] =- .5

    color[0] = buff.r;
    color[1] = buff.g;
    color[2] = buff.b;
    color[3] = buff.a;

}


#endif
