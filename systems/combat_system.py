# systems.combat_system.py
import random
import time
from typing import List, Dict
from systems.hero_system import Hero
from systems.party_system import PartySystem
from systems.difficulty_system import DifficultySystem
from game_data.monsters_data import MONSTER_BASE_STATS, MONSTER_SPAWN_CHANCES, MONSTER_COUNT_BY_FLOOR
from game_data.bosses_data import BOSS_STATS
from game_data.stats_base import StatsBase
from systems.combat_modifiers.locations import location_manager
from systems.combat_modifiers.weather import weather_system
from systems.combat_modifiers.traps import trap_system
from systems.combat_modifiers.status_effects import StatusEffectSystem
from systems.combat_modifiers.skills.boss_skills import BOSS_SKILLS

"""
Боевая система с локациями, погодой и ловушками.
Сохранен оригинальный пошаговый визуал боя.
"""


class Monster(StatsBase):
    def __init__(self, name, level, monster_type="normal"):
        super().__init__()
        self.name = name
        self.level = level
        self.monster_type = monster_type
        self.is_alive = True
        self.monster_id = f"{name}_{level}_{random.randint(1000,9999)}"
        self.monster_class = self._get_monster_class(name)
        
        # НОВОЕ: Система навыков для монстров
        self.skill_system = None
        if monster_type == "boss" and self.name in BOSS_SKILLS:
            from systems.combat_modifiers.skills.skill_system import SkillSystem
            self.skill_system = SkillSystem()
            for skill in BOSS_SKILLS[self.name]:
                self.skill_system.add_skill(skill)
        
        self._calculate_base_stats()
        self.calculate_derived_stats(self.level)
        self.status_system = StatusEffectSystem(self)
    
    def _get_monster_class(self, monster_type: str) -> str:
        """Определяет класс монстра на основе типа"""
        class_map = {
            "Гоблин": "warrior",
            "Скелет": "warrior", 
            "Орк": "warrior",
            "Паук": "beast",
            "Волк": "beast",
            "Древний Дракон": "dragon",
            "Повелитель Теней": "shadow",
            "Король Лич": "undead"
        }
        return class_map.get(monster_type, "warrior")
    
    def _calculate_base_stats(self):
        """Рассчитывает базовые характеристики на основе типа и уровня"""
        if self.monster_type == "boss" and self.name in BOSS_STATS:
            # Боссы - используем данные из bosses_data.py
            boss_data = BOSS_STATS[self.name]
            base_stats = boss_data["base_stats"]
            growth = boss_data["growth_per_level"]
            
            # Рассчитываем характеристики с учетом уровня
            self.strength = base_stats["strength"] + (growth["strength"] * (self.level - 1))
            self.dexterity = base_stats["dexterity"] + (growth["dexterity"] * (self.level - 1))
            self.constitution = base_stats["constitution"] + (growth["constitution"] * (self.level - 1))
            self.intelligence = base_stats["intelligence"] + (growth["intelligence"] * (self.level - 1))
            
            # Опыт за босса
            self.exp_value = int(100 * (self.level ** 0.7) * boss_data.get("exp_multiplier", 1.0))
        else:
            # Обычные монстры - используем данные из monsters_data.py
            monster_data = MONSTER_BASE_STATS.get(self.name, {})
            base_stats = monster_data.get("base_stats", {"strength": 8, "dexterity": 8, "constitution": 8, "intelligence": 8})
            growth = monster_data.get("growth_per_level", {"strength": 1.0, "dexterity": 1.0, "constitution": 1.0, "intelligence": 1.0})
            
            # Рассчитываем характеристики с учетом уровня
            self.strength = base_stats["strength"] + (growth["strength"] * (self.level - 1))
            self.dexterity = base_stats["dexterity"] + (growth["dexterity"] * (self.level - 1))
            self.constitution = base_stats["constitution"] + (growth["constitution"] * (self.level - 1))
            self.intelligence = base_stats["intelligence"] + (growth["intelligence"] * (self.level - 1))
            
            # Опыт за обычного монстра
            self.exp_value = int(100 * (self.level ** 0.7))

    def take_damage(self, damage, damage_type: str = ""):
        # Модифицируем урон статус-эффектами
        if hasattr(self, 'status_system'):
            damage = self.status_system.modify_damage(damage, damage_type)
        
        actual_damage = max(1, damage - self.defense)  # self.defense теперь из StatsBase
        blocked_damage = damage - actual_damage
        
        self.health_current -= actual_damage
        
        # Форматируем сообщение как ты хочешь
        if self.health_current <= 0:
            self.is_alive = False
            message = f"{self.name} повержен!"
            return message
        else:
            message = f"{self.name} получает {actual_damage} урона"
            if blocked_damage > 0:
                message += f" (заблокировано {blocked_damage})"
            message += f". Осталось {self.health_current} HP."
        
        return message

    def attack_target(self, target: Hero):
        damage_dealt = random.randint(self.attack // 2, self.attack)
        
        # НОВОЕ: Модифицируем урон статус-эффектами атакующего
        if hasattr(self, 'status_system'):
            damage_dealt = self.status_system.modify_damage(damage_dealt)
        
        result = target.take_damage(damage_dealt) 
        return result

    def use_special_ability(self, heroes):
        """Использование специальной способности (для боссов)"""
        if not self.skill_system:
            return None
        
        available_skills = self.skill_system.get_available_skills(self)
        if not available_skills:
            return None
        
        # Выбираем случайный доступный навык
        skill = random.choice(available_skills)
        result = skill.use(self, heroes)
        
        return result.get("message") if result else None

    def _execute_ability(self, ability_name, ability_data, heroes):
        """Выполняет специальную способность, используя новую систему навыков"""
        # Используем функцию из BOSS_SKILLS если она есть
        if ability_name in BOSS_SKILLS:
            return BOSS_SKILLS[ability_name](self, heroes, ability_data)
        
        # Если навыка нет в словаре, используем старую логику (для обратной совместимости)
        if ability_name == "Огненное дыхание":
            damage = int(self.attack * ability_data["damage_multiplier"])
            results = []
            for hero in heroes:
                if hero.is_alive:
                    result = hero.take_damage(damage // 2, "огненный")
                    results.append(f"{hero.name}: {result}")
            return f"{self.name} использует {ability_name}!\n" + "\n".join(results)
        
        return f"{self.name} использует {ability_name}!"

    def process_status_effects(self):
        """Обрабатывает статус-эффекты в начале хода"""
        if hasattr(self, 'status_system'):
            return self.status_system.process_turn_start()
        return []

    def can_act(self):
        """Может ли монстр действовать (не оглушен/заморожен)"""
        if hasattr(self, 'status_system'):
            return self.status_system.can_act()
        return True

    def to_dict(self):
        data = super().to_dict()  # Берем данные из StatsBase
        data.update({
            'name': self.name,
            'level': self.level,
            'monster_type': self.monster_type,
            'is_alive': self.is_alive,
            'monster_id': self.monster_id,
            'monster_class': self.monster_class,
            'exp_value': self.exp_value
        })
        return data
    
    @classmethod
    def from_dict(cls, data):
        monster = cls(data['name'], data['level'], data.get('monster_type', 'normal'))
        # Загружаем характеристики из StatsBase
        monster.from_dict(data)
        
        # Восстанавливаем дополнительные поля
        monster.is_alive = data['is_alive']
        monster.monster_class = data.get('monster_class', 'warrior')
        monster.exp_value = data.get('exp_value', 0)
        
        # Восстанавливаем статус-эффекты если есть
        if 'status_effects' in data and hasattr(monster, 'status_system'):
            monster.status_system.load_effects(data['status_effects'])
        
        return monster

class Combat:
    def __init__(self, hero_party, tower_level, game_state):
        self.heroes = hero_party
        self.tower_level = tower_level
        self.game_state = game_state
        
        # НОВОЕ: Создаем окружение для боя
        from systems.combat_modifiers.combat_environment import CombatEnvironment
        self.environment = CombatEnvironment()
        env_data = self.environment.generate_for_floor(tower_level)
        
        self.location = env_data["location"]
        self.weather = env_data["weather"]
        self.traps = env_data["traps"]
        
        self.monsters = self._get_or_generate_monsters()
        self.combat_log = []
        self.total_exp_earned = 0

    def _get_or_generate_monsters(self):
        if self.tower_level in self.game_state["tower_monsters"]:
            monsters_data = self.game_state["tower_monsters"][self.tower_level]
            return [Monster.from_dict(data) for data in monsters_data]
        else:
            monsters = self._generate_monsters_for_location()
            self.game_state["tower_monsters"][self.tower_level] = [m.to_dict() for m in monsters]
            return monsters

    def _generate_monsters_for_location(self):
        """Генерация монстров с учетом локации"""
        if self.tower_level % 5 == 0:
            # Босс-этаж
            boss_names = [name for name, data in BOSS_STATS.items() if self.tower_level >= data["min_level"]]
            if not boss_names:
                boss_names = list(BOSS_STATS.keys())
            boss_name = random.choice(boss_names)
            boss_level = self.tower_level + 2
            return [Monster(boss_name, boss_level, "boss")]
        
        else:
            # Обычный этаж - используем пул монстров локации
            location_monster_pool = self.location.base_monster_pool
            
            if not location_monster_pool:
                # Если у локации нет пула, используем общий
                floor_chances = {}
                for floor, chances in MONSTER_SPAWN_CHANCES.items():
                    if self.tower_level <= floor:
                        floor_chances = chances
                        break
                else:
                    floor_chances = MONSTER_SPAWN_CHANCES[max(MONSTER_SPAWN_CHANCES.keys())]
                location_monster_pool = list(floor_chances.keys())
            
            min_count, max_count = MONSTER_COUNT_BY_FLOOR.get(self.tower_level, (1, 3))
            monster_count = random.randint(min_count, max_count)
            
            monsters = []
            for _ in range(monster_count):
                monster_type = random.choice(location_monster_pool)
                level = max(1, self.tower_level + random.randint(-1, 1))
                monsters.append(Monster(monster_type, level))
            
            return monsters

    def start_combat(self):
        """Начинаем сбалансированный бой - ОРИГИНАЛЬНЫЙ ВИЗУАЛ"""
        from ui.combat_ui import (
            show_combat_intro, show_location_and_weather, show_enemies_info,
            show_traps_info, show_round_start, show_hero_action, show_monster_action,
            show_trap_activation, show_weather_effect, show_status_effect,
            show_kill_message, show_combat_timeout, show_damage_message,
            show_turn_divider
        )
        
        # НОВОЕ: Показываем вступление к бою
        show_combat_intro(self.heroes, self.monsters, self.tower_level)
        
        # НОВОЕ: Показываем локацию и погоду
        show_location_and_weather(
            self.location.name, self.location.description,
            self.weather.name, self.weather.description, 
            self.weather.is_dangerous
        )
        
        # НОВОЕ: Показываем информацию о монстрах
        show_enemies_info(self.monsters)
        
        # НОВОЕ: Показываем ловушки
        show_traps_info(self.traps)
        
        round_number = 1
        
        while any(h.is_alive for h in self.heroes) and any(m.is_alive for m in self.monsters):
            # Показываем начало раунда. ИСПРАВЛЕНО: Теперь передаем все три аргумента
            show_round_start(round_number, self.heroes, self.monsters)
            
            # Показываем разделитель хода героев
            show_turn_divider("heroes")
            
            # НОВОЕ: Применяем погодные эффекты в начале раунда
            weather_messages = weather_system.apply_weather_effects(self.heroes, self.monsters)
            for msg in weather_messages:
                show_weather_effect(msg)
            
            # НОВОЕ: Обрабатываем статус-эффекты у всех
            for hero in self.heroes:
                if hero.is_alive and hasattr(hero, 'status_system'):
                    hero_messages = hero.status_system.process_turn_start()
                    for msg in hero_messages:
                        show_status_effect(f"{hero.name}: {msg}")
            
            for monster in self.monsters:
                if monster.is_alive and hasattr(monster, 'status_system'):
                    monster_messages = monster.process_status_effects()
                    for msg in monster_messages:
                        show_status_effect(f"{monster.name}: {msg}")
            
            # Ход героев
            for hero in self.heroes:
                if hero.is_alive and any(m.is_alive for m in self.monsters):
                    # Проверяем ловушки перед действием
                    trap_messages = trap_system.check_trap_trigger(hero)
                    for msg in trap_messages:
                        show_trap_activation(msg)
                        self.combat_log.append(msg)
                    
                    # Если герой не может действовать из-за эффектов
                    if hasattr(hero, 'status_system') and not hero.status_system.can_act():
                        msg = f"{hero.name} не может действовать из-за эффектов!"
                        print(msg)
                        self.combat_log.append(msg)
                        time.sleep(0.6)
                        continue
                    
                    alive_monsters = [m for m in self.monsters if m.is_alive]
                    target = random.choice(alive_monsters)
                    action_text = hero.decide_action(target)
                    
                    # Разделяем на строки
                    lines = action_text.split('\n')
                    if lines:
                        # Первая строка - описание действия
                        show_hero_action(hero, lines[0])
                        self.combat_log.append(f"{hero.name}: {lines[0]}")
                        
                        # Если есть вторая строка (результат урона)
                        if len(lines) > 1 and lines[1].strip():
                            # Определяем, сильный ли это урон (пока не знаем, передаем False)
                            show_damage_message(lines[1], is_heavy_damage=False)
                            self.combat_log.append(f"({lines[1]})")
                    
                    # Проверяем ловушки после действия
                    trap_messages = trap_system.check_trap_trigger(target)
                    for msg in trap_messages:
                        show_trap_activation(msg)
                        self.combat_log.append(msg)
                    
                    # Проверяем, был ли монстр убит
                    if not target.is_alive:
                        self.total_exp_earned += target.exp_value
                        kill_msg = f"{target.name} повержен! +{target.exp_value} опыта"
                        show_kill_message(target, target.exp_value)
                        self.combat_log.append(kill_msg)
                    
                    time.sleep(0.6)
            
            # Проверяем, остались ли монстры
            if not any(m.is_alive for m in self.monsters):
                break
                
            # Показываем разделитель хода монстров
            show_turn_divider("monsters")
            
            # Ход монстров
            for monster in self.monsters:
                if monster.is_alive and any(h.is_alive for h in self.heroes):
                    # Проверяем ловушки перед действием
                    trap_messages = trap_system.check_trap_trigger(monster)
                    for msg in trap_messages:
                        show_trap_activation(msg)
                        self.combat_log.append(msg)
                    
                    # Если монстр не может действовать из-за эффектов
                    if not monster.can_act():
                        msg = f"{monster.name} не может действовать из-за эффектов!"
                        print(msg)
                        self.combat_log.append(msg)
                        time.sleep(0.6)
                        continue
                    
                    # Боссы могут использовать способности
                    if monster.monster_type == "boss" and random.random() < 0.3:
                        ability_result = monster.use_special_ability(self.heroes)
                        if ability_result:
                            from ui.color_utils import colorize_skill_message  # Добавляем импорт
                            colored_message = colorize_skill_message(ability_result)
                            print(colored_message)
                            self.combat_log.append(ability_result)
                            time.sleep(0.8)
                            continue
                    
                    alive_heroes = [h for h in self.heroes if h.is_alive]
                    if alive_heroes:
                        target = random.choice(alive_heroes)
                        attack_message = f"{monster.name} атакует {target.name} и наносит {monster.attack} урона!"
                        
                        # Показываем действие монстра
                        show_monster_action(monster, attack_message)
                        self.combat_log.append(attack_message)
                        time.sleep(0.4)
                        
                        # Атака и показ урона
                        damage_result = target.take_damage(monster.attack)

                        # Если это кортеж - берем только первый элемент (строку)
                        if isinstance(damage_result, tuple):
                            result = damage_result[0]  # Берем только строку
                            # Определяем сильный ли урон (более 50% от максимального HP)
                            is_heavy = monster.attack >= (target.health_max * 0.5) if hasattr(target, 'health_max') else False
                        else:
                            result = damage_result
                            is_heavy = False

                        show_damage_message(result, is_heavy_damage=is_heavy)
                        self.combat_log.append(f"({result})")
                        time.sleep(0.6)

            round_number += 1
            if round_number > 15:
                timeout_message = "Бой затянулся! Обе стороны истощены..."
                show_combat_timeout()
                self.combat_log.append(timeout_message)
                break

        victory = any(h.is_alive for h in self.heroes)
        
        # НЕ показываем повышение уровня здесь - только в наградах!
        
        # Очищаем после боя
        self._cleanup_after_combat()
        
        # Сохраняем состояние
        self.game_state["tower_monsters"][self.tower_level] = [m.to_dict() for m in self.monsters]
        
        return victory, self.combat_log, self.total_exp_earned

    def _cleanup_after_combat(self):
        """Очистка после боя"""
        # Очищаем группы от мертвых героев
        PartySystem(self.game_state).cleanup_dead_heroes()
        
        # Очищаем мертвых героев с ролей
        if self.game_state.get("role_system"):
            self.game_state["role_system"].cleanup_dead_heroes()
        
        # НОВОЕ: Очищаем окружение боя
        self.environment.clear()