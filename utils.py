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
    
    def save_world(player):
        player_data = {
            'position': [player.x, player.y, player.z],
            'rotation': [player.rotation_x, player.rotation_y, player.rotation_z],
            'inventory_index': player.inventory_index,
            'hunger': player.hunger,
            'health': player.health,
            'world_blocks': [block.serialize() for block in player.world_blocks if block.active]
        }

        with open('save.json', 'w') as f:
            json.dump(player_data, f, default=serialize_vec3, indent=4)
        print("World saved.")

    def load_world(player):
        try:
            with open('save.json', 'r') as f:
                player_data = json.load(f)

                player.position = Vec3(*player_data['position'])
                player.rotation_x = player_data['rotation'][0]
                player.rotation_y = player_data['rotation'][1]
                player.rotation_z = player_data['rotation'][2]
                player.inventory_index = player_data['inventory_index']
                player.hunger = player_data['hunger']
                player.health = player_data['health']

                for block in player.world_blocks:
                    block.active = False
                player.world_blocks.clear()

                for block_data in player_data['world_blocks']:
                    position = Vec3(*block_data['position'])
                    texture_path = block_data['texture_path']

                    existing_block = next((block for block in player.boxes if block.position == position), None)
                    if existing_block:
                        existing_block.active = True
                        player.world_blocks.append(existing_block)
                    else:
                        block = Block(position=position, texture_path=texture_path)
                        player.world_blocks.append(block)
                        player.boxes.append(block)

                player.update_gui()
                print("World loaded. godmode =")

        except FileNotFoundError:
            print("No saved world found.")

def serialize_vec3(vec):
    if isinstance(vec, Vec3):
        return [vec.x, vec.y, vec.z]
    raise TypeError(f"Object of type '{type(vec).__name__}' is not JSON serializable")
