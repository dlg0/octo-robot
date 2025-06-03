import arcade
import random
import math
from PIL import Image, ImageDraw
from arcade.types import Color as ArcadeColor # Import for type hinting
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from game.player import Player

ITEM_RADIUS = 15
ITEM_TYPES = {
    "battery": {"color": arcade.color.YELLOW, "value": 1, "spawn_rate": 0.4, "color_name": "yellow"},
    "gear": {"color": arcade.color.GRAY, "value": 2, "spawn_rate": 0.3, "color_name": "gray"},
    "gem": {"color": arcade.color.CYAN, "value": 5, "spawn_rate": 0.15, "color_name": "cyan"},
    "crystal": {"color": arcade.color.PURPLE, "value": 10, "spawn_rate": 0.1, "color_name": "purple"},
    "power_core": {"color": arcade.color.RED, "value": 20, "spawn_rate": 0.05, "color_name": "red"}
}

# Generation parameters
CHUNK_SIZE = 500  # Size of each generation chunk
ITEMS_PER_CHUNK = 8  # Average items per chunk
GENERATION_RADIUS = 2  # Generate chunks within this radius of player

# Texture cache
_texture_cache: dict[str, arcade.Texture] = {}

def _get_item_texture(item_type_name: str) -> arcade.Texture:
    if item_type_name in _texture_cache:
        return _texture_cache[item_type_name]

    item_props = ITEM_TYPES.get(item_type_name)
    
    r, g, b, a = 128, 128, 128, 255 # Default gray

    if not item_props:
        r, g, b, a = 255, 255, 255, 0 # Transparent for unknown type
    else:
        prop_color_value = item_props["color"]
        # Ensure prop_color_value is a tuple (it should be from arcade.color)
        if isinstance(prop_color_value, tuple):
            if len(prop_color_value) == 3:
                r, g, b = prop_color_value
                a = 255
            elif len(prop_color_value) == 4:
                r, g, b, a = prop_color_value
    
    defined_color: tuple[int, int, int, int] = (r, g, b, a)

    # Create a texture for a circle
    diameter = ITEM_RADIUS * 2
    img = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter -1, diameter -1), fill=defined_color)
    
    texture_name = f"item_{item_type_name}_{defined_color[0]}_{defined_color[1]}_{defined_color[2]}_{defined_color[3]}"
    texture = arcade.Texture(image=img, name=texture_name)
    _texture_cache[item_type_name] = texture
    return texture

class Item(arcade.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.x = x # Sprite position will be set by center_x, center_y
        self.y = y # Sprite position will be set by center_x, center_y
        self.type = item_type
        self.collected = False
        self.value = ITEM_TYPES[item_type]["value"]
        self.color_name = ITEM_TYPES[item_type]["color_name"]
        
        self.texture = _get_item_texture(item_type)
        self.center_x = x
        self.center_y = y

class ItemManager:
    def __init__(self):
        self.items = []  # Keep for raw data if needed, or phase out
        self.generated_chunks = set()
        self.chunk_items = {} 
        self.item_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        
    def reset(self):
        self.items = []
        self.generated_chunks = set()
        self.chunk_items = {}
        self.item_sprite_list.clear() # Clear the sprite list

    def get_chunk_key(self, x, y):
        chunk_x = int(x // CHUNK_SIZE)
        chunk_y = int(y // CHUNK_SIZE)
        return (chunk_x, chunk_y)

    def generate_chunk_items(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.generated_chunks:
            return
            
        self.generated_chunks.add(chunk_key)
        random.seed(hash(chunk_key) % (2**31))
        
        current_chunk_sprite_items = [] # Store sprites for this chunk's data
        
        num_items = random.randint(ITEMS_PER_CHUNK - 3, ITEMS_PER_CHUNK + 3)
        
        for _ in range(num_items):
            local_x = random.uniform(0, CHUNK_SIZE)
            local_y = random.uniform(0, CHUNK_SIZE)
            world_x = chunk_x * CHUNK_SIZE + local_x
            world_y = chunk_y * CHUNK_SIZE + local_y
            
            rand_val = random.random()
            cumulative_rate = 0
            selected_type = "battery" 
            
            for item_type_loop, props in ITEM_TYPES.items():
                cumulative_rate += props["spawn_rate"]
                if rand_val <= cumulative_rate:
                    selected_type = item_type_loop
                    break
            
            item_sprite = Item(world_x, world_y, selected_type)
            # self.items.append(item_sprite) # Decide if this raw list is still needed
            current_chunk_sprite_items.append(item_sprite)
            self.item_sprite_list.append(item_sprite)
        
        self.chunk_items[chunk_key] = current_chunk_sprite_items # Store sprites in chunk_items
        random.seed()

    def update_generation(self, player_x, player_y):
        player_chunk = self.get_chunk_key(player_x, player_y)
        for dx in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
            for dy in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
                chunk_x = player_chunk[0] + dx
                chunk_y = player_chunk[1] + dy
                self.generate_chunk_items(chunk_x, chunk_y)

    def check_collisions(self, player: Any):
        collected_value = 0
        
        # Player is now an arcade.Sprite, so we can use check_for_collision_with_list
        collided_items = arcade.check_for_collision_with_list(player, self.item_sprite_list)
        
        collected_items = []  # Store information about collected items
        for item_sprite in collided_items:
            # Ensure item_sprite is an instance of our Item class and not collected
            if isinstance(item_sprite, Item) and not item_sprite.collected:
                item_sprite.collected = True
                collected_value += item_sprite.value
                collected_items.append({
                    "value": item_sprite.value,
                    "color_name": item_sprite.color_name,
                    "type": item_sprite.type
                })
                item_sprite.remove_from_sprite_lists() # Remove from self.item_sprite_list and any other list it's in
        
        return collected_value, collected_items

    def get_active_items_near(self, center_x, center_y, radius=1000):
        # This method might need to return a list of sprites or a temporary SpriteList for rendering
        # if we don't draw the main self.item_sprite_list directly.
        # For now, let's adapt it to return culled sprites from self.item_sprite_list
        
        # Create a temporary SpriteList for culled results
        # visible_item_sprites = arcade.SpriteList() # Not used in current implementation of this func
        
        # More efficient culling might be needed if self.item_sprite_list is huge.
        # Arcade's spatial hash on the SpriteList helps with its own draw culling if a camera is used.
        # This manual culling is for cases where we pass a specific list to the renderer.
        
        # Simple distance check on all sprites in the main list
        # This could be slow if item_sprite_list is massive.
        # The chunk-based approach was better for culling.
        
        # Reverting to chunk-based culling for this method:
        active_sprites = []
        center_chunk = self.get_chunk_key(center_x, center_y)
        chunks_to_check = max(1, int(radius // CHUNK_SIZE) + 1)
        
        for dx in range(-chunks_to_check, chunks_to_check + 1):
            for dy in range(-chunks_to_check, chunks_to_check + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                if chunk_key in self.chunk_items: # self.chunk_items now stores sprites
                    for item_sprite in self.chunk_items[chunk_key]:
                        if not item_sprite.collected:
                            # Check if item is within render distance
                            # No need for sqrt if comparing squared distances
                            dist_sq = (center_x - item_sprite.center_x) ** 2 + (center_y - item_sprite.center_y) ** 2
                            if dist_sq <= radius ** 2:
                                active_sprites.append(item_sprite) # Add sprite to list
        return active_sprites # Return list of sprites, not SpriteList, to match renderer's old expectation

    def get_active_items(self):
        # This method is less relevant if we use the sprite list directly
        # but can be updated to filter self.item_sprite_list
        active_list = arcade.SpriteList()
        for item_sprite in self.item_sprite_list:
            if not item_sprite.collected: # Assuming Item has 'collected' attribute
                active_list.append(item_sprite)
        return active_list 