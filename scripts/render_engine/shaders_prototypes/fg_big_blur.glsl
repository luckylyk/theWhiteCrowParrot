#version 330

out vec4 color;
uniform sampler2D Texture;
in vec2 uv0;
vec4 buff;
const int samples = 5;
uniform int time;
// vec4 colortemp;
float contrast = 1.1;
float brightness = .025;
float radius = 0.0015;
float amount = 0.05;
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
float strength = 60.;


vec2 forceInScreenUV(vec2 uv) {
    if (uv[0] < -1) {uv[0] =-1;}
    if (uv[1] < -1) {uv[1] =-1;}
    if (uv[0] > 1) {uv[0] = 1;}
    if (uv[1] > 1) {uv[1] = 1;}
    return uv;
}


vec2 findClosestAlphaTextureCoord(vec2 uv) {
    // return uv;
    for (int i = 0; i < offsets.length(); i++)
        {
            vec2 offset = offsets[i];
            if (offset[0] != 0) {
                offset[0] *= ((offsets.length() - i) * radius);
            }
            if (offset[1] != 0) {
                offset[1] *= ((offsets.length() - i) * radius);
            }
            if (texture(Texture, uv + offset).a != 0) {
                return forceInScreenUV(uv + offset);
            }
        }
    return vec2(0, 0);
}

vec4 noiseIt(vec4 buff, vec2 uv) {
    float x = (uv.x + 4.0 ) * (uv.y + 4.0 ) * (time * 10.0);
    vec4 grain = vec4(mod((mod(x, 13.0) + 1.0) * (mod(x, 123.0) + 1.0), 0.01)-0.005) * strength;

    if(abs(uv.x - 0.5) < 0.002)
        color = vec4(0.0);

    grain = 1.0 - grain;
    return buff * grain;
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
            buff.a = texture(Texture, forceInScreenUV(uv0 + offset)).a / (samples - 1);
            color += (buff / offsets.length());
        }

    }
    buff = highlightIt(color);
    buff = noiseIt(vec4(color.b, color.g, color.r, color.a), uv0);

    // vec2 uv = findClosestAlphaTextureCoord(uv0);
    // buff = texture(Texture, uv);

    color[0] = buff.r;
    color[1] = buff.g;
    color[2] = buff.b;
    color[3] = buff.a;

}



// out vec4 color;
// uniform sampler2D Texture;
// in vec2 uv0;
// uniform float time;

// void main() {
//     float Pi = 6.28318530718; // Pi*2

//     // GAUSSIAN BLUR SETTINGS {{{
//     float Directions = 16.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
//     float Quality = 3.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
//     float Size = 2.0; // BLUR SIZE (Radius)
//     // GAUSSIAN BLUR SETTINGS }}}

//     vec2 Radius = vec2(Size/800.0, Size/450);
//     // Normalized pixel coordinates (from 0 to 1)
//     // Pixel colour
//     vec4 buff = texture(Texture, uv0);

//     // Blur calculations
//     for( float d=0.0; d<Pi; d+=Pi/Directions)
//     {
// 		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality)
//         {
// 			buff += texture( Texture, uv0+vec2(cos(d),sin(d))*Radius*i);
//         }
//     }

//     // Output to screen
//     buff /= Quality * Directions - 15.0;

//     color[0] = buff.b * (time/time);
//     color[1] = buff.g;
//     color[2] = buff.r;
//     color[3] = buff.a;
// }




// float GOLDEN_ANGLE = 2.40; //(3.0-sqrt(5))*PI
// int BLUR_NUMBER = 25;
// uniform sampler2D Texture;
// out vec4 color;
// in vec2 uv0;
// uniform float time;
// void main()
// {
//     mat2 rotate2D = (mat2(cos(GOLDEN_ANGLE), sin(GOLDEN_ANGLE), -sin(GOLDEN_ANGLE), cos(GOLDEN_ANGLE)));
// 	// vec2 uv = uv0.xy / iResolution.y;
//     vec3 col = vec3(0.);
//     vec3 tot = col;
//     float radius = 7.8 - 7.8 * cos(1.54);
//     vec2 angle = vec2(radius/(float(BLUR_NUMBER)*850.0));
//     float r = 0.0;
//     for(int i=0;i<BLUR_NUMBER;++i){
//         r += 1.;
//         angle = rotate2D * angle;
//     	vec3 c = texture(Texture, uv0+r*angle).rgb;
//     	c = c * c * 0.5;
//         vec3 bokeh = pow(c, vec3(4.0));
//         col += c*bokeh;
//         tot += bokeh;
//     }
//     col /= tot;
//     color[0] = col.b * (time/time);
//     color[1] = col.g;
//     color[2] = col.r;
//     color[3] = texture(Texture, uv0).a;
// }