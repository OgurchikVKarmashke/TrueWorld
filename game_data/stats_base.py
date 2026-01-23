# game_data/stats_base.py
"""
Базовый класс для характеристик всех существ (героев, монстров, боссов).
Содержит только основные характеристики без игровой логики.
"""


class StatsBase:
    """Базовые характеристики для всех существ"""
    
    # Коэффициенты для расчета характеристик
    HEALTH_PER_CONSTITUTION = 3
    MANA_PER_INTELLIGENCE = 2
    ATTACK_PER_STRENGTH = 0.5
    ATTACK_PER_DEXTERITY = 0.33
    DEFENSE_PER_CONSTITUTION = 0.33
    DEFENSE_PER_DEXTERITY = 0.25
    
    def __init__(self):
        self.strength = 0      # Сила - влияет на физическую атаку
        self.dexterity = 0     # Ловкость - влияет на атаку и защиту
        self.constitution = 0  # Выносливость - влияет на HP и защиту
        self.intelligence = 0  # Интеллект - влияет на ману и магию
        
        # Производные характеристики (будут рассчитаны отдельно)
        self.health_max = 0
        self.health_current = 0
        self.mana_max = 0
        self.mana_current = 0
        self.attack = 0
        self.defense = 0
    
    def calculate_derived_stats(self, level=1):
        """
        Рассчитывает производные характеристики на основе основных.
        level: уровень существа (используется в формулах)
        """
        # Расчет здоровья (округляем до целого)
        base_health = 20 + (level * 2)
        self.health_max = int(base_health + (self.constitution * self.HEALTH_PER_CONSTITUTION))
        
        # Расчет маны (округляем до целого)
        base_mana = 10 + (level * 1)
        self.mana_max = int(base_mana + (self.intelligence * self.MANA_PER_INTELLIGENCE))
        
        # Расчет атаки (уже целое число)
        base_attack = 3 + level
        strength_bonus = int(self.strength * self.ATTACK_PER_STRENGTH)
        dexterity_bonus = int(self.dexterity * self.ATTACK_PER_DEXTERITY)
        self.attack = base_attack + strength_bonus + dexterity_bonus
        
        # Расчет защиты (уже целое число)
        base_defense = 1
        constitution_bonus = int(self.constitution * self.DEFENSE_PER_CONSTITUTION)
        dexterity_defense_bonus = int(self.dexterity * self.DEFENSE_PER_DEXTERITY)
        self.defense = base_defense + constitution_bonus + dexterity_defense_bonus
        
        # Устанавливаем текущие значения равными максимальным
        self.health_current = self.health_max
        self.mana_current = self.mana_max
    
    def get_stats_string(self):
        """Возвращает строку с характеристиками"""
        return (f"Сила: {self.strength} | Ловкость: {self.dexterity} | "
                f"Выносливость: {self.constitution} | Интеллект: {self.intelligence}")
    
    def get_combat_stats_string(self):
        """Возвращает строку с боевыми характеристиками"""
        return (f"❤️ {self.health_current}/{self.health_max} | "
                f"✨ {self.mana_current}/{self.mana_max} | "
                f"⚔️ {self.attack} | 🛡️ {self.defense}")
    
    def to_dict(self):
        """Сериализация характеристик"""
        return {
            'strength': self.strength,
            'dexterity': self.dexterity,
            'constitution': self.constitution,
            'intelligence': self.intelligence,
            'health_max': self.health_max,
            'health_current': self.health_current,
            'mana_max': self.mana_max,
            'mana_current': self.mana_current,
            'attack': self.attack,
            'defense': self.defense
        }
    
    def from_dict(self, data):
        """Загрузка характеристик из словаря"""
        self.strength = data.get('strength', 0)
        self.dexterity = data.get('dexterity', 0)
        self.constitution = data.get('constitution', 0)
        self.intelligence = data.get('intelligence', 0)
        self.health_max = data.get('health_max', 0)
        self.health_current = data.get('health_current', 0)
        self.mana_max = data.get('mana_max', 0)
        self.mana_current = data.get('mana_current', 0)
        self.attack = data.get('attack', 0)
        self.defense = data.get('defense', 0)