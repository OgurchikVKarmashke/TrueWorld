# ui.research_manager.py
from ui.ui_utils import print_header, loading_screen, press_enter_to_continue
from ui.role_manager import manage_roles, init_role_system

def manage_research(game_state):
    """
    Лаборатория: отдельный экран, анимации, уровни исследований.
    Показывает только те технологии, которые открыты (is_visible).
    """
    research_mgr = game_state["research"]
    lab = game_state["buildings"].get_building("laboratory")

    # Проверка постройки
    if lab is None or lab.level == 0:
        print_header("🔬 Лаборатория")
        print("Лаборатория не построена! Постройте её в управлении зданиями.")
        press_enter_to_continue()
        return

    # Инициализируем систему ролей если её нет
    if "role_system" not in game_state:
        role_system = init_role_system(game_state)
    else:
        role_system = game_state["role_system"]

    while True:
        # Получаем информацию об исследователе через единый источник
        researcher_name = "Нет"
        assigned_researcher = None
        
        if role_system:
            assigned_heroes = role_system.get_assigned_heroes()
            if "laboratory" in assigned_heroes and assigned_heroes["laboratory"] is not None:
                researcher = assigned_heroes["laboratory"]
                researcher_name = f"{researcher.name} (ур. {researcher.level})"
                assigned_researcher = researcher

        print_header("🔬 Лаборатория")
        print(f"Уровень лаборатории - {lab.level}")
        print(f"🔬 Назначенный исследователь: {researcher_name}")
        print()

        # Берём только исследования, которые стали видимыми
        visible_keys = [k for k in research_mgr.researches.keys() if research_mgr.is_visible(k, game_state)]

        if visible_keys:
            # Отображаем доступные исследования с правильной нумерацией (начиная с 1)
            for i, key in enumerate(visible_keys, 1):
                r = research_mgr.researches[key]
                status = "✅" if r.is_researched and r.level >= r.max_level else "❌"
                current = r.level
                max_lvl = r.max_level

                if current < max_lvl:
                    nxt = current + 1
                    cost = r.next_level_cost()
                    can, msg = research_mgr.can_research(key, game_state)

                    print(f"{i}. {status} {r.name}")
                    print(f"   Следующий уровень: ур.{current} → ур.{nxt}")
                    print(f"   {r.description}")
                    print(f"   Стоимость: {cost['gold']} золота, {cost['crystals']} кристаллов")
                    print(f"   Требования: Лаборатория ур.{r.min_lab_level}")
                    
                    # Показываем статус доступности с причиной
                    if can:
                        print("   [✅ Доступно для исследования]")
                    else:
                        if "требуется назначить исследователя" in msg.lower():
                            print("   [❌ Требуется исследователь]")
                        else:
                            print(f"   [❌ {msg}]")
                else:
                    # Максимум
                    print(f"{i}. ✅ {r.name}")
                    print(f"   {r.description}")
                    print("   Достигнут максимальный уровень")
                print()
        else:
            print("📚 Нет доступных исследований.\n")

        # Меню действий (всегда показывается)
        print("R. 👥 Управление ролями (назначить исследователя)")
        print("0. ↩️ Вернуться в здания")
        
        choice = input("Выберите исследование или действие: ").strip()
        
        # Обработка выхода
        if choice in ("0", "b", "B", "back"):
            break
        
        # Обработка управления ролями
        if choice.lower() == "r":
            manage_roles(game_state)
            continue
        
        # Если ввод не цифра и не распознанная команда
        if not choice.isdigit():
            print("❌ Неверный ввод. Используйте цифры для выбора исследования или R/0 для действий.")
            press_enter_to_continue()
            continue
        
        # Обработка выбора исследования
        idx = int(choice)
        
        # Проверяем, что выбранный индекс в пределах списка исследований
        if idx < 1 or idx > len(visible_keys):
            print(f"❌ Неверный номер исследования. Доступно исследований: {len(visible_keys)}")
            press_enter_to_continue()
            continue
        
        # Получаем выбранное исследование
        key = visible_keys[idx - 1]
        r = research_mgr.researches[key]

        # Проверка максимального уровня
        if r.level >= r.max_level:
            print("⚠️ Исследование уже на максимальном уровне")
            press_enter_to_continue()
            continue

        # Проверка возможности исследования
        can, msg = research_mgr.can_research(key, game_state)
        if not can:
            print(f"❌ Нельзя изучить: {msg}")
            
            # Если причина - отсутствие исследователя, предлагаем назначить
            if "требуется назначить исследователя" in msg.lower():
                print("\nХотите назначить исследователя сейчас? (да/нет)")
                assign_choice = input("> ").strip().lower()
                if assign_choice in ("да", "д", "y", "yes"):
                    manage_roles(game_state)
            
            press_enter_to_continue()
            continue

        # Анимация изучения
        loading_screen(2, f"Изучение {r.name} ур.{r.level + 1}")

        # Запуск исследования
        ok, msg = research_mgr.start_research(key, game_state)
        print(("✅ " if ok else "❌ ") + msg)
        press_enter_to_continue()


# Функции для BuildingManager (оставляем без изменений)
def get_building_status_icon(self, building):
    if building.level == 0:
        return "🔒"  # Не построено
    elif building.level >= building.max_level:
        return "⭐"  # Максимальный уровень
    else:
        return "🏠"  # Построено, можно улучшать

def get_availability_status(self, building, tower_level):
    required_floors = {
        "laboratory": 5,
        "canteen": 7, 
        "forge": 10,
        "elevation_room": 15
    }
    if building.name in required_floors and tower_level < required_floors[building.name]:
        return f"🔒 Этаж {required_floors[building.name]}+"
    return "✅ Доступно"