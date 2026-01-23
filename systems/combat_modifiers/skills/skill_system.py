# systems/combat_modifiers/skills/skill_system.py
"""
Базовая система навыков для всех существ.
"""

import random
from typing import Dict, List, Any, Optional

class Skill:
    """Базовый класс навыка"""
    
    def __init__(self, **kwargs):
        """Инициализация навыка с параметрами"""
        self.name = kwargs.get('name', 'Неизвестный навык')
        self.mana_cost = kwargs.get('mana_cost', 0)
        self.cooldown = kwargs.get('cooldown', 0)
        self.current_cooldown = 0
        
    def can_use(self, caster) -> bool:
        """Проверяет, может ли кастер использовать навык"""
        if hasattr(caster, 'mana_current') and caster.mana_current < self.mana_cost:
            return False
        if self.current_cooldown > 0:
            return False
        return True
    
    def use(self, caster, targets: List) -> Dict[str, Any]:
        """Использование навыка"""
        raise NotImplementedError("Метод use должен быть реализован в дочернем классе")
    
    def update_cooldown(self):
        """Обновляет кулдаун"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class SkillSystem:
    """Система управления навыками"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
    
    def add_skill(self, skill: Skill):
        """Добавляет навык"""
        self.skills[skill.name] = skill
    
    def get_available_skills(self, caster) -> List[Skill]:
        """Возвращает доступные для использования навыки"""
        return [skill for skill in self.skills.values() if skill.can_use(caster)]
    
    def update_all_cooldowns(self):
        """Обновляет кулдауны всех навыков"""
        for skill in self.skills.values():
            skill.update_cooldown()