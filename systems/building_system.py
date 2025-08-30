# systems.building_system.py
from ui.building_manager import calculate_max_building_level

class Building:
    def __init__(self, name, description, max_level, cost_table, built=False, unlock_floor=0):
        self.name = name
        self.description = description
        self.level = 1 if built else 0
        self.max_level = max_level
        self.cost_table = cost_table  # Таблица стоимостей для каждого уровня
        self.built = built
        self.unlock_floor = unlock_floor
        self.unlocked = built
        self.initially_built = built

    def is_available(self, tower_level):
        return tower_level >= self.unlock_floor

    def build_cost(self):
        return self.cost_table[1]  # Стоимость постройки (уровень 1)

    def upgrade_cost(self):
        if self.level == 0:
            return self.build_cost()
        if self.level + 1 <= self.max_level:
            return self.cost_table[self.level + 1]
        return 0  # Максимальный уровень достигнут

    def can_upgrade(self, tower_level):
        max_allowed_level = calculate_max_building_level(tower_level)
        return (self.is_available(tower_level) and 
                self.level < self.max_level and 
                self.level < max_allowed_level and
                (self.level > 0 or not self.built))

    def effect(self):
        pass

    def __str__(self):
        status = "✅ Построено" if self.built else "🚧 Не построено"
        return f"{self.name} (Ур. {self.level}) - {status}"

# Таблицы стоимостей для каждого здания
DORMITORY_COSTS = {
    1: 500, 2: 800, 3: 1200, 4: 1800, 5: 2500,
    6: 3500, 7: 5000, 8: 7000, 9: 10000, 10: 15000
}

SYNTHESIS_COSTS = {
    1: 800, 2: 1000, 3: 1500, 4: 2200, 5: 3000,
    6: 4500, 7: 6500, 8: 9000, 9: 12000, 10: 16000
}

STORAGE_COSTS = {
    1: 400, 2: 600, 3: 900, 4: 1400, 5: 2100,
    6: 3100, 7: 4500, 8: 6500, 9: 9000, 10: 12000
}

LABORATORY_COSTS = {
    1: 1200, 2: 1800, 3: 2700, 4: 4000, 5: 6000
}

CANTEEN_COSTS = {
    1: 600, 2: 900, 3: 1400, 4: 2100, 5: 3200,
    6: 4800, 7: 7000, 8: 10000, 9: 14000, 10: 19000
}

FORGE_COSTS = {
    1: 1500, 2: 2200, 3: 3300, 4: 5000, 5: 7500,
    6: 11000, 7: 16000, 8: 22000
}

ELEVATION_COSTS = {
    1: 2000, 2: 3000, 3: 4500, 4: 6800, 5: 10000,
    6: 14000, 7: 19000, 8: 25000, 9: 32000, 10: 40000
}

class Dormitory(Building):
    def __init__(self):
        super().__init__(
            "Общежитие", 
            "Увеличивает лимит героев", 
            10,
            DORMITORY_COSTS,
            built=True,
            unlock_floor=0
        )
        self.base_capacity = 5

    def effect(self):
        capacity = self.get_capacity()
        return f"Вместимость: {capacity} героев"
    
    def get_capacity(self):
        return self.base_capacity + ((self.level - 1) * 2)

class SummonHall(Building):
    def __init__(self):
        super().__init__(
            "Зал призыва героев",
            "Постоянное здание для призыва новых героев",
            1,
            {1: 0},  # Бесплатное
            built=True,
            unlock_floor=0
        )

    def effect(self):
        return "Базовая функция призыва героев"

class SynthesisRoom(Building):
    def __init__(self):
        super().__init__(
            "Комната синтеза",
            "Позволяет объединять героев для повышения уровня",
            10,
            SYNTHESIS_COSTS,
            built=True,
            unlock_floor=0
        )

    def effect(self):
        return f"Макс. уровень для синтеза: {10 + self.level * 5}"

class Storage(Building):
    def __init__(self):
        super().__init__(
            "Склад",
            "Позволяет хранить предметы",
            10,
            STORAGE_COSTS,
            built=True,
            unlock_floor=0
        )
        
class Laboratory(Building):
    def __init__(self):
        super().__init__(
            "Лаборатория",
            "Позволяет исследовать новые технологии",
            5,
            LABORATORY_COSTS,
            built=False,
            unlock_floor=5
        )
        self.current_research = None
        self.research_progress = 0

    def effect(self):
        if self.level == 0:
            return "Не построена"
        if self.current_research:
            return f"Исследуется: {self.current_research} ({self.research_progress}%)"
        return "Готова к исследованиям"

class Canteen(Building):
    def __init__(self):
        super().__init__(
            "Столовая",
            "Увеличивает эффективность героев",
            10,
            CANTEEN_COSTS,
            built=False,
            unlock_floor=3
        )
        self.assigned_cook = None

class Forge(Building):
    def __init__(self):
        super().__init__(
            "Кузница",
            "Открывает систему крафта",
            8,
            FORGE_COSTS,
            built=False,
            unlock_floor=7
        )

class ElevationRoom(Building):
    def __init__(self):
        super().__init__(
            "Комната возвышения",
            "Позволяет повышать звёздность героев",
            10,
            ELEVATION_COSTS,
            built=False,
            unlock_floor=10
        )

class BuildingManager:
    def __init__(self):
        self.buildings = {
            "summon_hall": SummonHall(),
            "dormitory": Dormitory(),
            "synthesis": SynthesisRoom(),
            "storage": Storage(),
            "laboratory": Laboratory(),
            "canteen": Canteen(),
            "forge": Forge(),
            "elevation_room": ElevationRoom()
        }
    
    def unlock_buildings(self, tower_level):
        for building in self.buildings.values():
            if tower_level >= building.unlock_floor and not building.unlocked:
                building.unlocked = True
                print(f"🔓 Разблокировано здание: {building.name}")
    
    def get_available_buildings(self, tower_level):
        available = {}
        excluded_buildings = ["dormitory", "canteen"]
        
        for key, building in self.buildings.items():
            if (building.is_available(tower_level) and 
                building.built and 
                key not in excluded_buildings):
                available[key] = building
        return available
    
    def get_all_buildings_for_management(self, tower_level):
        available = {}
        for key, building in self.buildings.items():
            if building.is_available(tower_level):
                available[key] = building
        return available
    
    def get_building(self, name):
        return self.buildings.get(name)
    
    def get_new_unlocks(self, tower_level):
        new_unlocks = []
        for building in self.buildings.values():
            if (tower_level >= building.unlock_floor and 
                not building.built and 
                building.level == 0 and
                building.unlocked):
                new_unlocks.append(building)
        return new_unlocks
    
    def get_built_buildings(self):
        return {key: building for key, building in self.buildings.items() if building.built}