# ui.buildings_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.summon_system import summon_hero
from ui.building_manager import manage_buildings
from ui.research_manager import manage_research
from ui.synthesis_room_menu import manage_synthesis
from ui.summon_room_menu import manage_summon
from ui.storage_ui import storage_menu
from ui.forge_ui import forge_menu

def buildings_menu(game_state):
    """
    Меню управления зданиями
    """
    building_manager = game_state["buildings"]
    tower_level = game_state["tower_level"]
    
    # Автоматически разблокируем здания
    building_manager.unlock_buildings(tower_level)
    
    while True:
        print_header("🏛️ Комплекс зданий")
        print("Выберите здание для посещения:")
        print()
        
        available_buildings = building_manager.get_available_buildings(tower_level)
        menu_items = []
        
        counter = 1
        for key, building in available_buildings.items():
            if building.built:  # Показываем только построенные здания
                menu_items.append((counter, key, building.name))
                status_icon = "🏠"
                if key == "storage":
                    status_icon = "📦"
                elif key == "forge":
                    status_icon = "⚒️"
                print(f"{counter}. {status_icon} {building.name}")
                counter += 1
        
        # Добавляем меню улучшения (всегда доступно если есть этажи)
        if tower_level >= 1:
            menu_items.append((counter, "upgrade", "Улучшить здания"))
            print(f"{counter}. 🛠️ Улучшить здания")
            counter += 1
        
        print("0. ↩️ Вернуться в лобби")
        print()
        
        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        
        # Находим выбранный пункт
        selected = None
        for num, key, name in menu_items:
            if num == choice:
                selected = (key, name)
                break
        
        if selected:
            key, name = selected
            if key == "upgrade":
                manage_buildings(game_state)
            elif key == "summon_hall":
                manage_summon(game_state)
            elif key == "synthesis":
                manage_synthesis(game_state)
            elif key == "laboratory":
                manage_research(game_state)
            elif key == "storage":
                storage_menu(game_state)
            elif key == "forge":
                forge_menu(game_state)
            else:
                print(f"{name} в разработке...")
                press_enter_to_continue()
        else:
            print("Неверный выбор!")
            press_enter_to_continue()