# systems.tower_system.py
from systems.hero_system import Hero
from systems.combat_system import Combat
from systems.party_system import PartySystem
from game_data.monsters_data import MONSTER_SPAWN_CHANCES
from ui.tower_ui import (
    show_tower_management_menu, show_party_selection, show_expedition_preview,
    show_victory_screen, show_defeat_screen, show_tower_progress,
    show_healing_confirmation
)
from ui.ui_utils import loading_screen, press_enter_to_continue
import random

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
    current_floor = game_state["tower_level"]
    required_groups = 2 if current_floor % 10 == 0 else 1

    selected_parties, selected_party_ids = choose_parties_for_floor(game_state, required_groups)
    if selected_parties is None:
        return

    active_party_heroes = []
    for party_id in selected_party_ids:
        heroes = PartySystem(game_state).get_party_heroes(party_id)
        active_party_heroes.extend(heroes)

    if not active_party_heroes:
        print("❌ В выбранных группах нет героев!")
        press_enter_to_continue()
        return

    choice = show_expedition_preview(active_party_heroes, current_floor)
    if choice is None or choice == 0:
        return
    
    loading_screen(2, "Подготовка отряда")
    
    combat = Combat(active_party_heroes, current_floor, game_state)
    victory, log, total_exp = combat.start_combat()
    
    # Определяем живых и мертвых героев ПОСЛЕ боя
    dead_heroes = [h for h in active_party_heroes if not h.is_alive]
    living_heroes = [h for h in active_party_heroes if h.is_alive]
    
    if victory:
        # Получаем награды из объекта боя
        rewards = getattr(combat, 'victory_rewards', {})
        
        # Распределяем опыт между выжившими героями
        if living_heroes and total_exp > 0:
            exp_per_hero = total_exp // len(living_heroes)
            for hero in living_heroes:
                result = hero.add_experience(exp_per_hero)
                if result:
                    print(result)
        
        # Обновляем состав групп, убирая погибших героев
        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]

        # Повышаем этаж только если была победа
        game_state["tower_level"] += 1
        
        # Обновляем максимальный этаж
        if game_state["tower_level"] > game_state.get("max_tower_floor", 1):
            game_state["max_tower_floor"] = game_state["tower_level"]
        
        # Показываем экран победы с наградами
        show_victory_screen(
            reward=rewards.get('gold', 0),
            total_exp=total_exp,
            new_floor=game_state["tower_level"],
            dead_heroes=dead_heroes,
            item_rewards=rewards.get('items', {}),
            game_state=game_state  # Добавьте этот параметр
        )
        
    else:
        # Поражение - отступаем на этаж ниже
        game_state["tower_level"] = max(1, current_floor - 1)
        
        # Обновляем состав групп
        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]
        
        # Показываем экран поражения
        show_defeat_screen(dead_heroes, game_state["tower_level"])
    
    # Сохраняем окончательное состояние
    game_state["save_system"].save_game(game_state)
    return victory

def show_floor_monster_info(floor_level):
    """Получить информацию о монстрах на указанном этаже"""
    from systems.combat_system import Monster
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
                info += f"   ✨ Способabilities:\n"
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
    """Главное меню управления башней"""
    while True:
        choice = show_tower_management_menu(game_state)
        
        if choice is None:
            print("❌ Неверный ввод!")
            press_enter_to_continue()
            continue
        
        if choice == 1:
            result = send_to_tower(game_state)
            # Если была победа, выходим из цикла чтобы не показывать меню повторно
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