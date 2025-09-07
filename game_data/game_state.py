# game_data.game_state.py
from systems.currency import Wallet
from systems.building_system import BuildingManager
from systems.hero_system import Hero
from game_data.research_system import ResearchManager
from systems.storage_system import StorageSystem
from systems.crafting_system import CraftingSystem 
from systems.items_system import ItemManager 

# Инициализация состояния игры
game_state = {
    "wallet": Wallet(gold=10000, crystals=100),
    "tower_level": 1,
    "max_tower_floor": 1,
    "heroes": [],
    "buildings": BuildingManager(),
    "research": ResearchManager(),
    "inventory": {
        "materials": {},
        "equipment": {}
    },
    "achievement_system": None,
    "tower_monsters": {},
    "save_system": None,
    "role_system": None,
    "party_system": {
        "max_parties": 1,
        "parties": {
            "party_1": {
                "name": "Основная группа",
                "heroes": [],
                "is_unlocked": True
            }
        },
        "current_party": "party_1"
    },
    "storage": StorageSystem(),
    "crafting_system": CraftingSystem(),
    "item_manager": ItemManager()
}

def init_save_system():
    """Инициализирует систему сохранений при первом использовании"""
    if game_state["save_system"] is None:
        from game_data.save_system import SaveSystem
        game_state["save_system"] = SaveSystem()
    
    return game_state["save_system"]

def is_role_system_available():
    """Проверяет, доступна ли система ролей"""
    buildings = game_state["buildings"].buildings
    return (buildings["canteen"].built or 
            buildings["forge"].built or 
            buildings["laboratory"].built)

