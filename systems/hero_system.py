# systems.hero_system.py
import random
from game_data.name_library import generate_korean_name
from game_data.stats_base import StatsBase
from systems.character_traits_system import CharacterTraitSystem
from ui.visual_effects import VisualEffects
from systems.relationship_system import RelationshipSystem
from systems.combat_modifiers.status_effects import StatusEffectSystem

# Словарь для определения лимитов уровней по звёздности
STAR_LIMITS = {
    1: (1, 10),
    2: (11, 20),
    3: (21, 40),
    4: (41, 60),
    5: (61, 90),
    6: (91, 120),
    7: (121, 999)
}

# НОВАЯ ФУНКЦИЯ: Расчет опыта для следующего уровня (квадратичная формула)
def calculate_exp_requirement(level):
    """Рассчитывает необходимый опыт для достижения уровня"""
    return int(100 * (level ** 1.5))

class Hero(StatsBase):  # НАСЛЕДУЕМ ОТ StatsBase
    def __init__(self, name=None, star=1, level=1):
        # Инициализируем базовый класс
        super().__init__()
        
        self.name = name if name else generate_korean_name()
        self.star = star
        self.level = level
        self.experience = 0
        self.exp_to_next_level = self.calculate_exp_to_next_level()
        
        # Генерируем характеристики (4 вместо 6)
        self._generate_hidden_stats()
        
        # Инициализируем системы
        self.status_system = StatusEffectSystem(self)
        self.character = CharacterTraitSystem.get_random_trait()
        self.is_alive = True
        self.battle_log = []
        
        # Рассчитываем производные характеристики (HP, MP, атака, защита)
        self.calculate_derived_stats(self.level)
    
    def _generate_hidden_stats(self):
        """Генерирует 4 основные характеристики (без мудрости и харизмы)"""
        base_value = 5 + (self.star * 3)
        
        self.strength = base_value + random.randint(0, 5)
        self.dexterity = base_value + random.randint(0, 5)
        self.constitution = base_value + random.randint(0, 5)
        self.intelligence = base_value + random.randint(0, 5)
    
    def get_hidden_stats(self, game_state):
        """Показывает характеристики героя, если открыто исследование"""
        research_mgr = game_state.get("research")
        buildings = game_state.get("buildings")
        
        if research_mgr and buildings:
            lab = buildings.get_building("laboratory")
            hero_understanding = research_mgr.researches.get("hero_understanding")
            
            # Проверяем: лаборатория должна быть построена и исследование изучено
            if lab and lab.level >= 1 and hero_understanding and hero_understanding.is_researched:
                return self.get_stats_string()  # Используем метод из StatsBase
        
        return "Характеристики скрыты (исследуйте 'Понимание героев')"
    
    def calculate_exp_to_next_level(self):
        """Рассчитывает опыт, необходимый для следующего уровня"""
        return calculate_exp_requirement(self.level)
    
    def add_experience(self, amount):
        """Добавляет опыт герою с возможным повышением уровня"""
        if self.level >= STAR_LIMITS[self.star][1]:
            return f"{self.name} достиг максимального уровня для своей звёздности!"
        
        self.experience += amount
        level_ups = 0
        exp_gained = amount
        
        # Проверяем, достаточно ли опыта для повышения уровня
        while self.experience >= self.exp_to_next_level and self.level < STAR_LIMITS[self.star][1]:
            self.level_up()
            level_ups += 1
        
        # Формируем сообщение
        if level_ups > 0:
            current_exp = self.experience
            needed_exp = self.exp_to_next_level
            return (f"{self.name} получил {exp_gained} опыта и повысил уровень до {self.level}! "
                    f"[{current_exp}/{needed_exp}]")
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
        
        # Пересчитываем характеристики на новый уровень
        self.calculate_derived_stats(self.level)
        
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
        """Может ли герой повысить звездность"""
        return self.level >= STAR_LIMITS[self.star][1] and self.star < 7
    
    def take_damage(self, damage, damage_type: str = ""):
        """Нанесение урона герою"""
        # Модифицируем урон статус-эффектами
        if hasattr(self, 'status_system'):
            damage = self.status_system.modify_damage(damage, damage_type)
        
        actual_damage = max(1, damage - self.defense)
        blocked_damage = damage - actual_damage
        
        self.health_current -= actual_damage
        
        # Форматируем сообщение
        if self.health_current <= 0:
            self.health_current = 0
            self.is_alive = False
            message = f"Герой {self.name} вернулся в объятья Господа. Его боевой дух будут помнить до скончания времён."
            return message
        else:
            message = f"{self.name} получает {actual_damage} урона"
            if blocked_damage > 0:
                message += f" (заблокировано {blocked_damage})"
            message += f". Осталось {self.health_current} HP."
        
        return message
    
    def decide_action(self, target):
        """Решение о действии в бою"""
        action_chance = random.random()
        base_attack_text = f"{self.name} атакует {target.name} и наносит"
        
        # Используем систему черт характера для определения действия
        return CharacterTraitSystem.get_trait_action(
            self.character, target, action_chance, base_attack_text, self
        )
    
    def __str__(self):
        """Строковое представление героя"""
        try:
            return VisualEffects.format_hero_display(self)
        except Exception as e:
            # Фолбэк на случай ошибок с цветами
            exp_bar = self.get_experience_bar(10)
            combat_stats = self.get_combat_stats_string()  # Используем метод из StatsBase
            return (f"★{'★' * (self.star - 1)}{'☆' * (7 - self.star)} {self.name} (Ур. {self.level}) {self.character}\n"
                    f"{combat_stats}\n"
                    f"EXP: {self.experience}/{self.exp_to_next_level} [{exp_bar}]")
    
    def get_party_bonus(self, party_heroes):
        """Возвращает бонус от совместимости с другими героями группы"""
        if not party_heroes or len(party_heroes) < 2:
            return 1.0
        return RelationshipSystem.calculate_party_bonus(party_heroes)