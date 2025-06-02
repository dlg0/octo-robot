import arcade
import random
import math

ITEM_RADIUS = 15
ITEM_TYPES = {
    "battery": {"color": arcade.color.YELLOW, "value": 1, "spawn_rate": 0.4},
    "gear": {"color": arcade.color.GRAY, "value": 2, "spawn_rate": 0.3},
    "gem": {"color": arcade.color.CYAN, "value": 5, "spawn_rate": 0.15},
    "crystal": {"color": arcade.color.PURPLE, "value": 10, "spawn_rate": 0.1},
    "power_core": {"color": arcade.color.RED, "value": 20, "spawn_rate": 0.05}
}

# Generation parameters
CHUNK_SIZE = 500  # Size of each generation chunk
ITEMS_PER_CHUNK = 8  # Average items per chunk
GENERATION_RADIUS = 2  # Generate chunks within this radius of player

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.collected = False
        self.value = ITEM_TYPES[item_type]["value"]

class ItemManager:
    def __init__(self):
        self.items = []
        self.generated_chunks = set()  # Track which chunks have been generated
        self.chunk_items = {}  # Items organized by chunk for efficient lookup
        
    def reset(self):
        self.items = []
        self.generated_chunks = set()
        self.chunk_items = {}

    def get_chunk_key(self, x, y):
        """Get chunk coordinates for a world position"""
        chunk_x = int(x // CHUNK_SIZE)
        chunk_y = int(y // CHUNK_SIZE)
        return (chunk_x, chunk_y)

    def generate_chunk_items(self, chunk_x, chunk_y):
        """Generate items for a specific chunk"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.generated_chunks:
            return
            
        self.generated_chunks.add(chunk_key)
        
        # Seed random based on chunk coordinates for consistent generation
        random.seed(hash(chunk_key) % (2**31))
        
        chunk_items = []
        num_items = random.randint(ITEMS_PER_CHUNK - 3, ITEMS_PER_CHUNK + 3)
        
        for _ in range(num_items):
            # Generate position within chunk
            local_x = random.uniform(0, CHUNK_SIZE)
            local_y = random.uniform(0, CHUNK_SIZE)
            world_x = chunk_x * CHUNK_SIZE + local_x
            world_y = chunk_y * CHUNK_SIZE + local_y
            
            # Select item type based on spawn rates
            rand_val = random.random()
            cumulative_rate = 0
            selected_type = "battery"  # default
            
            for item_type, props in ITEM_TYPES.items():
                cumulative_rate += props["spawn_rate"]
                if rand_val <= cumulative_rate:
                    selected_type = item_type
                    break
            
            item = Item(world_x, world_y, selected_type)
            chunk_items.append(item)
            self.items.append(item)
        
        self.chunk_items[chunk_key] = chunk_items
        
        # Reset random seed
        random.seed()

    def update_generation(self, player_x, player_y):
        """Generate chunks around the player position"""
        player_chunk = self.get_chunk_key(player_x, player_y)
        
        # Generate chunks in a radius around the player
        for dx in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
            for dy in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
                chunk_x = player_chunk[0] + dx
                chunk_y = player_chunk[1] + dy
                self.generate_chunk_items(chunk_x, chunk_y)

    def check_collisions(self, player):
        """Check for item collisions with player"""
        collected_value = 0
        player_chunk = self.get_chunk_key(player.x, player.y)
        
        # Check items in nearby chunks for efficiency
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk_key = (player_chunk[0] + dx, player_chunk[1] + dy)
                if chunk_key in self.chunk_items:
                    for item in self.chunk_items[chunk_key]:
                        if not item.collected:
                            dist = math.sqrt((player.x - item.x) ** 2 + (player.y - item.y) ** 2)
                            if dist < ITEM_RADIUS + 25:  # 25 is player radius
                                item.collected = True
                                collected_value += item.value
        
        return collected_value

    def get_active_items_near(self, center_x, center_y, radius=1000):
        """Get active items near a position for rendering"""
        active_items = []
        center_chunk = self.get_chunk_key(center_x, center_y)
        
        # Calculate how many chunks to check based on radius
        chunks_to_check = max(1, int(radius // CHUNK_SIZE) + 1)
        
        for dx in range(-chunks_to_check, chunks_to_check + 1):
            for dy in range(-chunks_to_check, chunks_to_check + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                if chunk_key in self.chunk_items:
                    for item in self.chunk_items[chunk_key]:
                        if not item.collected:
                            # Check if item is within render distance
                            dist = math.sqrt((center_x - item.x) ** 2 + (center_y - item.y) ** 2)
                            if dist <= radius:
                                active_items.append(item)
        
        return active_items

    def get_active_items(self):
        """Get all active items (for backward compatibility)"""
        return [item for item in self.items if not item.collected] 