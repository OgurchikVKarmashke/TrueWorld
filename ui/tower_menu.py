# tower_menu.py
# ui/tower_menu.py
from ui.ui_utils import loading_screen, press_enter_to_continue
from ui.tower_ui import display_tower_header
from systems.tower_system import tower_management

def tower_menu(game_state):
    """
    Меню башни испытаний
    """
    while True:
        display_tower_header("🏰 Башня испытаний")
        print("Выберите локацию для исследования:")
        print()
        print("1. 🏰 Башня испытаний (основной прогресс)")
        print("2. 📅 Ежедневное подземелье (недоступно)")
        print("0. ↩️ Вернуться в лобби")
        print()
        
        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        elif choice == 1:
            tower_management(game_state)
        else:
            loading_screen(1, "🚫 Локация недоступна")
            print("Эта локация будет доступна в будущих обновлениях!")
            press_enter_to_continue()