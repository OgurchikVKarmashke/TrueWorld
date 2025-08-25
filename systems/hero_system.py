# hero_system.py
import random
from game_data.name_library import generate_korean_name

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

# РАСШИРЕННЫЙ СПИСОК ЧЕРТ ХАРАКТЕРА
CHARACTER_TRAITS = [
    "Хитрый", "Жадный", "Ленивый", "Везучий", "Храбрый",
    "Трусливый", "Мудрый", "Глупый", "Добрый", "Злой",
    "Верный", "Предатель", "Оптимист", "Пессимист", "Спокойный",
    "Вспыльчивый", "Терпеливый", "Нетерпеливый", "Сильный", "Слабый",
    "Быстрый", "Медлительный", "Красивый", "Уродливый", "Общительный",
    "Застенчивый", "Творческий", "Практичный", "Мечтатель", "Реалист",
    "Лидер", "Последователь", "Амбициозный", "Скромный", "Эгоистичный",
    "Альтруист", "Любопытный", "Равнодушный", "Энергичный", "Уставший"
]

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
        
        self.character = random.choice(CHARACTER_TRAITS)
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
        
        action_methods = {
            "Хитрый": self._cunning_action,
            "Жадный": self._greedy_action,
            "Ленивый": self._lazy_action,
            "Везучий": self._lucky_action,
            "Храбрый": self._brave_action,
            "Трусливый": self._cowardly_action,
            "Мудрый": self._wise_action,
            "Добрый": self._kind_action,
            "Злой": self._evil_action,
            "Сильный": self._strong_action,
            "Слабый": self._weak_action,
            "Быстрый": self._fast_action,
            "Медлительный": self._slow_action,
            "Творческий": self._creative_action,
            "Практичный": self._practical_action
        }
        
        if self.character in action_methods:
            return action_methods[self.character](target, action_chance, base_attack_text)
        else:
            return self._default_action(target, base_attack_text)

    def _cunning_action(self, target, chance, base_text):
        if chance < 0.7:
            damage = random.randint(self.attack // 2, self.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        elif chance < 0.9:
            damage1 = random.randint(self.attack // 2, self.attack)
            damage2 = random.randint(self.attack // 2, self.attack)
            total_damage = damage1 + damage2
            result = target.take_damage(total_damage)
            return f"{self.name} использует хитрый приём! Двойная атака наносит {total_damage} урона!\n{result}"
        else:
            return f"{self.name} строит хитрые планы вместо атаки."

    def _greedy_action(self, target, chance, base_text):
        if chance < 0.8:
            damage = random.randint(self.attack, int(self.attack * 1.5))
            result = target.take_damage(damage)
            return f"{self.name} жадно атакует, нанося {damage} урона!\n{result}"
        else:
            return f"{self.name} разглядывает блестящие вещи монстра вместо атаки."

    def _lazy_action(self, target, chance, base_text):
        if chance < 0.5:
            damage = random.randint(self.attack // 2, self.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона (очень нехотя).\n{result}"
        else:
            return f"{self.name} зевает и пропускает ход."

    def _lucky_action(self, target, chance, base_text):
        if chance < 0.3:
            return f"{self.name} неуклюже спотыкается и случайно уворачивается от атаки!"
        elif chance < 0.8:
            damage = random.randint(self.attack // 2, self.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        else:
            damage = random.randint(self.attack * 2, self.attack * 3)
            result = target.take_damage(damage)
            return f"{self.name} невероятно везуч! Критический удар наносит {damage} урона!\n{result}"

    def _brave_action(self, target, chance, base_text):
        if chance < 0.8:
            damage = random.randint(self.attack, int(self.attack * 1.2))
            if hasattr(target, 'defense'):
                damage += target.defense // 3
            result = target.take_damage(damage)
            return f"{self.name} храбро атакует, игнорируя защиту! Наносит {damage} урона!\n{result}"
        else:
            return f"{self.name} вдохновляет союзников своей храбростью!"

    def _cowardly_action(self, target, chance, base_text):
        if chance < 0.3:
            return f"{self.name} в ужасе убегает от боя!"
        elif chance < 0.7:
            damage = random.randint(self.attack // 3, self.attack // 2)
            result = target.take_damage(damage)
            return f"{self.name} трусливо атакует издалека, нанося {damage} урона.\n{result}"
        else:
            return f"{self.name} дрожит от страха и не может атаковать!"

    def _wise_action(self, target, chance, base_text):
        if chance < 0.6:
            damage = random.randint(self.attack // 2, self.attack) + (self.intelligence // 2)
            result = target.take_damage(damage)
            return f"{self.name} использует мудрость для точной атаки! Наносит {damage} урона.\n{result}"
        elif chance < 0.9:
            damage = random.randint(self.attack, int(self.attack * 1.5))
            result = target.take_damage(damage)
            return f"{self.name} находит слабое место противника! Наносит {damage} урона.\n{result}"
        else:
            return f"{self.name} анализирует тактику боя."

    def _kind_action(self, target, chance, base_text):
        if chance < 0.5:
            damage = random.randint(self.attack // 2, self.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        elif chance < 0.8:
            return f"{self.name} пытается образумить противника, снижая его боевой дух!"
        else:
            if self.health_current < self.health_max * 0.7:
                heal_amount = self.wisdom // 2
                self.health_current = min(self.health_max, self.health_current + heal_amount)
                return f"{self.name} проявляет доброту к себе и восстанавливает {heal_amount} здоровья!"
            return f"{self.name} колеблется, не желая причинять вред."

    def _evil_action(self, target, chance, base_text):
        if chance < 0.7:
            damage = random.randint(self.attack, int(self.attack * 1.8))
            result = target.take_damage(damage)
            return f"{self.name} злобно атакует, нанося {damage} урона!\n{result}"
        elif chance < 0.9:
            damage = random.randint(self.attack * 2, self.attack * 3)
            result = target.take_damage(damage)
            return f"{self.name} изливает свою ненависть! Чудовищный удар наносит {damage} урона!\n{result}"
        else:
            return f"{self.name} наслаждается страданиями противника."

    def _strong_action(self, target, chance, base_text):
        if chance < 0.8:
            damage = random.randint(self.attack, int(self.attack * 1.6)) + (self.strength // 2)
            result = target.take_damage(damage)
            return f"{self.name} использует свою силу для мощной атаки! Наносит {damage} урона.\n{result}"
        else:
            return f"{self.name} оглушает противника мощным ударом!"

    def _weak_action(self, target, chance, base_text):
        if chance < 0.4:
            damage = random.randint(self.attack // 3, self.attack // 2)
            result = target.take_damage(damage)
            return f"{self.name} слабо атакует, нанося {damage} урона.\n{result}"
        elif chance < 0.7:
            damage = random.randint(self.attack, int(self.attack * 1.2))
            result = target.take_damage(damage)
            return f"{self.name} использует хитрость! Наносит {damage} урона.\n{result}"
        else:
            return f"{self.name} ищет способ избежать прямого боя."

    def _fast_action(self, target, chance, base_text):
        if chance < 0.6:
            damage1 = random.randint(self.attack // 2, self.attack)
            damage2 = random.randint(self.attack // 2, self.attack)
            total_damage = damage1 + damage2
            result = target.take_damage(total_damage)
            return f"{self.name} быстро атакует дважды! Наносит {total_damage} урона!\n{result}"
        else:
            damage = random.randint(self.attack, int(self.attack * 1.3))
            result = target.take_damage(damage)
            return f"{self.name} молниеносно атакует! Наносит {damage} урона.\n{result}"

    def _slow_action(self, target, chance, base_text):
        if chance < 0.4:
            damage = random.randint(int(self.attack * 1.5), self.attack * 2)
            result = target.take_damage(damage)
            return f"{self.name} медленно, но мощно атакует! Наносит {damage} урона.\n{result}"
        else:
            return f"{self.name} медленно готовится к атаке..."

    def _creative_action(self, target, chance, base_text):
        creative_attacks = [
            f"{self.name} использует неожиданную тактику!",
            f"{self.name} импровизирует в бою!",
            f"{self.name} применяет творческий подход!"
        ]
        
        if chance < 0.7:
            damage = random.randint(self.attack, int(self.attack * 1.8))
            result = target.take_damage(damage)
            attack_text = random.choice(creative_attacks)
            return f"{attack_text} Наносит {damage} урона.\n{result}"
        else:
            return random.choice(creative_attacks)

    def _practical_action(self, target, chance, base_text):
        if chance < 0.9:
            damage = random.randint(int(self.attack * 0.8), int(self.attack * 1.2))
            result = target.take_damage(damage)
            return f"{self.name} атакует практично и эффективно. Наносит {damage} урона.\n{result}"
        else:
            return f"{self.name} оценивает ситуацию для оптимальной атаки."

    def _default_action(self, target, base_text):
        damage = random.randint(self.attack // 2, self.attack)
        result = target.take_damage(damage)
        return f"{base_text} {damage} урона.\n{result}"

    def __str__(self):
        star_symbol = "★" * self.star + "☆" * (7 - self.star)
        status = "❤️" if self.is_alive else "💀"
        return f"{status} {self.name} {star_symbol} (Ур. {self.level}) {self.character}\nЗдоровье: {self.health_current}/{self.health_max} Мана: {self.mana_current}/{self.mana_max}"