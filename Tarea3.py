#LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock
import pyglet
from utils.helpers import mesh_from_file

import sys, os
import numpy as np
import grafica.transformations as tr
import utils.camera as Camera

#MODULOS (cuidado con las rutas)
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))
from utils.helpers import init_axis, mesh_from_file
from utils.camera import FreeCamera
from utils.scene_graph import SceneGraph
from utils import shapes
from utils.drawables import Texture, Model, Material, DirectionalLight, PointLight, SpotLight
from grafica import lighting_shaders as light

#Controla la ventana
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False


#CAMARA mejorada con métodos corregidos
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0, 0, 0], dtype=np.float32)
        self.speed = 2

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

if __name__ == "__main__":

    controller = Controller(1280, 720, "Tarea 3")
    controller.set_exclusive_mouse(True)

    root = os.path.dirname(__file__)

    cam = MyCam([0.0, 8.0, 30.0])

    with open(root +  "/shaders/textured_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(root +  "/shaders/textured_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()
    
    pipeline = ShaderProgram(
    Shader(color_vertex_source_code, "vertex"),
    Shader(color_fragment_source_code, "fragment")
    )

    estadio_mesh = mesh_from_file(root + "/estadio/untitled.obj")[0]["mesh"]
    pikachu_mesh = mesh_from_file(root + "/Pikachu/Pikachu.obj")[0]["mesh"]
    quad = Model(shapes.Square["position"], index_data=shapes.Square["indices"], normal_data=shapes.Square["normal"])
    cube = Model(shapes.Cube["position"], index_data=shapes.Cube["indices"], normal_data=shapes.Cube["normal"])
    material = Material(ambient=[0.1, 0.1, 0.1], diffuse=[0.8, 0.8, 0.8], specular=[1.0, 1.0, 1.0], shininess=32.0)

    world = SceneGraph(cam)

    world.add_node("root")
    world.add_node("stadium")
    world.add_node("estadio", "stadium", pipeline = pipeline, mesh = estadio_mesh, material = material, scale = [1, 1, 1])
    world.add_node("luces", "stadium", pipeline = pipeline)
    world.add_node("luz 1", "luces", light = DirectionalLight(), pipeline = pipeline)
    world.add_node("pikachu", "stadium", pikachu_mesh, pipeline, material = material)

    

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pipeline.use()
        world.draw()

    def update(dt):
        controller.time += dt

        world.update()
    clock.schedule_interval(update,1/60)
    run()