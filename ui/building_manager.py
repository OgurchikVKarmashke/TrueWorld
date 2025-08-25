# building_manager.py
from ui.ui_utils import print_header, loading_screen, press_enter_to_continue

def manage_buildings(game_state):
    """
    Меню управления зданиями
    """
    # Проверяем доступность улучшений
    if game_state["tower_level"] < 1:
        print_header("Управление зданиями")
        print("Улучшение зданий доступно после прохождения 1 этажа башни!")
        press_enter_to_continue()
        return
    
    while True:
        print_header("Управление зданиями")
        print(f"Золото: {game_state['wallet'].gold}")
        print(f"Текущий этаж башни: {game_state['tower_level']}")
        print(f"Макс. уровень зданий: {calculate_max_building_level(game_state['tower_level'])}")
        print()
        
        buildings = game_state["buildings"].buildings
        available_buildings = {}
        
        # ФИЛЬТРУЕМ здания по доступности
        for key, building in buildings.items():
            # Лаборатория доступна только с 5 этажа
            if key == "laboratory" and game_state["tower_level"] < 5:
                continue
            available_buildings[key] = building
        
        for i, (key, building) in enumerate(available_buildings.items(), 1):
            cost = building.upgrade_cost()
            max_allowed_level = calculate_max_building_level(game_state["tower_level"])
            
            print(f"{i}. {building.name} (Ур. {building.level}/{max_allowed_level})")
            print(f"   {building.description}")
            print(f"   Эффект: {building.effect()}")
            
            if building.level >= max_allowed_level:
                print(f"   🔒 Максимальный уровень для текущего этажа")
            elif building.level == 0:
                print(f"   🏗️  Постройка: {cost} золота")
            elif building.level < max_allowed_level:
                print(f"   🔧 Улучшение: {cost} золота")
            print()
        
        print("0. Назад")
        print()
        
        try:
            choice = int(input("Выберите здание: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        
        building_keys = list(available_buildings.keys())
        if 1 <= choice <= len(building_keys):
            building_key = building_keys[choice - 1]
            building = available_buildings[building_key]
            
            max_allowed_level = calculate_max_building_level(game_state["tower_level"])
            
            if building.level >= max_allowed_level:
                print(f"Достигнут максимальный уровень для текущего этажа!")
                print(f"Пройдите больше этажей башни, чтобы увеличить лимит.")
                press_enter_to_continue()
                continue
            
            cost = building.upgrade_cost()
            if game_state["wallet"].subtract_gold(cost):
                building.level += 1
                if building.level == 1:
                    building.built = True
                    action = "построено"
                else:
                    action = "улучшено"
                
                loading_screen(2, f"{action.capitalize()} {building.name}")
                print(f"{building.name} {action} до уровня {building.level}!")
                print(f"Новый эффект: {building.effect()}")
            else:
                print("Недостаточно золота!")
            
            press_enter_to_continue()
            game_state["save_system"].save_game(game_state, 1)

        else:
            print("Неверный выбор!")
            press_enter_to_continue()

def calculate_max_building_level(tower_level):
    """
    Определяет максимальный уровень зданий на основе этажа башни
    Каждые 5 этажей +1 к максимальному уровню
    """
    base_level = 1
    bonus_levels = tower_level // 5  # Каждые 5 этажей +1 уровень
    return base_level + bonus_levels