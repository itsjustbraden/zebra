#version 330

#if defined VERTEX_SHADER

uniform mat4 Mvp;

in vec3 in_vert;
in vec3 in_norm;
in vec2 in_tex;

uniform vec3 Light;
uniform mat4 Rotate;
uniform bool ZebraUse;

out vec3 v_vert;
out vec3 v_norm;
out vec2 v_text;

void main() {
    float zebraScale = 192.0;
    float carScale = 192.0 * 20.0;

    float scale = ZebraUse ? zebraScale : carScale;

    vec3 my_vert = (in_vert / scale);

    my_vert = (Rotate * vec4(my_vert, 1.0)).xyz;
    gl_Position = Mvp * vec4(my_vert + Light, 1.0);
    v_vert = my_vert;
    v_norm = in_norm;
    v_text = in_tex;
}

#elif defined FRAGMENT_SHADER

uniform vec3 Light;
uniform sampler2D Texture;
uniform float time;
uniform vec3 color;

in vec3 v_vert;
in vec3 v_norm;
in vec2 v_text;

out vec4 f_color;

float random (in vec2 st) {
    return fract(sin(dot(st.xy,
                        vec2(12.9898,78.233)))
                * 43758.5453123);
}

float noise (in vec2 st) {
    float XYScale = 20.0;
    float ZScale = 1.0 / 20.0;

    st *= XYScale;

    vec2 i = floor(st);
    vec2 f = fract(st);

    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f*f*(3.0-2.0*f);

    float val = mix(a, b, u.x) +
            (c - a)* u.y * (1.0 - u.x) +
            (d - b) * u.x * u.y;
    return val * ZScale;
}

void main() {
    vec3 texcolor = color.rgb;
    if(texcolor == vec3(0.0)){
        texcolor = texture(Texture, v_text).rgb;
    }
    vec3 LightFR = v_vert;
    LightFR.x += 0.1;
    
    float ground = noise(Light.xy);
    float dist = abs(Light.z - ground);
    dist *= dist * 100.0;

    float lum = clamp(dot(normalize(LightFR - Light), normalize(v_norm)), 0.0, 1.0) * 0.5 + 0.1;
    lum /= dist;
    lum = clamp(lum, 0.0, 1.0);
    vec3 ambient = vec3(1.0,1.0,1.0) * .3;
    vec3 color = vec3(sin(time*4), cos(time*4), 0.6);
    f_color = vec4((ambient * texcolor) + (lum*color*texcolor), 1.0);
}


#endif
