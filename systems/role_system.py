#role_system.py
class RoleSystem:
    def __init__(self, game_state):
        self.game_state = game_state
        self.roles = {
            'cook': {
                'building': 'canteen',
                'title': '🍳 Повар',
                'bonus': 'Увеличивает получаемый опыт'
            },
            'blacksmith': {
                'building': 'forge', 
                'title': '⚒️ Кузнец',
                'bonus': 'Увеличивает атаку героев'
            },
            'researcher': {
                'building': 'laboratory',
                'title': '🔬 Исследователь',
                'bonus': 'Ускоряет исследования'
            }
        }
    
    def is_hero_available(self, hero):
        """Проверяет, доступен ли герой для назначения на роль"""
        # Герой не должен быть в группах
        party_system = self.game_state.get("party_system", {})
        parties = party_system.get("parties", {})
        
        for party_id, party_data in parties.items():
            if id(hero) in party_data.get("heroes", []):
                return False
        
        # Герой не должен быть уже назначен на другую роль
        buildings = self.game_state["buildings"].buildings
        for building in buildings.values():
            if hasattr(building, 'assigned_hero') and building.assigned_hero == hero:
                return False
        
        return True
    
    def get_available_heroes(self):
        """Возвращает героев, доступных для назначения на роли"""
        return [hero for hero in self.game_state["heroes"] if self.is_hero_available(hero)]
    
    def assign_hero(self, role_name, hero):
        """Назначает героя на роль"""
        if not self.is_hero_available(hero):
            return False, "Герой уже занят в группе или на другой роли!"
        
        role = self.roles[role_name]
        building = self.game_state["buildings"].get_building(role['building'])
        
        if building.level == 0:
            return False, "Здание не построено!"
        
        # Снимаем героя с других ролей
        self.remove_hero_from_all_roles(hero)
        
        # Назначаем на новую роль
        building.assigned_hero = hero
        return True, f"{hero.name} назначен {role['title']}!"
    
    def remove_hero_from_all_roles(self, hero):
        """Снимает героя со всех ролей"""
        buildings = self.game_state["buildings"].buildings
        for building in buildings.values():
            if hasattr(building, 'assigned_hero') and building.assigned_hero == hero:
                building.assigned_hero = None
    
    def get_assigned_heroes(self):
        """Возвращает всех назначенных героев"""
        assigned = {}
        buildings = self.game_state["buildings"].buildings
        for building_name, building in buildings.items():
            if hasattr(building, 'assigned_hero') and building.assigned_hero:
                assigned[building_name] = building.assigned_hero
        return assigned
    
    def get_hero_role(self, hero):
        """Возвращает роль героя, если он назначен"""
        buildings = self.game_state["buildings"].buildings
        for building_name, building in buildings.items():
            if hasattr(building, 'assigned_hero') and building.assigned_hero == hero:
                for role_name, role_info in self.roles.items():
                    if role_info['building'] == building_name:
                        return role_info['title']
        return None