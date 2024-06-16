import json
from ursina import Ursina, Vec3, Button, color, scene, mouse, destroy, application, load_texture, Text
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
        self.tooltip = Text(text=self.get_current_block_name(), origin=(0, 0), y=-0.4, parent=scene, eternal=True, ignore_paused=True)
        self.tooltip.visible = True  # Ensure tooltip is initially visible
        self.inventory_display = Text(text="Inventory", origin=(0, 0), y=0.4, parent=scene, eternal=True, ignore_paused=True)
        self.inventory_display.visible = True  # Ensure inventory display is initially visible
        self.health_display = Text(text="Health: 100", origin=(0, 0), y=0.3, parent=scene, eternal=True, ignore_paused=True)
        self.health_display.visible = True  # Ensure health display is initially visible
        self.hunger_display = Text(text="Hunger: 100", origin=(0, 0), y=0.2, parent=scene, eternal=True, ignore_paused=True)
        self.hunger_display.visible = True  # Ensure hunger display is initially visible
        
        # Initial setup
        self.tooltip.enabled = True
        self.inventory_display.enabled = True
        self.health_display.enabled = True
        self.hunger_display.enabled = True
        
        # Survival mode attributes
        self.health = 100
        self.hunger = 100

        # Debug chat variables
        self.chat_open = False
        self.chat_command_mode = False
        self.god_mode = False

    def update(self):
        super().update()
        self.tooltip.world_position = self.world_position + (0, 2, 0)  # Adjust tooltip position as needed
        
        # Update GUI elements
        self.update_gui()

        # Survival mode update logic
        self.update_survival_status()

    def update_gui(self):
        self.health_display.text = f"Health: {int(self.health)}"
        self.hunger_display.text = f"Hunger: {int(self.hunger)}"
        self.inventory_display.text = f"Inventory: {self.get_current_block_name()}"

    def update_survival_status(self):
        # Example: Decrease hunger over time
        self.hunger -= 0.01
        if self.hunger < 0:
            self.hunger = 0

    def input(self, key):
        # Handle movement and basic actions
        super().input(key)
        if key == 'q':
            self.inventory_index = (self.inventory_index - 1) % self.inventory_slots
            self.update_gui()
        elif key == 'e':
            self.inventory_index = (self.inventory_index + 1) % self.inventory_slots
            self.update_gui()
        elif key == 'n':
            self.save_world()
        elif key == 'm':
            self.load_world()

        if key == 'space':
            self.jump()
        # Debug commands
        if key == 't':
            self.toggle_tooltip()
        elif key == '/' and self.chat_open:
            self.chat_command_mode = True
            self.tooltip.text = '/'
        elif self.chat_command_mode:
            if key == 'enter':
                self.process_chat_command()
            elif key == 'escape':
                self.close_chat()
            else:
                self.tooltip.text += key

        # Survival mode inputs
        if not self.chat_open and not self.chat_command_mode:
            if key == 'space':
                self.jump()

    def toggle_tooltip(self):
        self.tooltip.visible = not self.tooltip.visible
        self.inventory_display.visible = not self.inventory_display.visible
        self.health_display.visible = not self.health_display.visible
        self.hunger_display.visible = not self.hunger_display.visible

    def open_chat(self):
        self.chat_open = True
        self.chat_command_mode = False
        self.tooltip.text = 'Chat: '
    
    def close_chat(self):
        self.chat_open = False
        self.tooltip.text = self.get_current_block_name()

    def process_chat_command(self):
        command = self.tooltip.text.strip()
        if command == '/godmode':
            self.toggle_god_mode()
        self.close_chat()

    def toggle_god_mode(self):
        if not self.god_mode:
            self.gravity = 0
            self.y = self.height
        else:
            self.gravity = 1
        self.god_mode = not self.god_mode

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
                # Calculate terrain height using Perlin noise
                noise_val = Noise.perlin_noise(i, j)
                height = int(noise_val * 5)  # Adjust multiplier for terrain height

                # Create block at calculated height
                position = Vec3(j, height, i)
                box = Block(position=position, texture_path='textures/grass.png')
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
            self.boxes.remove(target_box)

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
