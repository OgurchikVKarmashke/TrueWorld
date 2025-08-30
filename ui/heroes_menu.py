# ui.heroes_menu.py
from ui.ui_utils import print_header, press_enter_to_continue

def heroes_menu(game_state):
    """Меню управления героями"""
    
    # ДОБАВИТЬ: Очистка групп при входе в меню героев
    from systems.party_system import PartySystem
    PartySystem(game_state).cleanup_dead_heroes()

    while True:
        print_header("🎯 Управление героями")

        # Проверяем доступность системы ролей для отображения иконки
        role_available = 'role_system' in game_state and game_state['role_system'] is not None
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
            from ui.party_editor import manage_parties
            manage_parties(game_state)
        elif choice == 2:
            from ui.party_manager import view_party
            view_party(game_state)
        elif choice == 3:
            from ui.role_manager import manage_roles
            manage_roles(game_state)
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()