# main_loop.py
from game_data.game_state import game_state, init_save_system 
from systems.hero_system import Hero
from systems.achievement_system import AchievementSystem
from systems.party_system import PartySystem
from ui.achievements_menu import achievements_menu
from ui.tower_menu import tower_menu
from ui.heroes_menu import heroes_menu
from ui.buildings_menu import buildings_menu
from ui.ui_utils import clear_screen, loading_screen, print_header

def initialize_game():
    """Инициализирует игру с возможностью загрузки"""
    print_header("🏝️ Летающий остров - Загрузка")
    game_state["achievement_system"] = AchievementSystem()

    # Инициализируем систему сохранений
    save_system = init_save_system()  # Сохраняем в переменную

    # Проверяем наличие сохранений
    save_info = save_system.get_save_info(1)  # Используем save_system вместо init_save_system()
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
                if save_system.load_game(game_state, 1):  # Используем save_system
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
    """Проверяет и показывает новые возможности"""
    tower_level = game_state["tower_level"]
    unlocks = []
    
    # Проверяем исследования
    research_mgr = game_state["research"]
    for research_key, research in research_mgr.researches.items():
        if research.level < research.max_level:
            next_level = research.level + 1
            if next_level <= len(research.reveal_floors):
                required_floor = research.reveal_floors[next_level - 1]
                if tower_level >= required_floor and research.level < next_level:
                    unlocks.append(f"🔬 Исследование: {research.name} ур.{next_level}")
    
    # Проверяем здания (только непостроенные)
    building_manager = game_state["buildings"]
    building_manager.unlock_buildings(tower_level)  # Обновляем статус разблокировки
    
    for building in building_manager.buildings.values():
        if (tower_level >= building.unlock_floor and 
            not building.built and 
            building.level == 0 and
            building.unlocked):
            unlocks.append(f"🏗️ {building.name} (доступно для постройки)")
    
    return unlocks

def main_menu():
    """Главное меню игры"""
    if not initialize_game():
        return
    
    while True:
        # Разблокируем здания при достижении этажей
        game_state["buildings"].unlock_buildings(game_state["tower_level"])
        
        # Проверяем достижения
        achievement_system = game_state["achievement_system"]
        new_achievements = achievement_system.check_building_achievements(game_state)

        print_header("🏝️ Летающий остров - Центральное лобби")
        
        # Отображаем основную информацию
        wallet = game_state["wallet"]
        print(f"💰 {wallet}")
        print(f"🏰 Этаж башни: {game_state['tower_level']}")
        
        # Показываем только НЕПРОСМОТРЕННЫЕ достижения
        unviewed_achievements = achievement_system.get_unviewed_achievements()
        completed_count = achievement_system.get_completed_count()
        
        if unviewed_achievements:
            print(f"🏆 Новые достижения: {len(unviewed_achievements)}")
            for ach in unviewed_achievements[:2]:  # Показываем максимум 2
                print(f"   ⭐ {ach.name}")
        elif completed_count > 0:
            print(f"🏆 Достижения: {completed_count}/? (все просмотрены)")

        # Проверяем новые возможности (только непостроенные здания)
        new_unlocks = check_new_unlocks(game_state)
        if new_unlocks:
            print("🎉 НОВЫЕ ВОЗМОЖНОСТИ:")
            for unlock in new_unlocks:
                print(f"   {unlock}")
            print()

        # Очищаем мертвых героев из групп
        party_system = PartySystem(game_state)
        party_system.cleanup_dead_heroes()
        
        # Очищаем мертвых героев с ролей
        if game_state.get("role_system") is not None:
            game_state["role_system"].cleanup_dead_heroes()

        dormitory = game_state["buildings"].get_building("dormitory")
        
        living_heroes = [h for h in game_state["heroes"] if h.is_alive]
        hero_count = len(living_heroes)
        max_capacity = dormitory.get_capacity()
        print(f"👥 Герои: {hero_count}/{max_capacity}")

        print()
        
        # Меню
        print("1. 🏰 Башня испытаний")
        print("2. 🎯 Герои")
        print("3. 🏛️ Здания")
        print("4. 💾 Сохранения")
        print("5. 🏆 Достижения")
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

        elif choice == 5:
            achievements_menu(game_state)

        elif choice == 0:
            loading_screen(1.5, "🌀 Переход")
            print_header("👋 До свидания!")
            print("✨ Спасибо что играли в TrueWorld! Мы ждём вашего возвращения, мастер!")
            break

        else:
            loading_screen(0.5, "❌ Неверный выбор")

if __name__ == "__main__":
  main_menu()