# systems.difficulty_system.py

class DifficultySystem:
    @staticmethod
    def calculate_difficulty(hero_power, monster_power):
        ratio = monster_power / max(hero_power, 1)
        if ratio < 0.7:
            return "легко", "🟢"
        elif ratio < 1.2:
            return "средне", "🟡"
        else:
            return "тяжело", "🔴"