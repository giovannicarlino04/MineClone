import json, random
from ursina import Ursina, Vec3, Button, color, scene, mouse, destroy, application, load_texture, Text, Entity, camera, TextField, window
from ursina.prefabs.first_person_controller import FirstPersonController
from noise import Noise

class Block(Button):
    def __init__(self, position=Vec3(0, 0, 0), texture_path="textures/grass.png"):
        super().__init__(
            color=color.white,
            model='cube',
            texture=load_texture(texture_path),
            position=position,
            parent=scene,
            origin_y=0.5
        )
        self.texture_path = texture_path
        self.active = True

    def serialize(self):
        return {
            'position': [self.x, self.y, self.z],
            'texture_path': self.texture_path
        }