# systems.save_system.py
import json
import os
from datetime import datetime
from systems.party_system import PartySystem

class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save_game(self, game_state, slot=1):
        """Сохраняет игру в указанный слот"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")

        # Подготавливаем данные для сохранения
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "tower_level": game_state["tower_level"],
            "max_tower_floor": game_state.get("max_tower_floor", 1),
            "heroes": self._serialize_heroes(game_state["heroes"]),
            "wallet": {
                "gold": game_state["wallet"].gold,
                "crystals": game_state["wallet"].crystals
            },
            "buildings": self._serialize_buildings(game_state["buildings"]),
            "tower_monsters": game_state.get("tower_monsters", {}),
            "party_system": self._serialize_party_system(game_state),
            "research": self._serialize_research(game_state["research"]),
            # ДОБАВЛЯЕМ СИСТЕМУ СКЛАДА И ПРЕДМЕТОВ:
            "storage": self._serialize_storage(game_state["storage"]),
            "crafting_recipes": self._serialize_crafting(game_state["crafting_system"]),
        }
        
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def load_game(self, game_state, slot=1):
        """Загружает игру из указанного слота"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        
        if not os.path.exists(save_path):
            return False
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Восстанавливаем состояние игры
            game_state["tower_level"] = save_data.get("tower_level", 1)
            game_state["max_tower_floor"] = save_data.get("max_tower_floor", 1)
            game_state["heroes"] = self._deserialize_heroes(save_data.get("heroes", []))
            game_state["wallet"].gold = save_data.get("wallet", {}).get("gold", 0)
            game_state["wallet"].crystals = save_data.get("wallet", {}).get("crystals", 0)
            game_state["tower_monsters"] = save_data.get("tower_monsters", {})
            
            # Восстанавливаем здания и исследования
            self._deserialize_buildings(game_state["buildings"], save_data.get("buildings", {}))
            
            # Исследования
            research_mgr = game_state["research"]
            research_mgr.import_state(save_data.get("research", {}))
            research_mgr.apply_all_effects(game_state)

            # Партии
            self._deserialize_party_system(game_state, save_data.get("party_system", {}))

            # ВОССТАНАВЛИВАЕМ СКЛАД И КРАФТИНГ:
            self._deserialize_storage(game_state["storage"], save_data.get("storage", {}))
            self._deserialize_crafting(game_state["crafting_system"], save_data.get("crafting_recipes", {}))

            # ДОБАВИТЬ СЮДА - очищаем мертвых героев ПОСЛЕ загрузки
            if "party_system" in game_state:
                from systems.party_system import PartySystem
                PartySystem(game_state).cleanup_dead_heroes()
            
            # Очищаем мертвых героев с ролей (если система ролей инициализирована)
            if game_state.get("role_system") is not None:
                from systems.role_system import RoleSystem
                game_state["role_system"].cleanup_dead_heroes()
            
            return True
        
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
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
            heroes.append(hero)
        return heroes

    def _serialize_buildings(self, building_manager):
        """Сохраняет состояние зданий"""
        buildings_data = {}
        for key, building in building_manager.buildings.items():
            buildings_data[key] = {
                "level": building.level,
                "built": building.built
            }
        return buildings_data
    
    def _deserialize_buildings(self, building_manager, buildings_data):
        """Восстанавливает состояние зданий"""
        for key, data in buildings_data.items():
            if key in building_manager.buildings:
                building = building_manager.buildings[key]
                building.level = data.get("level", 1)
                building.built = data.get("built", False)

    def _serialize_research(self, research_manager):
        """Сохраняет состояние исследований"""
        return research_manager.export_state()

    def _serialize_party_system(self, game_state):
        """Сохраняет систему групп"""
        if "party_system" not in game_state:
            return {}
            
        party_system = game_state["party_system"]
        parties_serialized = {}
        
        # Создаем mapping id героя -> индекс
        hero_id_to_index = {id(hero): i for i, hero in enumerate(game_state["heroes"])}
        
        for party_id, party_data in party_system.get("parties", {}).items():
            # Сохраняем индексы героев вместо id объектов
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

    def _deserialize_party_system(self, game_state, saved_party_data):
        """Восстанавливает систему групп"""
        if not saved_party_data:
            return
            
        # Создаем mapping индекс -> id героя
        index_to_hero_id = {i: id(hero) for i, hero in enumerate(game_state["heroes"])}
        
        parties_restored = {}
        for party_id, party_data in saved_party_data.get("parties", {}).items():
            # Восстанавливаем id героев из индексов
            hero_ids = []
            for hero_index in party_data.get("heroes", []):
                if hero_index in index_to_hero_id:
                    hero_ids.append(index_to_hero_id[hero_index])
            
            parties_restored[party_id] = {
                "name": party_data.get("name", party_id),
                "heroes": hero_ids,
                "is_unlocked": party_data.get("is_unlocked", True)
            }
        
        # Убедимся, что есть хотя бы одна группа
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

    def _serialize_storage(self, storage):
        """Сохраняет состояние склада"""
        items_data = {}
        for item_id, item in storage.items.items():
            items_data[item_id] = {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "item_type": item.item_type.value,  # Сохраняем значение Enum
                "rarity": item.rarity.value,        # Сохраняем значение Enum
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

    def _deserialize_storage(self, storage, storage_data):
        """Восстанавливает состояние склада"""
        from systems.items_system import Item, ItemType, ItemRarity
        
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

    def _serialize_crafting(self, crafting_system):
        """Сохраняет рецепты крафта (если нужно сохранять прогресс)"""
        # Пока просто сохраняем ID всех рецептов
        # Можно расширить для сохранения прогресса разблокировки
        return {
            "available_recipes": list(crafting_system.recipes.keys())
        }

    def _deserialize_crafting(self, crafting_system, crafting_data):
        """Восстанавливает систему крафта"""
        # Пока просто проверяем, что все рецепты на месте
        # Можно расширить для восстановления прогресса разблокировки
        available_recipes = crafting_data.get("available_recipes", [])
        # Можно добавить логику разблокировки рецептов при загрузке

    def get_save_info(self, slot=1):
        """Возвращает информацию о сохранении"""
        save_path = os.path.join(self.save_dir, f"save_{slot}.json")
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # ФИКС: считаем только живых героев
            heroes_data = save_data.get("heroes", [])
            living_heroes = [hero for hero in heroes_data if hero.get("is_alive", True)]
            
            # ДОБАВЛЯЕМ ИНФОРМАЦИЮ О ПРЕДМЕТАХ:
            storage_data = save_data.get("storage", {})
            item_count = sum(item.get("quantity", 1) for item in storage_data.get("items", {}).values())
            
            return {
                "timestamp": save_data.get("timestamp"),
                "tower_level": save_data.get("tower_level", 1),
                "hero_count": len(living_heroes),
                "gold": save_data.get("wallet", {}).get("gold", 0),
                "crystals": save_data.get("wallet", {}).get("crystals", 0),
                "item_count": item_count  # Добавляем количество предметов
            }
        except Exception as e:
            print(f"Ошибка чтения сохранения: {e}")
            return None