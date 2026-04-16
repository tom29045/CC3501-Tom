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

        self.width = 600
        self.height = 600
        self.time = 0

        # Declare sus variables globales aquí
        self.particles_peq = deque()
        self.particles_gran = deque()
        self.particles_peq_gpu_object = None
        self.particles_gran_gpu_object = None



# Clase Particle que debe completar
# Esta clase encapsula la lógica de sus partículas
class Particle():

    # ¿Qué debe otros parámetros son necesarios para crear una partícula?
    def __init__(self, position, ttl, velocidad, aceleracion):
        self.position = np.array(position, dtype = float)
        self.max_ttl = ttl
        self.ttl =  ttl
        self.velocidad = np.array(velocidad, dtype = float)
        self.aceleracion = np.array(aceleracion, dtype = float)

    # ¿Qué se debe actualizar en cada frame?
    def step(self, dt):
        self.velocidad += self.aceleracion * dt
        self.position += self.velocidad*dt
        self.ttl -= dt
    

    # Puede definir más métodos si lo estima conveniente :D
    def alive(self):
        return bool(self.ttl > 0)



if __name__ == "__main__":

    controller = Controller(800, 800, "Tarea_1")

    # A continuación defina los shaders.
    vertex_source = """
    #version 330
    in vec2 position; 
    in vec3 color;
    in float ttl;
    in float max_ttl;    

    out vec3 fragColor; 
    out float alpha;

    void main() {
        gl_PointSize = 10.0 * (ttl / 3.0);
        gl_Position = vec4(position, 0.0, 1.0); 
        fragColor = color;
        alpha = ttl / max_ttl;
    }
    """

    fragment_source = """
    #version 330
    in vec3 fragColor;
    out vec4 outColor;
    
    void main() 
    {
        outColor = vec4(fragColor, 1.0);
    }
    """

    special_source = """
    #version 330
    in vec3 fragColor;
    in float alpha;
    out vec4 outColor;
    
    void main() 
    {
        outColor = vec4(1.0, 1.0, 0.0, alpha);
    }
    """



    # Luego su[s] pipeline[s]
    vert_shader = Shader(vertex_source, 'vertex')
    frag_shader = Shader(fragment_source, 'fragment')
    special_shader = Shader(special_source, 'fragment')
    pipeline = ShaderProgram(vert_shader, frag_shader)
    pipeline_special = ShaderProgram(vert_shader, special_shader)

    # Defina las figuras para los cañones
    indices_canon = [0, 1, 2, 
                    0, 2, 3]
    pos_vertices_izq = [
        -1.0, -1.0, # Ver 0
        -0.6, -1.0, # Ver 1
        -0.5, -0.8, # Ver 2
        -0.8, -0.6 # Ver 3
    ]
    colores_canones = [
        1.0, 0.2, 0.2, # Ver 0
        1.0, 0.2, 0.2, # Ver 1
        1.0, 0.2, 0.2, # Ver 2
        1.0, 0.2, 0.2 # Ver 3
    ]
    gpu_canon_izq = pipeline.vertex_list_indexed(4, GL_TRIANGLES, indices_canon)
    gpu_canon_izq.position = pos_vertices_izq
    gpu_canon_izq.color = colores_canones
    pos_vertices_der = [
        1.0, -1.0, # Ver 0
        0.6, -1.0, # Ver 1
        0.5, -0.8, # Ver 2
        0.8, -0.6 # Ver 3
    ]

    color_bala_grande = [1.0, 0.0, 1.0]
    color_bala_pequena = [0.0, 1.0, 1.0]
    gpu_canon_der = pipeline.vertex_list_indexed(4, GL_TRIANGLES, indices_canon)
    gpu_canon_der.position = pos_vertices_der
    gpu_canon_der.color = colores_canones

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
        pipeline.use()
        gpu_canon_izq.draw(GL_TRIANGLES)
        gpu_canon_der.draw(GL_TRIANGLES)
        if controller.particles_peq_gpu_object is not None:
            controller.particles_peq_gpu_object.draw(GL_POINTS)
        if controller.particles_gran_gpu_object is not None:
            controller.particles_gran_gpu_object.draw(GL_POINTS)


    # Esta función es importante, ya que le ayudará a interactuar con el teclado.
    # Actualmente, está programada para que cada vez que se presione "A", 
    # se imprima "Presionaste A!"
    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == key.A:
            v_x = np.random.uniform(2.0, 3.0)
            v_y = np.random.uniform(1.0, 2.0)
            p_pequena = Particle([-0.8, -0.7], 5.0, [v_x, v_y], [0.0 ,-2.0])
            controller.particles_peq.append(p_pequena)

        if symbol == key.D:
            v_x = np.random.uniform(-3.0, -2.0)
            v_y = np.random.uniform(0.9, 2.0)
            p_grande = Particle([0.8, -0.7], 10.0, [v_x, v_y], [0.0 ,-4.0])
            controller.particles_gran.append(p_grande)




    # Aquí se actualiza todo el sistema de partículas
    def update_particle_system(dt, controller):
        to_remove_peq = 0
        to_remove_gran = 0
        for i in range(len(controller.particles_peq)):
            p = controller.particles_peq[i]
            p.step(dt)
            if not p.alive():
                to_remove_peq += 1
        for i in range(to_remove_peq):
            controller.particles_peq.popleft()
        if controller.particles_peq_gpu_object is not None:
            controller.particles_peq_gpu_object.delete()
            controller.particles_peq_gpu_object = None
        if len(controller.particles_peq) > 0:
            controller.particles_peq_gpu_object = pipeline_special.vertex_list(len(controller.particles_peq), GL_POINTS)
            pos = []
            ttls = []
            for p in controller.particles_peq:
                pos += p.position.tolist()
                ttls.append(p.ttl)
            controller.particles_peq_gpu_object.position[:] = np.array(pos)
            controller.particles_peq_gpu_object.ttl[:] = np.array(ttls)
        for i in range(len(controller.particles_gran)):
            p = controller.particles_gran[i]
            p.step(dt)
            if not p.alive():
                to_remove_gran += 1
        for i in range(to_remove_gran):
            controller.particles_gran.popleft()
        if controller.particles_gran_gpu_object is not None:
            controller.particles_gran_gpu_object.delete()
            controller.particles_gran_gpu_object = None
        if len(controller.particles_gran) > 0:
            controller.particles_gran_gpu_object = pipeline_special.vertex_list(len(controller.particles_gran), GL_POINTS)
            pos = []
            ttls = []
            for p in controller.particles_gran:
                pos += p.position.tolist()
                ttls.append(p.ttl)
            controller.particles_gran_gpu_object.position[:] = np.array(pos)
            controller.particles_gran_gpu_object.ttl[:] = np.array(ttls)

        
    clock.schedule(update_particle_system, controller)
    run()