# tower_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from ui.tower_system import send_to_tower

def tower_menu(game_state):
    """
    Меню башни испытаний
    """
    while True:
        print_header("🏰 Башня испытаний")
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
            send_to_tower(game_state)
        else:
            loading_screen(1, "🚫 Локация недоступна")
            print("Эта локация будет доступна в будущих обновлениях!")
            press_enter_to_continue()