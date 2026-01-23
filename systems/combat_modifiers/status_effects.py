#systems/combat_modifiers/status_effects.py

import random
from enum import Enum
from typing import Dict, List, Optional, Callable, Any

"""
Система статус-эффектов для героев и монстров.
Используется для погоды, ловушек, навыков и других эффектов.
"""

class StatusEffectType(Enum):
    """Типы статус-эффектов"""
    POISON = "poison"           # Яд
    BURN = "burn"               # Горение
    FREEZE = "freeze"           # Заморозка
    STUN = "stun"               # Оглушение
    SLOW = "slow"               # Замедление
    WEAKNESS = "weakness"       # Слабость (снижение защиты)
    DAMAGE_OVER_TIME = "dot"    # Периодический урон
    BUFF_ATTACK = "buff_attack" # Усиление атаки
    BUFF_DEFENSE = "buff_defense" # Усиление защиты
    
class StatusEffect:
    """Класс для одного статус-эффекта"""
    
    def __init__(self, 
                 effect_type: StatusEffectType,
                 source: str,  # Кто наложил эффект
                 duration: int,  # Длительность в ходах
                 power: float = 1.0,  # Сила эффекта (множитель урона и т.д.)
                 data: Optional[Dict] = None):
        self.effect_type = effect_type
        self.source = source
        self.duration = duration
        self.power = power
        self.data = data or {}
        
    def apply_turn_start(self, target) -> Optional[str]:
        """Применяется в начале хода цели. Возвращает сообщение или None."""
        message = None
        
        if self.effect_type == StatusEffectType.POISON:
            # Яд наносит урон в начале хода
            damage = int(target.health_max * 0.05 * self.power)
            if damage < 1:
                damage = 1
            target.health_current = max(0, target.health_current - damage)
            message = f"{target.name} получает {damage} урона от яда"
            
        elif self.effect_type == StatusEffectType.BURN:
            # Горение наносит урон
            damage = int(target.health_max * 0.03 * self.power)
            if damage < 1:
                damage = 1
            target.health_current = max(0, target.health_current - damage)
            message = f"{target.name} горит, получая {damage} урона"
            
        elif self.effect_type == StatusEffectType.DAMAGE_OVER_TIME:
            # Общий периодический урон
            if "damage_per_turn" in self.data:
                damage = int(self.data["damage_per_turn"] * self.power)
                target.health_current = max(0, target.health_current - damage)
                element = self.data.get("element", "")
                message = f"{target.name} получает {damage} {element}урона"
        
        # Уменьшаем длительность
        self.duration -= 1
        
        return message
    
    def modify_damage(self, base_damage: int, damage_type: str = "") -> int:
        """Модифицирует урон в зависимости от эффекта"""
        if self.effect_type == StatusEffectType.WEAKNESS and "element" in self.data:
            # Если слабость к элементу совпадает с типом урона
            if damage_type == self.data["element"]:
                return int(base_damage * (1.0 + self.power))
        elif self.effect_type == StatusEffectType.BUFF_ATTACK:
            return int(base_damage * (1.0 + self.power * 0.1))
        elif self.effect_type == StatusEffectType.BUFF_DEFENSE:
            return int(base_damage * (1.0 - self.power * 0.05))
            
        return base_damage
    
    def can_act(self) -> bool:
        """Может ли цель действовать с этим эффектом?"""
        if self.effect_type in [StatusEffectType.STUN, StatusEffectType.FREEZE]:
            return False
        return True
    
    def modify_speed(self, base_speed: float) -> float:
        """Модифицирует скорость"""
        if self.effect_type == StatusEffectType.SLOW:
            return base_speed * (1.0 - self.power * 0.2)
        return base_speed
    
    def is_expired(self) -> bool:
        """Истек ли эффект?"""
        return self.duration <= 0
    
    def get_description(self) -> str:
        """Возвращает описание эффекта"""
        descriptions = {
            StatusEffectType.POISON: f"💀 Яд ({self.duration} ходов)",
            StatusEffectType.BURN: f"🔥 Горение ({self.duration} ходов)",
            StatusEffectType.FREEZE: f"❄️ Заморозка ({self.duration} ходов)",
            StatusEffectType.STUN: f"⚡ Оглушение ({self.duration} ходов)",
            StatusEffectType.SLOW: f"🐌 Замедление ({self.duration} ходов)",
            StatusEffectType.WEAKNESS: f"📉 Слабость ({self.duration} ходов)",
            StatusEffectType.DAMAGE_OVER_TIME: f"💔 Урон ({self.duration} ходов)",
            StatusEffectType.BUFF_ATTACK: f"⚔️ Усиление атаки ({self.duration} ходов)",
            StatusEffectType.BUFF_DEFENSE: f"🛡️ Усиление защиты ({self.duration} ходов)",
        }
        return descriptions.get(self.effect_type, f"Эффект ({self.duration} ходов)")

class StatusEffectSystem:
    """Система управления статус-эффектами для персонажей"""
    
    def __init__(self, target):
        self.target = target
        self.effects: List[StatusEffect] = []
        
    def add_effect(self, effect: StatusEffect) -> bool:
        """Добавляет эффект, если его еще нет или он сильнее"""
        # Проверяем, есть ли уже такой эффект
        for existing in self.effects:
            if existing.effect_type == effect.effect_type:
                # Если новый эффект сильнее или дольше - заменяем
                if effect.power > existing.power or effect.duration > existing.duration:
                    self.effects.remove(existing)
                    self.effects.append(effect)
                    return True
                return False
        
        # Эффекта нет - добавляем
        self.effects.append(effect)
        return True
    
    def remove_effect(self, effect_type: StatusEffectType):
        """Удаляет эффект указанного типа"""
        self.effects = [e for e in self.effects if e.effect_type != effect_type]
    
    def process_turn_start(self) -> List[str]:
        """Обрабатывает начало хода. Возвращает список сообщений."""
        messages = []
        
        for effect in self.effects[:]:  # Копируем список для безопасной итерации
            message = effect.apply_turn_start(self.target)
            if message:
                messages.append(message)
            
            if effect.is_expired():
                self.effects.remove(effect)
        
        return messages
    
    def modify_damage(self, base_damage: int, damage_type: str = "") -> int:
        """Модифицирует урон всеми эффектами"""
        modified_damage = base_damage
        
        for effect in self.effects:
            modified_damage = effect.modify_damage(modified_damage, damage_type)
        
        return modified_damage
    
    def can_act(self) -> bool:
        """Может ли цель действовать?"""
        for effect in self.effects:
            if not effect.can_act():
                return False
        return True
    
    def get_speed_multiplier(self) -> float:
        """Возвращает множитель скорости от эффектов"""
        multiplier = 1.0
        
        for effect in self.effects:
            multiplier = effect.modify_speed(multiplier)
        
        return multiplier
    
    def get_active_effects(self) -> List[str]:
        """Возвращает список активных эффектов"""
        return [effect.get_description() for effect in self.effects]
    
    def has_effect(self, effect_type: StatusEffectType) -> bool:
        """Проверяет, есть ли эффект указанного типа"""
        return any(e.effect_type == effect_type for e in self.effects)
    
    def clear_all(self):
        """Очищает все эффекты"""
        self.effects.clear()

# Фабрики для создания эффектов (удобные функции)

def create_poison_effect(duration: int = 3, power: float = 1.0) -> StatusEffect:
    """Создает эффект яда"""
    return StatusEffect(
        effect_type=StatusEffectType.POISON,
        source="poison",
        duration=duration,
        power=power
    )

def create_burn_effect(duration: int = 3, power: float = 1.0) -> StatusEffect:
    """Создает эффект горения"""
    return StatusEffect(
        effect_type=StatusEffectType.BURN,
        source="burn",
        duration=duration,
        power=power
    )

def create_stun_effect(duration: int = 1) -> StatusEffect:
    """Создает эффект оглушения"""
    return StatusEffect(
        effect_type=StatusEffectType.STUN,
        source="stun",
        duration=duration,
        power=1.0
    )

def create_freeze_effect(duration: int = 1) -> StatusEffect:
    """Создает эффект заморозки"""
    return StatusEffect(
        effect_type=StatusEffectType.FREEZE,
        source="freeze",
        duration=duration,
        power=1.0
    )

def create_slow_effect(duration: int = 2, power: float = 1.0) -> StatusEffect:
    """Создает эффект замедления"""
    return StatusEffect(
        effect_type=StatusEffectType.SLOW,
        source="slow",
        duration=duration,
        power=power
    )

def create_dot_effect(damage_per_turn: int, duration: int, element: str = "") -> StatusEffect:
    """Создает эффект периодического урона"""
    return StatusEffect(
        effect_type=StatusEffectType.DAMAGE_OVER_TIME,
        source="dot",
        duration=duration,
        power=1.0,
        data={"damage_per_turn": damage_per_turn, "element": element}
    )

def create_weakness_effect(element: str, duration: int = 2) -> StatusEffect:
    """Создает эффект слабости к элементу"""
    return StatusEffect(
        effect_type=StatusEffectType.WEAKNESS,
        source="weakness",
        duration=duration,
        power=1.0,
        data={"element": element}
    )