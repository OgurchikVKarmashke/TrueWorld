# ui.research_manager.py
from ui.ui_utils import print_header, loading_screen, press_enter_to_continue

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

    # Получаем информацию об исследователе
    researcher_name = "Нет"
    if "role_system" in game_state:
        role_system = game_state["role_system"]
        assigned_heroes = role_system.get_assigned_heroes()
        if "laboratory" in assigned_heroes and assigned_heroes["laboratory"] is not None:
            researcher = assigned_heroes["laboratory"]
            researcher_name = f"{researcher.name} (ур. {researcher.level})"
    elif hasattr(lab, 'assigned_hero') and lab.assigned_hero is not None:
        researcher_name = f"{lab.assigned_hero.name} (ур. {lab.assigned_hero.level})"

    while True:
        print_header("🔬 Лаборатория")
        print(f"Уровень лаборатории - {lab.level}")
        print(f"🔬 Назначенный исследователь: {researcher_name}")
        print()

        # Берём только исследования, которые стали видимыми
        visible_keys = [k for k in research_mgr.researches.keys() if research_mgr.is_visible(k, game_state)]

        if not visible_keys:
            print("📚 Нет доступных исследований.\n")
            print("1. 📋 Управление персоналом (назначить исследователя)")
            print("0. ↩️ Вернуться в здания")
            
            choice = input("Выберите действие: ").strip()
            if choice in ("0", "b", "B"):
                break
            elif choice == "1":
                # Открываем меню управления персоналом
                if "role_system" in game_state:
                    role_system = game_state["role_system"]
                    # Вызываем метод управления ролями (если он есть)
                    # Или просто показываем информацию
                    print("\n📋 Управление персоналом:")
                    print("Назначьте исследователя в здании Лаборатории")
                    press_enter_to_continue()
                continue
            continue

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
                    # Определяем, это из-за исследователя или других причин
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

        print("1. 📋 Управление персоналом (назначить исследователя)")
        print("0. ↩️ Вернуться в здания")
        
        choice = input("Выберите исследование или действие: ").strip()
        if choice in ("0", "b", "B"):
            break
        elif choice == "1":
            if "role_system" in game_state:
                print("\n📋 Управление персоналом:")
                print("Назначьте исследователя в здании Лаборатории")
                print("в меню управления зданиями -> Управление персоналом")
                press_enter_to_continue()
            continue

        if not choice.isdigit():
            press_enter_to_continue()
            continue

        idx = int(choice)
        if idx < 1 or idx > len(visible_keys):
            press_enter_to_continue()
            continue

        key = visible_keys[idx - 1]
        r = research_mgr.researches[key]

        if r.level >= r.max_level:
            print("⚠️ Исследование уже на максимальном уровне")
            press_enter_to_continue()
            continue

        can, msg = research_mgr.can_research(key, game_state)
        if not can:
            print(f"❌ Нельзя изучить: {msg}")
            
            # Если причина - отсутствие исследователя, предлагаем назначить
            if "требуется назначить исследователя" in msg.lower():
                if "role_system" in game_state:
                    print("\nХотите назначить исследователя сейчас? (да/нет)")
                    assign_choice = input("> ").strip().lower()
                    if assign_choice in ("да", "д", "y", "yes"):
                        # Здесь можно вызвать меню назначения ролей
                        print("Перейдите в меню управления зданиями -> Управление персоналом")
                        press_enter_to_continue()
            
            press_enter_to_continue()
            continue

        # Анимация изучения
        loading_screen(2, f"Изучение {r.name} ур.{r.level + 1}")

        ok, msg = research_mgr.start_research(key, game_state)
        print(("✅ " if ok else "❌ ") + msg)
        press_enter_to_continue()

# Добавить в BuildingManager методы для отображения статусов
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

