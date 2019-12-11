#!/usr/bin/env python3
#Brady Kruse
#bak225

#Braden Wells
#rbw214 

'''
Various Citations:

1)  2D Noise based on Morgan McGuire @morgan3d
    https://www.shadertoy.com/view/4dS3Wd

2)  ModernGL template projects
    https://github.com/moderngl/moderngl

3)  Dr. TJ's Tessellation Example Code
    (Thank you!)
'''


import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl
from ported._example import Example #Base class for our world
from moderngl_window.geometry.attributes import AttributeNames

class Camera():

    def __init__(self, ratio):
        self._zoom_step = 0.2 #Camera speeds
        self._move_vertically = 0.001
        self._move_horizontally = 0.001
        self._rotate_horizontally = 0.5
        self._rotate_vertically = 0.02

        self._field_of_view_degrees = 60.0
        self._z_near = 0.01
        self._z_far = 35
        self._ratio = ratio
        self.build_projection()

        self.camera_position = Vector3([-.1, 0.03, -.04]) #Default camera values
        self._camera_front = Vector3([0.0, 1.0, 0.0])
        self._camera_up = Vector3([0.0, 0.0, -1.0])
        self._cameras_target = (self.camera_position + self._camera_front)
        self.build_look_at()

    def zoom_in(self): #Possible movements
        self._field_of_view_degrees = self._field_of_view_degrees - self._zoom_step
        self.build_projection()

    def zoom_out(self):
        self._field_of_view_degrees = self._field_of_view_degrees + self._zoom_step
        self.build_projection()

    def move_forward(self):
        self.camera_position = self.camera_position + self._camera_front * self._move_horizontally
        self.build_look_at()

    def move_backwards(self):
        self.camera_position = self.camera_position - self._camera_front * self._move_horizontally
        self.build_look_at()

    def strafe_left(self):
        self.camera_position = self.camera_position - vector.normalize(self._camera_front ^ self._camera_up) * self._move_horizontally
        self.build_look_at()

    def strafe_right(self):
        self.camera_position = self.camera_position + vector.normalize(self._camera_front ^ self._camera_up) * self._move_horizontally
        self.build_look_at()

    def strafe_up(self):
        self.camera_position = self.camera_position + self._camera_up * self._move_vertically
        self.build_look_at()

    def strafe_down(self):
        self.camera_position = self.camera_position - self._camera_up * self._move_vertically
        self.build_look_at()

    def rotate_up(self):
        self._camera_front.z -= float(self._rotate_vertically)
        self.build_look_at()

    def rotate_down(self):
        self._camera_front.z += float(self._rotate_vertically)
        self.build_look_at()
    
    def rotate_left(self):
        rotation = Quaternion.from_z_rotation(-2 * float(self._rotate_horizontally) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def rotate_right(self):
        rotation = Quaternion.from_z_rotation(2 * float(self._rotate_horizontally) * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()

    def slow_rotate_right(self):
        rotation = Quaternion.from_z_rotation(2 * .2 * np.pi / 180)
        self._camera_front = rotation * self._camera_front
        self.build_look_at()
    
    def build_look_at(self):
        self._cameras_target = (self.camera_position + self._camera_front)
        self.mat_lookat = Matrix44.look_at(
            self.camera_position,
            self._cameras_target,
            self._camera_up)

    def build_projection(self):
        self.mat_projection = Matrix44.perspective_projection(
            self._field_of_view_degrees,
            self._ratio,
            self._z_near,
            self._z_far)

class Tessellation(Example):
    title = "Zebra Land"
    gl_version = (4, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
            #version 410 core
            in vec2 in_vert;
            void main() { gl_Position = vec4(in_vert, 0.0, 1.0); }
            ''',
            tess_control_shader='''
            #version 410 core
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
            ''',
            tess_evaluation_shader='''
            #version 410 core
            layout(quads) in;

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
            ''',
            fragment_shader='''
                #version 330

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
                    f_color = vec4(1.0,1.0,1.0,1.0); //Make color black & white
                }
            ''',
        )
        
        #Passing in of uniforms
        self.mvp = self.prog['Mvp']
        self.time = self.prog['time']
        self.camera_position = self.prog['camera_position']

        self.scale = self.prog['scale']
        
        # four vertices define a quad
        self.ctx.patch_vertices = 4

        vertices = np.array([
            [-0.9, -0.9],
            [ 0.9, -0.9],
            [ 0.9,  0.9],
            [-0.9,  0.9],
        ])

        vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert')
        

        # Create a custom attribute name spec
        # so attribute names are not forced to follow gltf standard
        attr_names = AttributeNames(position='in_vert', texcoord_0='in_tex', normal='in_norm')

        #Object input
        self.obj = self.load_scene('Zebra_OBJ.obj', attr_names=attr_names)
        self.texture = self.load_texture_2d('Zebra_skin_colors.jpg')
        self.vao2 = self.obj.root_nodes[0].mesh.vao.instance(self.prog)

        #Keybinds, camera setup.
        self.camera = Camera(self.aspect_ratio)
        
        # World scale (change to your heart's content)
        self.camera.scale = 256
        
        self.states = {
            self.wnd.keys.W: False,    
            self.wnd.keys.S: False,     
            self.wnd.keys.Q: False,    
            self.wnd.keys.E: False,  
            self.wnd.keys.A: False,     
            self.wnd.keys.D: False,     
            self.wnd.keys.UP: False,     
            self.wnd.keys.DOWN: False,     
            self.wnd.keys.Z: False,     
            self.wnd.keys.X: False,     
            self.wnd.keys.LEFT: False,
            self.wnd.keys.RIGHT: False,
            self.wnd.keys.T: False,
            self.wnd.keys.I: False,
            self.wnd.keys.Y: False,
        }

    def move_camera(self):
            if self.states.get(self.wnd.keys.W):
                self.camera.move_forward()

            if self.states.get(self.wnd.keys.S):
                self.camera.move_backwards()

            if self.states.get(self.wnd.keys.Q):
                self.camera.strafe_up()

            if self.states.get(self.wnd.keys.E):
                self.camera.strafe_down()

            if self.states.get(self.wnd.keys.A):
                self.camera.strafe_left()

            if self.states.get(self.wnd.keys.D):
                self.camera.strafe_right()

            if self.states.get(self.wnd.keys.UP):
                self.camera.rotate_up()

            if self.states.get(self.wnd.keys.DOWN):
                self.camera.rotate_down()

            if self.states.get(self.wnd.keys.LEFT):
                self.camera.rotate_left()

            if self.states.get(self.wnd.keys.RIGHT):
                self.camera.rotate_right()

            if self.states.get(self.wnd.keys.Z):
                self.camera.zoom_in()

            if self.states.get(self.wnd.keys.X):
                self.camera.zoom_out()

            if self.states.get(self.wnd.keys.I):
                self.camera.slow_rotate_right()

            if self.states.get(self.wnd.keys.T):
                self.states[self.wnd.keys.W] = True
                self.states[self.wnd.keys.I] = True
            
            if self.states.get(self.wnd.keys.Y):
                self.states[self.wnd.keys.W] = False
                self.states[self.wnd.keys.I] = False


    def key_event(self, key, action, modifiers):
            if key not in self.states:
                print(key, action)
                return

            if action == self.wnd.keys.ACTION_PRESS:
                self.states[key] = True
            else:
                self.states[key] = False

    def render(self, time, frame_time): #Creation of the world.
        self.move_camera()

        self.ctx.clear(1.0, 1.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.scale.write(np.float32(self.camera.scale).astype('f4').tobytes()) # pylint: disable=too-many-function-args

        self.mvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())
        self.time.write(np.float32(time*0.2).astype('f4').tobytes()) # pylint: disable=too-many-function-args
        self.camera_position.write(self.camera.camera_position.xy.astype('f4').tobytes())
        #self.vao.render(moderngl.PATCHES)
        
        #self.texture.use()
        self.vao2.render()



if __name__ == '__main__':
    Tessellation.run()
