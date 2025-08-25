# main_loop.py
from ui.ui_utils import clear_screen, loading_screen, print_header
from game_data.game_state import game_state
from ui.tower_menu import tower_menu
from ui.heroes_menu import heroes_menu
from ui.buildings_menu import buildings_menu
from systems.hero_system import Hero

def initialize_game():
    """Инициализирует игру с возможностью загрузки"""
    print_header("🏝️ Летающий остров - Загрузка")
    
    # Проверяем наличие сохранений
    save_info = game_state["save_system"].get_save_info(1)
    if save_info:
        print("💾 Обнаружено сохранение:")
        print(f"   Этаж: {save_info['tower_level']}")
        print(f"   Героев: {save_info['hero_count']}")
        print(f"   Золото: {save_info['gold']}")
        print(f"   Время: {save_info['timestamp'][:10]}")
        print("\n1. 🎮 Продолжить игру")
        print("2. 🆕 Новая игра")
        
        try:
            choice = int(input("\n🎯 Ваш выбор: "))
            if choice == 1:
                if game_state["save_system"].load_game(game_state, 1):
                    loading_screen(2, "Загрузка сохранения")
                    print("✅ Игра загружена!")
                    return True
                else:
                    print("❌ Ошибка загрузки!")
                    loading_screen(1)
        except ValueError:
            pass
    
    # Новая игра
    loading_screen(2, "Создание нового мира")
    return True

def check_new_unlocks(game_state):
    """Проверяет и показывает новые возможности после прохождения этажей"""
    tower_level = game_state["tower_level"]
    unlocks = []
    
    # Проверяем исследования
    research_mgr = game_state["research"]
    for research_key, research in research_mgr.researches.items():
        if research.level < research.max_level:
            next_level = research.level + 1
            if next_level <= len(research.reveal_floors):
                required_floor = research.reveal_floors[next_level - 1]
                if tower_level >= required_floor and (research.level == 0 or research.level < next_level):
                    unlocks.append(f"🔬 Исследование: {research.name} ур.{next_level}")
    
    # Проверяем здания
    buildings = game_state["buildings"].buildings
    building_unlocks = {
        3: "🏪 Столовая (уровень 1)",
        5: "🔬 Лаборатория (уровень 1)", 
        7: "⚒️ Кузница (уровень 1)",
        10: "🌟 Комната возвышения (уровень 1)",
        15: "⚗️ Улучшенная комната синтеза"
    }
    
    for floor, building_name in building_unlocks.items():
        if tower_level >= floor:
            unlocks.append(f"🏗️ {building_name}")
    
    return unlocks

def main_menu():
    """Главное меню игры"""
    if not initialize_game():
        return
    
    while True:
        # Проверяем разблокировку зданий
        game_state["buildings"].unlock_buildings(game_state["tower_level"])
        
        print_header("🏝️ Летающий остров - Центральное лобби")
        
        # Отображаем основную информацию
        wallet = game_state["wallet"]
        print(f"💰 {wallet}")
        print(f"🏰 Этаж башни: {game_state['tower_level']}")
        
        # Проверяем новые возможности
        new_unlocks = check_new_unlocks(game_state)
        if new_unlocks:
            print("🎉 НОВЫЕ ВОЗМОЖНОСТИ:")
            for unlock in new_unlocks:
                print(f"   {unlock}")
            print()

        dormitory = game_state["buildings"].get_building("dormitory")
        hero_count = len(game_state["heroes"])
        max_capacity = dormitory.get_capacity()
        print(f"👥 Герои: {hero_count}/{max_capacity}")
        print()
        
        # НОВОЕ МЕНЮ
        print("1. 🏰 Башня испытаний")
        print("2. 🎯 Герои")
        print("3. 🏛️ Здания")
        print("4. 💾 Сохранения")
        print("0. 🚪 Выйти из игры")
        print()
        
        try:
            choice = int(input("🎯 Ваш выбор: "))
        except ValueError:
            loading_screen(1, "❌ Ошибка ввода")
            continue
        
        if choice == 1:
            loading_screen(1.5, "🌀 Переход")
            tower_menu(game_state)
        elif choice == 2:
            heroes_menu(game_state)
        elif choice == 3:
            loading_screen(1.5, "🌀 Переход")
            buildings_menu(game_state)
        elif choice == 4:
            from ui.save_menu import save_menu
            save_menu(game_state)
        elif choice == 0:
            loading_screen(1.5, "🌀 Переход")
            print_header("👋 До свидания!")
            print("✨ Спасибо что играли в TrueWorld! Мы ждём вашего возвращения, мастер!")
            break
        else:
            loading_screen(1, "❌ Неверный выбор")

if __name__ == "__main__":
  main_menu()