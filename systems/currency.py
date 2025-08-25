# currency.py
class Wallet:
    def __init__(self, gold=100, crystals=0):
        self.gold = gold
        self.crystals = crystals

    def add_gold(self, amount):
        self.gold += amount

    def subtract_gold(self, amount, check_only=False):
        if check_only:
            return self.gold >= amount
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def subtract_crystals(self, amount, check_only=False):
        if check_only:
            return self.crystals >= amount
        if self.crystals >= amount:
            self.crystals -= amount
            return True
        return False

    def __str__(self):
        return f"Золото: {self.gold} | Кристаллы: {self.crystals}"