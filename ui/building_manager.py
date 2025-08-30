# ui.building_manager.py
from ui.ui_utils import print_header, loading_screen, press_enter_to_continue

def manage_buildings(game_state):
    tower_level = game_state["tower_level"]
    building_manager = game_state["buildings"]
    building_manager.unlock_buildings(tower_level)
    
    while True:
        print_header("Управление зданиями")
        print(f"Золото: {game_state['wallet'].gold}")
        print(f"Текущий этаж башни: {tower_level}")
        print(f"Макс. уровень зданий: {calculate_max_building_level(tower_level)}")
        print()
        
        available_buildings = building_manager.get_all_buildings_for_management(tower_level)
        
        for i, (key, building) in enumerate(available_buildings.items(), 1):
            max_allowed_level = calculate_max_building_level(tower_level)
            
            print(f"{i}. {building.name} (Ур. {building.level}/{building.max_level})")
            print(f"   {building.description}")
            print(f"   Эффект: {building.effect()}")
            
            if not building.built and building.level == 0:
                cost = building.build_cost()
                print(f"   🏗️  Постройка: {cost} золота")
            elif building.can_upgrade(tower_level):
                cost = building.upgrade_cost()
                print(f"   🔧 Улучшение до {building.level + 1}: {cost} золота")
            else:
                if building.level >= max_allowed_level:
                    print(f"   🔒 Максимальный уровень для текущего этажа")
                elif building.level >= building.max_level:
                    print(f"   ✅ Максимальный уровень достигнут")
                else:
                    print(f"   ❌ Недоступно для улучшения")
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
            
            if not building.can_upgrade(tower_level):
                print("Невозможно улучшить это здание!")
                press_enter_to_continue()
                continue
            
            cost = building.upgrade_cost() if building.level > 0 else building.build_cost()
            
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
                
                game_state["save_system"].save_game(game_state, 1)
            else:
                print("Недостаточно золота!")
            
            press_enter_to_continue()
        else:
            print("Неверный выбор!")
            press_enter_to_continue()

def calculate_max_building_level(tower_level):
    base_level = 1
    bonus_levels = tower_level // 5
    return base_level + bonus_levels