import arcade
import random

ITEM_RADIUS = 15
ITEM_TYPES = ["battery", "gear"]
ITEM_COLORS = {"battery": arcade.color.YELLOW, "gear": arcade.color.GRAY}
ITEM_COUNT = 5

class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.collected = False

class ItemManager:
    def __init__(self):
        self.items = []
        self.reset()

    def reset(self):
        self.items = []
        for _ in range(ITEM_COUNT):
            x = random.randint(ITEM_RADIUS, 800 - ITEM_RADIUS)
            y = random.randint(ITEM_RADIUS, 600 - ITEM_RADIUS)
            item_type = random.choice(ITEM_TYPES)
            self.items.append(Item(x, y, item_type))

    def check_collisions(self, player):
        collected = 0
        for item in self.items:
            if not item.collected:
                dist = ((player.x - item.x) ** 2 + (player.y - item.y) ** 2) ** 0.5
                if dist < ITEM_RADIUS + 25:  # 25 is player radius
                    item.collected = True
                    collected += 1
        return collected

    def get_active_items(self):
        return [item for item in self.items if not item.collected] 