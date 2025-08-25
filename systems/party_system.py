#party_system.py
class PartySystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.parties = game_state["party_system"]["parties"]
        self.max_parties = game_state["party_system"]["max_parties"]
    
    def cleanup_dead_heroes(self):
        """Очищает все группы от мертвых или удаленных героев"""
        alive_hero_ids = {id(hero) for hero in self.game_state["heroes"] if hero.is_alive}
        
        for party_id, party_data in self.parties.items():
            # Оставляем только живых героев, которые существуют в game_state
            party_data["heroes"] = [
                hero_id for hero_id in party_data["heroes"] 
                if hero_id in alive_hero_ids
            ]
    
    def is_hero_available(self, hero, current_party_id=None):
        """Проверяет, доступен ли герой для добавления в группы"""
        # Сначала очищаем мертвых героев
        self.cleanup_dead_heroes()
        
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
        """Возвращает героев конкретной группы"""
        party_hero_ids = set(self.parties[party_id]["heroes"])
        return [hero for hero in self.game_state["heroes"] if id(hero) in party_hero_ids and hero.is_alive]
    
    def get_active_party_heroes(self):
        """Возвращает героев активной группы"""
        current_party_id = self.game_state["party_system"]["current_party"]
        return self.get_party_heroes(current_party_id)
    
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
        
        return True