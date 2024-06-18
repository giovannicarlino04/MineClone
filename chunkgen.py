import random
from ursina import Vec3, scene, destroy
from noise import Noise
from block import Block

class Chunkgen:
    def __init__(self, player):
        self.player = player
        self.chunk_size = 6  # Size of each terrain chunk
        self.loaded_chunks = {}  # Dictionary to store loaded chunks

    def generate_chunk(self, chunk_key):
        chunk_position = Vec3(chunk_key[0] * self.chunk_size, 0, chunk_key[1] * self.chunk_size)

        for i in range(self.chunk_size):
            for j in range(self.chunk_size):
                noise_val = Noise.perlin_noise(chunk_key[0] * self.chunk_size + i, chunk_key[1] * self.chunk_size + j)
                height = int(noise_val * 5)
                position = chunk_position + Vec3(j, height, i)

                # Check if a block exists at this position in placed_blocks
                block_exists = False
                for block in self.player.placed_blocks:
                    if block['position'] == self.player.Vec3_to_list(position):
                        block_exists = True
                        break

                if not block_exists:
                    texture_path = 'textures/grass.png'  # Example: Customize texture generation here
                    block = Block(position=position, texture_path=texture_path)
                    self.player.world_blocks.append(block)
                    block.parent = scene

        self.loaded_chunks[chunk_key] = True

        # Re-add previously placed blocks in this chunk
        for block in self.player.placed_blocks:
            block_pos = Vec3(*block['position'])
            if chunk_position.x <= block_pos.x < chunk_position.x + self.chunk_size and \
               chunk_position.z <= block_pos.z < chunk_position.z + self.chunk_size:
                new_block = Block(position=block_pos, texture_path=block['texture_path'])
                self.player.world_blocks.append(new_block)
                new_block.parent = scene

        # Add other terrain features
        self.add_trees(chunk_position)
        self.add_structures(chunk_position)

    def add_trees(self, chunk_position):
        # Placeholder for adding trees
        for _ in range(1):  # Example: Add 3 trees randomly in the chunk
            x = chunk_position.x + random.randint(0, self.chunk_size - 1)
            z = chunk_position.z + random.randint(0, self.chunk_size - 1)
            position = Vec3(x, self.get_height_at(x, z), z)
            self.place_tree(position)

    def place_tree(self, position):
        trunk_height = 5
        leaves_radius = 3

        # Create trunk
        for i in range(trunk_height):
            trunk = Block(position=position + Vec3(0, i, 0), texture_path='textures/log.png')
            self.player.world_blocks.append(trunk)
            trunk.parent = scene

        # Create leaves
        for x in range(-leaves_radius, leaves_radius + 1):
            for z in range(-leaves_radius, leaves_radius + 1):
                for y in range(trunk_height, trunk_height + 4):
                    if abs(x) + abs(z) + abs(y - (trunk_height + 2)) <= leaves_radius:
                        leaves = Block(position=position + Vec3(x, y, z), texture_path='textures/leaves.png')
                        self.player.world_blocks.append(leaves)
                        leaves.parent = scene

    def add_structures(self, chunk_position):
        # Placeholder for adding structures, we'll add em in the future
        pass

    def get_height_at(self, x, z):
        noise_val = Noise.perlin_noise(x, z)
        return int(noise_val * 5)

    def update_terrain(self):
        player_chunk_x = int(self.player.x / self.chunk_size)
        player_chunk_z = int(self.player.z / self.chunk_size)

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
        for block in list(self.player.world_blocks):
            if chunk_position.x <= block.x < chunk_position.x + self.chunk_size and \
               chunk_position.z <= block.z < chunk_position.z + self.chunk_size:
                destroy(block)
                block.active = False
                self.player.world_blocks.remove(block)

        del self.loaded_chunks[chunk_key]
