# tower_system.py
from systems.hero_system import Hero
from ui.ui_utils import print_header, loading_screen, press_enter_to_continue
from systems.combat_system import Combat
from systems.party_system import PartySystem
from game_data.monsters_data import MONSTER_SPAWN_CHANCES
import random

def choose_parties_for_floor(game_state, required_groups=1):
    party_system = PartySystem(game_state)
    available_parties = list(party_system.parties.items())

    while True:
        print_header("⚔️ Выбор боевых групп для башни")

        for i, (party_id, party_data) in enumerate(available_parties, 1):
            heroes = party_system.get_party_heroes(party_id)
            hero_names = ", ".join([h.name for h in heroes]) or "— пусто —"
            print(f"{i}. {party_data['name']} → [{hero_names}]")

        print(f"\nЭтаж требует групп: {required_groups}")
        print("0. ↩️ Вернуться назад")
        choice = input("Введите номера групп через запятую: ").strip()

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
    print_header("🏰 Башня испытаний")
    current_floor = game_state["tower_level"]

    required_groups = 1
    if current_floor % 10 == 0:
        required_groups = 2

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

    print(f"📊 Текущий этаж: {current_floor}")
    print("🎯 Состав отряда:")
    print("-" * 30)

    for i, hero in enumerate(active_party_heroes, 1):
        status = "✅ Готов" if hero.is_alive else "❌ Неспособен"
        star_symbol = "★" * hero.star
        print(f"{i}. {hero.name} {star_symbol}")
        print(f"   📈 Ур. {hero.level} | {status}")
        print(f"   ❤️ Здоровье: {hero.health_current}/{hero.health_max}")
    
    print("\n1. ⚔️ Начать вылазку")
    print("2. ↩️ Вернуться в командный центр")
    print()

    try:
        choice = int(input("Выбор: "))
    except ValueError:
        press_enter_to_continue()
        return
    
    if choice == 2:
        return
    
    loading_screen(2, "Подготовка отряда")
    
    combat = Combat(active_party_heroes, current_floor, game_state)
    victory, log, total_exp = combat.start_combat()
    
    # Сохраняем состояние игры после боя
    game_state["save_system"].save_game(game_state)
    
    if victory:
        reward = current_floor * 25
        game_state["wallet"].add_gold(reward)
        game_state["tower_level"] += 1
        
        # Обновляем максимальный этаж
        if game_state["tower_level"] > game_state.get("max_tower_floor", 1):
            game_state["max_tower_floor"] = game_state["tower_level"]

        living_heroes = [h for h in active_party_heroes if h.is_alive]
        dead_heroes = [h for h in active_party_heroes if not h.is_alive]
        
        if living_heroes and total_exp > 0:
            exp_per_hero = total_exp // len(living_heroes)
            for hero in living_heroes:
                result = hero.add_experience(exp_per_hero)
                if result:
                    print(result)

        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            # Обновляем состав группы, убирая погибших героев
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]

        print(f"\n🎉 ПОБЕДА!")
        print(f"💰 Награда: {reward} золота")
        print(f"📈 Получено опыта: {total_exp}")
        
        if dead_heroes:
            print("💀 Погибшие в бою:")
            for hero in dead_heroes:
                print(f"- {hero.name}")
        print(f"🏆 Доступен этаж {game_state['tower_level']}")
        
    else:
        dead_heroes = [h for h in active_party_heroes if not h.is_alive]
        living_heroes = [h for h in active_party_heroes if h.is_alive]
        
        party_system = PartySystem(game_state)
        for party_id in selected_party_ids:
            # Обновляем состав группы
            party_heroes = party_system.get_party_heroes(party_id)
            party_system.parties[party_id]["heroes"] = [id(h) for h in party_heroes if h.is_alive]

        print("\n💥 ПОРАЖЕНИЕ")
        print("💀 Погибшие:")
        for hero in dead_heroes:
            print(f"- {hero.name} (Ур. {hero.level})")
        
        game_state["tower_level"] = max(1, current_floor - 1)
        print(f"🔙 Отступление к этажу {game_state['tower_level']}")
    
    # Сохраняем окончательное состояние
    game_state["save_system"].save_game(game_state)
    press_enter_to_continue()
    
    return victory


def show_floor_monster_info(floor_level):
    """Показывает информацию о монстрах на указанном этаже"""
    from systems.combat_system import Monster
    from game_data.monsters_data import MONSTER_BASE_STATS, BOSS_STATS
    
    print(f"\n📊 Монстры на этаже {floor_level}:")
    
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
            print(f"👑 БОСС: {boss_name} (Ур. {boss_level})")
            print(f"   ❤️ Здоровье: {monster.health_max}")
            print(f"   ⚔️ Атака: {monster.attack}")
            print(f"   🛡️ Защита: {monster.defense}")
            
            # Показываем способности босса
            from game_data.bosses_data import BOSS_ABILITIES
            if boss_name in BOSS_ABILITIES:
                print(f"   ✨ Способности:")
                for ability_name, ability_data in BOSS_ABILITIES[boss_name].items():
                    print(f"      - {ability_name} (шанс: {ability_data['chance']*100}%)")
        else:
            print("❌ Информация о боссах недоступна")
    else:
        # Обычный этаж
        floor_chances = {}
        for floor, chances in MONSTER_SPAWN_CHANCES.items():
            if floor_level <= floor:
                floor_chances = chances
                break
        
        if not floor_chances:
            floor_chances = MONSTER_SPAWN_CHANCES[max(MONSTER_SPAWN_CHANCES.keys())]
        
        print("Возможные монстры:")
        for monster_type, chance in floor_chances.items():
            monster_data = MONSTER_BASE_STATS.get(monster_type, {})
            level = max(1, floor_level + random.randint(-1, 1))
            health = monster_data.get("health_per_level", 8) * level
            attack = monster_data.get("attack_per_level", 2) * level
            defense = monster_data.get("defense_per_level", 1) * level
            
            print(f"  {monster_type}: ❤️{health} ⚔️{attack} 🛡️{defense} (шанс: {chance})")

def view_tower_progress(game_state):
    """Просмотр прогресса в башне"""
    print_header("🏰 Прогресс в Башне Испытаний")
    
    current_floor = game_state["tower_level"]
    max_floor_reached = game_state.get("max_tower_floor", current_floor)
    
    print(f"📊 Текущий этаж: {current_floor}")
    print(f"🏆 Максимальный достигнутый: {max_floor_reached}")
    print(f"💰 Награда за следующий этаж: {current_floor * 25} золота")
    
    # Показываем информацию о монстрах на текущем этаже
    show_floor_monster_info(current_floor)
    
    # Показываем информацию о следующих этапах
    if current_floor % 5 == 0:
        next_boss_floor = current_floor + 5
        print(f"\n⚠️  Следующий босс на этаже: {next_boss_floor}")
    elif (current_floor + 1) % 5 == 0:
        print(f"\n⚡ Следующий этаж: БОСС-БОЙ!")
    
    if current_floor % 10 == 0:
        next_multi_party_floor = current_floor + 10
        print(f"\n👥 На этаже {next_multi_party_floor} потребуется 2 группы")
    
    print("\nОсобые этажи:")
    for floor in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
        if floor <= max_floor_reached + 5:  # Показываем только ближайшие этажи
            status = "✅ Пройден" if current_floor > floor else "🔒 Заблокирован" if current_floor < floor else "🎯 Текущий"
            if floor % 5 == 0:
                print(f"  {floor}F - Босс - {status}")
            else:
                print(f"  {floor}F - Обычный - {status}")
    
    press_enter_to_continue()

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
    
    print(f"💊 Лечение {len(wounded_heroes)} героев: {healing_cost} золота")
    print("1. ✅ Подтвердить лечение")
    print("2. ❌ Отмена")
    
    try:
        confirm = int(input("Выбор: "))
    except ValueError:
        press_enter_to_continue()
        return
    
    if confirm == 1:
        wallet.spend_gold(healing_cost)
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
        print_header("🏰 Управление Башней Испытаний")
        
        current_floor = game_state["tower_level"]
        heroes_available = sum(1 for hero in game_state["heroes"] if hero.is_alive)
        
        print(f"📊 Текущий этаж: {current_floor}")
        print(f"🎯 Доступных героев: {heroes_available}")
        print(f"💰 Золото: {game_state['wallet'].gold}")
        
        print("\n1. ⚔️  Отправить в башню")
        print("2. 📈 Просмотреть прогресс")
        print("3. 🏥 Лечить всех героев (100 золота)")
        print("4. ↩️ Вернуться в главное меню")
        print()
        
        try:
            choice = int(input("Выбор: "))
        except ValueError:
            print("❌ Неверный ввод!")
            press_enter_to_continue()
            continue
        
        if choice == 1:
            send_to_tower(game_state)
        elif choice == 2:
            view_tower_progress(game_state)
        elif choice == 3:
            heal_all_heroes(game_state)
        elif choice == 4:
            break
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()