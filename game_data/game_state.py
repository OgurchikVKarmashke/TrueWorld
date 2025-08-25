#game_state.py
from systems.currency import Wallet
from systems.building_system import BuildingManager
from systems.hero_system import Hero
from game_data.research_system import ResearchManager
from game_data.save_system import SaveSystem

# Инициализация состояния игры
game_state = {
    "wallet": Wallet(gold=500, crystals=10),
    "tower_level": 1,
    "max_tower_floor": 1,
    "heroes": [],
    "buildings": BuildingManager(),
    "research": ResearchManager(),
    "inventory": {
        "materials": {},
        "equipment": {}
    },
    "tower_monsters": {},
    "save_system": SaveSystem(),
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
    }
}

def init_role_system():
    """Инициализирует систему ролей при первом использовании"""
    if game_state["role_system"] is None:
        from systems.role_system import RoleSystem
        game_state["role_system"] = RoleSystem(game_state)
    
    return game_state["role_system"]

def is_role_system_available():
    """Проверяет, доступна ли система ролей"""
    buildings = game_state["buildings"].buildings
    return (buildings["canteen"].built or 
            buildings["forge"].built or 
            buildings["laboratory"].built)