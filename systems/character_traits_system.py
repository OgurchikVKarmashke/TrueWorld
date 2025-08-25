# character_traits_system.py
# systems/character_traits_system.py
import random

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

class CharacterTraitSystem:
    @staticmethod
    def get_random_trait():
        """Возвращает случайную черту характера"""
        return random.choice(CHARACTER_TRAITS)
    
    @staticmethod
    def get_all_traits():
        """Возвращает все доступные черты характера"""
        return CHARACTER_TRAITS.copy()
    
    @staticmethod
    def get_trait_action(character, target, action_chance, base_attack_text, hero_instance):
        """
        Определяет действие на основе черты характера
        Возвращает строку с описанием действия
        """
        action_methods = {
            "Хитрый": CharacterTraitSystem._cunning_action,
            "Жадный": CharacterTraitSystem._greedy_action,
            "Ленивый": CharacterTraitSystem._lazy_action,
            "Везучий": CharacterTraitSystem._lucky_action,
            "Храбрый": CharacterTraitSystem._brave_action,
            "Трусливый": CharacterTraitSystem._cowardly_action,
            "Мудрый": CharacterTraitSystem._wise_action,
            "Добрый": CharacterTraitSystem._kind_action,
            "Злой": CharacterTraitSystem._evil_action,
            "Сильный": CharacterTraitSystem._strong_action,
            "Слабый": CharacterTraitSystem._weak_action,
            "Быстрый": CharacterTraitSystem._fast_action,
            "Медлительный": CharacterTraitSystem._slow_action,
            "Творческий": CharacterTraitSystem._creative_action,
            "Практичный": CharacterTraitSystem._practical_action
        }
        
        if character in action_methods:
            return action_methods[character](target, action_chance, base_attack_text, hero_instance)
        else:
            return CharacterTraitSystem._default_action(target, base_attack_text, hero_instance)

    # Методы действий для различных черт характера
    @staticmethod
    def _cunning_action(target, chance, base_text, hero):
        if chance < 0.7:
            damage = random.randint(hero.attack // 2, hero.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        elif chance < 0.9:
            damage1 = random.randint(hero.attack // 2, hero.attack)
            damage2 = random.randint(hero.attack // 2, hero.attack)
            total_damage = damage1 + damage2
            result = target.take_damage(total_damage)
            return f"{hero.name} использует хитрый приём! Двойная атака наносит {total_damage} урона!\n{result}"
        else:
            return f"{hero.name} строит хитрые планы вместо атаки."

    @staticmethod
    def _greedy_action(target, chance, base_text, hero):
        if chance < 0.8:
            damage = random.randint(hero.attack, int(hero.attack * 1.5))
            result = target.take_damage(damage)
            return f"{hero.name} жадно атакует, нанося {damage} урона!\n{result}"
        else:
            return f"{hero.name} разглядывает блестящие вещи монстра вместо атаки."

    @staticmethod
    def _lazy_action(target, chance, base_text, hero):
        if chance < 0.5:
            damage = random.randint(hero.attack // 2, hero.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона (очень нехотя).\n{result}"
        else:
            return f"{hero.name} зевает и пропускает ход."

    @staticmethod
    def _lucky_action(target, chance, base_text, hero):
        if chance < 0.3:
            return f"{hero.name} неуклюже спотыкается и случайно уворачивается от атаки!"
        elif chance < 0.8:
            damage = random.randint(hero.attack // 2, hero.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        else:
            damage = random.randint(hero.attack * 2, hero.attack * 3)
            result = target.take_damage(damage)
            return f"{hero.name} невероятно везуч! Критический удар наносит {damage} урона!\n{result}"

    @staticmethod
    def _brave_action(target, chance, base_text, hero):
        if chance < 0.8:
            damage = random.randint(hero.attack, int(hero.attack * 1.2))
            if hasattr(target, 'defense'):
                damage += target.defense // 3
            result = target.take_damage(damage)
            return f"{hero.name} храбро атакует, игнорируя защиту! Наносит {damage} урона!\n{result}"
        else:
            return f"{hero.name} вдохновляет союзников своей храбростью!"

    @staticmethod
    def _cowardly_action(target, chance, base_text, hero):
        if chance < 0.3:
            return f"{hero.name} в ужасе убегает от боя!"
        elif chance < 0.7:
            damage = random.randint(hero.attack // 3, hero.attack // 2)
            result = target.take_damage(damage)
            return f"{hero.name} трусливо атакует издалека, нанося {damage} урона.\n{result}"
        else:
            return f"{hero.name} дрожит от страха и не может атаковать!"

    @staticmethod
    def _wise_action(target, chance, base_text, hero):
        if chance < 0.6:
            damage = random.randint(hero.attack // 2, hero.attack) + (hero.intelligence // 2)
            result = target.take_damage(damage)
            return f"{hero.name} использует мудрость для точной атаки! Наносит {damage} урона.\n{result}"
        elif chance < 0.9:
            damage = random.randint(hero.attack, int(hero.attack * 1.5))
            result = target.take_damage(damage)
            return f"{hero.name} находит слабое место противника! Наносит {damage} урона.\n{result}"
        else:
            return f"{hero.name} анализирует тактику боя."

    @staticmethod
    def _kind_action(target, chance, base_text, hero):
        if chance < 0.5:
            damage = random.randint(hero.attack // 2, hero.attack)
            result = target.take_damage(damage)
            return f"{base_text} {damage} урона.\n{result}"
        elif chance < 0.8:
            return f"{hero.name} пытается образумить противника, снижая его боевой дух!"
        else:
            if hero.health_current < hero.health_max * 0.7:
                heal_amount = hero.wisdom // 2
                hero.health_current = min(hero.health_max, hero.health_current + heal_amount)
                return f"{hero.name} проявляет доброту к себе и восстанавливает {heal_amount} здоровья!"
            return f"{hero.name} колеблется, не желая причинять вред."

    @staticmethod
    def _evil_action(target, chance, base_text, hero):
        if chance < 0.7:
            damage = random.randint(hero.attack, int(hero.attack * 1.8))
            result = target.take_damage(damage)
            return f"{hero.name} злобно атакует, нанося {damage} урона!\n{result}"
        elif chance < 0.9:
            damage = random.randint(hero.attack * 2, hero.attack * 3)
            result = target.take_damage(damage)
            return f"{hero.name} изливает свою ненависть! Чудовищный удар наносит {damage} урона!\n{result}"
        else:
            return f"{hero.name} наслаждается страданиями противника."

    @staticmethod
    def _strong_action(target, chance, base_text, hero):
        if chance < 0.8:
            damage = random.randint(hero.attack, int(hero.attack * 1.6)) + (hero.strength // 2)
            result = target.take_damage(damage)
            return f"{hero.name} использует свою силу для мощной атаки! Наносит {damage} урона.\n{result}"
        else:
            return f"{hero.name} оглушает противника мощным ударом!"

    @staticmethod
    def _weak_action(target, chance, base_text, hero):
        if chance < 0.4:
            damage = random.randint(hero.attack // 3, hero.attack // 2)
            result = target.take_damage(damage)
            return f"{hero.name} слабо атакует, нанося {damage} урона.\n{result}"
        elif chance < 0.7:
            damage = random.randint(hero.attack, int(hero.attack * 1.2))
            result = target.take_damage(damage)
            return f"{hero.name} использует хитрость! Наносит {damage} урона.\n{result}"
        else:
            return f"{hero.name} ищет способ избежать прямого боя."

    @staticmethod
    def _fast_action(target, chance, base_text, hero):
        if chance < 0.6:
            damage1 = random.randint(hero.attack // 2, hero.attack)
            damage2 = random.randint(hero.attack // 2, hero.attack)
            total_damage = damage1 + damage2
            result = target.take_damage(total_damage)
            return f"{hero.name} быстро атакует дважды! Наносит {total_damage} урона!\n{result}"
        else:
            damage = random.randint(hero.attack, int(hero.attack * 1.3))
            result = target.take_damage(damage)
            return f"{hero.name} молниеносно атакует! Наносит {damage} урона.\n{result}"

    @staticmethod
    def _slow_action(target, chance, base_text, hero):
        if chance < 0.4:
            damage = random.randint(int(hero.attack * 1.5), hero.attack * 2)
            result = target.take_damage(damage)
            return f"{hero.name} медленно, но мощно атакует! Наносит {damage} урона.\n{result}"
        else:
            return f"{hero.name} медленно готовится к атаке..."

    @staticmethod
    def _creative_action(target, chance, base_text, hero):
        creative_attacks = [
            f"{hero.name} использует неожиданную тактику!",
            f"{hero.name} импровизирует в бою!",
            f"{hero.name} применяет творческий подход!"
        ]
        
        if chance < 0.7:
            damage = random.randint(hero.attack, int(hero.attack * 1.8))
            result = target.take_damage(damage)
            attack_text = random.choice(creative_attacks)
            return f"{attack_text} Наносит {damage} урона.\n{result}"
        else:
            return random.choice(creative_attacks)

    @staticmethod
    def _practical_action(target, chance, base_text, hero):
        if chance < 0.9:
            damage = random.randint(int(hero.attack * 0.8), int(hero.attack * 1.2))
            result = target.take_damage(damage)
            return f"{hero.name} атакует практично и эффективно. Наносит {damage} урона.\n{result}"
        else:
            return f"{hero.name} оценивает ситуацию для оптимальной атаки."

    @staticmethod
    def _default_action(target, base_text, hero):
        damage = random.randint(hero.attack // 2, hero.attack)
        result = target.take_damage(damage)
        return f"{base_text} {damage} урона.\n{result}"