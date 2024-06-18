import json
from ursina import Ursina, Vec3, Button, color, scene, mouse, destroy, application, load_texture, Text, Entity, camera, TextField, window, held_keys, raycast
from ursina.prefabs.first_person_controller import FirstPersonController
from noise import Noise
from block import Block
from utils import Utils
from mob import Mob
from chunkgen import Chunkgen  # Import the Chunk class

class Player(FirstPersonController):
    inventory = ["textures/grass.png", "textures/gravel.png", "textures/stone.png", "textures/stone_bricks.png", "textures/log.png", "textures/wood.png", "textures/glass.png"]
    inventory_names = ["Grass", "Gravel", "Stone", "Stone Bricks", "Log", "Wood", "Glass"]
    inventory_slots = len(inventory)

    def __init__(self):
        super().__init__()
        self.height = 0.6
        self.inventory_index = 0
        self.world_blocks = []
        self.boxes = []
        self.placed_blocks = []  # List to store placed block positions
        self.create_boxes()

        # GUI elements
        self.inventory_display = Text(text="Inventory: Grass", origin=(0, 0), x=-0.5, y=0.45, color=color.black, scale=1.5)
        self.health_display = Text(text="Health: 100", origin=(0, 0), x=-0.5, y=0.4, color=color.black, scale=1.5)
        self.chat_display = TextField(x=-0.5, y=-0.45, scale=1.5, limit=30, visible=False)
        self.x_display = Text(text="x: ", origin=(0, 0), x=-0.5, y=0.35, color=color.black, scale=1.5, visible=False)
        self.y_display = Text(text="y: ", origin=(0, 0), x=-0.5, y=0.30, color=color.black, scale=1.5, visible=False)
        self.z_display = Text(text="z: ", origin=(0, 0), x=-0.5, y=0.25, color=color.black, scale=1.5, visible=False)

        self.debug_info_visible = False
        self.chat_open = False
        self.chat_command_mode = False

        self.health = 100
        self.god_mode = False

        # Create Chunk instance for terrain management
        self.chunk_manager = Chunkgen(self)

        # Load previously placed blocks from file on startup
        self.load_placed_blocks()

    def load_placed_blocks(self):
        try:
            with open('placed_blocks.json', 'r') as file:
                self.placed_blocks = json.load(file)
        except FileNotFoundError:
            self.placed_blocks = []

    def save_placed_blocks(self):
        with open('placed_blocks.json', 'w') as file:
            json.dump(self.placed_blocks, file, default=self.Vec3_to_list)

    def place_new_box(self):
        hit_info = mouse.hovered_entity
        if hit_info and isinstance(hit_info, Block) and hit_info.active:
            selected_texture = self.inventory[self.inventory_index]
            new_position = hit_info.position + mouse.normal
            try:
                new_block = Block(position=new_position, texture_path=selected_texture)
                self.boxes.append(new_block)
                self.world_blocks.append(new_block)

                # Add to placed_blocks
                self.placed_blocks.append({
                    'position': self.Vec3_to_list(new_position),
                    'texture_path': selected_texture
                })

                # Save placed_blocks to file
                self.save_placed_blocks()
            except Exception as e:
                print(f"Failed to create new block: {e}")

    def remove_box(self):
        hit_info = mouse.hovered_entity
        if hit_info and isinstance(hit_info, Block) and hit_info.active:
            if hit_info in self.boxes:
                self.boxes.remove(hit_info)

            # Remove from placed_blocks
            block_to_remove = None
            for block in self.placed_blocks:
                if block['position'] == self.Vec3_to_list(hit_info.position):
                    block_to_remove = block
                    break

            if block_to_remove:
                self.placed_blocks.remove(block_to_remove)

            # Save updated placed_blocks to file
            self.save_placed_blocks()

            self.remove_block(hit_info)

    # Helper function to convert Vec3 to list for JSON serialization
    def Vec3_to_list(self, vec):
        return [vec.x, vec.y, vec.z]

    def create_boxes(self):
        for i in range(20):
            for j in range(20):
                noise_val = Noise.perlin_noise(i, j)
                height = int(noise_val * 5)
                position = Vec3(j, height, i)
                box = Block(position=position, texture_path='textures/grass.png')
                self.boxes.append(box)

    def update(self):
        super().update()
        self.update_gui()
        self.chunk_manager.update_terrain()  # Use chunk manager for terrain updates

    def attack(self):
        hit_info = raycast(self.position, self.forward, distance=3, ignore=[self])
        if hit_info.hit:
            if isinstance(hit_info.entity, Mob):
                mob = hit_info.entity
                mob.receive_damage(self.damage_amount)

    def update_gui(self):
        self.health_display.text = f"Health: {int(self.health)}"
        self.inventory_display.text = f"Inventory: {self.get_current_block_name()}"
        if self.debug_info_visible:
            self.x_display.text = f"x: {int(self.x)}"
            self.y_display.text = f"y: {int(self.y)}"
            self.z_display.text = f"z: {int(self.z)}"

    def input(self, key):
        if not self.chat_open:
            super().input(key)

        if key == 'scroll down':
            self.inventory_index = (self.inventory_index - 1) % self.inventory_slots
            self.update_gui()
        elif key == 'scroll up':
            self.inventory_index = (self.inventory_index + 1) % self.inventory_slots
            self.update_gui()

        if key == 'space':
            if not self.god_mode:
                self.jump()
        if self.god_mode and held_keys['space']:
            self.y += 1

        if self.god_mode and held_keys['left shift']:
            self.y -= 1

        if self.chat_open:
            if key == 'enter':
                self.process_chat_command()

        if key == 'escape':
            application.quit()
        elif key == 'right mouse down':
            self.place_new_box()
        elif key == 'left mouse down':
            hit_info = mouse.hovered_entity
            if hit_info and isinstance(hit_info, Block):
                self.remove_box()
                self.attack()
        if key == '/':
            self.toggle_chat()

        if key == 'f3':
            self.toggle_debug_info()

    def toggle_debug_info(self):
        # NEW GUI elements
        self.debug_info_visible = not self.debug_info_visible
        self.x_display.visible = self.debug_info_visible
        self.y_display.visible = self.debug_info_visible
        self.z_display.visible = self.debug_info_visible
        if self.debug_info_visible:
            self.x_display.visible = True
            self.y_display.visible = True
            self.z_display.visible = True
        else:
            self.x_display.visible = False
            self.y_display.visible = False
            self.z_display.visible = False

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
            self.speed = 10
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

    def decrease_health(self, by_how_much):
        self.health -= by_how_much
        if self.health <= 0:
            self.disable()  # Example: Disable player if health drops to zero
        self.update_gui()  # Update GUI after health changes

