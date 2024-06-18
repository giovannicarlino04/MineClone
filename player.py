import json
import time
from ursina import Ursina, Vec3, Button, color, scene, mouse, destroy, application, load_texture, Text, Entity, camera, TextField, window, held_keys, raycast
from ursina.prefabs.first_person_controller import FirstPersonController
from noise import Noise
from block import Block
from utils import Utils
from mob import Mob
from chunkgen import Chunkgen  # Import the Chunk class


TOOL_EFFICIENCY = {
    'stone_pickaxe': {
        'stone': 3.0,
        'coal_ore': 3.0,
        'copper_ore':3.0,
        'iron_ore': 3.0,
        'diamond_ore': 3.0
    },
    'stone_axe': {
        'log': 3.0,
        'wood': 3.0
    },
}
CRAFTING_RECIPES = {
    'stone_pickaxe': {
        'stone': 3,
        'wood': 2
    },
    'stone_axe': {
        'wood': 3
    }
}


class Player(FirstPersonController):
    removing_block = False
    inventory = {}
    inventory_names = ["Grass", "Gravel", "Stone", "Stone Bricks", "Log", "Wood", "Glass"]
    inventory_slots = len(inventory)

    tool_full_names = ["stone_pickaxe", "stone_axe"]
    tool_names = ["Stone Pickaxe", "Stone Axe"]
    tool_slots = len(tool_full_names)

    def craft_tool(self, tool_name):
        if tool_name in CRAFTING_RECIPES:
            recipe = CRAFTING_RECIPES[tool_name]
            for resource, amount in recipe.items():
                if self.inventory.get(resource, 0) < amount:
                    print(f"Cannot craft {tool_name}. Missing {resource}.")
                    return False

            # Remove resources from inventory
            for resource, amount in recipe.items():
                self.inventory[resource] -= amount

            # Set current tool
            self.current_tool = tool_name
            print(f"Crafted {tool_name}.")
            return True
        else:
            print(f"No crafting recipe found for {tool_name}.")
            return False

    def __init__(self):
        super().__init__()
        self.current_tool = None  # No initial tool
        self.inventory = {i: None for i in range(self.inventory_slots)}  # Initialize with placeholders
        self.height = 0.6
        self.inventory_index = 0
        self.tool_index = 0
        self.world_blocks = []
        self.boxes = []
        self.placed_blocks = []  # List to store placed block positions
        self.create_boxes()


        # GUI elements
        self.inventory_display = Text(text="Inventory: ", origin=(0, 0), x=-0.5, y=0.45, color=color.black, scale=1.5)
        self.health_display = Text(text="Health: 100", origin=(0, 0), x=-0.5, y=0.4, color=color.black, scale=1.5)
        self.current_tool_display = Text(text="Tool: Stone Pickaxe", origin=(0, 0), x=-0.5, y=0.35, color=color.black, scale=1.5)
        self.chat_display = TextField(x=-0.5, y=-0.45, scale=1.5, limit=30, visible=False)
        self.block_count_display = Text(text=f"Blocks: {len(self.inventory)}", origin=(0, 0), x=0, y=-0.45, color=color.black, scale=1.5)
        self.x_display = Text(text="X: ", origin=(0, 0), x=-0.5, y=0.35, color=color.black, scale=1.5, visible=False)
        self.y_display = Text(text="Y: ", origin=(0, 0), x=-0.5, y=0.30, color=color.black, scale=1.5, visible=False)
        self.z_display = Text(text="Z: ", origin=(0, 0), x=-0.5, y=0.25, color=color.black, scale=1.5, visible=False)

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
        
        # Check if currently removing a block
        if self.removing_block:
            self.timer += time.dt  # Increase timer based on delta time
            # Calculate removal progress (0 to 1)
            removal_progress = self.timer / self.removal_speed
            
            # Gradually destroy the block based on removal progress
            if removal_progress >= 1:
                destroy(self.block_to_remove)
                self.world_blocks.remove(self.block_to_remove)
                self.removing_block = False
            else:
                # Example: Gradually reduce block's scale
                self.block_to_remove.scale_y = 1 - removal_progress
                self.block_to_remove.scale_x = 1 - removal_progress
                self.block_to_remove.scale_z = 1 - removal_progress

    def attack(self):
        hit_info = raycast(self.position, self.forward, distance=3, ignore=[self])
        if hit_info.hit:
            if isinstance(hit_info.entity, Mob):
                mob = hit_info.entity
                mob.receive_damage(self.damage_amount)

    def update_gui(self):
        self.current_tool_display.text = f"Tool: {self.get_current_tool_name()}"
        self.health_display.text = f"Health: {int(self.health)}"
        self.inventory_display.text = f"Inventory: {self.get_current_block_name()}"
        self.block_count_display.text = f"Blocks: {len(self.inventory)}"
        if self.debug_info_visible:
            self.x_display.text = f"X: {int(self.x)}"
            self.y_display.text = f"Y: {int(self.y)}"
            self.z_display.text = f"Z: {int(self.z)}"

    def input(self, key):
        if not self.chat_open:
            super().input(key)

        if key == 'scroll down':
            if(self.inventory_index > 0):
                self.inventory_index = (self.inventory_index - 1) % self.inventory_slots
                self.update_gui()
        elif key == 'scroll up':
            if(self.inventory_index > 0):
                self.inventory_index = (self.inventory_index + 1) % self.inventory_slots
                self.update_gui()

        if key == 'q':
            self.tool_index = (self.tool_index + 1) % self.tool_slots
            self.update_gui()

        if key == 'e':
            # Attempt to craft the selected tool
            tool_to_craft = self.tool_full_names[self.tool_index]
            self.craft_tool(tool_to_craft)
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
        if self.inventory:
            return self.inventory_names[self.inventory_index]
        else:
            return "Empty"
    def get_current_tool_name(self):
        return self.tool_full_names[self.tool_index]

    def add_to_inventory(self, item_name):
        if item_name in self.inventory:
            self.inventory[item_name] += 1
        else:
            self.inventory[item_name] = 1

    def remove_block(self, block):
        if block in self.world_blocks:
            block_type = block.texture_path.split('/')[-1].split('.')[0]  # Extract block type from texture path

            # Check if the current tool is crafted and fetch efficiency accordingly
            if self.current_tool and self.current_tool in TOOL_EFFICIENCY:
                tool_name = self.current_tool
            else:
                tool_name = 'default_tool'  # Adjust as needed for default tool efficiency

            if block_type in TOOL_EFFICIENCY.get(tool_name, {}):
                efficiency = TOOL_EFFICIENCY[tool_name][block_type]
            else:
                efficiency = 0.1  # Default efficiency if not specified

            # Calculate removal speed based on block hardness and tool efficiency
            block_hardness = self.get_block_hardness(block_type)
            removal_speed = block_hardness / efficiency

            # Start the removal process using a timer
            self.timer = 0
            self.removal_speed = removal_speed
            self.block_to_remove = block
            self.removing_block = True

            # Remove the block from the world and update placed_blocks
            self.world_blocks.remove(block)
            self.placed_blocks = [b for b in self.placed_blocks if b['position'] != self.Vec3_to_list(block.position)]

            # Add the removed block to inventory
            self.add_to_inventory(block_type)

            # Save updated placed_blocks to file
            self.save_placed_blocks()


    def get_block_hardness(self, block_type):
        # Define block hardness values (example)
        block_hardness = {
            'grass': 1.0,
            'stone': 3.0,
            'log': 3.0,
            'wood': 3.0
        }
        return block_hardness.get(block_type, 0.1)  # Default hardness if not specified

    def decrease_health(self, by_how_much):
        self.health -= by_how_much
        if self.health <= 0:
            self.disable()  # Example: Disable player if health drops to zero
        self.update_gui()  # Update GUI after health changes

