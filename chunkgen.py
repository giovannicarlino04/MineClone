from ursina import Vec3, scene, destroy
import random
from noise import Noise
from block import Block

class Chunkgen:
    def __init__(self, player):
        self.player = player
        self.chunk_size = 16  # Increased chunk size for larger terrain features
        self.loaded_chunks = {}  # Dictionary to store loaded chunks

    def generate_chunk(self, chunk_key):
        chunk_position = Vec3(chunk_key[0] * self.chunk_size, 0, chunk_key[1] * self.chunk_size)

        # Track blocks to destroy
        blocks_to_destroy = []

        # Generate terrain for the chunk
        for i in range(self.chunk_size):
            for j in range(self.chunk_size):
                noise_val = random.random()  # Replace with your noise function
                height = int(noise_val * 20)

                for y in range(height + 1):
                    position = chunk_position + Vec3(j, y, i)
                    block_exists = any(block.position == position for block in self.player.world_blocks if block.active)

                    if not block_exists:
                        texture_path = 'textures/stone.png'  # Example texture path
                        block = Block(position=position, texture_path=texture_path)
                        self.player.world_blocks.append(block)
                        block.reparentTo(scene)

                # Example: Simulate occasional destruction of blocks
                if random.random() < 0.01:  # Adjust probability as needed
                    block_to_destroy = next((block for block in self.player.world_blocks if block.position == position), None)
                    if block_to_destroy:
                        blocks_to_destroy.append(block_to_destroy)

        # Destroy collected blocks
        for block in blocks_to_destroy:
            if block in self.player.world_blocks:
                self.player.world_blocks.remove(block)
            block.removeNode()

        self.loaded_chunks[chunk_key] = True

        # Example: Additional terrain modifications
        self.add_trees(chunk_position)
        self.add_structures(chunk_position)
        self.add_graves(chunk_position)

    def add_trees(self, chunk_position):
        # Placeholder for adding trees
        for _ in range(1):  # This value holds how many trees should be in a chunk
            x = chunk_position.x + random.randint(0, self.chunk_size - 1)
            z = chunk_position.z + random.randint(0, self.chunk_size - 1)
            position = Vec3(x, self.get_height_at(x, z), z)
            self.place_tree(position)

    def place_tree(self, position):
        # Placeholder for tree generation logic
        trunk_height = 5
        for i in range(trunk_height):
            trunk = Block(position=position + Vec3(0, i, 0), texture_path='textures/log.png')
            self.player.world_blocks.append(trunk)
            trunk.parent = scene

        # Add leaves (simple cube around the top)
        for x in range(-1, 2):
            for z in range(-1, 2):
                for y in range(trunk_height, trunk_height + 3):
                    if not (x == 0 and z == 0 and y == trunk_height):
                        leaves = Block(position=position + Vec3(x, y, z), texture_path='textures/leaves.png')
                        self.player.world_blocks.append(leaves)
                        leaves.parent = scene

    def add_structures(self, chunk_position):
        # Placeholder for adding structures
        pass

    def add_graves(self, chunk_position):
        # Placeholder for adding graves
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
        blocks_to_remove = []
        for block in self.player.world_blocks:
            if chunk_position.x <= block.position.x < chunk_position.x + self.chunk_size and \
            chunk_position.z <= block.position.z < chunk_position.z + self.chunk_size:
                destroy(block)
                blocks_to_remove.append(block)

        # Remove the blocks from the world_blocks list
        for block in blocks_to_remove:
            self.player.world_blocks.remove(block)

        # Remove the chunk from loaded_chunks dictionary
        del self.loaded_chunks[chunk_key]
