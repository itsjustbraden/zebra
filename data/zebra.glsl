#version 330

#if defined VERTEX_SHADER

uniform mat4 Mvp;

in vec3 in_vert;
in vec3 in_norm;
in vec2 in_tex;

uniform vec3 Light;
uniform mat4 Rotate;

out vec3 v_vert;
out vec3 v_norm;
out vec2 v_text;

void main() {
    vec3 my_vert = (in_vert / 128.0);
    v_vert = my_vert;
    my_vert = (Rotate * vec4(my_vert, 1.0)).xyz;
    gl_Position = Mvp * vec4(my_vert + Light, 1.0);
    v_norm = in_norm;
    v_text = in_tex;
}

#elif defined FRAGMENT_SHADER

uniform vec3 Light;
uniform sampler2D Texture;

in vec3 v_vert;
in vec3 v_norm;
in vec2 v_text;

out vec4 f_color;

void main() {
    float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.8 + 0.2;
    f_color = vec4(texture(Texture, v_text).rgb * lum, 1.0);
    //f_color = vec4(0.0, 0.0, 0.0, 1.0);
}


#endif
