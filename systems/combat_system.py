# systems.combat_system.py
import random
import time
from systems.hero_system import Hero
from systems.party_system import PartySystem
from systems.difficulty_system import DifficultySystem
from systems.combat_modifiers import COMBAT_MODIFIERS
from game_data.monsters_data import MONSTER_BASE_STATS, BOSS_STATS, MONSTER_SPAWN_CHANCES, MONSTER_COUNT_BY_FLOOR
from game_data.bosses_data import BOSS_ABILITIES
from app import app

class Monster:
    def __init__(self, name, level, monster_type="normal"):
        self.name = name
        self.level = level
        self.monster_type = monster_type
        self._calculate_stats()
        self.health_current = self.health_max
        self.is_alive = True
        self.monster_id = f"{name}_{level}_{random.randint(1000,9999)}"

    def _calculate_stats(self):
        """Рассчитывает статы на основе типа и уровня"""
        if self.monster_type == "boss" and self.name in BOSS_STATS:
            boss_data = BOSS_STATS[self.name]
            base_stats = MONSTER_BASE_STATS.get("Орк", {})
            
            self.health_max = int((base_stats.get("health_per_level", 10) * self.level) * boss_data["health_multiplier"])
            self.attack = int((base_stats.get("attack_per_level", 3) * self.level) * boss_data["attack_multiplier"])
            self.defense = int((base_stats.get("defense_per_level", 1) * self.level) * boss_data["defense_multiplier"])
            # УВЕЛИЧИМ: опыт для боссов
            self.exp_value = int(500 * (self.level ** 0.8) * boss_data["exp_multiplier"])
        else:
            monster_data = MONSTER_BASE_STATS.get(self.name, {})
            self.health_max = monster_data.get("health_per_level", 8) * self.level
            self.attack = monster_data.get("attack_per_level", 2) * self.level
            self.defense = monster_data.get("defense_per_level", 1) * self.level
            # УВЕЛИЧИМ: опыт для обычных монстров
            self.exp_value = int(100 * (self.level ** 0.7))

    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health_current -= actual_damage
        
        if self.health_current <= 0:
            self.is_alive = False
            return f"{self.name} повержен!"
        
        return f"{self.name} получает {actual_damage} урона. Осталось {self.health_current} HP."

    def attack_target(self, target: Hero):
        damage_dealt = random.randint(self.attack // 2, self.attack)
        result = target.take_damage(damage_dealt)
        time.sleep(0.3)
        return result

    def use_special_ability(self, heroes):
        """Использование специальной способности (для боссов)"""
        if self.monster_type != "boss" or self.name not in BOSS_ABILITIES:
            return None
            
        abilities = BOSS_ABILITIES[self.name]
        for ability_name, ability_data in abilities.items():
            if random.random() < ability_data["chance"]:
                return self._execute_ability(ability_name, ability_data, heroes)
        return None

    def _execute_ability(self, ability_name, ability_data, heroes):
        """Выполняет специальную способность"""
        if ability_name == "Огненное дыхание":
            damage = int(self.attack * ability_data["damage_multiplier"])
            results = []
            for hero in heroes:
                if hero.is_alive:
                    result = hero.take_damage(damage // 2)  # полный урон по всем
                    results.append(f"{hero.name}: {result}")
            return f"{self.name} использует {ability_name}!\n" + "\n".join(results)
        
        return f"{self.name} использует {ability_name}!"

    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'monster_type': self.monster_type,
            'health_max': self.health_max,
            'health_current': self.health_current,
            'attack': self.attack,
            'defense': self.defense,
            'is_alive': self.is_alive,
            'monster_id': self.monster_id
        }

    @classmethod
    def from_dict(cls, data):
        monster = cls(data['name'], data['level'], data.get('monster_type', 'normal'))
        monster.health_max = data['health_max']
        monster.health_current = data['health_current']
        monster.attack = data['attack']
        monster.defense = data['defense']
        monster.is_alive = data['is_alive']
        return monster

class Combat:
    def __init__(self, hero_party, tower_level, game_state):
        self.heroes = hero_party
        self.tower_level = tower_level
        self.game_state = game_state
        self.monsters = self._get_or_generate_monsters()
        self.combat_log = []
        self.total_exp_earned = 0
        self.modifiers = self._load_combat_modifiers(tower_level)

    def _load_combat_modifiers(self, floor_level):
        """Загружает модификаторы боя для этажа"""
        modifiers = []
        
        # Погодные модификаторы (случайная погода на каждом этаже)
        weather_chances = {
            "ясно": 40,      # 40% chance
            "облачно": 25,   # 25% chance  
            "дождь": 10,     # 10% chance
            "гроза": 5,      # 5% chance
            "туман": 8,      # 8% chance
            "снег": 5,       # 5% chance
            "ветер": 4,      # 4% chance
            "жара": 3        # 3% chance
        }
        
        weather_type = self._choose_random(weather_chances)
        modifiers.append(COMBAT_MODIFIERS["weather"](weather_type))
        
        # Ловушки (случайные на любом этаже, кроме 1-го)
        if floor_level > 1:
            trap_chances = {
                "none": 60,              # 60% без ловушки
                "огненная_ловушка": 15,  # 15% chance
                "ледяная_ловушка": 10,   # 10% chance
                "ядовитая_ловушка": 8,   # 8% chance
                "электрическая_ловушка": 7  # 7% chance
            }
            
            trap_type = self._choose_random(trap_chances)
            if trap_type != "none":
                modifiers.append(COMBAT_MODIFIERS["trap"](trap_type))
        
        return modifiers

    def _choose_random(self, chances_dict):
        """Выбирает случайный вариант на основе шансов"""
        total = sum(chances_dict.values())
        r = random.randint(1, total)
        current = 0
        for item, chance in chances_dict.items():
            current += chance
            if r <= current:
                return item
        return list(chances_dict.keys())[0]

    def _get_or_generate_monsters(self):
        if self.tower_level in self.game_state["tower_monsters"]:
            monsters_data = self.game_state["tower_monsters"][self.tower_level]
            return [Monster.from_dict(data) for data in monsters_data]
        else:
            monsters = self._generate_monsters()
            self.game_state["tower_monsters"][self.tower_level] = [m.to_dict() for m in monsters]
            return monsters

    def _generate_monsters(self):
        """Генерация сбалансированной группы монстров"""
        if self.tower_level % 5 == 0:
            # Босс-этаж
            boss_names = [name for name, data in BOSS_STATS.items() if self.tower_level >= data["min_level"]]
            if not boss_names:
                boss_names = list(BOSS_STATS.keys())
            boss_name = random.choice(boss_names)
            boss_level = self.tower_level + 2
            return [Monster(boss_name, boss_level, "boss")]
        
        else:
            # Обычный этаж
            min_count, max_count = MONSTER_COUNT_BY_FLOOR.get(self.tower_level, (1, 3))
            monster_count = random.randint(min_count, max_count)
            
            # Выбираем типы монстров для этого этажа
            floor_chances = {}
            for floor, chances in MONSTER_SPAWN_CHANCES.items():
                if self.tower_level <= floor:
                    floor_chances = chances
                    break
            else:
                floor_chances = MONSTER_SPAWN_CHANCES[max(MONSTER_SPAWN_CHANCES.keys())]
            
            monsters = []
            for _ in range(monster_count):
                monster_type = self._choose_monster_type(floor_chances)
                level = max(1, self.tower_level + random.randint(-1, 1))
                monsters.append(Monster(monster_type, level))
            
            return monsters

    def _choose_monster_type(self, chances_dict):
        total = sum(chances_dict.values())
        r = random.randint(1, total)
        current = 0
        for monster_type, chance in chances_dict.items():
            current += chance
            if r <= current:
                return monster_type
        return list(chances_dict.keys())[0]

    def start_combat(self):
        """Начинаем сбалансированный бой"""
        battle_intro = [
            "=" * 50,
            f"БАШНЯ ИСПЫТАНИЙ - ЭТАЖ {self.tower_level}",
            "=" * 50
        ]
        
        # Показываем силы сторон
        hero_power = sum(h.attack + h.defense for h in self.heroes if h.is_alive)
        monster_power = sum(m.attack + m.defense for m in self.monsters if m.is_alive)
        
        difficulty, color = DifficultySystem.calculate_difficulty(hero_power, monster_power)
        difficulty_display = f"{color} Сложность: {difficulty.upper()}"

        battle_intro.extend([
            f"Сила отряда: {hero_power}",
            f"Сила монстров: {monster_power}",
            "=" * 50
        ])
        
        for monster in self.monsters:
            battle_intro.append(f"- {monster.name} (Ур. {monster.level}) | ❤️{monster.health_max} ⚔️{monster.attack} 🛡️{monster.defense}")
        
        # Добавляем вводную часть в лог
        self.combat_log.extend(battle_intro)
        
        # Показываем вводную информацию
        for line in battle_intro:
            print(line)
        
        time.sleep(1.5)  # Пауза перед началом боя
        
        round_number = 1
        
        while any(h.is_alive for h in self.heroes) and any(m.is_alive for m in self.monsters):
            round_header = f"\n--- РАУНД {round_number} ---"
            print(round_header)
            self.combat_log.append(round_header)
            time.sleep(0.6)  # Комфортная пауза
            
            # Ход героев
            for hero in self.heroes:
                if hero.is_alive and any(m.is_alive for m in self.monsters):
                    alive_monsters = [m for m in self.monsters if m.is_alive]
                    target = random.choice(alive_monsters)
                    action_text = hero.decide_action(target)
                    print(action_text)
                    self.combat_log.append(action_text)
                    if hasattr(self, 'weather_modifier'):
                        # Применяем эффекты погоды к атаке
                        pass  # Реализуйте вызов weather_modifier.apply_weather_effect()

                    if hasattr(self, 'trap_modifier'):
                        # Проверяем активацию ловушки
                        trap_result = self.trap_modifier.trigger_trap(target)
                        if trap_result:
                            print(trap_result)
                            self.combat_log.append(trap_result)
                    
                    # Проверяем, был ли монстр убит и начисляем опыт
                    if not target.is_alive:
                        self.total_exp_earned += target.exp_value
                        kill_message = f"{target.name} повержен! +{target.exp_value} опыта"
                        print(kill_message)
                        self.combat_log.append(kill_message)
                    
                    time.sleep(0.6)  # Комфортная пауза между действиями
            
            if not any(m.is_alive for m in self.monsters):
                break
                
            # Ход монстров
            for monster in self.monsters:
                if monster.is_alive and any(h.is_alive for h in self.heroes):
                    # Боссы могут использовать способности
                    if monster.monster_type == "boss" and random.random() < 0.3:
                        ability_result = monster.use_special_ability(self.heroes)
                        if ability_result:
                            print(ability_result)
                            self.combat_log.append(ability_result)
                            time.sleep(0.8)  # Немного дольше для способностей
                            continue
                    
                    alive_heroes = [h for h in self.heroes if h.is_alive]
                    if alive_heroes:
                        target = random.choice(alive_heroes)
                        attack_message = f"{monster.name} атакует {target.name}!"
                        print(attack_message)
                        self.combat_log.append(attack_message)
                        time.sleep(0.4)
                        
                        result = monster.attack_target(target)
                        print(result)
                        self.combat_log.append(result)
                        time.sleep(0.6)

            round_number += 1
            if round_number > 15:
                timeout_message = "Бой затянулся! Обе стороны истощены..."
                print(timeout_message)
                self.combat_log.append(timeout_message)
                break

        victory = any(h.is_alive for h in self.heroes)
        
        # ВАЖНО: Распределяем опыт между выжившими героями ПЕРЕД выдачей наград
        if victory and self.total_exp_earned > 0:
            living_heroes = [h for h in self.heroes if h.is_alive]
            if living_heroes:
                exp_per_hero = self.total_exp_earned // len(living_heroes)
                exp_remainder = self.total_exp_earned % len(living_heroes)
                
                for i, hero in enumerate(living_heroes):
                    # Даем остаток опыта первому герою
                    hero_exp = exp_per_hero + (1 if i == 0 and exp_remainder > 0 else 0)
                    hero.add_experience(hero_exp)  # Просто начисляем без вывода
        
        # Выдаем награды только при победе
        if victory:
            self._give_victory_rewards()
            
        # Очищаем группы от мертвых героев
        PartySystem(self.game_state).cleanup_dead_heroes()
        
        # ДОБАВИТЬ ПРОВЕРКУ - очищаем мертвых героев с ролей, если система ролей инициализирована
        if self.game_state.get("role_system") is not None:
            self.game_state["role_system"].cleanup_dead_heroes()
        
        # Сохранение
        self.game_state["save_system"].save_game(self.game_state)
        
        # Асинхронное сохранение
        import threading
        def async_save():
            # ИСПРАВЛЕНИЕ: используем self.game_state вместо save_data
            self.game_state["save_system"].save_game(self.game_state)
        
        thread = threading.Thread(target=async_save)
        thread.daemon = True
        thread.start()

        # Добавляем результат боя в лог
        result_message = "\n🎉 ПОБЕДА!" if victory else "\n💥 ПОРАЖЕНИЕ"
        print(result_message)
        self.combat_log.append(result_message)
        
        self.game_state["tower_monsters"][self.tower_level] = [m.to_dict() for m in self.monsters]
        
        # ДОБАВЛЕНО: Пауза для просмотра результатов боя
        print("\n" + "="*50)
        print("Бой завершен. Нажмите Enter чтобы продолжить...")
        input()
        
        return victory, self.combat_log, self.total_exp_earned

    def cleanup_party_system(self):
        """Очищает систему групп от мертвых героев после боя"""
        if "party_system" in self.game_state:
            from systems.party_system import PartySystem
            party_system = PartySystem(self.game_state)
            party_system.cleanup_dead_heroes()

    def _give_victory_rewards(self):
        """Выдает награды за победу на этаже"""
        from game_data.tower_rewards import get_floor_rewards, generate_item_rewards
        
        rewards = get_floor_rewards(self.tower_level)
        wallet = self.game_state["wallet"]
        storage = self.game_state["storage"]
        
        # Добавляем золото и кристаллы
        wallet.add_gold(rewards["gold"])
        wallet.add_crystals(rewards.get("crystals", 0))
        
        # Генерируем и добавляем предметы
        item_rewards = {}
        if "items" in rewards:
            generated_items = generate_item_rewards(rewards["items"])
            for item_id, quantity in generated_items.items():
                item = self.game_state["item_manager"].create_item(item_id, quantity)
                if item and storage.add_item(item):
                    item_rewards[item_id] = quantity
        
        # Сохраняем информацию о полученных наградах для показа
        self.victory_rewards = {
            "gold": rewards["gold"],
            "crystals": rewards.get("crystals", 0),
            "items": item_rewards
        }