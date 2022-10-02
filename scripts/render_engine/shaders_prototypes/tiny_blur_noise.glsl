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
uniform int time;
uniform sampler2D Texture;
in vec2 uv0;
vec4 buff;
const int samples = 8;
// vec4 colortemp;
float contrast = 1.1;
float brightness = .025;
float radius = 0.0002;
float amount = 0.03;
vec2 offsets[9] = vec2[](
    vec2(0, 0),
    vec2(-1, -1),
    vec2(-1, 0),
    vec2(-1, 1),
    vec2(0, -1),
    vec2(0, 1),
    vec2(1, -1),
    vec2(1, 0),
    vec2(1, 1)
);


vec2 findClosestAlphaTextureCoord(vec2 uv) {
    for (int i = 0; i < offsets.length(); i++)
        {
            vec2 offset = offsets[i];
            if (offset[0] != 0) {
                offset[0] *= (i * radius);
            }
            if (offset[1] != 0) {
                offset[1] *= (i * radius);
            }
            if (texture(Texture, uv + offset).a != 0) {
                return uv + offset;
            }
        }
    return vec2(0, 0);
}

vec4 noiseIt(vec4 buff) {
    float noise = (fract(sin(dot(uv0, vec2(12.9898,78.233)*2.0)) * 43758.5453));
    vec4 result = buff - noise * (amount * (1 - ((buff.x + buff.y + buff.z) / 3)));
    return result;
}

vec4 highlightIt(vec4 buff) {
    vec4 result = buff;
    return result;
}

void main() {
    vec4 colortemp = texture(Texture, uv0);
    color = vec4(0, 0, 0, 0);
    for (int i = 0; i < samples; i ++)
    {

        for (int j = 0; j < offsets.length(); j++) {
            vec2 offset = offsets[j];
            if (offset[0] != 0) {
                offset[0] *= (i * radius);
            }
            if (offset[1] != 0) {
                offset[1] *= (i * radius);
            }
            vec2 uv = findClosestAlphaTextureCoord(uv0 + offset);
            buff.r = texture(Texture, uv).r / samples;
            buff.g = texture(Texture, uv).g / samples;
            buff.b = texture(Texture, uv).b / samples;
            buff.a = texture(Texture, uv0 + offset).a / samples;
            color += (buff / offsets.length());
        }

    }
    buff = highlightIt(color);
    buff = noiseIt(vec4(color.b, color.g, color.r, color.a));

    // vec2 uv = findClosestAlphaTextureCoord(uv0);
    // buff = texture(Texture, uv);

    color[0] = buff.r;
    color[1] = buff.g;
    color[2] = buff.b;
    color[3] = buff.a;

}


#endif
