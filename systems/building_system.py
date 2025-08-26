# building_system.py
# systems.building_system.py
from ui.building_manager import calculate_max_building_level

class Building:
    def __init__(self, name, description, max_level, base_cost, built=False, unlock_floor=0):
        self.name = name
        self.description = description
        self.level = 1 if built else 0
        self.max_level = max_level
        self.base_cost = base_cost
        self.built = built
        self.unlock_floor = unlock_floor  # Этаж, на котором разблокируется
        self.unlocked = built  # Если уже построено, то разблокировано

    def is_available(self, tower_level):
        """Проверяет, доступно ли здание для постройки/улучшения"""
        return tower_level >= self.unlock_floor

    def build_cost(self):
        return self.base_cost * 2

    def upgrade_cost(self):
        if self.level == 0:
            return self.build_cost()
        return self.base_cost * self.level

    def can_upgrade(self, tower_level):
        """Можно ли улучшить здание"""
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

class Dormitory(Building):
    def __init__(self):
        super().__init__(
            "Общежитие", 
            "Увеличивает лимит героев", 
            20,
            50,
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
            1,  # Не улучшается
            0,   # Бесплатное
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
            100,
            built=True,
            unlock_floor=0
        )

    def effect(self):
        return f"Макс. уровень для синтеза: {10 + self.level * 5}"

class Storage(Building):
    def __init__(self):
        super().__init__(
            "Склад",
            "Увеличивает лимит ресурсов",
            15,
            75,
            built=True,  # Оставляем True - склад изначально построен
            unlock_floor=3  # Разблокируется на 3 этаже
        )
        self.capacity = 1000

    def effect(self):
        self.capacity = 1000 + (self.level * 500)
        return f"Вместимость: {self.capacity} золота"
        
class Laboratory(Building):
    def __init__(self):
        super().__init__(
            "Лаборатория",
            "Позволяет исследовать новые технологии",
            5,
            300,
            built=False,
            unlock_floor=5  # Разблокируется на 5 этаже
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
            200,
            built=False,
            unlock_floor=3  # Разблокируется на 3 этаже
        )
        self.assigned_cook = None

class Forge(Building):
    def __init__(self):
        super().__init__(
            "Кузница",
            "Открывает систему крафта",
            8,
            300,
            built=False,
            unlock_floor=7  # Разблокируется на 7 этаже
        )

class ElevationRoom(Building):
    def __init__(self):
        super().__init__(
            "Комната возвышения",
            "Позволяет повышать звёздность героев",
            5,
            500,
            built=False,
            unlock_floor=10  # Разблокируется на 10 этаже
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
        """Автоматически разблокирует здания при достижении этажей"""
        for building in self.buildings.values():
            if tower_level >= building.unlock_floor and not building.unlocked:
                building.unlocked = True
                print(f"🔓 Разблокировано здание: {building.name}")
    
    def get_available_buildings(self, tower_level):
        """Возвращает список доступных для постройки/улучшения зданий"""
        available = {}
        for key, building in self.buildings.items():
            if building.is_available(tower_level) and building.built:  # Только построенные здания
                available[key] = building
        return available
    
    def get_all_buildings_for_management(self, tower_level):
        """Возвращает все здания для меню управления (включая недостроенные)"""
        available = {}
        for key, building in self.buildings.items():
            if building.is_available(tower_level):
                available[key] = building
        return available
    
    def get_building(self, name):
        return self.buildings.get(name)
    
    def get_new_unlocks(self, tower_level):
        """Возвращает список новых разблокировок зданий"""
        new_unlocks = []
        for building in self.buildings.values():
            if (tower_level >= building.unlock_floor and 
                not building.built and 
                building.level == 0 and
                building.unlocked):
                new_unlocks.append(building)
        return new_unlocks
    
    def get_built_buildings(self):
        """Возвращает только построенные здания"""
        return {key: building for key, building in self.buildings.items() if building.built}