# systems.hero_system.py
import random
from game_data.name_library import generate_korean_name
from systems.character_traits_system import CharacterTraitSystem
from ui.visual_effects import VisualEffects
from systems.relationship_system import RelationshipSystem

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

# НОВАЯ ФУНКЦИЯ: Расчет опыта для следующего уровня (квадратичная формула)
def calculate_exp_requirement(level):
    """Рассчитывает необходимый опыт для достижения уровня"""
    # Формула: 100 * уровень^1.5 (дает постепенное увеличение)
    return int(100 * (level ** 1.5))

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
        """Рассчитывает опыт, необходимый для следующего уровня"""
        return calculate_exp_requirement(self.level)

    def add_experience(self, amount):
        """Добавляет опыт герою с возможным повышением уровня"""
        if self.level >= STAR_LIMITS[self.star][1]:
            return f"{self.name} достиг максимального уровня для своей звёздности!"
        
        self.experience += amount  # <-- Вот здесь должно быть СЛОЖЕНИЕ
        level_ups = 0
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.experience >= self.exp_to_next_level and self.level < STAR_LIMITS[self.star][1]:
            self.level_up()
            level_ups += 1
        
        # Формируем сообщение
        if level_ups > 0:
            return f"{self.name} получил {amount} опыта и повысил уровень до {self.level}!"
        else:
            exp_left = self.exp_to_next_level - self.experience
            return f"{self.name} получил {amount} опыта. До следующего уровня: {exp_left}"

    def level_up(self):
        """Повышает уровень героя"""
        old_level = self.level
        self.level += 1
        
        # Вычитаем затраченный опыт
        self.experience -= calculate_exp_requirement(old_level)
        
        # Сохраняем проценты здоровья и маны
        old_health_percent = self.health_current / self.health_max if self.health_max > 0 else 1.0
        old_mana_percent = self.mana_current / self.mana_max if self.mana_max > 0 else 1.0
        
        # Пересчитываем статы
        self.health_max = self._calculate_max_health()
        self.mana_max = self._calculate_max_mana()
        self.attack = self._calculate_attack()
        self.defense = self._calculate_defense()
        
        # Восстанавливаем проценты здоровья и маны
        self.health_current = int(self.health_max * old_health_percent)
        self.mana_current = int(self.mana_max * old_mana_percent)
        
        # Обновляем требуемый опыт для следующего уровня
        self.exp_to_next_level = self.calculate_exp_to_next_level()

    def get_experience_bar(self, width=20):
        """Возвращает строку с прогресс-баром опыта"""
        if self.level >= STAR_LIMITS[self.star][1]:
            return "│" + "█" * width + "│ MAX"
        
        progress = self.experience / self.exp_to_next_level
        filled = int(width * progress)
        empty = width - filled
        
        bar = "│" + "█" * filled + "░" * empty + "│"
        percent = f" {progress*100:.1f}%"
        
        return bar + percent

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
        try:
            return VisualEffects.format_hero_display(self)
        except Exception as e:
            # Фолбэк на случай ошибок с цветами
            exp_bar = self.get_experience_bar(10)
            return (f"★{'★' * (self.star - 1)}{'☆' * (7 - self.star)} {self.name} (Ур. {self.level}) {self.character}\n"
                    f"❤️ {self.health_current}/{self.health_max} | ✨ {self.mana_current}/{self.mana_max}\n"
                    f"EXP: {self.experience}/{self.exp_to_next_level} [{exp_bar}]")

    def get_party_bonus(self, party_heroes):
        """Возвращает бонус от совместимости с другими героями группы"""
        if not party_heroes or len(party_heroes) < 2:
            return 1.0
        return RelationshipSystem.calculate_party_bonus(party_heroes)