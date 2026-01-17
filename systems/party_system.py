# systems/party_system.py
from systems.relationship_system import RelationshipSystem

class PartySystem:
    def __init__(self, game_state):
        self.game_state = game_state
        
        # Безопасное получение party_system
        party_system_data = game_state.get("party_system")
        
        # Если party_system None или пустой, создаем дефолтный
        if party_system_data is None or not isinstance(party_system_data, dict):
            party_system_data = {
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
            game_state["party_system"] = party_system_data
        
        # Проверяем структуру
        if "parties" not in party_system_data:
            party_system_data["parties"] = {
                "party_1": {"name": "Основная группа", "heroes": [], "is_unlocked": True}
            }
        if "max_parties" not in party_system_data:
            party_system_data["max_parties"] = 1
        if "current_party" not in party_system_data:
            party_system_data["current_party"] = "party_1"
        
        self.parties = party_system_data["parties"]
        self.max_parties = party_system_data["max_parties"]
    
    def get_hero_by_id(self, hero_id):
        """Находит героя по его идентификатору"""
        for hero in self.game_state["heroes"]:
            if id(hero) == hero_id:
                return hero
        return None
    
    def cleanup_dead_heroes(self):
        """Очищает все группы от мёртвых и удалённых героев"""
        for party_id, party_data in self.parties.items():
            # Создаём новый список, куда попадут только живые и существующие герои
            valid_hero_ids = []
            for hero_id in party_data["heroes"]:
                # Пытаемся найти героя по id
                hero = self.get_hero_by_id(hero_id)
                # Если герой найден И он жив, добавляем его id в новый список
                if hero is not None and hero.is_alive:
                    valid_hero_ids.append(hero_id)
                else:
                    # Удаляем связи и отношения если герой мёртв
                    self._cleanup_hero_relationships(hero_id)
            
            # Заменяем старый список героев в группе на новый, очищенный
            party_data["heroes"] = valid_hero_ids
    
    def _cleanup_hero_relationships(self, hero_id):
        """Очищает отношения и связи для удалённого героя"""
        # Очищаем из системы отношений
        if "relationship_system" in self.game_state:
            relationship_system = self.game_state["relationship_system"]
            if hasattr(relationship_system, 'remove_hero'):
                relationship_system.remove_hero(hero_id)
        
        # Очищаем из системы ролей
        if "role_system" in self.game_state:
            role_system = self.game_state["role_system"]
            if hasattr(role_system, 'remove_assignment'):
                role_system.remove_assignment(hero_id)
    
    def is_hero_available(self, hero, current_party_id=None):
        """Проверяет, доступен ли герой для добавления в группы"""
        # Сначала очищаем мертвых героев
        self.cleanup_dead_heroes()
        
        # Проверяем, жив ли герой
        if not hero.is_alive:
            return False
        
        # Проверяем, не находится ли герой в других группах
        for pid, pdata in self.parties.items():
            if pid != current_party_id and id(hero) in pdata["heroes"]:
                return False
        
        # Проверяем, не назначен ли герой на роль
        if self.game_state.get("role_system"):
            role_system = self.game_state["role_system"]
            if hasattr(role_system, 'is_hero_assigned') and role_system.is_hero_assigned(hero):
                return False
        
        return True
    
    def is_hero_in_any_party(self, hero):
        """Проверяет, находится ли герой в любой группе"""
        for pid, pdata in self.parties.items():
            if id(hero) in pdata["heroes"]:
                return True
        return False
    
    def get_available_heroes(self, current_party_id):
        """Возвращает героев, которые доступны для добавления в группу"""
        available_heroes = []
        current_party_hero_ids = set(self.parties[current_party_id]["heroes"])
        
        for hero in self.game_state["heroes"]:
            if hero.is_alive and id(hero) not in current_party_hero_ids and self.is_hero_available(hero, current_party_id):
                available_heroes.append(hero)
        
        return available_heroes

    def add_hero_to_party(self, party_id, hero):
        """Добавляет героя в группу"""
        # Проверяем, жив ли герой
        if not hero.is_alive:
            return False
            
        if len(self.parties[party_id]["heroes"]) >= 5:
            return False
        
        if not self.is_hero_available(hero, party_id):
            return False
        
        self.parties[party_id]["heroes"].append(id(hero))
        return True
    
    def remove_hero_from_party(self, party_id, hero):
        """Убирает героя из группы"""
        hero_id = id(hero)
        if hero_id in self.parties[party_id]["heroes"]:
            self.parties[party_id]["heroes"].remove(hero_id)
            return True
        return False
    
    def get_party_heroes(self, party_id):
        """Возвращает героев конкретной группы и ОЧИЩАЕТ её от мертвых"""
        # Сначала очищаем группу от мертвых героев
        self.cleanup_dead_heroes()
        
        party_hero_ids = set(self.parties[party_id]["heroes"])
        return [hero for hero in self.game_state["heroes"] 
                if id(hero) in party_hero_ids and hero.is_alive]
    
    def get_active_party_heroes(self):
        """Возвращает героев активной группы"""
        return self.get_party_heroes(self.current_party_id)
    
    def can_unlock_new_party(self):
        """Проверяет, можно ли создать новую группу"""
        return len(self.parties) < self.max_parties
    
    def unlock_new_party(self, party_name):
        """Создает новую группу"""
        if not self.can_unlock_new_party():
            return False
        
        new_party_id = f"party_{len(self.parties) + 1}"
        self.parties[new_party_id] = {
            "name": party_name,
            "heroes": [],
            "is_unlocked": True
        }
        
        # Обновляем game_state
        self.game_state["party_system"]["parties"] = self.parties
        self.game_state["party_system"]["max_parties"] = self.max_parties
        
        return True
    
    def increase_max_parties(self, amount=1):
        """Увеличивает максимальное количество доступных групп"""
        self.max_parties += amount
        if "party_system" in self.game_state:
            self.game_state["party_system"]["max_parties"] = self.max_parties
        return self.max_parties

    def get_party_bonus(self, party_id):
        """Возвращает бонус совместимости для группы"""
        party_heroes = self.get_party_heroes(party_id)
        return RelationshipSystem.calculate_party_bonus(party_heroes)

    def get_party_synergy_details(self, party_id):
        """Возвращает детали синергии группы"""
        party_heroes = self.get_party_heroes(party_id)
        return RelationshipSystem.get_party_synergy_details(party_heroes)
    
    def get_party_info(self, party_id):
        """Возвращает информацию о группе"""
        if party_id not in self.parties:
            return None
        return {
            "id": party_id,
            "name": self.parties[party_id]["name"],
            "hero_count": len(self.get_party_heroes(party_id)),
            "max_heroes": 5,
            "is_unlocked": self.parties[party_id]["is_unlocked"],
            "bonus": self.get_party_bonus(party_id)
        }