import pyglet
import math
import random
import numpy as np

window = pyglet.window.Window(800,600, 'Propuesto aux 3')
batch = pyglet.graphics.Batch()

class Particula(object):
    def __init__(self, posicion, velocidad, ttl, es_cohete = True):
        self.posicion = np.array(posicion, dtype = np.float32)
        self.velocidad = np.array(velocidad, dtype = np.float32)
        self.ttl = ttl
        self.es_cohete = es_cohete
        if es_cohete == True:
            color = (255, 255, 255)
        else:
            color = (255, random.randint(100, 200), 0)
        self.forma = pyglet.shapes.Rectangle(x = self.posicion[0], y = self.posicion[1], width=5, height=5, color=color, batch=batch)
    def step(self, dt):
        self.ttl = self.ttl - dt
        self.velocidad[1] -= 150.0 * dt
        self.posicion = self.posicion + dt * self.velocidad
        self.forma.x = self.posicion[0]
        self.forma.y = self.posicion[1]

particulas = []
def lanzar_cohete():
    cohete = Particula([400, 0, 0], [0, 400, 0], 1.5, True)
    particulas.append(cohete)
lanzar_cohete()
def update(dt):
    global particulas
    sobrevivientes = []
    for p in particulas:
        p.step(dt)
        if p.ttl > 0:
            sobrevivientes.append(p)
        else:
            if p.es_cohete:
                for _ in range(60):
                    angulo = random.uniform(0.0, 2 * math.pi)
                    fuerza = random.uniform(0.0, 2 * math.pi)
                    vel_x = math.cos(angulo) * fuerza
                    vel_y = math.sin(angulo) * fuerza
                    chispa = Particula([p.posicion[0], p.posicion[1], 0], [vel_x, vel_y, 0], random.uniform(0.5, 1.2), False)
                    sobrevivientes.append(chispa)
    particulas=sobrevivientes
    if len(particulas) == 0:
        lanzar_cohete()

@window.event
def on_draw():
    window.clear()
    batch.draw()
pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()