# systems/combat_modifiers/skills/boss_skills.py
"""
Навыки боссов.
"""

import random
from .skill_system import Skill
from typing import List, Dict, Any

class FireBreathSkill(Skill):
    """Огненное дыхание Дракона"""
    
    def __init__(self):
        super().__init__(name="Огненное дыхание", mana_cost=30, cooldown=3)
        self.damage_multiplier = 1.8
    
    def use(self, caster, targets: List) -> Dict[str, Any]:
        """Наносит урон всем целям"""
        results = []
        damage = int(caster.attack * self.damage_multiplier)
        
        for target in targets:
            if hasattr(target, 'is_alive') and target.is_alive:
                result = target.take_damage(damage // 2)
                results.append(f"{target.name}: {result}")
        
        caster.mana_current -= self.mana_cost
        self.current_cooldown = self.cooldown
        
        return {
            "message": f"{caster.name} использует {self.name}!\n" + "\n".join(results),
            "damage_dealt": damage,
            "targets_hit": len([t for t in targets if hasattr(t, 'is_alive') and t.is_alive])
        }

class ShadowBladeSkill(Skill):
    """Теневой клинок Повелителя Теней"""
    
    def __init__(self):
        super().__init__(name="Теневой клинок", mana_cost=25, cooldown=2)
        self.damage_multiplier = 1.6
    
    def use(self, caster, targets: List) -> Dict[str, Any]:
        """Наносит урон одной цели, игнорируя часть защиты"""
        alive_targets = [t for t in targets if hasattr(t, 'is_alive') and t.is_alive]
        if not alive_targets:
            return {"message": "Нет целей для атаки!", "damage_dealt": 0}
        
        target = random.choice(alive_targets)
        damage = int(caster.attack * self.damage_multiplier)
        
        # Игнорируем половину защиты цели
        if hasattr(target, 'defense'):
            effective_defense = target.defense // 2
            actual_damage = max(1, damage - effective_defense)
        else:
            actual_damage = damage
        
        old_health = getattr(target, 'health_current', 0)
        target.health_current -= actual_damage
        
        message = f"{caster.name} использует {self.name} на {target.name}!\n"
        if target.health_current <= 0:
            target.is_alive = False
            message += f"{target.name} повержен!"
        else:
            message += f"{target.name} получает {actual_damage} урона. Осталось {target.health_current} HP."
        
        caster.mana_current -= self.mana_cost
        self.current_cooldown = self.cooldown
        
        return {
            "message": message,
            "damage_dealt": actual_damage,
            "target": target
        }

class SummonShadowsSkill(Skill):
    """Призыв теней"""
    
    def __init__(self):
        super().__init__(name="Призыв теней", mana_cost=40, cooldown=4)
    
    def use(self, caster, targets: List) -> Dict[str, Any]:
        """Призывает помощников (пока только сообщение)"""
        caster.mana_current -= self.mana_cost
        self.current_cooldown = self.cooldown
        
        return {
            "message": f"{caster.name} использует {self.name}! Появляются теневые прислужники...",
            "summon_count": 2
        }

# Словарь навыков боссов
BOSS_SKILLS = {
    "Древний Дракон": [FireBreathSkill()],
    "Повелитель Теней": [ShadowBladeSkill(), SummonShadowsSkill()],
    "Король Лич": []  # Пока пусто, добавим позже
}