FRAGMENT_SHADER = """
#version 330

out vec4 color;
uniform sampler2D Texture;
in vec2 uv0;
vec4 buff;
void main() {
    buff = texture(Texture, uv0);
    // time /= time;
    // dummy usage of time to force add it to modern gl program
    color[0] = buff.b;
    color[1] = buff.g;
    color[2] = buff.r;
    color[3] = buff.a;
}
"""

VERTEX_SHADER = """
#version 330

in vec3 in_position;
in vec2 in_texcoord_0;
out vec2 uv0;

void main() {
    gl_Position = vec4(in_position, 1);
    uv0 = vec2(in_texcoord_0[0], -in_texcoord_0[1]);
}
"""
