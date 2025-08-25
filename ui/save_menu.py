#save_menu.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from datetime import datetime

def save_menu(game_state):
    """
    Меню сохранения игры (один слот)
    """
    while True:
        print_header("💾 Меню сохранений")
        
        # Показываем информацию о сохранении
        save_info = game_state["save_system"].get_save_info(1)
        if save_info:
            time = datetime.fromisoformat(save_info["timestamp"]).strftime("%d.%m.%Y %H:%M")
            print("📁 Единственный слот сохранения:")
            print(f"   🏰 Этаж: {save_info['tower_level']}")
            print(f"   🕒 Время: {time}")
            print(f"   👥 Героев: {save_info['hero_count']}")
            print(f"   💰 Золото: {save_info['gold']}")
        else:
            print("📁 Слот сохранения - Пусто")
            print("   ℹ️ Сохраните игру чтобы создать файл сохранения")
        print()
        
        print("1. 💾 Сохранить игру")
        if save_info:
            print("2. 🔄 Загрузить игру")
        print("0. ↩️ Назад")
        print()
        
        try:
            choice = int(input("🎯 Ваш выбор: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        elif choice == 1:
            # Сохранение игры
            if game_state["save_system"].save_game(game_state, 1):
                loading_screen(2, "💾 Сохранение игры")
                print("✅ Игра успешно сохранена!")
            else:
                print("❌ Ошибка сохранения!")
            press_enter_to_continue()
        elif choice == 2 and save_info:
            # Загрузка сохранения
            if game_state["save_system"].load_game(game_state, 1):
                loading_screen(2, "🔄 Загрузка игры")
                print("✅ Игра успешно загружена!")
            else:
                print("❌ Ошибка загрузки!")
            press_enter_to_continue()
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()