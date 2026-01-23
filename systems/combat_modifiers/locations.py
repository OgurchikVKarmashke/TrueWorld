#systems/combat_modifiers/locations.py
import random
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

"""
Система локаций (биомов) для башни.
Локации меняются каждые 5 этажей, кроме особых.
"""

class LocationType(Enum):
    """Типы локаций"""
    PLAINS = "plains"           # Равнина/поле
    FOREST = "forest"           # Лес
    DESERT = "desert"           # Пустыня
    MOUNTAINS = "mountains"     # Горный перевал
    CASTLE = "castle"           # Замок/крепость
    DUNGEON = "dungeon"         # Подземелье
    SWAMP = "swamp"             # Болото
    CAVE = "cave"               # Пещера
    # Особые локации (меняются чаще)
    GOBLIN_VILLAGE = "goblin_village"  # Деревня гоблинов
    NECROPOLIS = "necropolis"   # Некрополь

@dataclass
class Location:
    """Класс локации"""
    name: str
    location_type: LocationType
    description: str
    is_special: bool = False
    base_monster_pool: List[str] = None
    possible_weather: List[str] = None
    trap_chance: float = 0.0
    trap_types: List[str] = None
    magic_trap_chance: float = 0.0
    
    def __post_init__(self):
        if self.base_monster_pool is None:
            self.base_monster_pool = []
        if self.possible_weather is None:
            self.possible_weather = ["ясно", "облачно"]
        if self.trap_types is None:
            self.trap_types = []

class LocationManager:
    """Менеджер локаций для башни"""
    
    def __init__(self):
        self.current_location: Optional[Location] = None
        self.location_streak = 0  # Сколько этажей подряд текущая локация
        self.locations_history: List[LocationType] = []
        
        # Инициализируем все локации
        self.all_locations = self._init_locations()
        
        # Шансы появления особых локаций
        self.special_location_chances = {
            "goblin_village": 0.1,  # 10% на этажах, кратных 3
            "necropolis": 0.05      # 5% на этажах, кратных 7
        }
    
    def _init_locations(self) -> Dict[LocationType, Location]:
        """Инициализирует все доступные локации"""
        return {
            LocationType.PLAINS: Location(
                name="Равнина",
                location_type=LocationType.PLAINS,
                description="Бескрайние поля с высокой травой и редкими деревьями.",
                base_monster_pool=["Гоблин", "Волк", "Орк"],
                possible_weather=["ясно", "облачно", "дождь", "ветер", "гроза"],
                trap_chance=0.1,
                trap_types=["капкан", "волчья яма"]
            ),
            
            LocationType.FOREST: Location(
                name="Лес",
                location_type=LocationType.FOREST,
                description="Густой древний лес с высокими деревьями и запутанными тропами.",
                base_monster_pool=["Паук", "Волк", "Гоблин"],
                possible_weather=["ясно", "облачно", "дождь", "туман"],
                trap_chance=0.3,
                trap_types=["капкан", "силки", "ядовитые шипы"]
            ),
            
            LocationType.DESERT: Location(
                name="Пустыня",
                location_type=LocationType.DESERT,
                description="Бескрайние пески под палящим солнцем.",
                base_monster_pool=["Скелет", "Орк"],
                possible_weather=["ясно", "жара", "песчаная буря", "ветер"],
                trap_chance=0.05,
                trap_types=["песчаная ловушка", "капкан скорпиона"]
            ),
            
            LocationType.MOUNTAINS: Location(
                name="Горный перевал",
                location_type=LocationType.MOUNTAINS,
                description="Каменистые тропы среди высоких гор.",
                base_monster_pool=["Орк", "Гоблин"],
                possible_weather=["ясно", "облачно", "ветер", "снег", "туман"],
                trap_chance=0.2,
                trap_types=["камнепад", "обрыв"]
            ),
            
            LocationType.CASTLE: Location(
                name="Замок",
                location_type=LocationType.CASTLE,
                description="Древний полуразрушенный замок.",
                base_monster_pool=["Скелет", "Гоблин"],
                possible_weather=["ясно", "облачно", "дождь", "туман"],
                trap_chance=0.4,
                trap_types=["магическая ловушка", "падающая решетка", "дротиковая ловушка"],
                magic_trap_chance=0.6
            ),
            
            LocationType.DUNGEON: Location(
                name="Подземелье",
                location_type=LocationType.DUNGEON,
                description="Темное сырое подземелье с каменными стенами.",
                base_monster_pool=["Скелет", "Паук", "Гоблин"],
                possible_weather=["ясно"],  # В подземелье нет погоды
                trap_chance=0.5,
                trap_types=["магическая ловушка", "ядовитый газ", "шипы", "дротиковая ловушка"],
                magic_trap_chance=0.7
            ),
            
            LocationType.SWAMP: Location(
                name="Болото",
                location_type=LocationType.SWAMP,
                description="Топистые болота с туманом и гниющими деревьями.",
                base_monster_pool=["Паук", "Гоблин"],
                possible_weather=["ясно", "облачно", "туман", "дождь"],
                trap_chance=0.35,
                trap_types=["трясина", "ядовитые споры", "капкан"]
            ),
            
            LocationType.CAVE: Location(
                name="Пещера",
                location_type=LocationType.CAVE,
                description="Темная глубокая пещера с каменными сталагмитами.",
                base_monster_pool=["Паук", "Скелет"],
                possible_weather=["ясно"],  # В пещере нет погоды
                trap_chance=0.25,
                trap_types=["камнепад", "ядовитый гриб", "шипы"]
            ),
            
            # Особые локации
            LocationType.GOBLIN_VILLAGE: Location(
                name="Деревня гоблинов",
                location_type=LocationType.GOBLIN_VILLAGE,
                description="Примитивное поселение гоблинов с хижинами и частоколом.",
                is_special=True,
                base_monster_pool=["Гоблин", "Гоблин-воин", "Гоблин-маг", "Волк"],
                possible_weather=["ясно", "облачно", "дождь"],
                trap_chance=0.6,
                trap_types=["капкан", "силки", "ядовитые шипы", "засада"],
                magic_trap_chance=0.3
            ),
            
            LocationType.NECROPOLIS: Location(
                name="Некрополь",
                location_type=LocationType.NECROPOLIS,
                description="Город мертвых с древними склепами и мавзолеями.",
                is_special=True,
                base_monster_pool=["Скелет", "Скелет-воин", "Скелет-маг"],
                possible_weather=["ясно", "туман"],
                trap_chance=0.45,
                trap_types=["магическая ловушка", "проклятие", "духовные оковы"],
                magic_trap_chance=0.8
            )
        }
    
    def get_location_for_floor(self, floor: int, force_change: bool = False) -> Location:
        """
        Получает локацию для этажа.
        Логика: обычные локации меняются раз в 5 этажей.
        Особые локации могут появиться с шансом.
        """
        # Проверяем особые локации на определенных этажах
        if not force_change:
            if floor % 3 == 0 and random.random() < self.special_location_chances["goblin_village"]:
                return self.all_locations[LocationType.GOBLIN_VILLAGE]
            
            if floor % 7 == 0 and random.random() < self.special_location_chances["necropolis"]:
                return self.all_locations[LocationType.NECROPOLIS]
        
        # Если локации нет или нужно сменить
        if self.current_location is None or force_change:
            return self._choose_new_location(floor, is_special=False)
        
        # Проверяем, не пора ли сменить обычную локацию
        if not self.current_location.is_special:
            if self.location_streak >= 5:
                # Шансы на смену: 0% на 4 раз, 5% на 3 раз, 15% на 2 раз, 25% на 1 раз
                streak_over = min(4, self.location_streak - 4)
                chance_to_stay = [0.25, 0.15, 0.05, 0.0][streak_over]
                
                if random.random() < chance_to_stay:
                    self.location_streak += 1
                    return self.current_location
                else:
                    return self._choose_new_location(floor, is_special=False)
            else:
                self.location_streak += 1
                return self.current_location
        else:
            # Особые локации всегда только на 1 этаж
            return self._choose_new_location(floor, is_special=False)
    
    def _choose_new_location(self, floor: int, is_special: bool) -> Location:
        """Выбирает новую локацию"""
        if is_special:
            # Выбираем из особых локаций
            special_locations = [loc for loc in self.all_locations.values() if loc.is_special]
            self.current_location = random.choice(special_locations)
        else:
            # Выбираем из обычных локаций
            normal_locations = [loc for loc in self.all_locations.values() if not loc.is_special]
            self.current_location = random.choice(normal_locations)
        
        self.location_streak = 1
        self.locations_history.append(self.current_location.location_type)
        
        # Ограничиваем историю последними 10 локациями
        if len(self.locations_history) > 10:
            self.locations_history = self.locations_history[-10:]
        
        return self.current_location
    
    def get_monster_pool_for_location(self, location_type: LocationType) -> List[str]:
        """Возвращает пул монстров для локации"""
        location = self.all_locations.get(location_type)
        if location:
            return location.base_monster_pool
        return []
    
    def get_possible_weather(self, location_type: LocationType) -> List[str]:
        """Возвращает возможные типы погоды для локации"""
        location = self.all_locations.get(location_type)
        if location:
            return location.possible_weather
        return ["ясно"]
    
    def get_location_info(self, location_type: LocationType) -> Optional[Location]:
        """Возвращает информацию о локации"""
        return self.all_locations.get(location_type)

# Глобальный экземпляр менеджера локаций
location_manager = LocationManager()