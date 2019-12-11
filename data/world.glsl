#version 410

#if defined VERTEX_SHADER
in vec2 in_vert;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
}

#elif defined TESS_CONTROL_SHADER

layout(vertices = 4) out;
uniform float scale;
void main() {
    // set tesselation levels
    gl_TessLevelOuter[0] = scale;
    gl_TessLevelOuter[1] = scale;
    gl_TessLevelOuter[2] = scale;
    gl_TessLevelOuter[3] = scale;
    gl_TessLevelInner[0] = scale;
    gl_TessLevelInner[1] = scale;
    // pass through vertex positions
    gl_out[gl_InvocationID].gl_Position = gl_in[gl_InvocationID].gl_Position;
}

#elif defined TESS_EVALUATION_SHADER

layout (quads) in;

uniform mat4 Mvp;
uniform vec2 camera_position;
out vec3 out_vert;


float random (in vec2 st) {
    return fract(sin(dot(st.xy,
                        vec2(12.9898,78.233)))
                * 43758.5453123);
}

float noise (in vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);

    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f*f*(3.0-2.0*f);

    return mix(a, b, u.x) +
            (c - a)* u.y * (1.0 - u.x) +
            (d - b) * u.x * u.y;
}


// bilinear interplotion
void main() {
    float u = gl_TessCoord.x;
    vec4 p1 = mix(gl_in[1].gl_Position,gl_in[0].gl_Position,gl_TessCoord.x);
    vec4 p2 = mix(gl_in[2].gl_Position,gl_in[3].gl_Position,gl_TessCoord.x);

    vec4 Position = mix(p1, p2, sin(gl_TessCoord.y));


    float XYScale = 20.0;
    float ZScale = 1.0 / 20.0;
    Position.xy += camera_position;
    Position.z = noise((Position.xy + camera_position - 0.5) * XYScale) * ZScale;

    out_vert = Position.xyz;

    Position = Mvp * Position;
    gl_Position = Position;
}

#elif defined FRAGMENT_SHADER

uniform float time;
uniform vec2 camera_position;
uniform float scale;

in vec3 out_vert;
out vec4 f_color;

void main() {
    f_color = vec4(sin(time*4), cos(time*4), .6, 1.0); //Change color over time
    float gridScale = scale / 2.0;
    vec2 pos = (out_vert.xy - fract(camera_position)) * gridScale;
    bool griddy = abs( floor(pos.x) - pos.x ) < 0.1;
    griddy = griddy || (abs( floor(pos.y) - pos.y ) < 0.1);
    f_color = f_color * float(griddy);
    //f_color = vec4(1.0,1.0,1.0,1.0); //Make color black & white
}

#endif
