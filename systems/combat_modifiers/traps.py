# systems.combat_modifiers.traps.py
from systems.combat_modifiers import register_modifier
import random

class TrapModifier:
    def __init__(self, trap_type):
        self.trap_type = trap_type
        self.traps = {
            "огненная_ловушка": {
                "damage": 0.3,
                "max_uses": 3,
                "description": "🔥 Огненная ловушка: 30% урона при атаке (макс. 3 раза)"
            },
            "ледяная_ловушка": {
                "slow": 0.4,
                "freeze_chance": 0.2,
                "max_uses": 2,
                "description": "❄️ Ледяная ловушка: -40% скорости, 20% шанс заморозки (макс. 2 раза)"
            },
            "ядовитая_ловушка": {
                "poison_damage": 0.1,
                "max_uses": 4,
                "description": "☠️ Ядовитая ловушка: 10% урона ядом каждый ход (макс. 4 раза)"
            },
            "электрическая_ловушка": {
                "stun_chance": 0.25,
                "max_uses": 2,
                "description": "⚡ Электрическая ловушка: 25% шанс оглушения (макс. 2 раза)"
            }
        }
        self.uses_remaining = 0
    
    def apply(self, combat_system):
        if self.trap_type in self.traps:
            trap = self.traps[self.trap_type]
            self.uses_remaining = trap["max_uses"]
            combat_system.trap_modifier = self  # Сохраняем для использования в бою
            return trap
        return {}
    
    def trigger_trap(self, target):
        """Активирует ловушку и возвращает сообщение о эффекте"""
        if self.uses_remaining <= 0:
            return None
        
        trap = self.traps[self.trap_type]
        self.uses_remaining -= 1
        
        if "damage" in trap:
            damage = int(target.health_max * trap["damage"])
            target.health_current = max(0, target.health_current - damage)
            return f"{target.name} активирует {self.trap_type}! Получает {damage} урона."
        
        elif "freeze_chance" in trap and random.random() < trap["freeze_chance"]:
            target.frozen = True
            return f"{target.name} активирует {self.trap_type}! Заморожен."
        
        elif "stun_chance" in trap and random.random() < trap["stun_chance"]:
            target.stunned = True
            return f"{target.name} активирует {self.trap_type}! Оглушен."
        
        return None

register_modifier("trap", TrapModifier)