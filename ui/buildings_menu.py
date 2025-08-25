#buildings_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from systems.summon_system import summon_hero
from ui.building_manager import manage_buildings
from ui.research_manager import manage_research
from ui.synthesis_room import manage_synthesis

def buildings_menu(game_state):
    """
    Меню управления зданиями
    """
    while True:
        print_header("🏛️ Комплекс зданий")
        print("Выберите здание для посещения:")
        print()
        
        # Определяем доступность зданий на основе этажа
        tower_level = game_state["tower_level"]
        available_buildings = []
        
        # Всегда доступны
        available_buildings.append(("Зал призыва героев", True, None))
        available_buildings.append(("Комната синтеза", True, None))
        
        # Склад доступен с 3 этажа
        available_buildings.append(("Склад", tower_level >= 3, "Этаж 3+"))
        
        # Лаборатория доступна с 5 этажа
        available_buildings.append(("Лаборатория", tower_level >= 5, "Этаж 5+"))
        
        # Столовая доступна с 7 этажа
        available_buildings.append(("Столовая", tower_level >= 7, "Этаж 7+"))
        
        # Кузница доступна с 10 этажа
        available_buildings.append(("Кузница", tower_level >= 10, "Этаж 10+"))
        
        # Улучшение зданий доступно с 1 этажа
        available_buildings.append(("Улучшить здания", tower_level >= 1, "Этаж 1+"))
        
        # Фильтруем только доступные здания
        menu_items = []
        counter = 1
        for name, available, requirement in available_buildings:
            if available:
                menu_items.append((counter, name))
                status_icon = "🛠️" if name == "Улучшить здания" else "🏠"
                print(f"{counter}. {status_icon} {name}")
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
        for num, name in menu_items:
            if num == choice:
                selected = name
                break
        
        if selected == "Зал призыва героев":
            summon_hall(game_state)
        elif selected == "Комната синтеза":
            manage_synthesis(game_state)
        elif selected == "Улучшить здания":
            manage_buildings(game_state)
        elif selected == "Лаборатория":
            manage_research(game_state)
        elif selected == "Склад":
            print("Склад в разработке...")
            press_enter_to_continue()
        elif selected == "Столовая":
            print("Столовая в разработке...")
            press_enter_to_continue()
        elif selected == "Кузница":
            print("Кузница в разработке...")
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