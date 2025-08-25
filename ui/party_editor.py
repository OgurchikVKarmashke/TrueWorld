#party_editor.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen

def manage_parties(game_state):
    """
    Редактор боевых групп
    """
    from systems.party_system import PartySystem
    party_system = PartySystem(game_state)
    
    while True:
        print_header("⚔️ Управление боевыми группами")
        print(f"🏰 Текущий этаж: {game_state['tower_level']}")
        print(f"📊 Доступно групп: {len(party_system.parties)}/{party_system.max_parties}")
        print()
        
        # Показываем текущие группы
        for i, (party_id, party_data) in enumerate(party_system.parties.items(), 1):
            party_heroes = party_system.get_party_heroes(party_id)
            status = "✅" if party_data["is_unlocked"] else "🔒"
            print(f"{i}. {status} {party_data['name']}")
            print(f"   👥 Героев: {len(party_heroes)}/5")
            for hero in party_heroes:
                print(f"   - {hero.name} (Ур. {hero.level})")
            print()
        
        # Опции меню
        if len(party_system.parties) < party_system.max_parties:
            print(f"{len(party_system.parties) + 1}. 🆕 Создать новую группу")
        
        print("0. ↩️ Назад")
        print()
        
        try:
            choice = int(input("🎯 Ваш выбор: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        elif choice <= len(party_system.parties):
            # Редактирование существующей группы
            party_id = list(party_system.parties.keys())[choice - 1]
            edit_party(game_state, party_system, party_id)
        elif choice == len(party_system.parties) + 1 and choice <= party_system.max_parties:
            # Создание новой группы
            create_new_party(game_state, party_system)
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()

def edit_party(game_state, party_system, party_id):
    """Редактирование конкретной группы"""
    while True:
        party = party_system.parties[party_id]
        party_heroes = party_system.get_party_heroes(party_id)
        available_heroes = party_system.get_available_heroes(party_id)
        
        print_header(f"⚔️ Редактирование: {party['name']}")
        
        # Верхний блок: текущие герои группы
        print("Текущий состав:")
        for i, hero in enumerate(party_heroes, 1):
            # Показываем роль героя, если он назначен
            role = ""
            if hasattr(game_state.get("role_system", None), 'get_hero_role'):
                hero_role = game_state["role_system"].get_hero_role(hero)
                if hero_role:
                    role = f" - {hero_role}"
            print(f"{i}. {hero.name} (Ур. {hero.level}){role} - ❤️{hero.health_current}/{hero.health_max}")
        print()
        
        # Нижний блок: доступные герои
        if available_heroes:
            print("Доступные герои для добавления:")
            for i, hero in enumerate(available_heroes, 1):
                print(f"{len(party_heroes)+i}. ➕ {hero.name} (Ур. {hero.level})")
            print()
        else:
            print("❌ Все герои заняты в других группах или на ролях")
            print()
        
        print("0. ↩️ Назад\n")
        
        try:
            choice = int(input("🎯 Выберите героя для удаления или добавления: "))
        except ValueError:
            press_enter_to_continue()
            continue
        
        if choice == 0:
            break
        elif 1 <= choice <= len(party_heroes):
            # Удаление героя из группы
            hero = party_heroes[choice - 1]
            if party_system.remove_hero_from_party(party_id, hero):
                print(f"❌ {hero.name} удален из группы")
            press_enter_to_continue()
        elif len(party_heroes) < choice <= len(party_heroes) + len(available_heroes):
            # Добавление героя в группу
            if len(party_heroes) >= 5:
                print("❌ Группа уже полная (5/5)")
                press_enter_to_continue()
                continue
                
            hero = available_heroes[choice - len(party_heroes) - 1]
            if party_system.add_hero_to_party(party_id, hero):
                print(f"✅ {hero.name} добавлен в группу")
            press_enter_to_continue()
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()

def create_new_party(game_state, party_system):
    """Создание новой группы"""
    if not party_system.can_unlock_new_party():
        print("❌ Достигнут лимит групп!")
        press_enter_to_continue()
        return
    
    print_header("🆕 Создание новой группы")
    party_name = input("Введите название группы: ").strip()
    
    if not party_name:
        print("❌ Название не может быть пустым!")
        press_enter_to_continue()
        return
    
    if party_system.unlock_new_party(party_name):
        loading_screen(2, "Создание группы")
        print(f"✅ Группа '{party_name}' создана!")
    else:
        print("❌ Ошибка создания группы!")
    
    press_enter_to_continue()