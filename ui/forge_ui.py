# ui.forge_ui.py
from ui.ui_utils import print_header, press_enter_to_continue, loading_screen

def forge_menu(game_state):
    storage = game_state["storage"]
    crafting = game_state["crafting_system"]
    forge = game_state["buildings"].get_building("forge")
    
    if not forge or forge.level == 0:
        print("Кузница не построена!")
        press_enter_to_continue()
        return
    
    while True:
        print_header("⚒️ Кузница")
        print(f"Уровень кузницы: {forge.level}")
        print()
        
        available_recipes = crafting.get_available_recipes(storage, forge.level)
        
        if not available_recipes:
            print("Нет доступных рецептов для крафта!")
            print("Улучшайте кузницу и собирайте материалы.")
            print()
        else:
            print("=== Доступные рецепты ===")
            for i, (recipe_id, recipe) in enumerate(available_recipes, 1):
                result_item = crafting.item_manager.get_item(recipe.result_id)
                print(f"{i}. {result_item.name} (Ур. кузницы: {recipe.required_forge_level})")
                print("   Материалы:")
                for mat_id, quantity in recipe.materials.items():
                    mat_item = crafting.item_manager.get_item(mat_id)
                    has_quantity = storage.items[mat_id].quantity if mat_id in storage.items else 0
                    status = "✅" if has_quantity >= quantity else "❌"
                    print(f"   {status} {mat_item.name} x{quantity} (есть: {has_quantity})")

                # После вывода материалов добавь:
                success_chance = crafting.get_crafting_success_chance(game_state, recipe_id)
                print(f"   Шанс успеха: {success_chance*100:.0f}%")

        print("0. Назад")
        print()
        
        try:
            choice = input("Выберите рецепт для крафта: ")
            
            if choice == "0":
                break
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(available_recipes):
                recipe_id, recipe = available_recipes[choice_idx]
                
                if crafting.craft(recipe_id, storage, forge.level, game_state):
                    result_item = crafting.item_manager.get_item(recipe.result_id)
                    loading_screen(2, f"Кузнец работает над {result_item.name}...")
                    print(f"Успешно создано: {result_item.name} x{recipe.result_quantity}!")
                else:
                    print("Не удалось создать предмет!")
                
                press_enter_to_continue()
                
        except (ValueError, IndexError):
            print("Неверный выбор!")
            press_enter_to_continue()