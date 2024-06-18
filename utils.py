import json
from block import Block
from ursina import Vec3

class Utils:

    def __init__(self) -> None:
        pass

    def update(self):
        self.player.update()

    def input(key, self):
        self.player.input(key)

def serialize_vec3(vec):
    if isinstance(vec, Vec3):
        return [vec.x, vec.y, vec.z]
    raise TypeError(f"Object of type '{type(vec).__name__}' is not JSON serializable")
