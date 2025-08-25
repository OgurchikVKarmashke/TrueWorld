# ui/research_manager.py
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

    while True:
        print_header("🔬 Лаборатория")
        print(f"Уровень лаборатории - {lab.level}\n")

        # Берём только исследования, которые стали видимыми
        visible_keys = [k for k in research_mgr.researches.keys() if research_mgr.is_visible(k, game_state)]

        if not visible_keys:
            print("📚 Нет доступных исследований.\n")
            print("0. ↩️ Вернуться в здания")
            choice = input("Выберите действие: ").strip()
            if choice in ("0", "b", "B"):
                break
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
                if can:
                    print("   [Доступно для исследования]")
                else:
                    print(f"   [Недоступно: {msg}]")
            else:
                # Максимум
                print(f"{i}. ✅ {r.name}")
                print(f"   {r.description}")
                print("   Достигнут максимальный уровень")
            print()

        print("0. ↩️ Вернуться в здания")
        choice = input("Выберите исследование: ").strip()
        if choice in ("0", "b", "B"):
            break

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
            press_enter_to_continue()
            continue

        # Анимация изучения
        loading_screen(2, f"Изучение {r.name} ур.{r.level + 1}")

        ok, msg = research_mgr.start_research(key, game_state)
        print(("✅ " if ok else "❌ ") + msg)
        press_enter_to_continue()
