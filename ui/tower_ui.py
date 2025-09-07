# ui.tower_ui.py
from game_data.tower_rewards import get_floor_rewards, generate_item_rewards
from systems.difficulty_system import DifficultySystem
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen, clear_screen
from ui.visual_effects import VisualEffects
import time
import random

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
    
    # Показываем возможные награды за текущий этаж
    rewards = get_floor_rewards(current_floor)
    print(f"🎁 Награда: {rewards['gold']} золота + предметы")
    
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
    
    print(f"📋 Требуется групп: {required_groups}")
    print("Доступные группы:")
    print("-" * 50)
    
    for i, (party_id, party_data) in enumerate(available_parties, 1):
        # Получаем реальные объекты героев из game_state
        hero_objects = []
        for hero_id in party_data["heroes"]:
            for hero in game_state["heroes"]:
                if id(hero) == hero_id:
                    hero_objects.append(hero)
                    break
        
        # Подсчитываем живых героев
        alive_heroes = [h for h in hero_objects if h.is_alive]
        total_power = sum(h.attack + h.defense for h in alive_heroes)
        
        print(f"{i}. {party_data['name']}")
        print(f"   👥 Героев: {len(alive_heroes)}/{len(hero_objects)}")
        print(f"   💪 Сила: {total_power}")
        
        # Показываем имена героев
        if alive_heroes:
            hero_names = ", ".join([h.name for h in alive_heroes[:3]])
            if len(alive_heroes) > 3:
                hero_names += f" ... (+{len(alive_heroes) - 3})"
            print(f"   🎯 Состав: {hero_names}")
        else:
            print("   ❌ Нет живых героев!")
        print()

    print("0. ↩️ Вернуться назад")
    print("-" * 50)
    
    if required_groups > 1:
        print("💡 Введите номера групп через запятую (например: 1,2)")
    else:
        print("💡 Введите номер группы")
    
    try:
        choice = input("🎯 Ваш выбор: ").strip()
        if choice.lower() in ['0', 'b', 'back']:
            return "0"
        return choice
    except:
        return "0"

def show_expedition_preview(active_party_heroes, current_floor):
    """Показать предпросмотр вылазки"""
    display_tower_header("🏰 Подготовка к вылазке")
    
    print(f"📊 Текущий этаж: {current_floor}")
    print("🎯 Состав отряда:")
    print("-" * 30)

    for i, hero in enumerate(active_party_heroes, 1):
        status = "✅ Готов" if hero.is_alive else "❌ Неспособен"
        # Используем метод из VisualEffects
        star_display = VisualEffects.get_star_display(hero.star)
        print(f"{i}. {hero.name} {star_display}")
        print(f"   📈 Ур. {hero.level} | {status}")
        print(f"   ❤️ Здоровье: {hero.health_current}/{hero.health_max}")
    
    # Показываем общую силу отряда
    total_power = sum(h.attack + h.defense for h in active_party_heroes if h.is_alive)
    print(f"\n💪 Общая сила отряда: {total_power}")
    
    print("\n1. ⚔️ Начать вылазку")
    print("0. ↩️ Вернуться в командный центр")
    print()
    
    try:
        return int(input("Выбор: "))
    except ValueError:
        return None

def show_victory_screen(reward, total_exp, new_floor, dead_heroes, item_rewards=None, game_state=None):
    """Показать экран победы с наградами"""
    display_tower_header("🎉 ПОБЕДА!")
    print(f"💰 Награда: {reward} золота")
    print(f"📈 Получено опыта: {total_exp}")
    
    # ПОКАЗЫВАЕМ ПОЛУЧЕННЫЕ ПРЕДМЕТЫ
    if item_rewards:
        print("📦 Полученные предметы:")
        for item_id, quantity in item_rewards.items():
            if game_state and "item_manager" in game_state:
                item = game_state["item_manager"].get_item(item_id)
                if item:
                    print(f"   - {item.name} x{quantity}")
            else:
                # Фолбэк если game_state не передан
                print(f"   - Предмет ID: {item_id} x{quantity}")
    
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
    """Показать прогресс башни с информацией о наградах"""
    display_tower_header("🏰 Прогресс в Башне Испытаний")
    
    current_floor = game_state["tower_level"]
    max_floor_reached = game_state.get("max_tower_floor", current_floor)
    
    print(f"📊 Текущий этаж: {current_floor}")
    print(f"🏆 Максимальный достигнутый: {max_floor_reached}")
    
    # Показываем награды за текущий и следующие этапы
    print(f"\n🎁 Награды за этажи:")
    
    # Текущий этаж
    current_rewards = get_floor_rewards(current_floor)
    print(f"   {current_floor}F: {current_rewards['gold']} золота + предметы")
    
    # Следующие 5 этапов
    for floor in range(current_floor + 1, min(current_floor + 6, 101)):
        rewards = get_floor_rewards(floor)
        status = "🔒 " if floor > max_floor_reached else "🔓 "
        print(f"   {status}{floor}F: {rewards['gold']} золота + предметы")
    
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
            rewards = get_floor_rewards(floor)
            if floor % 5 == 0:
                print(f"  {floor}F - Босс - {status} - {rewards['gold']} золота")
            else:
                print(f"  {floor}F - Обычный - {status} - {rewards['gold']} золота")
    
    press_enter_to_continue()

def show_detailed_rewards(game_state, floor_number):
    """Показать детальную информацию о наградах за этаж"""
    display_tower_header(f"🎁 Награды за этаж {floor_number}")
    
    rewards = get_floor_rewards(floor_number)
    item_manager = game_state["item_manager"]
    
    print(f"💰 Золото: {rewards['gold']}")
    print(f"💎 Кристаллы: {rewards['crystals']}")
    
    if "items" in rewards:
        print("📦 Предметы:")
        for item_id, (min_qty, max_qty) in rewards["items"].items():
            item = item_manager.get_item(item_id)
            if item:
                chance = "Высокий" if max_qty > 3 else "Средний" if max_qty > 1 else "Низкий"
                print(f"   - {item.name}: {min_qty}-{max_qty} шт. ({chance} шанс)")
    
    if "unlocks" in rewards:
        print("🔓 Разблокировки:")
        for unlock in rewards["unlocks"]:
            if unlock.endswith("_recipe"):
                recipe_name = unlock.replace("_recipe", "").replace("_", " ").title()
                print(f"   - Рецепт: {recipe_name}")
    
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