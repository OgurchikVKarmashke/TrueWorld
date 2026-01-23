# app.py
from systems.currency import Wallet
from systems.building_system import BuildingManager
from game_data.research_system import ResearchManager
from systems.storage_system import StorageSystem
from systems.crafting_system import CraftingSystem
from systems.items_system import ItemManager
from systems.achievement_system import AchievementSystem
from game_data.save_system import SaveSystem
from systems.role_system import RoleSystem  # <-- ДОБАВЛЕНО

class App:
    """Главный контейнер приложения для управления зависимостями"""
    
    def __init__(self):
        self._components = {}
        self._initialized = False
        
        # ИНИЦИАЛИЗИРУЕМ ВСЕ ОСНОВНЫЕ ПОЛЯ ДАЖЕ ЕСЛИ ИГРА НЕ ЗАПУЩЕНА
        self.tower_level = 1
        self.max_tower_floor = 1
        self.heroes = []
        self.tower_monsters = {}
        self.role_system = None  # <-- Пока None, инициализируется позже
        self.wallet = None
        self.buildings = None
        self.research = None
        self.save_system = None
        self.achievement_system = None
        self.storage = None
        self.crafting_system = None
        self.item_manager = None
        
        # КОНФИГУРАЦИЯ НОВОЙ ИГРЫ
        self._new_game_config = {
            "wallet": {"gold": 10000, "crystals": 100},
            "tower_level": 1,
            "max_tower_floor": 1,
            "heroes": [],
            "inventory": {"materials": {}, "equipment": {}},
            "tower_monsters": {},
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
    
    def initialize(self):
        """Инициализирует все компоненты приложения"""
        if self._initialized:
            return
            
        # Инициализируем основные системы в правильном порядке
        self._init_wallet()
        self._init_item_manager()
        self._init_storage()
        self._init_crafting()
        self._init_buildings()
        self._init_research()
        self._init_save_system()
        self._init_achievements()
        self._init_role_system()  # <-- ДОБАВЛЕНО

        self._initialized = True
    
    # ДОБАВЛЕННЫЕ МЕТОДЫ ИНИЦИАЛИЗАЦИИ
    
    def _init_wallet(self):
        """Инициализирует кошелек"""
        self.wallet = Wallet()
    
    def _init_item_manager(self):
        """Инициализирует менеджер предметов"""
        self.item_manager = ItemManager()
    
    def _init_storage(self):
        """Инициализирует систему хранения"""
        self.storage = StorageSystem()
    
    def _init_crafting(self):
        """Инициализирует систему крафта"""
        self.crafting_system = CraftingSystem()
    
    def _init_buildings(self):
        """Инициализирует систему зданий"""
        self.buildings = BuildingManager()
    
    def _init_research(self):
        """Инициализирует систему исследований"""
        self.research = ResearchManager()
    
    def _init_save_system(self):
        """Инициализирует систему сохранений"""
        self.save_system = SaveSystem()
    
    def _init_achievements(self):
        """Инициализирует систему достижений"""
        self.achievement_system = AchievementSystem()
    
    def _init_role_system(self):
        """Инициализирует систему ролей"""
        # Создаем временный game_state для инициализации RoleSystem
        temp_game_state = {
            "heroes": self.heroes,
            "buildings": self.buildings,
            "party_system": self._components.get('party_system', {})
        }
        self.role_system = RoleSystem(temp_game_state)
    
    def _start_new_game(self):
        """Запускает новую игру с начальными значениями"""
        config = self._new_game_config
        
        # Устанавливаем начальные значения
        self.tower_level = config["tower_level"]
        self.max_tower_floor = config["max_tower_floor"]
        self.heroes = config["heroes"].copy()
        self.tower_monsters = config["tower_monsters"].copy()
        self._components['inventory'] = config["inventory"].copy()
        self.role_system = config["role_system"]
        
        # Кошелек с начальными деньгами
        wallet_config = config["wallet"]
        self.wallet.gold = wallet_config["gold"]
        self.wallet.crystals = wallet_config["crystals"]
        
        # Система групп (обновляем в _components)
        self._components['party_system'] = config["party_system"].copy()
    
    def start_new_game(self):
        """Публичный метод для начала новой игры"""
        # Сначала сбрасываем инициализацию
        self._initialized = False
        self._components = {}
        
        # Заново инициализируем системы
        self.initialize()
        
        # Теперь создаем новую игру
        self._start_new_game()
        
        # Инициализируем систему ролей после создания игры
        # Используем существующий метод
        self._init_role_system()
        
        return self.get_game_state_dict()
    
    
    # ДОБАВЛЯЕМ МЕТОД ДЛЯ ПОЛУЧЕНИЯ СОСТОЯНИЯ
    def get_game_state_dict(self):
        """Возвращает состояние игры в виде словаря"""
        # Проверяем что все обязательные поля существуют
        if not hasattr(self, 'tower_monsters'):
            self.tower_monsters = {}
        if not hasattr(self, 'heroes'):
            self.heroes = []
        if not hasattr(self, 'role_system'):
            self.role_system = None
        if not hasattr(self, '_components'):
            self._components = {}
        
        # Получаем party_system из _components или создаем по умолчанию
        party_system = self._components.get('party_system')
        if party_system is None:
            # Создаем дефолтную систему групп
            party_system = {
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
            self._components['party_system'] = party_system
        
        # Создаем полный game_state для системы ролей
        full_game_state = {
            "wallet": self.wallet,
            "tower_level": self.tower_level,
            "max_tower_floor": self.max_tower_floor,
            "heroes": self.heroes,
            "buildings": self.buildings,
            "research": self.research,
            "inventory": self._components.get('inventory', {"materials": {}, "equipment": {}}),
            "achievement_system": self.achievement_system,
            "tower_monsters": self.tower_monsters,
            "save_system": self.save_system,
            "role_system": self.role_system,
            "party_system": party_system,
            "storage": self.storage,
            "crafting_system": self.crafting_system,
            "item_manager": self.item_manager
        }
        
        # Обновляем game_state в системе ролей, если она существует
        if self.role_system:
            self.role_system.game_state = full_game_state
        
        return full_game_state

    def load_game_state_dict(self, game_state):
        """Загружает состояние игры из словаря"""
        # Обновляем основные поля
        self.tower_level = game_state.get("tower_level", 1)
        self.max_tower_floor = game_state.get("max_tower_floor", 1)
        self.heroes = game_state.get("heroes", [])
        self.tower_monsters = game_state.get("tower_monsters", {})
        self.role_system = game_state.get("role_system", None)
        
        # Обновляем системы
        if "wallet" in game_state:
            self.wallet = game_state["wallet"]
        
        if "buildings" in game_state:
            self.buildings = game_state["buildings"]
        
        if "research" in game_state:
            self.research = game_state["research"]
        
        if "party_system" in game_state:
            self._components['party_system'] = game_state["party_system"]
        
        if "storage" in game_state:
            self.storage = game_state["storage"]
        
        if "crafting_system" in game_state:
            self.crafting_system = game_state["crafting_system"]
        
        if "item_manager" in game_state:
            self.item_manager = game_state["item_manager"]
        
        if "achievement_system" in game_state:
            self.achievement_system = game_state["achievement_system"]
        
        if "save_system" in game_state:
            self.save_system = game_state["save_system"]
        
        # Обновляем game_state в системе ролей, если она существует
        if self.role_system:
            self.role_system.game_state = self.get_game_state_dict()
    
    # ДОБАВИМ ЕЩЕ ОДИН МЕТОД ДЛЯ СОВМЕСТИМОСТИ
    def load_from_save(self, slot=1):
        """Загружает игру из сохранения (удобный wrapper)"""
        if not self.save_system:
            self._init_save_system()
        
        return self.save_system.load_into_app(self, slot)

app = App()