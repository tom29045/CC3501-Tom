#LIBRERIAS
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import math
from pyglet import clock

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
from utils.drawables import Texture, Model

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

    controller = Controller(800,600,"Tarea 2")
    controller.set_exclusive_mouse(True)


# Cambio de color a textura
    vert_source = """ 
    #version 330

    in vec3 position;
    in vec2 texCoord; 

    out vec2 fragTexCoord; 

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        fragTexCoord = texCoord;
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """
    frag_source = """ 
    #version 330
    in vec2 fragTexCoord;

    uniform sampler2D u_texture;

    out vec4 outColor;

    void main() {
        outColor = texture(u_texture, fragTexCoord);
    }
    """

    # parte A
    vertex_shader = Shader(vert_source, "vertex")
    fragment_shader = Shader(frag_source, "fragment")
    pipeline = ShaderProgram(vertex_shader, fragment_shader)
    root = os.path.dirname(__file__)

    cam = MyCam([0,0,2])

    world = SceneGraph(cam)

    Tileset = Texture(root + "/TileSet.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST)
    background = Texture(root + "/backgroundColor.png", minFilterMode=GL_NEAREST, maxFilterMode=GL_NEAREST, sWrapMode=GL_REPEAT, tWrapMode=GL_REPEAT)

    aW = Tileset.width
    aH = Tileset.height

    bW = background.width
    bH = background.height

    fondo = [
        0.0, 0.0,
        1.0, 0.0,
        1.0, 1.0,
        1.0, 1.0
    ]

    paisaje = Model(shapes.Square["position"], fondo, index_data=shapes.Square["indices"])
    world.add_node("root")
    world.add_node("Plataformas", attach_to="root")
    world.add_node("Fondo", attach_to="root")
    world.add_node("Color", attach_to="Fondo", mesh=paisaje, texture = background, pipeline=pipeline)
    world.add_node("Player", attach_to="root")

    hierba_verde_vert = [
        0.125, 0.95,
        0.3, 0.95,
        0.3, 1.0,
        0.125, 1.0
    ]

    hierba_verde_izq = [
        0.125, 0.84375,
        0.1375, 0.84375,
        0.1375, 1.0,
        0.125, 1.0
    ]

    hierba_verde_der = [
        0.48375, 0.84375,
        0.5, 0.84375,
        0.5, 1.0,
        0.48375, 1.0
    ]

    barro = [
        0.1875, 0.875,
        0.25, 0.875,
        0.25, 0.9375,
        0.1875, 0.9375
    ]


    head = [
        0.655, 0.0,
        0.790, 0.0,
        0.790, 0.201,
        0.655, 0.201
    ]
    body = [
        0.790, 0.0,
        1.0, 0.0,
        1.0, 0.250,
        0.790, 0.250

    ]

    HVV = Model(shapes.Square["position"], hierba_verde_vert, index_data=shapes.Square["indices"])
    HVI = Model(shapes.Square["position"], hierba_verde_izq, index_data=shapes.Square["indices"])
    HVD = Model(shapes.Square["position"], hierba_verde_der, index_data=shapes.Square["indices"])
    tierra = Model(shapes.Square["position"], barro, index_data=shapes.Square["indices"])
    cabeza = Model(shapes.Square["position"], head, index_data=shapes.Square["indices"])
    cuerpo = Model(shapes.Square["position"], body, index_data=shapes.Square["indices"])

    world.add_node("head", attach_to="Player", mesh=cabeza, texture=Tileset, pipeline=pipeline, )
    world["head"]["transform"] = tr.matmul([tr.translate(0.0, 0.6, -0.1), tr.scale(0.5, 0.8, 1)])
    world.add_node("body", attach_to="Player", mesh=cuerpo, texture=Tileset, pipeline=pipeline)
    world["body"]["transform"] = tr.matmul([tr.translate(0.0, -0.01, 0.0), tr.scale(0.5, 0.8, 1)])
    world.add_node("Plataforma 1", attach_to="Plataformas")
    world.add_node("Pasto1", attach_to="Plataforma 1", mesh = HVV, texture=Tileset, pipeline=pipeline)
    world.add_node("Tierra1", attach_to="Plataforma 1", mesh = tierra, texture=Tileset, pipeline=pipeline)
    world["Tierra1"]["transform"] = tr.matmul([tr.translate(-0.6, 0, 1), tr.scale(0.4, 0.2, 1)] )
    world["Pasto1"]["transform"] = tr.matmul([tr.translate(-0.6, 0.05, 1), tr.scale(0.35, 0.1, 1)])


    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pipeline.use()
        world.draw()
        
    player_x = 0.0
    zoom = 0.0
    #CAMARA vista en aux5
    @controller.event
    def on_key_press(symbol, modifiers):
        global player_x, zoom
        if symbol == key.W:
            zoom -= 0.001
        if symbol == key.S:
            zoom += 0.001

        if symbol == key.A:
            player_x -= 0.01
        if symbol == key.D:
            player_x += 0.01

    @controller.event
    def on_key_release(symbol, modifiers):
        global player_vel, zoom_vel
        if symbol == key.W or symbol == key.S:
            zoom = 0.0

        if symbol == key.A or symbol == key.D:
            player_x = 0.0


    #Informacion que se actualiza con el tiempo
    def update(dt):
        global player_x, player_vel, zoom_vel
        world["Player"]["transform"] = tr.translate(player_x, 0.0, 0.0)
        world["Fondo"]["transform"] = tr.matmul([tr.translate(player_x*0.8, 0.0, -2.0), tr.scale(20, 20, 1)])
        cam.position[2] += zoom
        cam.position[0] = player_x
        cam.focus[0] = player_x
        cam.time_update(dt)
        world.update()

    clock.schedule_interval(update,1/60)
    run()
