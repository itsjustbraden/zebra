import moderngl
import numpy as np
from pyrr import Matrix44

from ported._example import Example
from moderngl_window.geometry.attributes import AttributeNames


class CrateExample(Example):
    title = "Zebra"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.load_program('zebra.glsl')

        self.mvp = self.prog['Mvp']
        self.light = self.prog['Light']


        # Create a custom attribute name spec
        # so attribute names are not forced to follow gltf standard
        attr_names = AttributeNames(position='in_vert', texcoord_0='in_tex', normal='in_norm')

        self.scene = self.load_scene('Zebra_OBJ.obj', attr_names=attr_names)
        self.vao = self.scene.root_nodes[0].mesh.vao.instance(self.prog)
        self.texture = self.load_texture_2d('Zebra_skin_colors.jpg')

    def render(self, time, frame_time):
        angle = time
        self.ctx.clear(1.0, 1.0, 1.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        camera_pos = (np.cos(angle) * 1.0, np.sin(angle) * 1.0, 2.0)

        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)
        lookat = Matrix44.look_at(
            camera_pos,
            (0.0, 0.0, 0.5),
            (0.0, 0.0, 1.0),
        )

        self.mvp.write((proj * lookat).astype('f4').tobytes())
        self.light.value = camera_pos
        self.texture.use()
        self.vao.render()


if __name__ == '__main__':
    CrateExample.run()
