# systems.tower_system.py
import random
from systems.hero_system import Hero
from systems.combat_system import Combat, Monster
from systems.party_system import PartySystem
from game_data.monsters_data import MONSTER_SPAWN_CHANCES
from game_data.tower_rewards import get_floor_rewards, generate_item_rewards
from ui.tower_ui import (
    show_tower_management_menu, show_party_selection, show_expedition_preview,
    show_tower_progress, show_healing_confirmation,
    show_tower_rewards, show_tower_defeat
)
from ui.combat_ui import (
    show_combat_intro,  # ← ТОЛЬКО функции боя
    show_location_and_weather, show_traps_info, show_combat_result
)
from ui.ui_utils import loading_screen, press_enter_to_continue, clear_screen

# Импортируем новые системы
from systems.combat_modifiers.locations import location_manager
from systems.combat_modifiers.weather import weather_system
from systems.combat_modifiers.traps import trap_system

"""
Система башни - отправка отрядов, управление этажами.
Использует новую боевую систему с локациями, погодой и ловушками.
"""

def choose_parties_for_floor(game_state, required_groups=1):
    party_system = PartySystem(game_state)
    available_parties = list(party_system.parties.items())

    while True:
        choice = show_party_selection(available_parties, required_groups, game_state) 

        if choice in ("0", "b", "B"):
            return None, None

        try:
            chosen_ids = [int(x) for x in choice.split(",") if x.strip().isdigit()]
        except ValueError:
            print("❌ Ошибка ввода!")
            press_enter_to_continue()
            continue

        if len(chosen_ids) != required_groups:
            print(f"❌ Нужно выбрать ровно {required_groups} группы!")
            press_enter_to_continue()
            continue

        chosen_parties = []
        chosen_party_ids = []
        for idx in chosen_ids:
            if 1 <= idx <= len(available_parties):
                pid, pdata = available_parties[idx - 1]
                chosen_parties.append(pdata)
                chosen_party_ids.append(pid)
            else:
                print("❌ Неверный номер группы!")
                break
        else:
            return chosen_parties, chosen_party_ids

def send_to_tower(game_state):
    """
    Основная функция отправки отряда в башню.
    Использует новую боевую систему с локациями, погодой и ловушками.
    """
    current_floor = game_state["tower_level"]
    required_groups = 2 if current_floor % 10 == 0 else 1

    # Выбираем группы
    selected_parties, selected_party_ids = choose_parties_for_floor(game_state, required_groups)
    if selected_parties is None:
        return

    # Собираем всех героев из выбранных групп
    active_party_heroes = []
    for party_id in selected_party_ids:
        heroes = PartySystem(game_state).get_party_heroes(party_id)
        active_party_heroes.extend(heroes)

    if not active_party_heroes:
        print("❌ В выбранных группах нет героев!")
        press_enter_to_continue()
        return

    # Показываем предварительный просмотр
    choice = show_expedition_preview(active_party_heroes, current_floor)
    if choice is None or choice == 0:
        return
    
    loading_screen(2, "Подготовка отряда")
    
    # Создаем объект боя с новой системой
    combat = Combat(active_party_heroes, current_floor, game_state)
    
    # Запускаем бой (теперь пошаговый)
    victory, log, total_exp = combat.start_combat()
    
    # ШАГ 1: Показываем результат боя (только "ПОБЕДА!" или "ПОРАЖЕНИЕ") и ждем нажатия Enter
    show_combat_result(victory)
    
    # ШАГ 2: Очищаем экран
    clear_screen()
    
    # Определяем живых и мертвых героев ПОСЛЕ боя
    dead_heroes = [h for h in active_party_heroes if not h.is_alive]
    living_heroes = [h for h in active_party_heroes if h.is_alive]
    
    if victory:
        # Получаем награды за этаж из tower_rewards.py
        floor_rewards = get_floor_rewards(current_floor)
        
        # Генерируем конкретные количества предметов
        item_rewards = {}
        if "items" in floor_rewards:
            item_rewards = generate_item_rewards(floor_rewards["items"])
        
        # Формируем полные награды
        rewards = {
            'gold': floor_rewards['gold'],
            'crystals': floor_rewards.get('crystals', 0),
            'items': item_rewards
        }
        
        # Распределяем опыт между выжившими героями
        level_up_messages = []
        if living_heroes and total_exp > 0:
            exp_per_hero = total_exp // len(living_heroes)
            exp_remainder = total_exp % len(living_heroes)
            
            for i, hero in enumerate(living_heroes):
                # Даем остаток опыта первому герою
                hero_exp = exp_per_hero + (1 if i == 0 and exp_remainder > 0 else 0)
                
                # Сохраняем текущий уровень
                old_level = hero.level
                
                # Добавляем опыт
                result_message = hero.add_experience(hero_exp)
                
                # Запоминаем, если герой повысил уровень
                if hero.level > old_level:
                    level_up_messages.append(f"{hero.name} повысил уровень до {hero.level}!")
        
        # Обновляем состав групп
        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]

        # Повышаем этаж только если была победа
        new_floor = current_floor + 1
        game_state["tower_level"] = new_floor
        
        # Обновляем максимальный этаж
        if new_floor > game_state.get("max_tower_floor", 1):
            game_state["max_tower_floor"] = new_floor
        
        # ШАГ 3: Показываем награды башни (отдельный экран)
        show_tower_rewards(
            rewards=rewards,
            total_exp=total_exp,
            new_floor=new_floor,
            dead_heroes=dead_heroes,
            game_state=game_state,
            heroes=active_party_heroes
        )
        
    else:
        # Поражение - отступаем на этаж ниже
        game_state["tower_level"] = max(1, current_floor - 1)
        
        # ВАЖНО: Удаляем монстров с текущего этажа (проигранного), чтобы при следующей попытке они сгенерировались заново
        if current_floor in game_state["tower_monsters"]:
            del game_state["tower_monsters"][current_floor]
        
        # Обновляем состав групп
        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]
        
        # ШАГ 3: Показываем поражение в башне (отдельный экран)
        show_tower_defeat(dead_heroes, game_state["tower_level"])
    
    # Сохраняем окончательное состояние
    game_state["save_system"].save_game(game_state)
    
    return victory

def show_floor_monster_info(floor_level):
    """Получить информацию о монстрах на указанном этаже"""
    from game_data.monsters_data import MONSTER_BASE_STATS, BOSS_STATS
    
    info = f"\n📊 Монстры на этаже {floor_level}:\n"
    
    if floor_level % 5 == 0:
        # Босс-этаж
        possible_bosses = []
        for boss_name, boss_data in BOSS_STATS.items():
            if floor_level >= boss_data["min_level"]:
                possible_bosses.append(boss_name)
        
        if possible_bosses:
            boss_name = random.choice(possible_bosses)
            boss_level = floor_level + 2
            monster = Monster(boss_name, boss_level, "boss")
            info += f"👑 БОСС: {boss_name} (Ур. {boss_level})\n"
            info += f"   ❤️ Здоровье: {monster.health_max}\n"
            info += f"   ⚔️ Атака: {monster.attack}\n"
            info += f"   🛡️ Защита: {monster.defense}\n"
            
            # Способности босса
            from game_data.bosses_data import BOSS_ABILITIES
            if boss_name in BOSS_ABILITIES:
                info += f"   ✨ Способности:\n"
                for ability_name, ability_data in BOSS_ABILITIES[boss_name].items():
                    info += f"      - {ability_name} (шанс: {ability_data['chance']*100}%)\n"
        else:
            info += "❌ Информация о боссах недоступна\n"
    else:
        # Обычный этаж
        floor_chances = {}
        for floor, chances in MONSTER_SPAWN_CHANCES.items():
            if floor_level <= floor:
                floor_chances = chances
                break
        
        if not floor_chances:
            floor_chances = MONSTER_SPAWN_CHANCES[max(MONSTER_SPAWN_CHANCES.keys())]
        
        info += "Возможные монстры:\n"
        for monster_type, chance in floor_chances.items():
            monster_data = MONSTER_BASE_STATS.get(monster_type, {})
            level = max(1, floor_level + random.randint(-1, 1))
            health = monster_data.get("health_per_level", 8) * level
            attack = monster_data.get("attack_per_level", 2) * level
            defense = monster_data.get("defense_per_level", 1) * level
            
            info += f"  {monster_type}: ❤️{health} ⚔️{attack} 🛡️{defense} (шанс: {chance})\n"
    
    return info

def view_tower_progress(game_state):
    """Просмотр прогресса в башне"""
    floor_info = show_floor_monster_info(game_state["tower_level"])
    show_tower_progress(game_state, floor_info)

def heal_all_heroes(game_state):
    """Лечение всех героев за золото"""
    wallet = game_state["wallet"]
    healing_cost = 100
    
    if wallet.gold < healing_cost:
        print(f"❌ Недостаточно золота! Нужно {healing_cost}, есть {wallet.gold}")
        press_enter_to_continue()
        return
    
    # Подсчитываем сколько героев нужно вылечить
    wounded_heroes = [h for h in game_state["heroes"] if h.is_alive and h.health_current < h.health_max]
    
    if not wounded_heroes:
        print("✅ Все герои уже полностью здоровы!")
        press_enter_to_continue()
        return
    
    confirm = show_healing_confirmation(len(wounded_heroes), healing_cost)
    
    if confirm == 1:
        wallet.subtract_gold(healing_cost)
        for hero in wounded_heroes:
            hero.health_current = hero.health_max
            hero.mana_current = hero.mana_max
        
        print(f"✅ Все герои вылечены! Потрачено {healing_cost} золота")
    else:
        print("❌ Лечение отменено")
    
    press_enter_to_continue()

def tower_management(game_state):
    """Главное меню управления башни"""
    while True:
        choice = show_tower_management_menu(game_state)
        
        if choice is None:
            print("❌ Неверный ввод!")
            press_enter_to_continue()
            continue
        
        if choice == 1:
            result = send_to_tower(game_state)
            if result:
                break
        elif choice == 2:
            view_tower_progress(game_state)
        elif choice == 3:
            heal_all_heroes(game_state)
        elif choice == 0:
            break
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()