#!/usr/bin/env python3
#Brady Kruse
#bak225

#Braden Wells
#rbw214 

'''
Various Citations:

1)  2D Noise based on Morgan McGuire @morgan3d
    https://www.shadertoy.com/view/4dS3Wd
    Introduced to us by Book of Shaders
    https://thebookofshaders.com/11/

2)  ModernGL template projects
    https://github.com/moderngl/moderngl

3)  Dr. TJ's Tessellation Example Code
    (Thank you!)
'''

# Here they come, it's the modules
import numpy as np
from pyrr import Matrix44, Quaternion, Vector3, vector

import moderngl
from ported._example import Example #Base class for our world
from moderngl_window.geometry.attributes import AttributeNames # pylint: disable=no-name-in-module

# Noise algorithm
#  Not quite working, unused
def doRandom (st):
    x = (np.sin( np.dot(st, [12.9898,78.233])) * 43758.5453123)
    return abs(x - np.floor(x))

def lerp(a, b, val):
    out = b * val + a * (1 - val)
    return out

def noise (st):
    st = np.array(st)
    XYScale = 20.0
    ZScale = 1.0 / 20.0

    st = XYScale * st

    i = np.floor(st)
    f = abs(np.modf(st)[0])

    a = doRandom(i)
    b = doRandom(i + [1.0, 0.0])
    c = doRandom(i + [0.0, 1.0])
    d = doRandom(i + [1.0, 1.0])

    u = f * f * ( 3.0 - (2.0 * f) )

    val = lerp(a, b, u[0]) + (c - a) * u[1] * (1.0 - u[0]) + (d - b) * u[0] * u[1]

    return abs(val * ZScale)

# Camera class modified from simple_camera.py
class Camera():
    def __init__(self, ratio):
        # Camera speeds
        self._zoom_step = 0.2
        self._move_vertically = 0.001
        self._move_horizontally = 0.001
        self._rotate_horizontally = -0.02
        self._rotate_vertically = 0.02

        # Angle of rotation
        self.angle = 0

        # Distance back the camera moves
        self.dist = 0.1

        # Projection? In my camera? It's more likely than you think
        self._field_of_view_degrees = 60.0
        self._z_near = 0.01
        self._z_far = 35
        self._ratio = ratio
        self.build_projection()

        # What are you looking at? Huh?
        # I'm looking at a zebra
        self.camera_position = Vector3([-.1, 0.03, -.06]) #Default camera values
        self.camera_front = Vector3([0.0, 1.0, 0.0])
        self._camera_up = Vector3([0.0, 0.0, -1.0])
        self._cameras_target = (self.camera_position + self.camera_front)
        self.build_look_at()

    # What if you could like zoom in, but in real life? 
    def zoom_in(self):
        self._field_of_view_degrees = self._field_of_view_degrees - self._zoom_step
        self.build_projection()

    # Oh wait never mind you can just get closer
    def zoom_out(self):
        self._field_of_view_degrees = self._field_of_view_degrees + self._zoom_step
        self.build_projection()

    # Do hot sine-cosine action on the angle to get x-y vectors of movement
    #  Then scale it down because cos(0) == 1 and moving 1 in GL space is B A D
    def move_forward(self):
        self.camera_position = self.camera_position + Vector3([np.cos(self.angle),np.sin(self.angle), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def move_backwards(self):
        self.camera_position = self.camera_position - Vector3([np.cos(self.angle),np.sin(self.angle), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    # Same as forwards and backwards, except add in a pretty little 90 degree turn
    def strafe_left(self):
        self.camera_position = self.camera_position - Vector3([np.cos(self.angle + np.pi / 2),np.sin(self.angle + np.pi / 2), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    def strafe_right(self):
        self.camera_position = self.camera_position + Vector3([np.cos(self.angle + np.pi / 2),np.sin(self.angle + np.pi / 2), 0.0 ]) * self._move_horizontally
        self.build_look_at()

    # Thankfully, the up vector never changes, so we can just add/subtract that
    def strafe_up(self):
        self.camera_position = self.camera_position + self._camera_up * self._move_vertically
        self.build_look_at()

    def strafe_down(self):
        self.camera_position = self.camera_position - self._camera_up * self._move_vertically
        self.build_look_at()

    '''
    # Oh, that's rotate-holm
    # ...We don't go there anymore.
    # (is that reference forced? i dunno)
    # (we just decided these were too complex to add to the new rotation system we use)
    def rotate_up(self):
        self.camera_front.z -= float(self._rotate_vertically)
        self.build_look_at()

    def rotate_down(self):
        self.camera_front.z += float(self._rotate_vertically)
        self.build_look_at()
    '''

    # The beauty of this system: just add or subtract to the angle!
    def rotate_left(self):
        self.angle += self._rotate_horizontally
        self.build_look_at()

    def rotate_right(self):
        self.angle -= self._rotate_horizontally
        self.build_look_at()
    
    # Slow rotation for the auto spin/move
    def slow_rotate_right(self):
        self.angle -= self._rotate_horizontally / 5
        self.build_look_at()
    
    # Generate the look-at matrix with the following setup:
    #   Camera_position is the look-at point
    #   Camera_target is the eye point (just the position, except moved opposite the angle)
    #   the up is up, up is always up, up up up up up up up
    def build_look_at(self):
        #ground = noise(np.array(self.camera_position.xy)) - 0.02
        ground = 0.0
        if self.camera_position.z > ground:
            self.camera_position.z = ground
        
        self._camera_dist = Vector3([np.cos(self.angle), np.sin(self.angle), 0]) * self.dist
        self.camera_target = self.camera_position - self._camera_dist

        # Move camera up slightly to get over-shoulder view type deal
        self.camera_target.z -= 0.04
        self.mat_lookat = Matrix44.look_at(
            self.camera_target,
            self.camera_position,
            self._camera_up)

    # Make a lovely projection matrix out of the stuff that they're always made of
    def build_projection(self):
        self.mat_projection = Matrix44.perspective_projection(
            self._field_of_view_degrees,
            self._ratio,
            self._z_near,
            self._z_far)

class Zebra(Example):
    title = "Zebra Land"
    gl_version = (4, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Shaders for the terrain/world/floor/sludge
        self.prog = self.load_program('world.glsl')
        
        #Passing in of uniforms
        self.mvp = self.prog['Mvp']
        self.time = self.prog['time']
        self.camera_position = self.prog['camera_position']
        self.scale = self.prog['scale']
        
        # four vertices define a quad
        self.ctx.patch_vertices = 4

        vertices = np.array([
            [-1.0, -1.0],
            [ 1.0, -1.0],
            [ 1.0,  1.0],
            [-1.0,  1.0],
        ])

        vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert')
        
        
        # Create a custom attribute name spec
        # so attribute names are not forced to follow gltf standard
        attr_names = AttributeNames(position='in_vert', texcoord_0='in_tex', normal='in_norm', color_0 = "color")

        # Shaders for zebra/car/whatever it takes
        self.zprog = self.load_program('zebra.glsl')

        # Uniforms for that
        self.zlight = self.zprog['Light']
        self.zmvp = self.zprog['Mvp']
        self.zuse = self.zprog['ZebraUse']
        self.zcolor = self.zprog['color']
        self.zrotate = self.zprog['Rotate']
        self.ztime = self.zprog['time']

        self.zebraTime = False
        self.zebraPressed = False

        # Get our zebra in town
        self.zebra = self.load_scene('Zebra_OBJ.obj', attr_names=attr_names)
        self.texture = self.load_texture_2d('Zebra_skin_colors.jpg')
        self.vao2 = self.zebra.root_nodes[0].mesh.vao.instance(self.zprog)

        # Car (brought to you by "Educational Purposes")
        self.carDict = {
            "mini_body.obj" : [0,0,0],
            "mini_brakes.obj" : [0.75, 0.75, 0.75],
            "mini_glass.obj" : [0.5, 0.5, 0.5],
            "mini_interior.obj" : [0.33, 0.1, 0.02],
            "mini_parts.obj" : [0.2, 0.2, 0.2],
            "mini_rims.obj" : [0.95, 0.95, 0.93],
            "mini_tires.obj" : [0.1, 0.1, 0.1],
            "mini_underpart.obj" : [0,0,0],
        }

        # Load our car into a dictionary so that we can run through all the parts
        self.car = {}
        self.car["texture"] = self.load_texture_2d('mini_body_diffuse.png')
        for i in self.carDict:
            self.car[i] = {}
            self.car[i]["model"] = self.load_scene(i, attr_names=attr_names)
            self.car[i]["vao"] = self.car[i]["model"].root_nodes[0].mesh.vao.instance(self.zprog)
        
        # Keybinds, camera setup.
        self.camera = Camera(self.aspect_ratio)
        
        # World scale (change to your heart's content)
        self.camera.scale = 256
        
        # Wow that's a few keys, I tell ya what
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
            self.wnd.keys.K: False,
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
            '''
            if self.states.get(self.wnd.keys.UP):
                self.camera.rotate_up()

            if self.states.get(self.wnd.keys.DOWN):
                self.camera.rotate_down()
            '''
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
            
            if self.states.get(self.wnd.keys.K):
                if not self.zebraPressed:
                    self.zebraTime = not self.zebraTime
                    self.zebraPressed = True
            else:
                self.zebraPressed = False


    def key_event(self, key, action, modifiers):
        if key not in self.states:
            print(key, action)
            return

        if action == self.wnd.keys.ACTION_PRESS:
            self.states[key] = True
        else:
            self.states[key] = False

    # It's time to actually see stuff!
    def render(self, time, frame_time):

        # Move our camera depending on keybinds
        self.move_camera()

        # Black background, turn on depth
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Set our world scale for tessellation
        self.scale.write(np.float32(self.camera.scale).astype('f4').tobytes()) # pylint: disable=too-many-function-args

        # Put projection and look-at matrix into uniform
        self.mvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())

        # Setup time, camera_position into shaders
        self.time.write(np.float32(time*0.2).astype('f4').tobytes()) # pylint: disable=too-many-function-args
        self.camera_position.write(self.camera.camera_position.xy.astype('f4').tobytes())

        # Tessellate that floor!
        self.vao.render(moderngl.PATCHES)

        # ZEBRA TIME
        # Put in projection, camera position (which we call light for some reason?), and the time
        self.zmvp.write((self.camera.mat_projection * self.camera.mat_lookat).astype('f4').tobytes())
        self.zlight.write((self.camera.camera_position).astype('f4').tobytes())
        self.ztime.write(np.float32(time*0.2).astype('f4').tobytes()) # pylint: disable=too-many-function-args

        self.zuse.write(np.float32(self.zebraTime).astype('f4').tobytes()) # pylint: disable=too-many-function-args
        
        if not self.zebraTime:
            # Make the car look forwards properly
            wheresMyCar = Matrix44.from_translation([0, 0, -0.02])
            wheresMyCar = Matrix44.from_x_rotation(np.pi) * wheresMyCar
            wheresMyCar = Matrix44.from_z_rotation((np.pi / 2) - self.camera.angle) * wheresMyCar
            # Put that movement into the shader
            self.zrotate.write((wheresMyCar).astype('f4').tobytes())

            self.car["texture"].use()
            for i in self.carDict:
                color = self.carDict[i]
                self.zcolor.write(np.array(color).astype('f4').tobytes())
                self.car[i]["vao"].render()

        else:
            # We need to get our zebra looking the right way and also slightly lower than where he starts
            rotateMyZebra = Matrix44.from_translation([0, -0.05, 0])
            rotateMyZebra = Matrix44.from_x_rotation(np.pi / 2) * rotateMyZebra
            rotateMyZebra = Matrix44.from_z_rotation((np.pi / 2) - self.camera.angle) * rotateMyZebra
            # Put that movement into the shader
            self.zrotate.write((rotateMyZebra).astype('f4').tobytes())

            # Show us the zebra!
            self.texture.use()
            self.vao2.render()


if __name__ == '__main__':
    Zebra.run()
