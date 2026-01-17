# ui.role_manager.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen

def manage_roles(game_state):
    """Меню управления ролями героев"""
    # Проверяем, доступна ли система ролей
    if not is_role_system_available(game_state):
        print_header("👑 Управление ролями героев")
        print("❌ Система ролей недоступна!")
        print()
        print("Для назначения ролей необходимо построить:")
        print("🍳 Столовую (доступна с 3 этажа)")
        print("🔬 Лабораторию (доступна с 5 этажа)")
        print("⚒️ Кузницу (доступна с 7 этажа)")
        print()
        print("Взбирайтесь по башне, чтобы разблокировать новые функции!")
        press_enter_to_continue()
        return
    
    from systems.role_system import RoleSystem
    role_system = init_role_system(game_state)
    
    while True:
        print_header("👥 Управление ролями героев")
        
        # Используем существующий метод get_assigned_heroes()
        assigned_heroes = role_system.get_assigned_heroes()
        available_heroes = role_system.get_available_heroes()
        
        print("📋 Текущие назначения:")
        print("═" * 40)
        
        # Изменим порядок ролей:
        roles_in_order = [
            ('cook', '🍳 Повар', 'Увеличивает получаемый опыт'),
            ('researcher', '🔬 Исследователь', 'Ускоряет исследования'),
            ('blacksmith', '⚒️ Кузнец', 'Увеличивает шанс успеха крафта')
        ]
        
        has_assignments = False
        for i, (role_name, title, bonus) in enumerate(roles_in_order, 1):
            role_info = role_system.roles[role_name]
            building = game_state["buildings"].get_building(role_info['building'])
            
            if building.built:
                # Ищем назначенного героя для этого здания
                assigned_hero = assigned_heroes.get(role_info['building'])
                if assigned_hero:
                    print(f"{i}. {title}: ✅ {assigned_hero.name} ({assigned_hero.level} ур.)")
                    has_assignments = True
                else:
                    print(f"{i}. {title}: ❌ Не назначен")
            else:
                print(f"{i}. {title}: 🔒 Здание не построено")
        
        print()
        print("👥 Доступные герои:")
        print("═" * 40)
        
        if available_heroes:
            for i, hero in enumerate(available_heroes, 1):
                role = role_system.get_hero_role(hero)
                if role:
                    print(f"{i}. {hero.name} (Ур. {hero.level}) - ⚠️ Уже назначен как {role}")
                else:
                    print(f"{i}. {hero.name} (Ур. {hero.level}) - ✅ Свободен")
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
            assign_hero_to_role(game_state, role_system, available_heroes, roles_in_order)
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
    if game_state.get("role_system") is None:
        from systems.role_system import RoleSystem
        game_state["role_system"] = RoleSystem(game_state)
    
    return game_state["role_system"]

def assign_hero_to_role(game_state, role_system, available_heroes, roles_in_order=None):
    """Назначение героя на роль"""
    if not available_heroes:
        print("❌ Нет доступных героев для назначения!")
        press_enter_to_continue()
        return
    
    print_header("📝 Назначение героя на роль")
    
    # Выбор роли
    print("Выберите роль:")
    
    # Используем переданный порядок ролей или стандартный
    if roles_in_order is None:
        roles_in_order = [
            ('cook', '🍳 Повар', 'Увеличивает получаемый опыт'),
            ('researcher', '🔬 Исследователь', 'Ускоряет исследования'),
            ('blacksmith', '⚒️ Кузнец', 'Увеличивает шанс успеха крафта')
        ]
    
    roles_list = []
    for i, (role_name, title, bonus) in enumerate(roles_in_order, 1):
        role_info = role_system.roles[role_name]
        building = game_state["buildings"].get_building(role_info['building'])
        
        if building.built:
            # Проверяем, занята ли уже эта роль
            assigned_hero = None
            for building_name, hero in role_system.get_assigned_heroes().items():
                if building_name == role_info['building']:
                    assigned_hero = hero
                    break
            
            if assigned_hero:
                print(f"{i}. {title} - ⚠️ Занято: {assigned_hero.name}")
            else:
                print(f"{i}. {title} - ✅ Свободно: {bonus}")
            
            roles_list.append((role_name, role_info, title, assigned_hero))
    
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
    
    role_name, role_info, title, assigned_hero = roles_list[role_choice - 1]
    
    # Если роль уже занята, спрашиваем подтверждение на замену
    if assigned_hero:
        print(f"\n⚠️ Роль {title} уже занята {assigned_hero.name}")
        print("1. Заменить героя")
        print("2. Отмена")
        
        try:
            replace_choice = int(input("🎯 Ваш выбор: "))
            if replace_choice != 1:
                print("❌ Отмена назначения!")
                press_enter_to_continue()
                return
        except ValueError:
            print("❌ Отмена!")
            press_enter_to_continue()
            return
    
    # Выбор героя (показываем только доступных)
    available_for_role = []
    for hero in available_heroes:
        # Пропускаем героя, который уже на этой роли (если заменяем)
        if assigned_hero and id(hero) == id(assigned_hero):
            continue
        if role_system.is_hero_available(hero):
            available_for_role.append(hero)
    
    if not available_for_role:
        print("❌ Нет доступных героев для этой роли!")
        press_enter_to_continue()
        return
    
    print(f"\nВыберите героя для роли {title}:")
    for i, hero in enumerate(available_for_role, 1):
        current_role = role_system.get_hero_role(hero)
        if current_role:
            print(f"{i}. {hero.name} (Ур. {hero.level}) - ⚠️ Текущая роль: {current_role}")
        else:
            print(f"{i}. {hero.name} (Ур. {hero.level}) - ✅ Свободен")
    
    try:
        hero_choice = int(input("🎯 Выберите героя: "))
        if not 1 <= hero_choice <= len(available_for_role):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор!")
        press_enter_to_continue()
        return
    
    hero = available_for_role[hero_choice - 1]
    
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
        # Находим информацию о роли для этого здания
        for role_name, role_info in role_system.roles.items():
            if role_info['building'] == building_name:
                assignments.append((role_name, role_info, hero))
                break
    
    if not assignments:
        print("❌ Нет назначенных героев!")
        press_enter_to_continue()
        return
    
    for i, (role_name, role_info, hero) in enumerate(assignments, 1):
        print(f"{i}. {role_info['title']}: {hero.name} (Ур. {hero.level})")
    
    try:
        choice = int(input("🎯 Выберите назначение для удаления: "))
        if not 1 <= choice <= len(assignments):
            raise ValueError
    except ValueError:
        print("❌ Неверный выбор!")
        press_enter_to_continue()
        return
    
    role_name, role_info, hero = assignments[choice - 1]
    removed = role_system.remove_hero_from_role(hero)
    if removed:
        print(f"✅ {hero.name} снят с роли {role_info['title']}!")
    else:
        print(f"❌ Не удалось снять {hero.name} с роли!")
    press_enter_to_continue()