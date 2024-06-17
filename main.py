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

class Player(FirstPersonController):
    inventory = ["textures/grass.png", "textures/stone.png", "textures/log.png", "textures/wood.png", "textures/glass.png"]
    inventory_names = ["Grass", "Stone", "Log", "Wood", "Glass"]
    inventory_slots = len(inventory)

    def __init__(self):
        super().__init__()
        self.height = 1
        self.inventory_index = 0
        self.world_blocks = []

        # GUI elements
        self.inventory_display = Text(text="Inventory: Grass", origin=(0, 0), x=-0.5, y=0.45, color=color.black, scale=1.5)
        self.health_display = Text(text="Health: 100", origin=(0, 0), x=-0.5, y=0.4, color=color.black, scale=1.5)
        self.hunger_display = Text(text="Hunger: 100", origin=(0, 0), x=-0.5, y=0.35, color=color.black, scale=1.5)
        self.chat_display = TextField(x=-0.5, y=-0.45, scale=1.5, limit=30, visible=False)
        
        self.chat_open = False
        self.chat_command_mode = False
        self.god_mode = False
        
        self.health = 100
        self.hunger = 100


class Player(FirstPersonController):
    inventory = ["textures/grass.png", "textures/stone.png", "textures/log.png", "textures/wood.png", "textures/glass.png"]
    inventory_names = ["Grass", "Stone", "Log", "Wood", "Glass"]
    inventory_slots = len(inventory)

    def __init__(self):
        super().__init__()
        self.height = 1
        self.inventory_index = 0
        self.world_blocks = []

        # GUI elements
        self.inventory_display = Text(text="Inventory: Grass", origin=(0, 0), x=-0.5, y=0.45, color=color.black, scale=1.5)
        self.health_display = Text(text="Health: 100", origin=(0, 0), x=-0.5, y=0.4, color=color.black, scale=1.5)
        self.hunger_display = Text(text="Hunger: 100", origin=(0, 0), x=-0.5, y=0.35, color=color.black, scale=1.5)
        self.chat_display = TextField(x=-0.5, y=-0.45, scale=1.5, limit=30, visible=False)
        
        self.chat_open = False
        self.chat_command_mode = False
        self.god_mode = False
        
        self.health = 100
        self.hunger = 100

        # Terrain generation variables
        self.chunk_size = 16  # Size of each terrain chunk
        self.loaded_chunks = {}  # Dictionary to store loaded chunks

    def update_visible_faces(self):
            for block in self.world_blocks:
                if block.active:
                    self.load_visible_faces(block)
                else:
                    self.unload_faces(block)

    def load_visible_faces(self, block):
        # Example: Simple visibility logic (replace with actual logic)
        block.visible_faces = { 'up': True, 'down': True, 'north': True, 'south': True, 'east': True, 'west': True }
        # Implement logic to determine which faces are visible based on game rules

    def unload_faces(self, block):
        # Remove non-visible faces
        for face in list(block.visible_faces.keys()):
            if not block.visible_faces[face]:
                block.faces[face].disable()  # Example: disable() method to disable face rendering
            else:
                block.faces[face].enable()  # Example: enable() method to enable face rendering
    def update(self):
        super().update()
        self.update_gui()
        self.update_survival_status()
        self.update_terrain()

    def update_gui(self):
        self.health_display.text = f"Health: {int(self.health)}"
        self.hunger_display.text = f"Hunger: {int(self.hunger)}"
        self.inventory_display.text = f"Inventory: {self.get_current_block_name()}"

    def update_survival_status(self):
        self.hunger -= 0.0001
        if self.hunger < 0:
            self.hunger = 0

    def generate_chunk(self, chunk_key):
        chunk_position = Vec3(chunk_key[0] * self.chunk_size, 0, chunk_key[1] * self.chunk_size)

        for i in range(self.chunk_size):
            for j in range(self.chunk_size):
                noise_val = Noise.perlin_noise(chunk_key[0] * self.chunk_size + i, chunk_key[1] * self.chunk_size + j)
                height = int(noise_val * 5)
                position = chunk_position + Vec3(j, height, i)
                texture_path = 'textures/grass.png'  # Example: Customize texture generation here
                block = Block(position=position, texture_path=texture_path)
                self.world_blocks.append(block)
                block.parent = scene

        self.loaded_chunks[chunk_key] = True

    def update_terrain(self):
        player_chunk_x = int(self.x / self.chunk_size)
        player_chunk_z = int(self.z / self.chunk_size)

        # Load chunks around the player if not already loaded
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                chunk_key = (player_chunk_x + dx, player_chunk_z + dz)
                if chunk_key not in self.loaded_chunks:
                    self.generate_chunk(chunk_key)

        # Unload chunks that are far from the player
        chunks_to_remove = []
        for chunk_key in list(self.loaded_chunks.keys()):  # Use list() to iterate over a copy of keys
            if abs(chunk_key[0] - player_chunk_x) > 1 or abs(chunk_key[1] - player_chunk_z) > 1:
                chunks_to_remove.append(chunk_key)

        for chunk_key in chunks_to_remove:
            self.unload_chunk(chunk_key)
   
    def unload_chunk(self, chunk_key):
        chunk_position = Vec3(chunk_key[0] * self.chunk_size, 0, chunk_key[1] * self.chunk_size)

        # Remove blocks from the scene and deactivate them
        for block in list(self.world_blocks):
            if chunk_position.x <= block.x < chunk_position.x + self.chunk_size and \
            chunk_position.z <= block.z < chunk_position.z + self.chunk_size:
                destroy(block)
                block.active = False
                self.world_blocks.remove(block)

        del self.loaded_chunks[chunk_key]
        
    def input(self, key):
        if(self.chat_open == False):
            super().input(key)

        if key == 'scroll down':
            self.inventory_index = (self.inventory_index - 1) % self.inventory_slots
            self.update_gui()
        elif key == 'scroll up':
            self.inventory_index = (self.inventory_index + 1) % self.inventory_slots
            self.update_gui()
        elif key == 'n':
            if(self.chat_open == False):
                self.save_world()
        elif key == 'm':
            if(self.chat_open == False):
                self.load_world()

        if key == 'space':
            if(self.god_mode == False):
                self.jump()
            if(self.god_mode):
                self.y += 1
        if key == 'left shift':
            if(self.god_mode):
                self.y -= 1

        if self.chat_open:
            if key == 'enter':
                self.process_chat_command()
            elif key == 'escape':
                self.close_chat()

        elif key == 't':
            self.toggle_chat()

    def toggle_chat(self):
        self.chat_open = not self.chat_open
        self.chat_display.visible = self.chat_open
        if self.chat_open:
            self.chat_display.text = ""
            self.chat_display.active = True
        else:
            self.chat_display.text = ""
            self.chat_display.active = False

    def process_chat_command(self):
        command = self.chat_display.text.strip().lower()
        if command == '/godmode':
            self.toggle_god_mode()
        self.close_chat()

    def close_chat(self):
        self.chat_open = False
        self.chat_display.text = ""
        self.chat_display.visible = False

    def toggle_god_mode(self):
        self.god_mode = not self.god_mode
        if self.god_mode:
            self.gravity = 0
            self.y = self.height
        else:
            self.gravity = 1

    def jump(self):
        if not self.god_mode:
            super().jump()

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
            'hunger': self.hunger,
            'health': self.health,
            'world_blocks': [block.serialize() for block in self.world_blocks if block.active]
        }

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
                self.hunger = player_data['hunger']
                self.health = player_data['health']

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

                self.update_gui()
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
                noise_val = Noise.perlin_noise(i, j)
                height = int(noise_val * 5)
                position = Vec3(j, height, i)
                box = Block(position=position, texture_path='textures/grass.png')
                self.boxes.append(box)

    def input(self, key):
        if key == 'escape':
            application.quit()
        elif key == 'right mouse down':
            self.place_new_box()
        elif key == 'left mouse down':
            self.remove_box()

    def place_new_box(self):
        hit_info = mouse.hovered_entity
        if hit_info and isinstance(hit_info, Block) and hit_info.active:
            selected_texture = self.player.inventory[self.player.inventory_index]
            new_position = hit_info.position + mouse.normal  # Corrected line
            try:
                new_block = Block(position=new_position, texture_path=selected_texture)
                self.boxes.append(new_block)
                self.player.world_blocks.append(new_block)
            except Exception as e:
                print(f"Failed to create new block: {e}")

    def remove_box(self):
        hit_info = mouse.hovered_entity
        if isinstance(hit_info, Block) and hit_info.active:
            self.player.remove_block(hit_info)  # Remove from player's world_blocks
            if hit_info in self.boxes:
                self.boxes.remove(hit_info)  # Remove from environment's boxes

class MainMenu(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui)
        self.visible = True

        self.start_button = Button(
            text='Start Game',
            color=color.azure,
            scale=(0.2, 0.1),
            position=(0, 0.1),
            on_click=self.start_game
        )

        self.load_button = Button(
            text='Load Game',
            color=color.azure,
            scale=(0.2, 0.1),
            position=(0, 0),
            on_click=self.load_game
        )

        self.quit_button = Button(
            text='Quit',
            color=color.azure,
            scale=(0.2, 0.1),
            position=(0, -0.1),
            on_click=application.quit
        )

    def start_game(self):
        for box in environment.boxes:
            box.enabled = True
        player.enabled = True
        self.start_button.enabled = False
        self.load_button.enabled = False
        self.quit_button.enabled = False  

    def load_game(self):
        player.load_world()
        self.start_game()
        self.start_button.enabled = False
        self.load_button.enabled = False
        self.quit_button.enabled = False
    


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
for box in environment.boxes:
    box.enabled = False
player.enabled = False

application.development_mode = False

main_menu = MainMenu()

app.run()
