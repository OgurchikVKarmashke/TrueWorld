# main_loop.py
from systems.hero_system import Hero
from systems.achievement_system import AchievementSystem
from systems.party_system import PartySystem
from ui.achievements_menu import achievements_menu
from ui.tower_menu import tower_menu
from ui.heroes_menu import heroes_menu
from ui.buildings_menu import buildings_menu
from ui.ui_utils import clear_screen, loading_screen, print_header
from app import app

def initialize_game():
    """Инициализирует игру с возможностью загрузки"""
    print_header("🏝️ Летающий остров - Загрузка")
    
    # Сначала проверяем сохранения ДО инициализации App
    save_system = app.save_system if hasattr(app, 'save_system') else None
    if not save_system:
        # Создаем временную систему сохранений для проверки
        from game_data.save_system import SaveSystem
        save_system = SaveSystem()
    
    save_info = save_system.get_save_info(1)
    
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
                # Загружаем сохранение напрямую в App
                loading_screen(2, "Загрузка сохранения")
                # После загрузки игры обновляем состояние app и получаем game_state
                if save_system.load_into_app(app, 1):
                    print("✅ Игра загружена!")
                    # Получаем состояние после загрузки
                    game_state = app.get_game_state_dict()
                    return game_state  # <-- ВАЖНО: добавить return здесь!
                else:
                    print("❌ Ошибка загрузки! Создаем новую игру...")
                    loading_screen(1)
                    # Если не удалось загрузить, создаем новую
                    app.initialize()
                    game_state = app.get_game_state_dict()
                    return game_state
            elif choice == 2:
                # Создаем новую игру
                game_state = app.start_new_game()
                save_system.save_game(game_state, 1)
                loading_screen(2, "Создание нового мира")
                return game_state
        except ValueError:
            pass  # Если ошибка ввода, продолжаем с новой игрой
    
    # Если сохранения нет или произошла ошибка - создаем новую игру
    game_state = app.start_new_game()
    
    # Сохраняем новую игру
    save_system = game_state["save_system"]
    save_system.save_game(game_state, 1)
    
    loading_screen(2, "Создание нового мира")
    return game_state

def _update_app_from_state(game_state):
    """Обновляет состояние App из загруженного game_state"""
    # Обновляем основные поля
    app.tower_level = game_state.get("tower_level", 1)
    app.max_tower_floor = game_state.get("max_tower_floor", 1)
    app.heroes = game_state.get("heroes", [])
    app.tower_monsters = game_state.get("tower_monsters", {})
    
    # Обновляем компоненты
    if "wallet" in game_state:
        app.wallet.gold = game_state["wallet"].gold
        app.wallet.crystals = game_state["wallet"].crystals
    
    if "buildings" in game_state:
        app.buildings = game_state["buildings"]
    
    if "research" in game_state:
        app.research = game_state["research"]
    
    if "party_system" in game_state:
        app._components['party_system'] = game_state["party_system"]
    
    if "storage" in game_state:
        app.storage = game_state["storage"]

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
    game_state = initialize_game()
    if not game_state:
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

        # Очищаем мертвых героев из групп
        party_system = PartySystem(game_state)
        dead_heroes_in_parties = party_system.cleanup_dead_heroes()

        # НОВОЕ: Удаляем мертвых героев из основного списка game_state
        if dead_heroes_in_parties:
            game_state["heroes"] = [h for h in game_state["heroes"] if h.is_alive]
            print(f"💀 Удалено {len(dead_heroes_in_parties)} мёртвых героев из списка")
        
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