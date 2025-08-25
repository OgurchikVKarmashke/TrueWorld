# tower_ui.py
# ui/tower_ui.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen, clear_screen
import time

def display_tower_header(title):
    """Отображение заголовка башни"""
    clear_screen()
    print("=" * 50)
    print(f"=== {title.upper()} ===")
    print("=" * 50)
    print()

def show_tower_management_menu(game_state):
    """Показать меню управления башней"""
    display_tower_header("🏰 Управление Башней Испытаний")
    
    current_floor = game_state["tower_level"]
    heroes_available = sum(1 for hero in game_state["heroes"] if hero.is_alive)
    
    print(f"📊 Текущий этаж: {current_floor}")
    print(f"🎯 Доступных героев: {heroes_available}")
    print(f"💰 Золото: {game_state['wallet'].gold}")
    
    print("\n1. ⚔️  Отправить в башню")
    print("2. 📈 Просмотреть прогресс")
    print("3. 🏥 Лечить всех героев (100 золота)")
    print("0. ↩️ Вернуться в главное меню")
    print()
    
    try:
        return int(input("Выбор: "))
    except ValueError:
        return None

def show_party_selection(available_parties, required_groups, game_state):
    """Показать выбор групп для башни"""
    display_tower_header("⚔️ Выбор боевых групп для башни")

    for i, (party_id, party_data) in enumerate(available_parties, 1):
        # Получаем реальные объекты героев из game_state
        hero_objects = []
        for hero_id in party_data["heroes"]:
            for hero in game_state["heroes"]:
                if id(hero) == hero_id:
                    hero_objects.append(hero)
                    break
        
        hero_names = ", ".join([h.name for h in hero_objects]) if hero_objects else "— пусто —"
        print(f"{i}. {party_data['name']} → [{hero_names}]")

    print(f"\nЭтаж требует групп: {required_groups}")
    print("0. ↩️ Вернуться назад")
    return input("Введите номера групп через запятую: ").strip()

def show_expedition_preview(active_party_heroes, current_floor):
    """Показать предпросмотр вылазки"""
    display_tower_header("🏰 Подготовка к вылазке")
    
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
    print("0. ↩️ Вернуться в командный центр")
    print()
    
    try:
        return int(input("Выбор: "))
    except ValueError:
        return None

def show_victory_screen(reward, total_exp, new_floor, dead_heroes):
    """Показать экран победы"""
    display_tower_header("🎉 ПОБЕДА!")
    print(f"💰 Награда: {reward} золота")
    print(f"📈 Получено опыта: {total_exp}")
    
    if dead_heroes:
        print("💀 Погибшие в бою:")
        for hero in dead_heroes:
            print(f"- {hero.name}")
    
    print(f"🏆 Доступен этаж {new_floor}")
    press_enter_to_continue()

def show_defeat_screen(dead_heroes, retreat_floor):
    """Показать экран поражения"""
    display_tower_header("💥 ПОРАЖЕНИЕ")
    print("💀 Погибшие:")
    for hero in dead_heroes:
        print(f"- {hero.name} (Ур. {hero.level})")
    
    print(f"🔙 Отступление к этажу {retreat_floor}")
    press_enter_to_continue()

def show_tower_progress(game_state, floor_info):
    """Показать прогресс башни"""
    display_tower_header("🏰 Прогресс в Башне Испытаний")
    
    current_floor = game_state["tower_level"]
    max_floor_reached = game_state.get("max_tower_floor", current_floor)
    
    print(f"📊 Текущий этаж: {current_floor}")
    print(f"🏆 Максимальный достигнутый: {max_floor_reached}")
    print(f"💰 Награда за следующий этаж: {current_floor * 25} золota")
    
    # Информация о монстрах
    print(f"\n{floor_info}")
    
    # Информация о следующих этапах
    if current_floor % 5 == 0:
        next_boss_floor = current_floor + 5
        print(f"⚠️  Следующий босс на этаже: {next_boss_floor}")
    elif (current_floor + 1) % 5 == 0:
        print(f"⚡ Следующий этаж: БОСС-БОЙ!")
    
    if current_floor % 10 == 0:
        next_multi_party_floor = current_floor + 10
        print(f"👥 На этаже {next_multi_party_floor} потребуется 2 группы")
    
    print("\nОсобые этажи:")
    for floor in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
        if floor <= max_floor_reached + 5:
            status = "✅ Пройден" if current_floor > floor else "🔒 Заблокирован" if current_floor < floor else "🎯 Текущий"
            if floor % 5 == 0:
                print(f"  {floor}F - Босс - {status}")
            else:
                print(f"  {floor}F - Обычный - {status}")
    
    press_enter_to_continue()

def show_healing_confirmation(wounded_count, cost):
    """Показать подтверждение лечения"""
    display_tower_header("🏥 Лечение героев")
    print(f"💊 Лечение {wounded_count} героев: {cost} золота")
    print("1. ✅ Подтвердить лечение")
    print("0. ❌ Отмена")
    print()
    
    try:
        return int(input("Выбор: "))
    except ValueError:
        return None