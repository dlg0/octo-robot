import arcade
import random
import math
import logging

logger = logging.getLogger(__name__)

class BackgroundLayer:
    """A single layer of the background that can scroll infinitely"""
    def __init__(self, color, depth, pattern_size=1000):
        self.color = color
        self.depth = depth  # Higher depth = moves slower (parallax effect)
        self.pattern_size = pattern_size
        self.elements = []
        self.generated_regions = set()

    def generate_region(self, region_x, region_y):
        """Generate background elements for a specific region"""
        region_key = (region_x, region_y)
        if region_key in self.generated_regions:
            return
            
        self.generated_regions.add(region_key)
        
        # Seed based on region and depth for consistent generation
        random.seed(hash((region_x, region_y, self.depth)) % (2**31))
        
        # Generate elements based on layer type
        if self.depth == 1:  # Sky layer - clouds
            num_clouds = random.randint(2, 5)
            for _ in range(num_clouds):
                x = region_x * self.pattern_size + random.uniform(0, self.pattern_size)
                y = region_y * self.pattern_size + random.uniform(400, 600)
                size = random.uniform(30, 80)
                self.elements.append({
                    'type': 'cloud',
                    'x': x,
                    'y': y,
                    'size': size,
                    'alpha': random.randint(50, 150)
                })
        
        elif self.depth == 2:  # Mid layer - distant hills
            num_hills = random.randint(1, 3)
            for _ in range(num_hills):
                x = region_x * self.pattern_size + random.uniform(0, self.pattern_size)
                y = random.uniform(200, 350)
                width = random.uniform(200, 400)
                height = random.uniform(50, 120)
                self.elements.append({
                    'type': 'hill',
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height
                })
        
        elif self.depth == 3:  # Ground details layer
            num_patches = random.randint(3, 8)
            for _ in range(num_patches):
                x = region_x * self.pattern_size + random.uniform(0, self.pattern_size)
                y = random.uniform(0, 150)
                size = random.uniform(20, 60)
                patch_type = random.choice(['grass', 'dirt', 'sand'])
                self.elements.append({
                    'type': patch_type,
                    'x': x,
                    'y': y,
                    'size': size
                })
        
        # Reset random seed
        random.seed()

class BackgroundManager:
    def __init__(self):
        self.layers = [
            BackgroundLayer(arcade.color.SKY_BLUE, 1, 2000),      # Sky with clouds
            BackgroundLayer(arcade.color.LIGHT_BLUE, 2, 1500),   # Distant hills
            BackgroundLayer(arcade.color.DARK_SPRING_GREEN, 3, 800)  # Ground details
        ]
        self.base_colors = {
            1: arcade.color.SKY_BLUE,
            2: arcade.color.LIGHT_GREEN,
            3: arcade.color.DARK_SPRING_GREEN
        }
        
    def reset(self):
        for layer in self.layers:
            layer.elements = []
            layer.generated_regions = set()

    def update_generation(self, camera_x, camera_y, screen_width, screen_height):
        """Generate background elements around the camera position"""
        for layer in self.layers:
            # Calculate effective camera position for this layer (parallax)
            effective_x = camera_x / layer.depth
            effective_y = camera_y / layer.depth
            
            # Calculate which regions need to be generated
            left_region = int((effective_x - screen_width) // layer.pattern_size)
            right_region = int((effective_x + screen_width) // layer.pattern_size) + 1
            bottom_region = int((effective_y - screen_height) // layer.pattern_size)
            top_region = int((effective_y + screen_height) // layer.pattern_size) + 1
            
            # Generate regions
            for region_x in range(left_region, right_region + 1):
                for region_y in range(bottom_region, top_region + 1):
                    layer.generate_region(region_x, region_y)

    def draw_background(self, camera_x, camera_y, screen_width, screen_height):
        """Draw the infinite scrolling background"""
        logger.debug(f"Drawing background - camera: ({camera_x}, {camera_y}), screen: {screen_width}x{screen_height}")
        
        # Draw base background with extra large buffer for fullscreen transitions
        buffer_size = max(500, max(screen_width, screen_height) * 0.5)
        view_left = camera_x - screen_width / 2
        view_right = camera_x + screen_width / 2
        view_bottom = camera_y - screen_height / 2
        view_top = camera_y + screen_height / 2
        
        logger.debug(f"Buffer size: {buffer_size}")
        logger.debug(f"View bounds: left={view_left}, right={view_right}, bottom={view_bottom}, top={view_top}")
        logger.debug(f"Background rect: {view_left - buffer_size} to {view_right + buffer_size}, {view_bottom - buffer_size} to {view_top + buffer_size}")
        
        # Sky background - ensure it covers the entire viewport and more
        arcade.draw_rect_filled(
            arcade.LRBT(view_left - buffer_size, view_right + buffer_size, 
                       view_bottom - buffer_size, view_top + buffer_size),
            self.base_colors[1]
        )
        
        # Draw each layer from back to front
        for i, layer in enumerate(reversed(self.layers)):  # Draw back to front
            logger.debug(f"Drawing layer {i} (depth {layer.depth})")
            self.draw_layer(layer, camera_x, camera_y, screen_width, screen_height)

    def draw_layer(self, layer, camera_x, camera_y, screen_width, screen_height):
        """Draw a specific background layer"""
        effective_x = camera_x / layer.depth
        effective_y = camera_y / layer.depth
        
        # Calculate render bounds
        left_bound = effective_x - screen_width
        right_bound = effective_x + screen_width
        bottom_bound = effective_y - screen_height
        top_bound = effective_y + screen_height
        
        for element in layer.elements:
            # Skip elements outside render bounds
            if (element['x'] < left_bound or element['x'] > right_bound or
                element['y'] < bottom_bound or element['y'] > top_bound):
                continue
            
            # Apply parallax offset
            render_x = element['x'] * layer.depth
            render_y = element['y'] * layer.depth
            
            if element['type'] == 'cloud':
                self.draw_cloud(render_x, render_y, element['size'], element['alpha'])
            elif element['type'] == 'hill':
                self.draw_hill(render_x, render_y, element['width'], element['height'])
            elif element['type'] in ['grass', 'dirt', 'sand']:
                self.draw_ground_patch(render_x, render_y, element['size'], element['type'])

    def draw_cloud(self, x, y, size, alpha):
        """Draw a simple cloud"""
        # Use white color with proper alpha handling
        cloud_color = (255, 255, 255, alpha)
        # Main cloud body
        arcade.draw_circle_filled(x, y, size * 0.6, cloud_color)
        arcade.draw_circle_filled(x - size * 0.4, y, size * 0.4, cloud_color)
        arcade.draw_circle_filled(x + size * 0.4, y, size * 0.4, cloud_color)
        arcade.draw_circle_filled(x, y + size * 0.3, size * 0.3, cloud_color)

    def draw_hill(self, x, y, width, height):
        """Draw a background hill"""
        hill_color = arcade.color.LIGHT_GREEN
        # Simple elliptical hill
        arcade.draw_ellipse_filled(x, y, width, height, hill_color)

    def draw_ground_patch(self, x, y, size, patch_type):
        """Draw ground detail patches"""
        colors = {
            'grass': arcade.color.GREEN,
            'dirt': arcade.color.BROWN,
            'sand': arcade.color.TAN
        }
        color = colors.get(patch_type, arcade.color.GREEN)
        arcade.draw_circle_filled(x, y, size, color) 