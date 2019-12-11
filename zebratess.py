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
        self._rotate_horizontally = -0.02
        self._rotate_vertically = 0.02

        self.angle = 0
        self.dist = 0.1

        self._field_of_view_degrees = 60.0
        self._z_near = 0.01
        self._z_far = 35
        self._ratio = ratio
        self.build_projection()

        self.camera_position = Vector3([-.1, 0.03, -.06]) #Default camera values
        self.camera_front = Vector3([0.0, 1.0, 0.0])
        self._camera_up = Vector3([0.0, 0.0, -1.0])
        self._cameras_target = (self.camera_position + self.camera_front)
        self.build_look_at()

    def zoom_in(self): #Possible movements
        self._field_of_view_degrees = self._field_of_view_degrees - self._zoom_step
        self.build_projection()

    def zoom_out(self):
        self._field_of_view_degrees = self._field_of_view_degrees + self._zoom_step
        self.build_projection()

    def move_forward(self):
        self.camera_position = self.camera_position + Vector3([np.cos(self.angle),np.sin(self.angle), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def move_backwards(self):
        self.camera_position = self.camera_position - Vector3([np.cos(self.angle),np.sin(self.angle), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def strafe_left(self):
        self.camera_position = self.camera_position - Vector3([np.cos(self.angle + np.pi / 2),np.sin(self.angle + np.pi / 2), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def strafe_right(self):
        self.camera_position = self.camera_position + Vector3([np.cos(self.angle + np.pi / 2),np.sin(self.angle + np.pi / 2), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def strafe_up(self):
        self.camera_position = self.camera_position + self._camera_up * self._move_vertically
        self.build_look_at()

    def strafe_down(self):
        self.camera_position = self.camera_position - self._camera_up * self._move_vertically
        self.build_look_at()

    def rotate_up(self):
        self.camera_front.z -= float(self._rotate_vertically)
        self.build_look_at()

    def rotate_down(self):
        self.camera_front.z += float(self._rotate_vertically)
        self.build_look_at()
    
    def rotate_left(self):
        self.angle += self._rotate_horizontally
        self.build_look_at()

    def rotate_right(self):
        self.angle -= self._rotate_horizontally
        self.build_look_at()


        '''
        rotation = Quaternion.from_z_rotation(2 * float(self._rotate_horizontally) * np.pi / 180)
        self.camera_front = rotation * self.camera_front
        self.build_look_at()
        '''

    def slow_rotate_right(self):
        rotation = Quaternion.from_z_rotation(2 * .2 * np.pi / 180)
        self.camera_front = rotation * self.camera_front
        self.build_look_at()
    
    def build_look_at(self):
        self._camera_dist = Vector3([np.cos(self.angle), np.sin(self.angle), 0]) * self.dist
        self.camera_target = self.camera_position - self._camera_dist
        self.camera_target.z -= 0.04
        self.mat_lookat = Matrix44.look_at(
            self.camera_target,
            self.camera_position,
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

        self.prog = self.load_program('world.glsl')
        
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
        self.zprog = self.load_program('zebra.glsl')
        self.zlight = self.zprog['Light']
        self.zmvp = self.zprog['Mvp']
        self.zrotate = self.zprog['Rotate']
        self.ztime = self.zprog['time']

        self.obj = self.load_scene('Zebra_OBJ.obj', attr_names=attr_names)
        self.texture = self.load_texture_2d('Zebra_skin_colors.jpg')
        self.vao2 = self.obj.root_nodes[0].mesh.vao.instance(self.zprog)

        #Keybinds, camera setup.
        self.camera = Camera(self.aspect_ratio)
        
        # World scale (change to your heart's content)
        self.camera.scale = 256;
        
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

        self.scale.write(np.float32(self.camera.scale).astype('f4').tobytes())

        self.mvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())
        self.time.write(np.float32(time*0.2).astype('f4').tobytes()) # pylint: disable=too-many-function-args
        self.camera_position.write(self.camera.camera_position.xy.astype('f4').tobytes())
        self.vao.render(moderngl.PATCHES)

        self.zmvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())
        self.zlight.write((self.camera.camera_position).astype('f4').tobytes())
        self.ztime.write(np.float32(time*0.2).astype('f4').tobytes()) # pylint: disable=too-many-function-args

        rotateMyZebra = Matrix44.from_translation([0, -0.05, 0])
        rotateMyZebra = Matrix44.from_x_rotation(np.pi / 2) * rotateMyZebra
        rotateMyZebra = Matrix44.from_z_rotation((np.pi / 2) - self.camera.angle) * rotateMyZebra
        self.zrotate.write((rotateMyZebra).astype('f4').tobytes())
        
        self.texture.use()
        self.vao2.render() #Uncomment after object loads



if __name__ == '__main__':
    Tessellation.run()
