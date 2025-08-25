# heroes_menu.py
from ui.ui_utils import print_header, press_enter_to_continue
from ui.party_editor import manage_parties
from ui.role_manager import manage_roles

def heroes_menu(game_state):
    """Меню управления героями"""
    while True:
        print_header("🎯 Управление героями")

        # Проверяем доступность системы ролей для отображения иконки
        from ui.role_manager import is_role_system_available
        role_available = is_role_system_available(game_state)
        role_icon = "👑" if role_available else "🔒"

        print("1. ⚔️ Управление боевыми группами")
        print("2. 👥 Просмотреть всех героев")
        print(f"3. {role_icon} Управление ролями героев")
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
            manage_parties(game_state)
        elif choice == 2:
            from ui.party_manager import view_party
            view_party(game_state)
        elif choice == 3:
            manage_roles(game_state)
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()