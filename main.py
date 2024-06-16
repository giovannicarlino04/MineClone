import json
from ursina import Ursina, Vec3, Button, color, scene, mouse, destroy, application, load_texture, Text
from ursina.prefabs.first_person_controller import FirstPersonController

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

class Player(FirstPersonController):
    inventory = ["textures/grass.png", "textures/stone.png", "textures/log.png", "textures/wood.png", "textures/glass.png"]
    inventory_names = ["Grass", "Stone", "Log", "Wood", "Glass"]
    inventory_slots = len(inventory)

    def __init__(self):
        super().__init__()
        self.height = 2
        self.inventory_index = 0
        self.world_blocks = []
        self.tooltip = Text(text=self.get_current_block_name(), origin=(0, 0), y=0.5, parent=self)

    def update(self):
        super().update()
        self.tooltip.world_position = self.world_position + (0, 1, 0)

    def input(self, key):
        if key == 'q':
            self.inventory_index = (self.inventory_index - 1) % self.inventory_slots
            self.tooltip.text = self.get_current_block_name()
        elif key == 'e':
            self.inventory_index = (self.inventory_index + 1) % self.inventory_slots
            self.tooltip.text = self.get_current_block_name()
        elif key == 'n':
            self.save_world()
        elif key == 'm':
            self.load_world()

    def get_current_block_name(self):
        return self.inventory_names[self.inventory_index]
        
    def remove_block(self, block):
        if block in self.world_blocks:
            self.world_blocks.remove(block)
            destroy(block)
            block.active = False

    def save_world(self):
        player_data = {
            'position': [self.x, self.y, self.z],
            'rotation': [self.rotation_x, self.rotation_y, self.rotation_z],
            'inventory_index': self.inventory_index,
            'world_blocks': []
        }

        for block in self.world_blocks:
            if block.active:
                player_data['world_blocks'].append(block.serialize())

        with open('save.json', 'w') as f:
            json.dump(player_data, f, default=serialize_vec3, indent=4)
        print("World saved.")

    def load_world(self):
        try:
            with open('save.json', 'r') as f:
                player_data = json.load(f)

                self.position = Vec3(*player_data['position'])
                self.rotation_x = player_data['rotation'][0]
                self.rotation_y = player_data['rotation'][1]
                self.rotation_z = player_data['rotation'][2]
                self.inventory_index = player_data['inventory_index']

                for block in self.world_blocks:
                    block.active = False
                self.world_blocks.clear()

                for block_data in player_data['world_blocks']:
                    position = Vec3(*block_data['position'])
                    texture_path = block_data['texture_path']

                    existing_block = next((block for block in environment.boxes if block.position == position), None)
                    if existing_block:
                        existing_block.active = True
                        self.world_blocks.append(existing_block)
                    else:
                        block = Block(position=position, texture_path=texture_path)
                        self.world_blocks.append(block)
                        environment.boxes.append(block)

                self.tooltip.text = self.get_current_block_name()
                print("World loaded.")

        except FileNotFoundError:
            print("No saved world found.")

class Environment:
    def __init__(self, player):
        self.player = player
        self.boxes = []
        self.create_boxes()

    def create_boxes(self):
        for i in range(20):
            for j in range(20):
                box = Block(position=Vec3(j, 0, i), texture_path='textures/grass.png')
                self.boxes.append(box)

    def input(self, key):
        if key == 'escape':
            application.close_window()
        for box in self.boxes:
            if box.hovered:
                if key == 'right mouse down':
                    self.place_new_box(box)
                if key == 'left mouse down':
                    self.remove_box(box)

    def place_new_box(self, target_box):
        if target_box.active:
            selected_texture = self.player.inventory[self.player.inventory_index]
            new_position = target_box.position + mouse.normal
            try:
                new_box = Block(position=new_position, texture_path=selected_texture)
                self.boxes.append(new_box)
                self.player.world_blocks.append(new_box)
            except Exception as e:
                print(f"Failed to create new box: {e}")

    def remove_box(self, target_box):
        if target_box.active:
            self.player.remove_block(target_box)

def serialize_vec3(vec):
    if isinstance(vec, Vec3):
        return [vec.x, vec.y, vec.z]
    raise TypeError(f"Object of type '{type(vec).__name__}' is not JSON serializable")

def update():
    player.update()

def input(key):
    player.input(key)
    environment.input(key)

app = Ursina()

player = Player()
environment = Environment(player)

app.run()
