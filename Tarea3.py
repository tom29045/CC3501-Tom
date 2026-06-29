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

    controller = Controller(1280,720,"Tarea 2")
    controller.set_exclusive_mouse(True)

    vert_source = """
    #version 330

    in vec3 position;
    in vec2 texCoord;
    in vec3 normal;

    out vec2 fragTexCoord;
    out vec3 fragNormal;
    out vec3 fragPosition;

    uniform mat4 u_model = mat4(1.0);
    uniform mat4 u_view = mat4(1.0);
    uniform mat4 u_projection = mat4(1.0);

    void main() {
        fragTexCoord = texCoord;
        fragPosition = vec3(u_model * vec4(position, 1.0));
        fragNormal = mat3(transpose(inverse(u_model))) * normal;
        gl_Position = u_projection * u_view * u_model * vec4(position, 1.0f);
    }
    """

    frag_source = """
    #version 330

    in vec2 fragTexCoord;
    in vec3 fragNormal;
    in vec3 fragPosition;

    uniform sampler2D u_texture;
    uniform vec3 u_viewPos;
    uniform vec3 u_lightPositions[4];
    uniform vec3 u_lightColor = vec3(1.0, 0.95, 0.85);

    vec3 Ka = vec3(0.15);
    vec3 Ks = vec3(0.4);
    float Ns = 32.0;
    out vec4 outColor;

    void main() {
        vec3 N = normalize(fragNormal);
        vec3 V = normalize(u_viewPos - fragPosition);
    
        vec3 totalDiffuse = vec3(0.0);
        vec3 totalSpecular = vec3(0.0);
    

        for(int i = 0; i < 4; i++) {
            vec3 L = normalize(u_lightPositions[i] - fragPosition);
        
            float diff = max(dot(N, L), 0.0);
            totalDiffuse += diff * u_lightColor;
        
            vec3 H = normalize(L + V);
            float spec = pow(max(dot(N, H), 0.0), Ns);
            totalSpecular += spec * u_lightColor * Ks;
        }
    
        vec4 texColor = texture(u_texture, fragTexCoord);
    
        vec3 ambientFactor = Ka * u_lightColor;
        vec3 finalColor = (ambientFactor + totalDiffuse) * texColor.rgb + totalSpecular;
    
        outColor = vec4(finalColor, texColor.a);
    }
    """

    vertex_shader = Shader(vert_source, "vertex")
    fragment_shader = Shader(frag_source, "fragment")
    pipeline = ShaderProgram(vertex_shader, fragment_shader)

    cam = MyCam([0.0, 8.0, 30.0])
    
    focos_estadio = [
        19.5, 12.0, 13.5,
        -19.5, 12.0, 13.5,
        19.5, 12.0, -13.5,
        -19.5, 12.0, -13.5
    ]

    pipeline["u_lightPositions"] = focos_estadio

    @controller.event
    def on_draw():
        controller.clear()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pipeline.use()
        world.draw()

    clock.schedule_interval(update,1/60)
    run()