# ui.storage_ui.py
from ui.ui_utils import print_header, press_enter_to_continue
from systems.items_system import ItemType

def storage_menu(game_state):
    storage = game_state["storage"]
    
    while True:
        print_header("📦 Склад")
        print(f"Вместимость: {storage.get_item_count()}/{storage.capacity}")
        print()
        
        if not storage.items:
            print("Склад пуст!")
            print()
            print("1. Получить тестовые предметы")
            print("0. Назад")
        else:
            # Группируем предметы по типам
            item_types = {
                "Материалы": storage.get_items_by_type("Материал"),
                "Оружие": storage.get_items_by_type("Оружие"),
                "Броня": storage.get_items_by_type("Броня"),
                "Аксессуары": storage.get_items_by_type("Аксессуар")
            }
            
            for category, items in item_types.items():
                if items:
                    print(f"=== {category} ===")
                    for item_id, item in items.items():
                        if item.stackable:
                            print(f"• {item.name} x{item.quantity} - {item.rarity.value}")
                        else:
                            print(f"• {item.name} - {item.rarity.value}")
                    print()
            
            print("0. Назад")
        
        try:
            choice = input("Ваш выбор: ")
            
            if choice == "0":
                break
            elif choice == "1" and not storage.items:
                # Добавляем тестовые предметы
                from systems.items_system import ItemManager
                item_manager = ItemManager()
                
                test_items = [
                    item_manager.create_item("iron_ore", 10),
                    item_manager.create_item("steel_bar", 3),
                    item_manager.create_item("magic_crystal", 1),
                    item_manager.create_item("iron_sword", 1)
                ]
                
                for item in test_items:
                    storage.add_item(item)
                
                print("Тестовые предметы добавлены!")
                press_enter_to_continue()
                
        except ValueError:
            press_enter_to_continue()