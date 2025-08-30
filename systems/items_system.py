# systems.items_system.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class ItemType(Enum):
    WEAPON = "Оружие"
    ARMOR = "Броня"
    ACCESSORY = "Аксессуар"
    MATERIAL = "Материал"
    CONSUMABLE = "Расходник"

class ItemRarity(Enum):
    COMMON = "Обычный"
    UNCOMMON = "Необычный"
    RARE = "Редкий"
    EPIC = "Эпический"
    LEGENDARY = "Легендарный"

@dataclass
class Item:
    id: str
    name: str
    description: str
    item_type: ItemType
    rarity: ItemRarity
    stats: Dict[str, int]
    required_level: int = 1
    stackable: bool = False
    max_stack: int = 1
    quantity: int = 1
    
    def __str__(self):
        return f"{self.rarity.value} {self.name}"

class ItemManager:
    def __init__(self):
        self.items = {}
        self.initialize_items()
    
    def initialize_items(self):
        # Материалы для крафта
        self.items = {
            # Материалы
            "iron_ore": Item("iron_ore", "Железная руда", "Базовая железная руда для крафта", 
                           ItemType.MATERIAL, ItemRarity.COMMON, {}, stackable=True, max_stack=99),
            "steel_bar": Item("steel_bar", "Стальной слиток", "Обработанная сталь", 
                            ItemType.MATERIAL, ItemRarity.UNCOMMON, {}, stackable=True, max_stack=50),
            "magic_crystal": Item("magic_crystal", "Магический кристалл", "Источник магической энергии", 
                                ItemType.MATERIAL, ItemRarity.RARE, {}, stackable=True, max_stack=25),
            
            # Готовое оружие
            "iron_sword": Item("iron_sword", "Железный меч", "Простой железный меч", 
                             ItemType.WEAPON, ItemRarity.COMMON, {"attack": 15, "crit_chance": 5}, 5),
            "steel_sword": Item("steel_sword", "Стальной меч", "Качественный стальной меч", 
                              ItemType.WEAPON, ItemRarity.UNCOMMON, {"attack": 25, "crit_chance": 8}, 10),
        }
    
    def get_item(self, item_id: str) -> Optional[Item]:
        return self.items.get(item_id)
    
    def create_item(self, item_id: str, quantity: int = 1) -> Optional[Item]:
        base_item = self.get_item(item_id)
        if not base_item:
            return None
        
        # Создаем копию с указанным количеством
        import copy
        new_item = copy.copy(base_item)
        new_item.quantity = quantity
        return new_item