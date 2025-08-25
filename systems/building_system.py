#building_system.py
class Building:
    def __init__(self, name, description, max_level, base_cost, built=False):
        self.name = name
        self.description = description
        self.level = 1 if built else 0
        self.max_level = max_level
        self.base_cost = base_cost
        self.built = built

    def build_cost(self):
        return self.base_cost * 2

    def upgrade_cost(self):
        if self.level == 0:
            return self.build_cost()
        return self.base_cost * self.level

    def effect(self):
        pass

class Dormitory(Building):
    def __init__(self):
        super().__init__(
            "Общежитие", 
            "Увеличивает лимит героев", 
            20,
            50,
            built=True
        )
        self.base_capacity = 5  # Базовая вместимость

    def effect(self):
        capacity = self.get_capacity()
        return f"Вместимость: {capacity} героев"
    
    def get_capacity(self):
        """Возвращает текущую вместимость"""
        return self.base_capacity + ((self.level - 1) * 2)

class SummonHall(Building):
    def __init__(self):
        super().__init__(
            "Зал призыва героев",
            "Постоянное здание для призыва новых героев",
            1,  # Не улучшается
            0,   # Бесплатное
            built=True
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
            built=True
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
            built=True
        )
        self.capacity = 1000

    def effect(self):
        self.capacity = 1000 + (self.level * 500)
        return f"Вместимость: {self.capacity} золata"

class Laboratory(Building):
    def __init__(self):
        super().__init__(
            "Лаборатория",
            "Позволяет исследовать новые технологии",
            5,
            300,
            built=False
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
            built=False
        )
        self.assigned_cook = None

    def effect(self):
        if self.level == 0:
            return "Не построена"
        if self.assigned_cook:
            return f"Повар: {self.assigned_cook.name} | Бонус: +{self.level}% к опыту"
        return "Нет повара"

class Forge(Building):
    def __init__(self):
        super().__init__(
            "Кузница",
            "Улучшает экипировку героев",
            8,
            300,
            built=False
        )
        self.assigned_blacksmith = None

    def effect(self):
        if self.level == 0:
            return "Не построена"
        if self.assigned_blacksmith:
            return f"Кузнец: {self.assigned_blacksmith.name} | Бонус: +{self.level}% к атаке"
        return "Нет кузнеца"

class ElevationRoom(Building):
    def __init__(self):
        super().__init__(
            "Комната возвышения",
            "Позволяет повышать звёздность героев",
            5,
            500,
            built=False
        )
        self.required_level = 15

    def effect(self):
        if self.level == 0:
            return "Не построена"
        return f"Макс. уровень повышения: {self.level} звёзд"

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
        """Разблокирует здания по достижении этажей"""
        if tower_level >= 3:
            self.buildings["storage"].built = True
        if tower_level >= 5:
            self.buildings["laboratory"].built = True
        if tower_level >= 7:
            self.buildings["canteen"].built = True
        if tower_level >= 10:
            self.buildings["forge"].built = True
        if tower_level >= 15:
            self.buildings["elevation_room"].built = True
    
    def get_building(self, name):
        return self.buildings.get(name)