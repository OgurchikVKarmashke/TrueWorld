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
        self.assigned_hero = None

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

    def to_dict(self):
        """Конвертирует здание в словарь для сохранения"""
        return {
            'name': self.name,
            'description': self.description,
            'level': self.level,
            'max_level': self.max_level,
            'built': self.built,
            'unlock_floor': self.unlock_floor,
            'unlocked': self.unlocked,
            'assigned_hero_id': id(self.assigned_hero) if self.assigned_hero else None
        }
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        """Создает здание из словаря"""
        building = cls(
            data['name'],
            data['description'],
            data['max_level'],
            {},  # cost_table будет установлен отдельно
            data['built'],
            data['unlock_floor']
        )
        building.level = data['level']
        building.unlocked = data['unlocked']
        
        # Восстанавливаем назначенного героя
        hero_id = data.get('assigned_hero_id')
        if hero_id and all_heroes:
            for hero in all_heroes:
                if id(hero) == hero_id:
                    building.assigned_hero = hero
                    break
        
        return building

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
    def __init__(self, name=None, description=None, max_level=10, cost_table=None, built=True, unlock_floor=0):
        # Используем переданные значения или значения по умолчанию
        name = name or "Общежитие"
        description = description or "Увеличивает лимит героев"
        max_level = max_level if max_level is not None else 10
        cost_table = cost_table or DORMITORY_COSTS
        built = built if built is not None else True
        unlock_floor = unlock_floor if unlock_floor is not None else 0
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)
        self.base_capacity = 5

    def effect(self):
        capacity = self.get_capacity()
        return f"Вместимость: {capacity} героев"
    
    def get_capacity(self):
        return self.base_capacity + ((self.level - 1) * 2)
    
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        # Создаем таблицу стоимостей для этого конкретного здания
        cost_table = DORMITORY_COSTS.copy()
        return super().from_dict(data, all_heroes)

class SummonHall(Building):
    def __init__(self, name=None, description=None, max_level=1, cost_table=None, built=True, unlock_floor=0):
        # Используем переданные значения или значения по умолчанию
        name = name or "Зал призыва героев"
        description = description or "Постоянное здание для призыва новых героев"
        max_level = max_level if max_level is not None else 1
        cost_table = cost_table or {1: 0}  # Бесплатное
        built = built if built is not None else True
        unlock_floor = unlock_floor if unlock_floor is not None else 0
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)

    def effect(self):
        return "Базовая функция призыва героев"
 
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        return super().from_dict(data, all_heroes)

class SynthesisRoom(Building):
    def __init__(self, name=None, description=None, max_level=10, cost_table=None, built=True, unlock_floor=0):
        # Используем переданные значения или значения по умолчанию
        name = name or "Комната синтеза"
        description = description or "Позволяет объединять героев для повышения уровня"
        max_level = max_level if max_level is not None else 10
        cost_table = cost_table or SYNTHESIS_COSTS
        built = built if built is not None else True
        unlock_floor = unlock_floor if unlock_floor is not None else 0
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)

    def effect(self):
        return f"Макс. уровень для синтеза: {10 + self.level * 5}"
            
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        return super().from_dict(data, all_heroes)

class Storage(Building):
    def __init__(self, name=None, description=None, max_level=10, cost_table=None, built=True, unlock_floor=0):
        # Используем переданные значения или значения по умолчанию
        name = name or "Склад"
        description = description or "Позволяет хранить предметы"
        max_level = max_level if max_level is not None else 10
        cost_table = cost_table or STORAGE_COSTS
        built = built if built is not None else True
        unlock_floor = unlock_floor if unlock_floor is not None else 0
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)
            
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        return super().from_dict(data, all_heroes)
        
class Laboratory(Building):
    def __init__(self, name=None, description=None, max_level=5, cost_table=None, built=False, unlock_floor=5):
        # Используем переданные значения или значения по умолчанию
        name = name or "Лаборатория"
        description = description or "Позволяет исследовать новые технологии"
        max_level = max_level if max_level is not None else 5
        cost_table = cost_table or LABORATORY_COSTS
        built = built if built is not None else False
        unlock_floor = unlock_floor if unlock_floor is not None else 5
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)
        self.current_research = None
        self.research_progress = 0

    def effect(self):
        if self.level == 0:
            return "Не построена"
        if self.current_research:
            return f"Исследуется: {self.current_research} ({self.research_progress}%)"
        return "Готова к исследованиям"
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            'current_research': self.current_research,
            'research_progress': self.research_progress
        })
        return data
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        building = super().from_dict(data, all_heroes)
        building.current_research = data.get('current_research')
        building.research_progress = data.get('research_progress', 0)
        return building

class Canteen(Building):
    def __init__(self, name=None, description=None, max_level=10, cost_table=None, built=False, unlock_floor=3):
        # Используем переданные значения или значения по умолчанию
        name = name or "Столовая"
        description = description or "Увеличивает эффективность героев"
        max_level = max_level if max_level is not None else 10
        cost_table = cost_table or CANTEEN_COSTS
        built = built if built is not None else False
        unlock_floor = unlock_floor if unlock_floor is not None else 3
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)
        # assinged_hero уже есть в родительском классе
    
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        return super().from_dict(data, all_heroes)

class Forge(Building):
    def __init__(self, name=None, description=None, max_level=8, cost_table=None, built=False, unlock_floor=7):
        # Используем переданные значения или значения по умолчанию
        name = name or "Кузница"
        description = description or "Открывает систему крафта"
        max_level = max_level if max_level is not None else 8
        cost_table = cost_table or FORGE_COSTS
        built = built if built is not None else False
        unlock_floor = unlock_floor if unlock_floor is not None else 7
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)
    
    def to_dict(self):
        return super().to_dict()
    
    @classmethod
    def from_dict(cls, data, all_heroes=None):
        return super().from_dict(data, all_heroes)

class ElevationRoom(Building):
    def __init__(self, name=None, description=None, max_level=10, cost_table=None, built=False, unlock_floor=10):
        # Используем переданные значения или значения по умолчанию
        name = name or "Комната возвышения"
        description = description or "Позволяет повышать звёздность героев"
        max_level = max_level if max_level is not None else 10
        cost_table = cost_table or ELEVATION_COSTS
        built = built if built is not None else False
        unlock_floor = unlock_floor if unlock_floor is not None else 10
        
        super().__init__(name, description, max_level, cost_table, built, unlock_floor)

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

    def to_dict(self, all_heroes=None):
        """Сохраняет все здания"""
        buildings_data = {}
        for key, building in self.buildings.items():
            buildings_data[key] = {
                'class': building.__class__.__name__,
                'data': building.to_dict()
            }
        return buildings_data
    
    def from_dict(self, buildings_data, all_heroes):
        """Восстанавливает все здания"""
        if not buildings_data:
            return
        
        # Маппинг имен классов на классы
        building_classes = {
            'Dormitory': Dormitory,
            'Laboratory': Laboratory,
            'Canteen': Canteen,
            'Forge': Forge,
            'SummonHall': SummonHall,
            'SynthesisRoom': SynthesisRoom,
            'Storage': Storage,
            'ElevationRoom': ElevationRoom
        }
        
        for key, building_info in buildings_data.items():
            class_name = building_info['class']
            building_data = building_info['data']
            
            if class_name in building_classes:
                building_class = building_classes[class_name]
                try:
                    # Создаем здание с параметрами из сохранения
                    building = building_class.from_dict(building_data, all_heroes)
                    self.buildings[key] = building
                except Exception as e:
                    print(f"Ошибка при восстановлении здания {key} ({class_name}): {e}")
                    # Создаем дефолтное здание если не получилось восстановить
                    self.buildings[key] = building_class()