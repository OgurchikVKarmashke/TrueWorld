# systems.crafting_system.py
from typing import Dict, List
from systems.items_system import Item, ItemManager

class Recipe:
    def __init__(self, result_id: str, result_quantity: int = 1, 
                 materials: Dict[str, int] = None, required_forge_level: int = 1):
        self.result_id = result_id
        self.result_quantity = result_quantity
        self.materials = materials or {}
        self.required_forge_level = required_forge_level

class CraftingSystem:
    def __init__(self):
        self.recipes = {}
        self.item_manager = ItemManager()
        self.initialize_recipes()
    
    def initialize_recipes(self):
        self.recipes = {
            "steel_bar": Recipe(
                "steel_bar", 1,
                {"iron_ore": 3}, 1
            ),
            "iron_sword": Recipe(
                "iron_sword", 1,
                {"iron_ore": 5, "steel_bar": 2}, 2
            ),
            "steel_sword": Recipe(
                "steel_sword", 1,
                {"steel_bar": 5, "magic_crystal": 1}, 3
            ),
        }
    
    def can_craft(self, recipe_id: str, storage, forge_level: int) -> bool:
        if recipe_id not in self.recipes:
            return False
        
        recipe = self.recipes[recipe_id]
        if forge_level < recipe.required_forge_level:
            return False
        
        for material_id, quantity in recipe.materials.items():
            if material_id not in storage.items or storage.items[material_id].quantity < quantity:
                return False
        
        return storage.has_space()
    
    def craft(self, recipe_id: str, storage, forge_level: int, game_state=None) -> bool:
        if not self.can_craft(recipe_id, storage, forge_level):
            return False
        
        recipe = self.recipes[recipe_id]
        success_chance = self.get_crafting_success_chance(game_state, recipe_id) if game_state else 1.0
        
        import random
        success = random.random() <= success_chance
        
        # Удаляем материалы в любом случае
        for material_id, quantity in recipe.materials.items():
            # При неудаче удаляем только половину материалов
            remove_quantity = quantity if success else max(1, quantity // 2)
            storage.remove_item(material_id, remove_quantity)
        
        # Добавляем результат только при успехе
        if success:
            result_item = self.item_manager.create_item(recipe.result_id, recipe.result_quantity)
            if not storage.add_item(result_item):
                print("Недостаточно места на складе!")
                return False
        
        return success
    
    def get_available_recipes(self, storage, forge_level: int) -> List[Recipe]:
        """Возвращает доступные рецепты для крафта"""
        available = []
        for recipe_id, recipe in self.recipes.items():
            if self.can_craft(recipe_id, storage, forge_level):
                available.append((recipe_id, recipe))
        return available

    def get_crafting_success_chance(self, game_state, recipe_id: str) -> float:
        """Возвращает шанс успешного крафта с учетом бонусов"""
        base_chance = 1.0  # 100% базовый шанс
        
        # Проверяем, есть ли кузнец в кузнице
        forge = game_state["buildings"].get_building("forge")
        if forge and hasattr(forge, 'assigned_hero') and forge.assigned_hero:
            # Кузнец дает +15% к шансу успеха
            base_chance += 0.15
        
        # Дополнительные бонусы можно добавить здесь
        # Например, от уровня кузницы, навыков героя и т.д.
        
        return min(base_chance, 1.0)  # Не больше 100%