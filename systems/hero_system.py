# hero_system.py
# systems/hero_system.py
import random
from game_data.name_library import generate_korean_name
from systems.character_traits_system import CharacterTraitSystem

# Словарь для определения лимитов уровней по звёздности
STAR_LIMITS = {
    1: (1, 10),
    2: (11, 20),
    3: (21, 40),
    4: (41, 60),
    5: (61, 80),
    6: (81, 100),
    7: (101, 120)
}

class Hero:
    def __init__(self, name=None, star=1, level=1):
        self.name = name if name else generate_korean_name()
        self.star = star
        self.level = level
        self.experience = 0
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        
        self._generate_hidden_stats()
        
        self.health_max = self._calculate_max_health()
        self.health_current = self.health_max
        self.mana_max = self._calculate_max_mana()
        self.mana_current = self.mana_max
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        
        self.character = CharacterTraitSystem.get_random_trait()
        self.is_alive = True
        self.battle_log = []

    def _generate_hidden_stats(self):
        base_value = 5 + (self.star * 3)
        
        self.strength = base_value + random.randint(0, 5)
        self.dexterity = base_value + random.randint(0, 5)
        self.constitution = base_value + random.randint(0, 5)
        self.intelligence = base_value + random.randint(0, 5)
        self.wisdom = base_value + random.randint(0, 5)
        self.charisma = base_value + random.randint(0, 5)

    def _calculate_max_health(self):
        return 20 + (self.constitution * 3) + (self.level * 2)

    def _calculate_max_mana(self):
        return 10 + (self.intelligence * 2) + (self.level * 1)

    def _calculate_attack(self):
        return 3 + (self.strength // 2) + (self.dexterity // 3) + (self.level * 1)

    def _calculate_defense(self):
        return 1 + (self.constitution // 3) + (self.wisdom // 4)

    def get_hidden_stats(self, game_state):
        research_mgr = game_state.get("research")
        buildings = game_state.get("buildings")
        
        if research_mgr and buildings:
            lab = buildings.get_building("laboratory")
            hero_understanding = research_mgr.researches.get("hero_understanding")
            
            if (lab and lab.level >= 2 and 
                hero_understanding and hero_understanding.is_researched):
                return (f"Сила: {self.strength} | Ловкость: {self.dexterity} | "
                    f"Выносливость: {self.constitution} | Интеллект: {self.intelligence} | "
                    f"Мудрость: {self.wisdom} | Харизма: {self.charisma}")
        
        return "Характеристики скрыты (исследуйте 'Понимание героев')"

    def calculate_exp_to_next_level(self):
        return self.level * 100

    def add_experience(self, amount):
        if self.level >= STAR_LIMITS[self.star][1]:
            return f"{self.name} достиг максимального уровня для своей звёздности!"
        
        self.experience += amount
        result = []
        while (self.experience >= self.exp_to_next_level and 
               self.level < STAR_LIMITS[self.star][1]):
            self.level_up()
            result.append(f"{self.name} достиг {self.level} уровня!")
        
        return "\n".join(result) if result else f"{self.name} получил {amount} опыта."

    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        
        old_max_health = self.health_max
        old_max_mana = self.mana_max
        
        self.health_max = self._calculate_max_health()
        self.mana_max = self._calculate_max_mana()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        
        if old_max_health > 0:
            health_percentage = self.health_current / old_max_health
            self.health_current = int(self.health_max * health_percentage)
        
        if old_max_mana > 0:
            mana_percentage = self.mana_current / old_max_mana
            self.mana_current = int(self.mana_max * mana_percentage)
        
        self.exp_to_next_level = self.calculate_exp_to_next_level()

    def can_star_up(self):
        return self.level >= STAR_LIMITS[self.star][1] and self.star < 7

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health_current -= actual_damage
        
        if self.health_current <= 0:
            self.health_current = 0
            self.is_alive = False
            return f"Герой {self.name} вернулся в объятия господа. Его боевой дух будет жить вечно."
        
        return f"{self.name} получает {actual_damage} урона (заблокировано {damage - actual_damage}). Осталось {self.health_current} HP."

    def decide_action(self, target):
        action_chance = random.random()
        base_attack_text = f"{self.name} атакует {target.name} и наносит"
        
        # Используем систему черт характера для определения действия
        return CharacterTraitSystem.get_trait_action(
            self.character, target, action_chance, base_attack_text, self
        )

    def __str__(self):
        star_symbol = "★" * self.star + "☆" * (7 - self.star)
        status = "❤️" if self.is_alive else "💀"
        return f"{status} {self.name} {star_symbol} (Ур. {self.level}) {self.character}\nЗдоровье: {self.health_current}/{self.health_max} Мана: {self.mana_current}/{self.mana_max}"