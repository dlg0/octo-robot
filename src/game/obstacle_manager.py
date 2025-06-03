import arcade
import random
import math
from PIL import Image, ImageDraw
from arcade.types import Color as ArcadeColor # Import for type hinting
from typing import cast # For explicit type casting

# Obstacle types and their properties
OBSTACLE_TYPES = {
    "rock": {
        "color": arcade.color.DARK_GRAY,
        "radius": 30,
        "spawn_rate": 0.5,
        "destructible": False,
        "shape": "irregular_polygon" # Hint for texture generation
    },
    "tree": {
        "color": arcade.color.DARK_GREEN,
        "radius": 25, # Represents foliage radius
        "spawn_rate": 0.3,
        "destructible": False,
        "shape": "tree" # Hint for texture generation
    },
    "crystal_formation": {
        "color": arcade.color.LIGHT_BLUE,
        "radius": 35,
        "spawn_rate": 0.15,
        "destructible": False,
        "shape": "crystal_cluster" # Hint for texture generation
    },
    "metal_debris": {
        "color": arcade.color.RUST,
        "radius": 20,
        "spawn_rate": 0.05,
        "destructible": True,
        "shape": "rect_cluster" # Hint for texture generation
    }
}

# Generation parameters
CHUNK_SIZE = 500
OBSTACLES_PER_CHUNK = 6
GENERATION_RADIUS = 2

_obstacle_texture_cache: dict[str, arcade.Texture] = {}

def _get_obstacle_texture(obstacle_type_name: str) -> arcade.Texture:
    if obstacle_type_name in _obstacle_texture_cache:
        return _obstacle_texture_cache[obstacle_type_name]

    props = OBSTACLE_TYPES.get(obstacle_type_name)
    if not props:
        # Fallback: transparent texture
        img = Image.new('RGBA', (1, 1), (0,0,0,0))
        texture = arcade.Texture(image=img, name=f"obstacle_{obstacle_type_name}_unknown")
        _obstacle_texture_cache[obstacle_type_name] = texture
        return texture

    # Use cast for dictionary values to satisfy linter
    color_val = cast(ArcadeColor, props.get("color", arcade.color.GRAY))
    radius = cast(float, props.get("radius", 30.0))
    shape = cast(str, props.get("shape", "circle"))
    diameter = int(radius * 2)

    final_color: tuple[int, int, int, int]
    color_tuple = tuple(color_val)
    if len(color_tuple) == 3:
        final_color = (color_tuple[0], color_tuple[1], color_tuple[2], 255)
    elif len(color_tuple) == 4:
        # Ensure all elements are int for the tuple type hint for final_color
        final_color = (int(color_tuple[0]), int(color_tuple[1]), int(color_tuple[2]), int(color_tuple[3]))
    else:
        final_color = (128, 128, 128, 255) # Default gray for unexpected format

    img = Image.new('RGBA', (diameter, diameter), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    # Simplified texture generation based on shape hint
    # These won't exactly match the old renderer's detailed drawings but are faster for sprites.
    if shape == "irregular_polygon": # Rock
        points = []
        for i in range(8):
            angle = math.radians(i * 45)
            # Vary radius for irregular shape
            eff_radius = radius * (0.7 + 0.3 * math.sin(i * 2)) 
            point_x = radius + math.cos(angle) * eff_radius
            point_y = radius + math.sin(angle) * eff_radius
            points.append((point_x, point_y))
        draw.polygon(points, fill=final_color)
    elif shape == "tree":
        # Trunk (brown)
        trunk_w = radius * 0.3
        trunk_h = radius # Simple trunk
        # Ensure BROWN is RGBA for PIL
        brown_color_val = arcade.color.BROWN
        pil_brown: tuple[int,int,int,int] = (brown_color_val[0], brown_color_val[1], brown_color_val[2], 255) if len(brown_color_val) == 3 else cast(tuple[int,int,int,int], brown_color_val)
        draw.rectangle([
            (radius - trunk_w/2, radius),
            (radius + trunk_w/2, radius + trunk_h)], 
            fill=pil_brown)
        # Foliage (main color)
        draw.ellipse((0,0, diameter-1, diameter-1), fill=final_color)
    elif shape == "crystal_cluster":
        for i in range(5):
            angle = math.radians(i * 72 + 15) # Offset angle
            eff_radius = radius * (0.4 + 0.3 * (i % 2))
            cx, cy = radius + math.cos(angle) * radius * 0.3, radius + math.sin(angle) * radius * 0.3
            # Simple diamond shape for crystals
            points = [
                (cx, cy - eff_radius),
                (cx + eff_radius * 0.7, cy),
                (cx, cy + eff_radius),
                (cx - eff_radius * 0.7, cy)
            ]
            draw.polygon(points, fill=final_color)
    elif shape == "rect_cluster": # Metal Debris
        for i in range(3):
            rx, ry = random.uniform(-radius*0.4, radius*0.4), random.uniform(-radius*0.4, radius*0.4)
            rw, rh = random.uniform(radius*0.2, radius*0.5), random.uniform(radius*0.2, radius*0.5)
            draw.rectangle([
                (radius + rx - rw/2, radius + ry - rh/2),
                (radius + rx + rw/2, radius + ry + rh/2)],
                fill=final_color)
    else: # Default: circle
        draw.ellipse((0,0, diameter-1, diameter-1), fill=final_color)

    texture_name = f"obstacle_{obstacle_type_name}_{shape}_{final_color[0]}_{final_color[1]}_{final_color[2]}_{final_color[3]}"
    texture = arcade.Texture(image=img, name=texture_name)
    _obstacle_texture_cache[obstacle_type_name] = texture
    return texture

class Obstacle(arcade.Sprite):
    def __init__(self, x, y, obstacle_type):
        super().__init__()
        self.type = obstacle_type
        props = OBSTACLE_TYPES[obstacle_type]
        self.radius = cast(float, props.get("radius", 30.0))
        self.destructible = cast(bool, props.get("destructible", False))
        self.destroyed = False
        
        self.texture = _get_obstacle_texture(obstacle_type)
        self.center_x = x
        self.center_y = y
        # self.scale can be used if texture size vs. collision radius differs

class ObstacleManager:
    def __init__(self):
        self.obstacles = [] # Potentially phase out
        self.generated_chunks = set()
        self.chunk_obstacles = {}
        self.obstacle_sprite_list = arcade.SpriteList(use_spatial_hash=True)
        
    def reset(self):
        self.obstacles = []
        self.generated_chunks = set()
        self.chunk_obstacles = {}
        self.obstacle_sprite_list.clear()

    def get_chunk_key(self, x, y):
        chunk_x = int(x // CHUNK_SIZE)
        chunk_y = int(y // CHUNK_SIZE)
        return (chunk_x, chunk_y)

    def generate_chunk_obstacles(self, chunk_x, chunk_y):
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.generated_chunks:
            return
            
        self.generated_chunks.add(chunk_key)
        random.seed(hash((chunk_key[0] + 1000, chunk_key[1] + 1000)) % (2**31))
        
        current_chunk_sprites = []
        num_obstacles = random.randint(OBSTACLES_PER_CHUNK - 2, OBSTACLES_PER_CHUNK + 4)
        attempts = 0
        max_attempts = num_obstacles * 3
        
        while len(current_chunk_sprites) < num_obstacles and attempts < max_attempts:
            attempts += 1
            local_x = random.uniform(50, CHUNK_SIZE - 50)
            local_y = random.uniform(50, CHUNK_SIZE - 50)
            world_x = chunk_x * CHUNK_SIZE + local_x
            world_y = chunk_y * CHUNK_SIZE + local_y
            
            rand_val = random.random()
            cumulative_rate = 0
            selected_type = "rock"
            for obstacle_type_loop, props_loop in OBSTACLE_TYPES.items(): 
                cumulative_rate += cast(float, props_loop.get("spawn_rate", 0.0))
                if rand_val <= cumulative_rate:
                    selected_type = obstacle_type_loop
                    break
            
            new_obstacle_sprite = Obstacle(world_x, world_y, selected_type)
            valid_position = True
            # Check against sprites already added in this chunk generation pass
            for existing_sprite in current_chunk_sprites:
                dist = math.sqrt((new_obstacle_sprite.center_x - existing_sprite.center_x) ** 2 + 
                                 (new_obstacle_sprite.center_y - existing_sprite.center_y) ** 2)
                # Use sprite's radius for collision check during placement
                min_distance = new_obstacle_sprite.radius + existing_sprite.radius + 20 
                if dist < min_distance:
                    valid_position = False
                    break
            
            if valid_position:
                current_chunk_sprites.append(new_obstacle_sprite)
                # self.obstacles.append(new_obstacle_sprite) # Decide if this list is needed
                self.obstacle_sprite_list.append(new_obstacle_sprite)
        
        self.chunk_obstacles[chunk_key] = current_chunk_sprites
        random.seed()

    def update_generation(self, player_x, player_y):
        player_chunk = self.get_chunk_key(player_x, player_y)
        for dx in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
            for dy in range(-GENERATION_RADIUS, GENERATION_RADIUS + 1):
                chunk_x = player_chunk[0] + dx
                chunk_y = player_chunk[1] + dy
                self.generate_chunk_obstacles(chunk_x, chunk_y)

    def check_collision(self, sprite_to_check: arcade.Sprite) -> Obstacle | None:
        """Check if a sprite collides with any obstacle. Returns the collided obstacle sprite or None."""
        # Player is a sprite, so we can use check_for_collision_with_list
        # This method is called by Player.update()
        # The player sprite itself has .center_x, .center_y, .width, .height

        # We need to get a list of nearby obstacles to check against.
        # The old check_collision took x, y, radius. Now we have a sprite.
        
        # Get obstacles from chunks near the sprite_to_check
        nearby_obstacles_to_check: arcade.SpriteList = arcade.SpriteList()
        center_chunk = self.get_chunk_key(sprite_to_check.center_x, sprite_to_check.center_y)
        # Check 1 chunk around the sprite's chunk. Adjust as needed.
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                if chunk_key in self.chunk_obstacles:
                    for obs_sprite in self.chunk_obstacles[chunk_key]:
                        if hasattr(obs_sprite, 'destroyed') and not obs_sprite.destroyed:
                            nearby_obstacles_to_check.append(obs_sprite)
        
        if not nearby_obstacles_to_check:
            return None

        collided_obstacle_list = arcade.check_for_collision_with_list(sprite_to_check, nearby_obstacles_to_check)
        
        if collided_obstacle_list:
            # Return the first collided obstacle (it's an Obstacle sprite)
            # Ensure it's an instance of our Obstacle class if other sprites might be in these lists.
            collided_obs = collided_obstacle_list[0]
            if isinstance(collided_obs, Obstacle):
                 return collided_obs 
        return None

    def get_active_obstacles_near(self, center_x, center_y, radius=1000):
        # This method is used by renderer. If renderer draws the main SpriteList, this might not be needed
        # or could return a SpriteList of culled obstacles.
        # For now, keep similar logic, returning a list of sprites.
        active_obstacle_sprites = []
        center_chunk = self.get_chunk_key(center_x, center_y)
        chunks_to_check = max(1, int(radius // CHUNK_SIZE) + 1)
        
        for dx in range(-chunks_to_check, chunks_to_check + 1):
            for dy in range(-chunks_to_check, chunks_to_check + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                if chunk_key in self.chunk_obstacles: # chunk_obstacles stores Obstacle sprites
                    for obs_sprite in self.chunk_obstacles[chunk_key]:
                        if hasattr(obs_sprite, 'destroyed') and not obs_sprite.destroyed:
                            dist_sq = (center_x - obs_sprite.center_x) ** 2 + (center_y - obs_sprite.center_y) ** 2
                            if dist_sq <= radius ** 2:
                                active_obstacle_sprites.append(obs_sprite)
        return active_obstacle_sprites 