import arcade
import random
import math

# Obstacle types and their properties
OBSTACLE_TYPES = {
    "rock": {
        "color": arcade.color.DARK_GRAY,
        "radius": 30,
        "spawn_rate": 0.5,
        "destructible": False
    },
    "tree": {
        "color": arcade.color.DARK_GREEN,
        "radius": 25,
        "spawn_rate": 0.3,
        "destructible": False
    },
    "crystal_formation": {
        "color": arcade.color.LIGHT_BLUE,
        "radius": 35,
        "spawn_rate": 0.15,
        "destructible": False
    },
    "metal_debris": {
        "color": arcade.color.RUST,
        "radius": 20,
        "spawn_rate": 0.05,
        "destructible": True
    }
}

# Generation parameters
CHUNK_SIZE = 500  # Should match item manager
OBSTACLES_PER_CHUNK = 6  # Average obstacles per chunk
GENERATION_RADIUS = 2  # Generate chunks within this radius of player

class Obstacle:
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.radius = OBSTACLE_TYPES[obstacle_type]["radius"]
        self.destructible = OBSTACLE_TYPES[obstacle_type]["destructible"]
        self.destroyed = False

class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.generated_chunks = set()
        self.chunk_obstacles = {}
        
    def reset(self):
        self.obstacles = []
        self.generated_chunks = set()
        self.chunk_obstacles = {}

    def get_chunk_key(self, x, y):
        """Get chunk coordinates for a world position"""
        chunk_x = int(x // CHUNK_SIZE)
        chunk_y = int(y // CHUNK_SIZE)
        return (chunk_x, chunk_y)

    def generate_chunk_obstacles(self, chunk_x, chunk_y):
        """Generate obstacles for a specific chunk"""
        chunk_key = (chunk_x, chunk_y)
        if chunk_key in self.generated_chunks:
            return
            
        self.generated_chunks.add(chunk_key)
        
        # Seed random based on chunk coordinates for consistent generation
        random.seed(hash((chunk_key[0] + 1000, chunk_key[1] + 1000)) % (2**31))
        
        chunk_obstacles = []
        num_obstacles = random.randint(OBSTACLES_PER_CHUNK - 2, OBSTACLES_PER_CHUNK + 4)
        
        attempts = 0
        max_attempts = num_obstacles * 3  # Prevent infinite loops
        
        while len(chunk_obstacles) < num_obstacles and attempts < max_attempts:
            attempts += 1
            
            # Generate position within chunk
            local_x = random.uniform(50, CHUNK_SIZE - 50)  # Leave some margin
            local_y = random.uniform(50, CHUNK_SIZE - 50)
            world_x = chunk_x * CHUNK_SIZE + local_x
            world_y = chunk_y * CHUNK_SIZE + local_y
            
            # Select obstacle type based on spawn rates
            rand_val = random.random()
            cumulative_rate = 0
            selected_type = "rock"  # default
            
            for obstacle_type, props in OBSTACLE_TYPES.items():
                cumulative_rate += props["spawn_rate"]
                if rand_val <= cumulative_rate:
                    selected_type = obstacle_type
                    break
            
            # Check if position conflicts with existing obstacles
            new_obstacle = Obstacle(world_x, world_y, selected_type)
            valid_position = True
            
            for existing in chunk_obstacles:
                dist = math.sqrt((new_obstacle.x - existing.x) ** 2 + (new_obstacle.y - existing.y) ** 2)
                min_distance = new_obstacle.radius + existing.radius + 20  # 20 pixel buffer
                if dist < min_distance:
                    valid_position = False
                    break
            
            if valid_position:
                chunk_obstacles.append(new_obstacle)
                self.obstacles.append(new_obstacle)
        
        self.chunk_obstacles[chunk_key] = chunk_obstacles
        
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
                self.generate_chunk_obstacles(chunk_x, chunk_y)

    def check_collision(self, x, y, radius):
        """Check if a position collides with any obstacle"""
        player_chunk = self.get_chunk_key(x, y)
        
        # Check obstacles in nearby chunks
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                chunk_key = (player_chunk[0] + dx, player_chunk[1] + dy)
                if chunk_key in self.chunk_obstacles:
                    for obstacle in self.chunk_obstacles[chunk_key]:
                        if not obstacle.destroyed:
                            dist = math.sqrt((x - obstacle.x) ** 2 + (y - obstacle.y) ** 2)
                            if dist < radius + obstacle.radius:
                                return obstacle
        return None

    def get_active_obstacles_near(self, center_x, center_y, radius=1000):
        """Get active obstacles near a position for rendering"""
        active_obstacles = []
        center_chunk = self.get_chunk_key(center_x, center_y)
        
        # Calculate how many chunks to check based on radius
        chunks_to_check = max(1, int(radius // CHUNK_SIZE) + 1)
        
        for dx in range(-chunks_to_check, chunks_to_check + 1):
            for dy in range(-chunks_to_check, chunks_to_check + 1):
                chunk_key = (center_chunk[0] + dx, center_chunk[1] + dy)
                if chunk_key in self.chunk_obstacles:
                    for obstacle in self.chunk_obstacles[chunk_key]:
                        if not obstacle.destroyed:
                            # Check if obstacle is within render distance
                            dist = math.sqrt((center_x - obstacle.x) ** 2 + (center_y - obstacle.y) ** 2)
                            if dist <= radius:
                                active_obstacles.append(obstacle)
        
        return active_obstacles 