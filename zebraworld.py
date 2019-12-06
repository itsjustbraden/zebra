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
'''

import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl
from ported._example import Example #Base class for our world


def terrain(size):
    vertices = np.dstack(np.mgrid[0:size, 0:size][::-1]) / size #Defining of vertices & indices for terrain generation. Could probably be cleaned up as to not generate 3 points since we only currently use two.
    temp = np.dstack([np.arange(0, size * size - size), np.arange(size, size * size)])
    index = np.pad(temp.reshape(size - 1, 2 * size), [[0, 0], [0, 1]], 'constant', constant_values=-1)
    return vertices, index


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

class ZebraWorld(Example):
    title = "zebra world"
    gl_version = (3, 3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                uniform mat4 Mvp;

                uniform vec2 camera_position;

                in vec2 in_vert;
                out vec2 v_text;

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

                void main() {
                    float XYScale = 20.0;
                    float ZScale = 1.0 / 20.0;
                    vec4 vertex = vec4(in_vert-0.5+camera_position, noise((in_vert + camera_position) * XYScale) * ZScale, 1.0); //Infinite Generation. Might want to work on it to make it less...wavey.
                    gl_Position = Mvp * vertex;
                                }
                            ''',

            fragment_shader='''
                #version 330

                uniform sampler2D Color1;
                uniform sampler2D Color2;

                uniform sampler2D Cracks;
                uniform sampler2D Darken;

                uniform float time; 

                out vec4 f_color;

                void main() {

                    f_color = vec4(sin(time*4), cos(time*4), .4, 1.0); //Change color over time
                    //f_color = vec4(1.0,1.0,1.0,1.0); //Make color black & white
                }
            ''',
        )

        #Passing in of uniforms
        self.mvp = self.prog['Mvp']
        self.time = self.prog['time']
        self.camera_position = self.prog['camera_position']

        vertices, index = terrain(512)

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.ibo = self.ctx.buffer(index.astype('i4').tobytes())

        vao_content = [
            (self.vbo, '2f', 'in_vert'),
        ]

        self.vao = self.ctx.vertex_array(self.prog, vao_content, self.ibo)

        #Keybinds, camera setup.
        self.camera = Camera(self.aspect_ratio)
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

        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.4, 0.4, .8),
            (0.0, 0.0, 0.1),
            (0.0, 0.0, 1.0),
        )

        self.mvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())
        self.time.write(np.float32(time*0.2).astype('f4').tobytes())
        self.camera_position.write(self.camera.camera_position.xy.astype('f4').tobytes())
        self.vao.render(moderngl.LINE_STRIP)


if __name__ == '__main__':
    ZebraWorld.run()


#To Do:
'''
3) Put in objects (both car & zebra)

Other Ideas:
Non-skeletal world
Lighting / color bleed. Environment map
Change car perspective
Prevent collision
'''
