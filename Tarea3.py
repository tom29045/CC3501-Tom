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


class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.time = 0
        self.light_mode = False
        
        # Banderas de movimiento
        self.W = False
        self.S = False
        self.A = False
        self.D = False
        self.ESPACIO = False
        self.SHIFT = False

    # ¡EVENTOS INTEGRADOS DIRECTAMENTE EN LA CLASE! (Imposibles de ignorar)
    def on_key_press(self, symbol, modifiers):
        if symbol == key.W: self.W = True
        elif symbol == key.S: self.S = True
        elif symbol == key.A: self.A = True
        elif symbol == key.D: self.D = True
        elif symbol == key.SPACE: self.ESPACIO = True
        elif symbol == key.LSHIFT: self.SHIFT = True
        elif symbol == key.ESCAPE: self.close()

    def on_key_release(self, symbol, modifiers):
        if symbol == key.W: self.W = False
        elif symbol == key.S: self.S = False
        elif symbol == key.A: self.A = False
        elif symbol == key.D: self.D = False
        elif symbol == key.SPACE: self.ESPACIO = False
        elif symbol == key.LSHIFT: self.SHIFT = False



#CAMARA mejorada con métodos corregidos
class MyCam(FreeCamera):
    def __init__(self, position=np.array([0, 0, 0]), camera_type="perspective"):
        super().__init__(position, camera_type)
        self.direction = np.array([0, 0, 0], dtype=np.float32)
        self.speed = 100

    def time_update(self, dt):
        self.update()
        dir = self.direction[0]*self.forward + self.direction[1]*self.right
        dir_norm = np.linalg.norm(dir)
        if dir_norm:
            dir /= dir_norm
        self.position += dir*self.speed*dt
        self.focus = self.position + self.forward

if __name__ == "__main__":

    controller = Controller(1920, 1080, "Tarea 3")
    #controller.set_exclusive_mouse(True)
    root = os.path.dirname(__file__)
    cam = MyCam([0.0, 1.0, 15.0])
    teclas = key.KeyStateHandler()
    controller.push_handlers(teclas)

    with open(root +  "/shaders/textured_mesh_lit.vert") as f:
        color_vertex_source_code = f.read()

    with open(root +  "/shaders/textured_mesh_lit.frag") as f:
        color_fragment_source_code = f.read()
    
    pipeline = ShaderProgram(
    Shader(color_vertex_source_code, "vertex"),
    Shader(color_fragment_source_code, "fragment")
    )

    uv_cuadrado = [
        0.0, 0.0,
        1.0, 0.0,
        1.0, 1.0,
        0.0, 1.0
    ]

    estadio_parts = mesh_from_file(root + "/estadio/untitled.obj")
    pikachu_parts = mesh_from_file(root + "/Pikachu/Pikachu.obj")
    porygon_parts = mesh_from_file(root + "/Porygon/Porygon.obj")
    quad = Model(shapes.Square["position"], index_data=shapes.Square["indices"], normal_data=shapes.Square["normal"], uv_data = uv_cuadrado)
    material = Material(ambient=[1.0, 1.0, 1.0], diffuse=[0.8, 0.8, 0.8], specular=[0.1, 0.1, 0.1], shininess=32.0)

    world = SceneGraph(cam)

    world.add_node("root")
    world.add_node("stadium")


    cielo_tex = Texture(root + "/estadio/sky01.png")
    
    cielo_mat = Material(ambient=[1.0, 1.0, 1.0], diffuse=[0.0, 0.0, 0.0], specular=[0.0, 0.0, 0.0])

    cielo_transform = np.matmul(tr.translate(0.0, 10.0, -60.0), tr.uniformScale(200.0))
    cielo2_transform = np.matmul(tr.translate(0.0, 10.0, 60.0), tr.uniformScale(200.0))
    
    world.add_node("cielo", "root", mesh=quad, texture=cielo_tex, material=cielo_mat, pipeline=pipeline, transform=cielo_transform)
    world.add_node("cielo2", "root", mesh=quad, texture=cielo_tex, material=cielo_mat, pipeline=pipeline, transform=cielo2_transform)


    texturas_estadio = {}
    ruta_estadio = root + "/estadio/"
    
    for archivo in os.listdir(ruta_estadio):
        if archivo.endswith(".png") or archivo.endswith(".jpg"):
            texturas_estadio[archivo] = Texture(ruta_estadio + archivo, sWrapMode=GL_REPEAT, tWrapMode=GL_REPEAT)

    mapa_mat_tex = {}
    mat_actual = None
    
    with open(root + "/estadio/untitled.mtl", "r") as f:
        for linea in f:
            linea = linea.strip()
            if linea.startswith("newmtl "): 
                mat_actual = linea.split()[1]
            elif linea.startswith("map_Kd ") and mat_actual:
                mapa_mat_tex[mat_actual] = linea.split()[1].split("/")[-1].split("\\")[-1]

    world.add_node("estadio_padre", "stadium")

    for i, part in enumerate(estadio_parts):
        nombre_geom = str(part["id"])
        malla = part["mesh"]
        tex_final = None
        for mat_name in sorted(mapa_mat_tex.keys(), key=len, reverse=True):
            if mat_name in nombre_geom:
                img_name = mapa_mat_tex[mat_name]
                tex_final = texturas_estadio.get(img_name)
                break
        if tex_final is not None:
            world.add_node(f"estadio_parte_{i}", 
                           "estadio_padre", 
                           pipeline=pipeline, 
                           mesh=malla,
                           texture=tex_final,
                           material=material)
        else:
            world.add_node(f"estadio_parte_{i}", 
                           "estadio_padre", 
                           pipeline=pipeline, 
                           mesh=malla,
                           material=material)


    texturas_pikachu = [
        Texture(root + "/Pikachu/PikachuHohoDh.png"),
        Texture(root + "/Pikachu/PikachuEyeDh.png"),
        Texture(root + "/Pikachu/PikachuMouthDh.png"),
        Texture(root + "/Pikachu/PikachuDh.png")
    ]
    pikachu_transform = np.matmul(tr.uniformScale(0.05), tr.translate(-10.0, 0.0, 250.0))
    world.add_node("pikachu_padre", "stadium", transform=pikachu_transform)
    for i, part in enumerate(pikachu_parts):
        tex = texturas_pikachu[i] if i < len(texturas_pikachu) else texturas_pikachu[0]
        world.add_node(f"pikachu_parte_{i}", 
                       "pikachu_padre", 
                       pipeline=pipeline, 
                       mesh=part["mesh"],
                       texture=tex, 
                       material=material,
                       rotation= [0, np.pi/2, 0])
    
    texturas_porygon = [
        Texture(root + "/Porygon/Porygon_bodyCl_ctr.png"),
        Texture(root + "/Porygon/Porygon_eyeCl_ctr.png")
    ]

    porygon_transform = np.matmul(tr.uniformScale(0.0025), tr.translate(175.0, 0.0, 5000.0))
    world.add_node("porygon_padre", "stadium", transform=porygon_transform)
    for i, part in enumerate(porygon_parts):
        tex = texturas_porygon[i] if i < len(texturas_porygon) else texturas_porygon[0]
        world.add_node(f"porygon_parte_{i}", 
                       "porygon_padre", 
                       pipeline=pipeline, 
                       mesh=part["mesh"],
                       texture=tex, 
                       material=material,
                       rotation= [0, -np.pi/2, 0])

    luz_sol = DirectionalLight(
        ambient=[0.8, 0.8, 0.8],
        diffuse=[1.0, 1.0, 1.0],
        specular=[0.5, 0.5, 0.5]
    )
    
    luz_sol.direction = np.array([-1.0, -1.0, -1.0]) 

    world.add_node("luces", "stadium")
    world.add_node("luz_solar", "luces", light=luz_sol, pipeline=pipeline)

    @controller.event
    def on_mouse_motion(x, y, dx, dy):
    
        try:
            cam.yaw -= dx * 0.002
            cam.pitch += dy * 0.002
            cam.pitch = np.clip(cam.pitch, -np.pi/2 + 0.1, np.pi/2 - 0.1)
        except AttributeError:
            cam.phi -= dx * 0.002
            cam.theta += dy * 0.002
            cam.theta = np.clip(cam.theta, -np.pi/2 + 0.1, np.pi/2 - 0.1)

    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.W or symbol == key.UP: controller.W = True
        elif symbol == key.S or symbol == key.DOWN: controller.S = True
        elif symbol == key.A or symbol == key.LEFT: controller.A = True
        elif symbol == key.D or symbol == key.RIGHT: controller.D = True
        elif symbol == key.SPACE: controller.ESPACIO = True
        elif symbol == key.LSHIFT: controller.SHIFT = True
        elif symbol == key.ESCAPE: controller.close()

    @controller.event
    def on_key_release(symbol, modifiers):
        if symbol == key.W or symbol == key.UP: controller.W = False
        elif symbol == key.S or symbol == key.DOWN: controller.S = False
        elif symbol == key.A or symbol == key.LEFT: controller.A = False
        elif symbol == key.D or symbol == key.RIGHT: controller.D = False
        elif symbol == key.SPACE: controller.ESPACIO = False
        elif symbol == key.LSHIFT: controller.SHIFT = False

   
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
        cam.update()
    
        velocidad = 10.0 * dt
    
    # Leemos directamente desde el ADN del controlador
        if controller.W: cam.position += cam.forward * velocidad
        if controller.S: cam.position -= cam.forward * velocidad
        if controller.A: cam.position -= cam.right * velocidad
        if controller.D: cam.position += cam.right * velocidad
    
    # Volar (para que puedas ver el estadio desde arriba)
        if controller.ESPACIO: cam.position[1] += velocidad
        if controller.SHIFT: cam.position[1] -= velocidad

    # Apuntamos la cámara
        cam.focus = cam.position + cam.forward
    
    # Nuestro detector de mentiras
        print(f"Posición: X={cam.position[0]:.1f}, Y={cam.position[1]:.1f}, Z={cam.position[2]:.1f} | W: {controller.W}")
    
        world.update()



    clock.schedule_interval(update,1/60)
    run()