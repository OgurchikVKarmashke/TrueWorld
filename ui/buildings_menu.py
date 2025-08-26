# buildings_menu.py
# ui.buildings_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.summon_system import summon_hero
from ui.building_manager import manage_buildings
from ui.research_manager import manage_research
from ui.synthesis_room_menu import manage_synthesis

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
                summon_hall(game_state)
            elif key == "synthesis":
                manage_synthesis(game_state)
            elif key == "laboratory":
                manage_research(game_state)
            else:
                print(f"{name} в разработке...")
                press_enter_to_continue()
        else:
            print("Неверный выбор!")
            press_enter_to_continue()

def summon_hall(game_state):
    """
    Зал призыва героев
    """
    while True:
        # Получаем информацию о лимите героев
        dormitory = game_state["buildings"].get_building("dormitory")
        current_heroes = len(game_state["heroes"])
        max_heroes = dormitory.get_capacity()
        
        print_header("Зал призыва героев")
        print(f"Золото: {game_state['wallet'].gold}")
        print(f"Кристаллы: {game_state['wallet'].crystals}")
        print(f"Героев: {current_heroes}/{max_heroes}")
        print()
        print("1. Призыв за золото (50 золота)")
        print("2. Призыв за кристаллы (недоступно)")
        print("0. Назад")
        print()
        
        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        elif choice == 1:
            if current_heroes >= max_heroes:
                print("Достигнут лимит героев!")
                print("Улучшите Общежитие, чтобы увеличить лимит")
                press_enter_to_continue()
            else:
                summon_hero(game_state)
        elif choice == 2:
            print("Призыв за кристаллы будет доступен в будущем!")
            press_enter_to_continue()
        else:
            print("Неверный выбор!")
            press_enter_to_continue()