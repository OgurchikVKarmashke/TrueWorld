# systems.storage_system.py
from systems.items_system import Item, ItemManager

class StorageSystem:
    def __init__(self, initial_capacity=50):
        self.capacity = initial_capacity
        self.items = {}  # item_id: Item
        self.item_manager = ItemManager()
    
    def add_item(self, item: Item) -> bool:
        if len(self.items) >= self.capacity and item.id not in self.items:
            return False
        
        if item.stackable and item.id in self.items:
            # Увеличиваем количество существующего предмета
            existing = self.items[item.id]
            if existing.quantity + item.quantity <= existing.max_stack:
                existing.quantity += item.quantity
                return True
            else:
                # Не помещается в один стек, пробуем создать новый
                if len(self.items) < self.capacity:
                    remaining = existing.max_stack - existing.quantity
                    existing.quantity = existing.max_stack
                    new_item = self.item_manager.create_item(item.id, item.quantity - remaining)
                    self.items[item.id + "_extra"] = new_item  # Уникальный ID для дополнительного стека
                    return True
                return False
        else:
            # Добавляем новый предмет
            self.items[item.id] = item
            return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        if item_id not in self.items:
            return False
        
        item = self.items[item_id]
        if item.stackable:
            if item.quantity > quantity:
                item.quantity -= quantity
                return True
            elif item.quantity == quantity:
                del self.items[item_id]
                return True
            else:
                return False
        else:
            del self.items[item_id]
            return True
    
    def get_items_by_type(self, item_type: str) -> dict:
        return {id: item for id, item in self.items.items() 
                if item.item_type.value == item_type}
    
    def get_item_count(self) -> int:
        return sum(item.quantity for item in self.items.values())
    
    def has_space(self) -> bool:
        return self.get_item_count() < self.capacity
    
    def upgrade_capacity(self, additional_slots: int) -> None:
        self.capacity += additional_slots