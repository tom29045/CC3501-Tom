# LIBRERIAS externas
from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.window import Window, key
from pyglet.gl import *
from pyglet.app import run
from pyglet import clock

import sys, os
import numpy as np
# la siguiente linea le dice a python que cuando busque librerías, busque en la carpeta actual
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(__file__)))))

# Revise lo que es un queue, le será útil para entender por qué es conveniente usarlo
# https://en.wikipedia.org/wiki/Queue_(abstract_data_type)
from collections import deque


# Controla la ventana y el paso del tiempo
class Controller(Window):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.time = 0

        # Declare sus variables globales aquí



# Clase Particle que debe completar
# Esta clase encapsula la lógica de sus partículas
class Particle():

    # ¿Qué debe otros parámetros son necesarios para crear una partícula?
    def __init__(self, position, ttl ... ???):
        ???

    # ¿Qué se debe actualizar en cada frame?
    def step(self, dt):
        ???

    # Puede definir más métodos si lo estima conveniente :D




if __name__ == "__main__":

    controller = Controller(800, 800, "Tarea_1")

    # A continuación defina los shaders.
    ???


    # Luego su[s] pipeline[s]
    ???

    # Defina las figuras para los cañones
    ???

    @controller.event
    def on_draw():
        # Limpia pantalla y la coloca en el color determinado
        glClearColor(0.8,0.9,1,1)
        controller.clear()

        # Flags de OpenGL para dibujar puntos y usar transparencia
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        

        # Aquí debe selecicionar el pipeline que usara y luego dibujar sus cosas...




    # Esta función es importante, ya que le ayudará a interactuar con el teclado.
    # Actualmente, está programada para que cada vez que se presione "A", 
    # se imprima "Presionaste A!"
    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.A:
            print("Presionaste A!")

        # Use esta función de Pyglet para generar sus partículas.




    # Aquí se actualiza todo el sistema de partículas
    def update_particle_system(dt, controller):

        # Estudie el aux 3 para entender bien este paso.

        

    clock.schedule(update_particle_system, controller)
    run()