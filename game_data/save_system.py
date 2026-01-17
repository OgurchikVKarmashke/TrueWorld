# systems.save_system.py
import json
import os
from datetime import datetime
from typing import Dict, Any

class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    # ===== СОВМЕСТИМЫЕ МЕТОДЫ =====
    
    def save_game(self, game_state, slot=1):
        """
        Старый метод для обратной совместимости
        Сохраняет игру из словаря game_state
        """
        return self._save_from_dict(game_state, slot)
    
    def load_game(self, game_state, slot=1):
        """
        Старый метод для обратной совместимости
        Загружает игру в словарь game_state
        """
        return self._load_into_dict(game_state, slot)
    
    # ===== НОВЫЕ МЕТОДЫ ДЛЯ App =====
    
    def save_from_app(self, app_instance, slot=1):
        """
        Новый метод: сохраняет игру из экземпляра App
        """
        # Получаем состояние из App
        game_state = app_instance.get_game_state_dict()
        return self._save_from_dict(game_state, slot)
    
    def load_into_app(self, app_instance, slot=1):
        """
        Новый метод: загружает игру в экземпляр App
        """
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return False
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Убедимся, что App инициализирован
            if not app_instance._initialized:
                app_instance.initialize()
            
            # Восстанавливаем героев ПЕРВЫМ делом (нужны для восстановления назначений)
            app_instance.heroes = self._deserialize_heroes(save_data.get("heroes", []))
            
            # Восстанавливаем базовые значения в App
            app_instance.tower_level = save_data.get("tower_level", 1)
            app_instance.max_tower_floor = save_data.get("max_tower_floor", 1)
            
            # Восстанавливаем кошелек - СНАЧАЛА ПРОВЕРЯЕМ СУЩЕСТВОВАНИЕ
            if not hasattr(app_instance, 'wallet') or app_instance.wallet is None:
                if hasattr(app_instance, '_init_wallet'):
                    app_instance._init_wallet()  # Инициализируем кошелек если его нет
                else:
                    from systems.currency import Wallet
                    app_instance.wallet = Wallet()
            
            wallet_data = save_data.get("wallet", {})
            app_instance.wallet.gold = wallet_data.get("gold", 0)
            app_instance.wallet.crystals = wallet_data.get("crystals", 0)
            
            # Восстанавливаем монстров
            app_instance.tower_monsters = save_data.get("tower_monsters", {})
            
            # Восстанавливаем здания (С НОВЫМ МЕТОДОМ)
            buildings_data = save_data.get("buildings", {})
            if hasattr(app_instance.buildings, 'from_dict'):
                # Новый метод с восстановлением назначений
                app_instance.buildings.from_dict(buildings_data, app_instance.heroes)
            else:
                # Старый метод для совместимости
                for key, data in buildings_data.items():
                    building = app_instance.buildings.buildings.get(key)
                    if building:
                        building.level = data.get("level", 1)
                        building.built = data.get("built", False)
                        # Пытаемся восстановить назначенного героя
                        if 'assigned_hero_id' in data and data['assigned_hero_id']:
                            for hero in app_instance.heroes:
                                if id(hero) == data['assigned_hero_id']:
                                    building.assigned_hero = hero
                                    break
            
            # Восстанавливаем исследования
            research_data = save_data.get("research", {})
            if hasattr(app_instance.research, 'import_state'):
                app_instance.research.import_state(research_data)
            
            # Применяем эффекты исследований (если есть такой метод)
            if hasattr(app_instance.research, 'apply_all_effects'):
                app_instance.research.apply_all_effects(app_instance.get_game_state_dict())
            
            # Восстанавливаем систему групп
            self._deserialize_party_system_to_app(app_instance, save_data.get("party_system", {}))
            
            # Восстанавливаем назначения на роли (должно быть ПОСЛЕ восстановления зданий!)
            role_assignments_data = save_data.get("role_assignments", {})
            self._deserialize_role_assignments_to_app(app_instance, role_assignments_data)

            # Восстанавливаем склад
            self._deserialize_storage_to_app(app_instance, save_data.get("storage", {}))
            
            # Восстанавливаем крафтинг
            self._deserialize_crafting_to_app(app_instance, save_data.get("crafting_recipes", {}))
            
            # Очищаем мертвых героев
            self._cleanup_after_load(app_instance)
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            import traceback
            traceback.print_exc()  # Добавим для отладки
            return False
    
    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====
    
    def _save_from_dict(self, game_state: Dict[str, Any], slot: int):
        """Сохраняет игру из словаря состояния"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")

        save_data = {
            "timestamp": datetime.now().isoformat(),
            "tower_level": game_state.get("tower_level", 1),
            "max_tower_floor": game_state.get("max_tower_floor", 1),
            "heroes": self._serialize_heroes(game_state.get("heroes", [])),
            "wallet": {
                "gold": game_state.get("wallet", {}).gold,
                "crystals": game_state.get("wallet", {}).crystals
            },
            "buildings": self._serialize_buildings_from_state(game_state),
            "tower_monsters": game_state.get("tower_monsters", {}),
            "party_system": self._serialize_party_system_from_state(game_state),
            "research": self._serialize_research_from_state(game_state),
            "storage": self._serialize_storage_from_state(game_state),
            "crafting_recipes": self._serialize_crafting_from_state(game_state),
            "role_assignments": self._serialize_role_assignments(game_state),
        }
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def _load_into_dict(self, game_state: Dict[str, Any], slot: int):
        """Загружает игру в словарь состояния"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return False
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Восстанавливаем героев ПЕРВЫМ делом
            heroes = self._deserialize_heroes(save_data.get("heroes", []))
            game_state["heroes"] = heroes
            
            # Восстанавливаем базовые значения
            game_state["tower_level"] = save_data.get("tower_level", 1)
            game_state["max_tower_floor"] = save_data.get("max_tower_floor", 1)
            
            # Кошелек
            if "wallet" in game_state:
                wallet_data = save_data.get("wallet", {})
                game_state["wallet"].gold = wallet_data.get("gold", 0)
                game_state["wallet"].crystals = wallet_data.get("crystals", 0)
            
            game_state["tower_monsters"] = save_data.get("tower_monsters", {})
            
            # Здания (с новой логикой восстановления назначений)
            if "buildings" in game_state:
                buildings_data = save_data.get("buildings", {})
                if hasattr(game_state["buildings"], 'from_dict'):
                    # Новый метод с восстановлением назначений
                    game_state["buildings"].from_dict(buildings_data, heroes)
                else:
                    # Старый метод для совместимости
                    for key, data in buildings_data.items():
                        building = game_state["buildings"].buildings.get(key)
                        if building:
                            building.level = data.get("level", 1)
                            building.built = data.get("built", False)
                            # Пытаемся восстановить назначенного героя
                            if 'assigned_hero_id' in data and data['assigned_hero_id']:
                                for hero in heroes:
                                    if id(hero) == data['assigned_hero_id']:
                                        building.assigned_hero = hero
                                        break
            
            # Исследования
            if "research" in game_state and hasattr(game_state["research"], 'import_state'):
                research_data = save_data.get("research", {})
                game_state["research"].import_state(research_data)
                # Применяем эффекты если есть метод
                if hasattr(game_state["research"], 'apply_all_effects'):
                    game_state["research"].apply_all_effects(game_state)
            
            # Система групп
            self._deserialize_party_system_into_state(game_state, save_data.get("party_system", {}))
            
            # Восстанавливаем назначения на роли
            role_assignments_data = save_data.get("role_assignments", {})
            self._deserialize_role_assignments_into_state(game_state, role_assignments_data)

            # Склад
            storage_data = save_data.get("storage", {})
            if "storage" in game_state:
                self._deserialize_storage_into_state(game_state["storage"], storage_data)
            
            # Крафтинг
            crafting_data = save_data.get("crafting_recipes", {})
            if "crafting_system" in game_state:
                self._deserialize_crafting_into_state(game_state["crafting_system"], crafting_data)
            
            # Очистка
            self._cleanup_after_load_dict(game_state)
            
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    # ===== СЕРИАЛИЗАЦИЯ =====
    
    def _serialize_heroes(self, heroes):
        """Преобразует героев в сериализуемый формат"""
        serialized = []
        for hero in heroes:
            serialized.append({
                "name": hero.name,
                "star": hero.star,
                "level": hero.level,
                "experience": hero.experience,
                "health_current": hero.health_current,
                "health_max": hero.health_max,
                "mana_current": hero.mana_current,
                "mana_max": hero.mana_max,
                "is_alive": hero.is_alive,
                "character": hero.character,
                "strength": hero.strength,
                "dexterity": hero.dexterity,
                "constitution": hero.constitution,
                "intelligence": hero.intelligence,
                "wisdom": hero.wisdom,
                "charisma": hero.charisma
            })
        return serialized
    
    def _serialize_buildings_from_state(self, game_state):
        """Сохраняет состояние зданий из game_state"""
        buildings = game_state.get("buildings")
        if not buildings or not hasattr(buildings, 'buildings'):
            return {}
        
        # Используем новый метод to_dict если есть
        if hasattr(buildings, 'to_dict'):
            try:
                # Передаем героев для сериализации назначений
                heroes = game_state.get("heroes", [])
                return buildings.to_dict(heroes)
            except Exception as e:
                print(f"Ошибка сериализации зданий (новый метод): {e}")
                # Fallback на старый метод
        
        # Старый метод для совместимости
        buildings_data = {}
        for key, building in buildings.buildings.items():
            building_dict = {
                "level": building.level,
                "built": building.built
            }
            # Добавляем ID назначенного героя если есть
            if hasattr(building, 'assigned_hero') and building.assigned_hero:
                building_dict["assigned_hero_id"] = id(building.assigned_hero)
            
            buildings_data[key] = building_dict
        return buildings_data
    
    def _serialize_party_system_from_state(self, game_state):
        """Сохраняет систему групп из game_state"""
        party_system = game_state.get("party_system", {})
        if not party_system:
            return {}
        
        parties_serialized = {}
        hero_id_to_index = {id(hero): i for i, hero in enumerate(game_state.get("heroes", []))}
        
        for party_id, party_data in party_system.get("parties", {}).items():
            hero_indices = []
            for hero_id in party_data.get("heroes", []):
                if hero_id in hero_id_to_index:
                    hero_indices.append(hero_id_to_index[hero_id])
            
            parties_serialized[party_id] = {
                "name": party_data.get("name", party_id),
                "heroes": hero_indices,
                "is_unlocked": party_data.get("is_unlocked", True)
            }
        
        return {
            "max_parties": party_system.get("max_parties", 1),
            "current_party": party_system.get("current_party", "party_1"),
            "parties": parties_serialized
        }
    
    def _serialize_research_from_state(self, game_state):
        """Сохраняет исследования из game_state"""
        research = game_state.get("research")
        if research and hasattr(research, 'export_state'):
            return research.export_state()
        return {}
    
    def _serialize_storage_from_state(self, game_state):
        """Сохраняет склад из game_state"""
        storage = game_state.get("storage")
        if not storage or not hasattr(storage, 'items'):
            return {"capacity": 50, "items": {}}
        
        items_data = {}
        for item_id, item in storage.items.items():
            items_data[item_id] = {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "item_type": item.item_type.value,
                "rarity": item.rarity.value,
                "stats": item.stats,
                "required_level": item.required_level,
                "stackable": item.stackable,
                "max_stack": item.max_stack,
                "quantity": item.quantity
            }
        
        return {
            "capacity": storage.capacity,
            "items": items_data
        }
    
    def _serialize_crafting_from_state(self, game_state):
        """Сохраняет крафтинг из game_state"""
        crafting = game_state.get("crafting_system")
        if crafting and hasattr(crafting, 'recipes'):
            return {
                "available_recipes": list(crafting.recipes.keys())
            }
        return {"available_recipes": []}
    
    def _serialize_role_assignments(self, game_state):
        """Сохраняет назначения героев на роли"""
        role_system = game_state.get("role_system")
        if not role_system or not hasattr(role_system, 'get_assigned_heroes'):
            return {}
        
        assigned_heroes = role_system.get_assigned_heroes()
        assignments = {}
        
        # Создаем mapping герой -> id
        hero_id_map = {id(hero): i for i, hero in enumerate(game_state.get("heroes", []))}
        
        for building_name, hero in assigned_heroes.items():
            if hero and hero.is_alive:
                hero_idx = hero_id_map.get(id(hero))
                if hero_idx is not None:
                    assignments[building_name] = hero_idx
        
        return assignments

    # ===== ДЕСЕРИАЛИЗАЦИЯ ДЛЯ App =====
    
    def _deserialize_heroes(self, heroes_data):
        """Восстанавливает героев из данных"""
        from systems.hero_system import Hero
        heroes = []
        for data in heroes_data:
            hero = Hero(name=data["name"], star=data["star"])
            hero.level = data["level"]
            hero.experience = data["experience"]
            hero.health_current = data["health_current"]
            hero.health_max = data["health_max"]
            hero.mana_current = data["mana_current"]
            hero.mana_max = data["mana_max"]
            hero.is_alive = data.get("is_alive", True)
            hero.character = data.get("character", "Обычный")
            hero.strength = data.get("strength", 5)
            hero.dexterity = data.get("dexterity", 5)
            hero.constitution = data.get("constitution", 5)
            hero.intelligence = data.get("intelligence", 5)
            hero.wisdom = data.get("wisdom", 5)
            hero.charisma = data.get("charisma", 5)
            hero.exp_to_next_level = hero.calculate_exp_to_next_level()
            heroes.append(hero)
        return heroes
    
    def _deserialize_party_system_to_app(self, app_instance, saved_party_data):
        """Восстанавливает систему групп в App"""
        if not saved_party_data:
            # Создаем новую систему групп
            app_instance._components['party_system'] = {
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
            return
        
        # Создаем mapping индекс -> id героя
        index_to_hero_id = {i: id(hero) for i, hero in enumerate(app_instance.heroes)}
        
        parties_restored = {}
        for party_id, party_data in saved_party_data.get("parties", {}).items():
            hero_ids = []
            for hero_index in party_data.get("heroes", []):
                if hero_index in index_to_hero_id:
                    hero_ids.append(index_to_hero_id[hero_index])
            
            parties_restored[party_id] = {
                "name": party_data.get("name", party_id),
                "heroes": hero_ids,
                "is_unlocked": party_data.get("is_unlocked", True)
            }
        
        # Если групп нет, создаем базовую
        if not parties_restored:
            parties_restored["party_1"] = {
                "name": "Основная группа",
                "heroes": [],
                "is_unlocked": True
            }
        
        app_instance._components['party_system'] = {
            "max_parties": saved_party_data.get("max_parties", 1),
            "current_party": saved_party_data.get("current_party", "party_1"),
            "parties": parties_restored
        }
    
    def _deserialize_storage_to_app(self, app_instance, storage_data):
        """Восстанавливает склад в App"""
        from systems.items_system import Item, ItemType, ItemRarity
        
        storage = app_instance.storage
        storage.capacity = storage_data.get("capacity", 50)
        storage.items = {}
        
        items_data = storage_data.get("items", {})
        for item_id, item_data in items_data.items():
            # Восстанавливаем Enum значения
            item_type = ItemType(item_data["item_type"])
            rarity = ItemRarity(item_data["rarity"])
            
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data["description"],
                item_type=item_type,
                rarity=rarity,
                stats=item_data["stats"],
                required_level=item_data.get("required_level", 1),
                stackable=item_data.get("stackable", False),
                max_stack=item_data.get("max_stack", 1),
                quantity=item_data.get("quantity", 1)
            )
            storage.items[item_id] = item
    
    def _deserialize_crafting_to_app(self, app_instance, crafting_data):
        """Восстанавливает крафтинг в App"""
        # Пока просто сохраняем список рецептов
        # В будущем можно добавить прогресс разблокировки
        available_recipes = crafting_data.get("available_recipes", [])
        # Можно добавить логику восстановления
    
    def _deserialize_role_assignments_to_app(self, app_instance, assignments_data):
        """Восстанавливает назначения героев на роли в App"""
        if not assignments_data:
            return
        
        # Создаем mapping индекс -> герой
        index_to_hero = {i: hero for i, hero in enumerate(app_instance.heroes)}
        
        # Убедимся, что система ролей инициализирована
        if not hasattr(app_instance, 'role_system') or app_instance.role_system is None:
            # Создаем временный game_state для инициализации RoleSystem
            temp_game_state = {
                "heroes": app_instance.heroes,
                "buildings": app_instance.buildings,
                "party_system": app_instance._components.get('party_system', {})
            }
            from systems.role_system import RoleSystem
            app_instance.role_system = RoleSystem(temp_game_state)
        
        # Восстанавливаем назначения
        for building_name, hero_index in assignments_data.items():
            if hero_index in index_to_hero:
                hero = index_to_hero[hero_index]
                if hero and hero.is_alive:
                    # Прямо назначаем героя на здание (минуя систему ролей, чтобы избежать проверок)
                    building = app_instance.buildings.get_building(building_name)
                    if building and hasattr(building, 'assigned_hero'):
                        # Сначала снимаем героя с других ролей
                        for other_building_name, other_building in app_instance.buildings.buildings.items():
                            if (hasattr(other_building, 'assigned_hero') and 
                                other_building.assigned_hero and 
                                id(other_building.assigned_hero) == id(hero)):
                                other_building.assigned_hero = None
                        
                        # Назначаем на текущую роль
                        building.assigned_hero = hero

    def _deserialize_role_assignments_into_state(self, game_state, assignments_data):
        """Восстанавливает назначения героев на роли в старый формат"""
        if not assignments_data:
            return
        
        # Создаем mapping индекс -> герой
        heroes = game_state.get("heroes", [])
        index_to_hero = {i: hero for i, hero in enumerate(heroes)}
        
        # Восстанавливаем назначения напрямую в здания
        for building_name, hero_index in assignments_data.items():
            if hero_index in index_to_hero:
                hero = index_to_hero[hero_index]
                if hero and hero.is_alive:
                    building = game_state["buildings"].get_building(building_name)
                    if building and hasattr(building, 'assigned_hero'):
                        # Сначала снимаем героя с других ролей
                        for other_building_name, other_building in game_state["buildings"].buildings.items():
                            if (hasattr(other_building, 'assigned_hero') and 
                                other_building.assigned_hero and 
                                id(other_building.assigned_hero) == id(hero)):
                                other_building.assigned_hero = None
                        
                        # Назначаем на текущую роль
                        building.assigned_hero = hero

    # ===== ДЕСЕРИАЛИЗАЦИЯ ДЛЯ СТАРОГО ФОРМАТА =====
    
    def _deserialize_party_system_into_state(self, game_state, saved_party_data):
        """Восстанавливает систему групп в старый game_state"""
        if not saved_party_data:
            return
        
        index_to_hero_id = {i: id(hero) for i, hero in enumerate(game_state.get("heroes", []))}
        
        parties_restored = {}
        for party_id, party_data in saved_party_data.get("parties", {}).items():
            hero_ids = []
            for hero_index in party_data.get("heroes", []):
                if hero_index in index_to_hero_id:
                    hero_ids.append(index_to_hero_id[hero_index])
            
            parties_restored[party_id] = {
                "name": party_data.get("name", party_id),
                "heroes": hero_ids,
                "is_unlocked": party_data.get("is_unlocked", True)
            }
        
        if not parties_restored:
            parties_restored["party_1"] = {
                "name": "Основная группа",
                "heroes": [],
                "is_unlocked": True
            }
        
        game_state["party_system"] = {
            "max_parties": saved_party_data.get("max_parties", 1),
            "current_party": saved_party_data.get("current_party", "party_1"),
            "parties": parties_restored
        }
    
    def _deserialize_storage_into_state(self, storage, storage_data):
        """Восстанавливает склад в старый формат"""
        from systems.items_system import Item, ItemType, ItemRarity
        
        storage.capacity = storage_data.get("capacity", 50)
        storage.items = {}
        
        items_data = storage_data.get("items", {})
        for item_id, item_data in items_data.items():
            item_type = ItemType(item_data["item_type"])
            rarity = ItemRarity(item_data["rarity"])
            
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data["description"],
                item_type=item_type,
                rarity=rarity,
                stats=item_data["stats"],
                required_level=item_data.get("required_level", 1),
                stackable=item_data.get("stackable", False),
                max_stack=item_data.get("max_stack", 1),
                quantity=item_data.get("quantity", 1)
            )
            storage.items[item_id] = item
    
    def _deserialize_crafting_into_state(self, crafting_system, crafting_data):
        """Восстанавливает крафтинг в старый формат"""
        available_recipes = crafting_data.get("available_recipes", [])
        # Можно добавить логику восстановления
    
    # ===== ОЧИСТКА =====
    
    def _cleanup_after_load(self, app_instance):
        """Очистка после загрузки в App"""
        # Очищаем группы от мертвых героев
        if hasattr(app_instance, 'get_game_state_dict'):
            from systems.party_system import PartySystem
            try:
                game_state = app_instance.get_game_state_dict()
                party_system = PartySystem(game_state)
                party_system.cleanup_dead_heroes()
            except:
                pass
        
        # Очищаем мертвых героев с ролей
        if hasattr(app_instance, 'role_system') and app_instance.role_system:
            from systems.role_system import RoleSystem
            app_instance.role_system.cleanup_dead_heroes()
        elif hasattr(app_instance, 'buildings'):
            # Если системы ролей нет, но есть здания, очищаем назначения у мертвых героев
            buildings = app_instance.buildings.buildings
            for building in buildings.values():
                if hasattr(building, 'assigned_hero') and building.assigned_hero:
                    if not building.assigned_hero.is_alive:
                        building.assigned_hero = None
    
    def _cleanup_after_load_dict(self, game_state):
        """Очистка после загрузки в старый формат"""
        # Очищаем группы от мертвых героев
        if "party_system" in game_state:
            from systems.party_system import PartySystem
            PartySystem(game_state).cleanup_dead_heroes()
        
        # Очищаем мертвых героев с ролей
        if game_state.get("role_system"):
            from systems.role_system import RoleSystem
            game_state["role_system"].cleanup_dead_heroes()
        elif "buildings" in game_state:
            # Если системы ролей нет, но есть здания, очищаем назначения у мертвых героев
            buildings = game_state["buildings"].buildings
            for building in buildings.values():
                if hasattr(building, 'assigned_hero') and building.assigned_hero:
                    if not building.assigned_hero.is_alive:
                        building.assigned_hero = None
    
    # ===== ИНФОРМАЦИЯ О СОХРАНЕНИЯХ =====
    
    def get_save_info(self, slot=1):
        """Возвращает информацию о сохранении"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Считаем только живых героев
            heroes_data = save_data.get("heroes", [])
            living_heroes = [hero for hero in heroes_data if hero.get("is_alive", True)]
            
            # Информация о предметах
            storage_data = save_data.get("storage", {})
            item_count = sum(item.get("quantity", 1) for item in storage_data.get("items", {}).values())
            
            return {
                "timestamp": save_data.get("timestamp"),
                "tower_level": save_data.get("tower_level", 1),
                "hero_count": len(living_heroes),
                "gold": save_data.get("wallet", {}).get("gold", 0),
                "crystals": save_data.get("wallet", {}).get("crystals", 0),
                "item_count": item_count
            }
        except Exception as e:
            print(f"Ошибка чтения сохранения: {e}")
            return None