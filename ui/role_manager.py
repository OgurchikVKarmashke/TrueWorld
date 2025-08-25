#role_manager.py
from ui.ui_utils import print_header, press_enter_to_continue

from ui.ui_utils import print_header, press_enter_to_continue, loading_screen

def manage_roles(game_state):
    """Меню управления ролями героев"""
    # Проверяем, доступна ли система ролей
    if not is_role_system_available(game_state):
        print_header("👑 Управление ролями героев")
        print("❌ Система ролей недоступна!")
        print()
        print("Для назначения ролей необходимо построить:")
        print("🍳 Столовую (доступна с 7 этажа)")
        print("⚒️ Кузницу (доступна с 10 этажа)") 
        print("🔬 Лабораторию (доступна с 5 этажа)")
        print()
        print("Отправляйтесь в башню, чтобы открыть новые этажи!")
        press_enter_to_continue()
        return
    
    from systems.role_system import RoleSystem
    role_system = init_role_system(game_state)
    
    while True:
        print_header("👥 Управление ролями героев")
        
        # Показываем текущие назначения
        assigned_heroes = role_system.get_assigned_heroes()
        available_heroes = role_system.get_available_heroes()
        
        print("📋 Текущие назначения:")
        print("═" * 40)
        
        has_assignments = False
        for role_name, role_info in role_system.roles.items():
            building = game_state["buildings"].get_building(role_info['building'])
            if building.built:
                assigned_hero = assigned_heroes.get(role_info['building'])
                if assigned_hero:
                    print(f"{role_info['title']}: ✅ {assigned_hero.name}")
                    has_assignments = True
                else:
                    print(f"{role_info['title']}: ❌ Не назначен")
            else:
                print(f"{role_info['title']}: 🔒 Здание не построено")
        
        print()
        print("👥 Доступные герои:")
        print("═" * 40)
        
        if available_heroes:
            for i, hero in enumerate(available_heroes, 1):
                print(f"{i}. {hero.name} (Ур. {hero.level})")
        else:
            print("❌ Нет доступных героев")
            print("Все герои заняты в группах или на других ролях")
        
        print()
        print("1. 📝 Назначить героя на роль")
        print("2. 🗑️ Снять героя с роли")
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
            assign_hero_to_role(game_state, role_system, available_heroes)
        elif choice == 2:
            remove_hero_from_role(game_state, role_system, assigned_heroes)
        else:
            print("❌ Неверный выбор!")
            press_enter_to_continue()

def is_role_system_available(game_state):
    """Проверяет, доступна ли система ролей (построены ли нужные здания)"""
    buildings = game_state["buildings"].buildings
    # Система ролей доступна, если построена хотя бы одно здание с ролью
    return (buildings["canteen"].built or 
            buildings["forge"].built or 
            buildings["laboratory"].built)

def init_role_system(game_state):
    """Инициализирует систему ролей"""
    if game_state["role_system"] is None:
        from systems.role_system import RoleSystem
        game_state["role_system"] = RoleSystem(game_state)
    
    return game_state["role_system"]

def assign_hero_to_role(game_state, role_system, available_heroes):
    """Назначение героя на роль"""
    if not available_heroes:
        print("❌ Нет доступных героев для назначения!")
        press_enter_to_continue()
        return
    
    print_header("📝 Назначение героя на роль")
    
    # Выбор роли
    print("Выберите роль:")
    roles_list = []
    for i, (role_name, role_info) in enumerate(role_system.roles.items(), 1):
        building = game_state["buildings"].get_building(role_info['building'])
        if building.built:
            print(f"{i}. {role_info['title']} - {role_info['bonus']}")
            roles_list.append((role_name, role_info))
    
    if not roles_list:
        print("❌ Нет доступных ролей!")
        press_enter_to_continue()
        return
    
    try:
        role_choice = int(input("🎯 Выберите роль: "))
        if not 1 <= role_choice <= len(roles_list):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор!")
        press_enter_to_continue()
        return
    
    role_name, role_info = roles_list[role_choice - 1]
    
    # Выбор героя
    print(f"\nВыберите героя для роли {role_info['title']}:")
    for i, hero in enumerate(available_heroes, 1):
        print(f"{i}. {hero.name} (Ур. {hero.level})")
    
    try:
        hero_choice = int(input("🎯 Выберите героя: "))
        if not 1 <= hero_choice <= len(available_heroes):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор!")
        press_enter_to_continue()
        return
    
    hero = available_heroes[hero_choice - 1]
    
    # Назначение
    success, message = role_system.assign_hero(role_name, hero)
    print(message)
    press_enter_to_continue()

def remove_hero_from_role(game_state, role_system, assigned_heroes):
    """Снятие героя с роли"""
    if not assigned_heroes:
        print("❌ Нет назначенных героев!")
        press_enter_to_continue()
        return
    
    print_header("🗑️ Снятие героя с роли")
    
    # Создаем список назначений
    assignments = []
    for building_name, hero in assigned_heroes.items():
        for role_name, role_info in role_system.roles.items():
            if role_info['building'] == building_name:
                assignments.append((role_name, role_info, hero))
    
    for i, (role_name, role_info, hero) in enumerate(assignments, 1):
        print(f"{i}. {role_info['title']}: {hero.name}")
    
    try:
        choice = int(input("🎯 Выберите назначение для удаления: "))
        if not 1 <= choice <= len(assignments):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор!")
        press_enter_to_continue()
        return
    
    role_name, role_info, hero = assignments[choice - 1]
    role_system.remove_hero_from_all_roles(hero)
    print(f"✅ {hero.name} снят с роли {role_info['title']}!")
    press_enter_to_continue()