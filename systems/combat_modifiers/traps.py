# systems.combat_modifiers.traps.py
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum
from systems.combat_modifiers.status_effects import (
    StatusEffect, StatusEffectType,
    create_poison_effect, create_burn_effect, 
    create_stun_effect, create_freeze_effect,
    create_slow_effect, create_weakness_effect
)

"""
Система ловушек для боя.
Включает статические ловушки на локациях и магические ловушки, призываемые магами.
Использует систему статус-эффектов.
"""

class TrapType(Enum):
    """Типы ловушек"""
    PHYSICAL = "physical"      # Физические ловушки (капканы, ямы)
    MAGICAL = "magical"        # Магические ловушки (призываемые)
    ELEMENTAL = "elemental"    # Элементальные ловушки

class Trap:
    """Класс ловушки"""
    
    def __init__(self, trap_id: str, trap_type: TrapType, name: str, description: str):
        self.trap_id = trap_id
        self.trap_type = trap_type
        self.name = name
        self.description = description
        self.is_active = True
        self.trigger_chance = 0.3  # Базовый шанс срабатывания
        self.uses_remaining = random.randint(1, 3)  # Сколько раз сработает
        self.detected = False  # Обнаружена ли ловушка
        self.effects: List[StatusEffect] = []
        
    def add_effect(self, effect: StatusEffect):
        """Добавляет эффект к ловушке"""
        self.effects.append(effect)
    
    def trigger(self, target) -> Tuple[bool, Optional[str]]:
        """
        Активирует ловушку на цели.
        Возвращает (сработала_ли, сообщение)
        """
        if not self.is_active or self.uses_remaining <= 0:
            return False, None
        
        # Проверяем шанс срабатывания
        if random.random() > self.trigger_chance:
            return False, None
        
        self.uses_remaining -= 1
        if self.uses_remaining <= 0:
            self.is_active = False
        
        # Применяем эффекты
        messages = []
        for effect in self.effects:
            if hasattr(target, 'status_system') and target.status_system:
                target.status_system.add_effect(effect)
                messages.append(effect.get_description())
        
        # Формируем сообщение
        if messages:
            effect_desc = ", ".join(messages)
            message = f"{target.name} активировал {self.name}! Эффекты: {effect_desc}"
        else:
            message = f"{target.name} активировал {self.name}!"
        
        return True, message
    
    def detect(self) -> bool:
        """Обнаруживает ловушку"""
        if not self.detected:
            self.detected = True
            # После обнаружения снижаем шанс срабатывания
            self.trigger_chance *= 0.5
            return True
        return False

class TrapSystem:
    """Система управления ловушками"""
    
    def __init__(self):
        self.active_traps: List[Trap] = []
        self.templates = self._init_trap_templates()
    
    def _init_trap_templates(self) -> Dict[str, Dict]:
        """Инициализирует шаблоны ловушек"""
        return {
            # Физические ловушки
            "капкан": {
                "name": "🐾 Капкан",
                "type": TrapType.PHYSICAL,
                "description": "Скрытый металлический капкан с острыми зубьями.",
                "effects": [create_poison_effect(duration=2, power=1.0)],
                "damage": 15
            },
            
            "волчья яма": {
                "name": "🕳️ Волчья яма",
                "type": TrapType.PHYSICAL,
                "description": "Замаскированная яма с кольями на дне.",
                "effects": [create_stun_effect(duration=1)],
                "damage": 20
            },
            
            "силки": {
                "name": "🪢 Силки",
                "type": TrapType.PHYSICAL,
                "description": "Петля, затягивающаяся при наступлении.",
                "effects": [create_slow_effect(duration=2, power=0.5)],
                "damage": 5
            },
            
            "ядовитые шипы": {
                "name": "☠️ Ядовитые шипы",
                "type": TrapType.PHYSICAL,
                "description": "Шипы, покрытые ядом.",
                "effects": [
                    create_poison_effect(duration=3, power=1.5),
                    create_slow_effect(duration=1, power=0.3)
                ],
                "damage": 10
            },
            
            # Магические ловушки
            "магическая ловушка (огонь)": {
                "name": "🔥 Магическая огненная ловушка",
                "type": TrapType.MAGICAL,
                "description": "Руна, выпускающая огненную струю при активации.",
                "effects": [
                    create_burn_effect(duration=3, power=1.0),
                    create_weakness_effect("огненный", duration=2)
                ],
                "damage": 25,
                "mana_cost": 20
            },
            
            "магическая ловушка (лед)": {
                "name": "❄️ Магическая ледяная ловушка",
                "type": TrapType.MAGICAL,
                "description": "Руна, замораживающая все вокруг.",
                "effects": [
                    create_freeze_effect(duration=1),
                    create_slow_effect(duration=3, power=0.7)
                ],
                "damage": 15,
                "mana_cost": 25
            },
            
            "магическая ловушка (электричество)": {
                "name": "⚡ Магическая электрическая ловушка",
                "type": TrapType.MAGICAL,
                "description": "Руна, бьющая электрическим разрядом.",
                "effects": [
                    create_stun_effect(duration=1),
                    create_weakness_effect("электрический", duration=2)
                ],
                "damage": 20,
                "mana_cost": 15
            },
            
            "дротиковая ловушка": {
                "name": "🎯 Дротиковая ловушка",
                "type": TrapType.PHYSICAL,
                "description": "Скрытые духовые трубки, стреляющие отравленными дротиками.",
                "effects": [create_poison_effect(duration=4, power=2.0)],
                "damage": 12
            },
            
            "песчаная ловушка": {
                "name": "🏜️ Песчаная ловушка",
                "type": TrapType.PHYSICAL,
                "description": "Зыбучие пески, затягивающие жертву.",
                "effects": [create_slow_effect(duration=3, power=0.8)],
                "damage": 8
            }
        }
    
    def generate_location_traps(self, location_type: str, trap_chance: float) -> List[Trap]:
        """Генерирует ловушки для локации"""
        from systems.combat_modifiers.locations import location_manager
        
        location = location_manager.get_location_info(location_type)
        if not location:
            return []
        
        traps = []
        
        # Проверяем шанс появления ловушек
        if random.random() > trap_chance:
            return traps
        
        # Определяем сколько ловушек
        trap_count = random.randint(1, 2)
        
        # Выбираем ловушки из доступных для локации
        available_traps = location.trap_types
        if not available_traps:
            return traps
        
        for _ in range(trap_count):
            trap_name = random.choice(available_traps)
            if trap_name in self.templates:
                template = self.templates[trap_name]
                trap = Trap(
                    trap_id=f"trap_{len(self.active_traps) + 1}",
                    trap_type=template["type"],
                    name=template["name"],
                    description=template["description"]
                )
                
                # Добавляем эффекты
                for effect in template.get("effects", []):
                    trap.add_effect(effect)
                
                # Устанавливаем шанс срабатывания
                if trap.trap_type == TrapType.MAGICAL:
                    trap.trigger_chance = 0.4  # Магические ловушки чаще срабатывают
                
                traps.append(trap)
        
        self.active_traps.extend(traps)
        return traps
    
    def create_magical_trap(self, caster, element: str) -> Optional[Trap]:
        """Создает магическую ловушку (призывается магом)"""
        trap_key = f"магическая ловушка ({element})"
        
        if trap_key not in self.templates:
            # Если нет шаблона для элемента, используем общий
            trap_key = "магическая ловушка (огонь)"
        
        template = self.templates[trap_key]
        
        # Проверяем ману кастера
        if hasattr(caster, 'mana_current') and hasattr(caster, 'mana_max'):
            mana_cost = template.get("mana_cost", 30)
            if caster.mana_current < mana_cost:
                return None
            
            caster.mana_current -= mana_cost
        
        trap = Trap(
            trap_id=f"magic_trap_{len(self.active_traps) + 1}",
            trap_type=TrapType.MAGICAL,
            name=template["name"],
            description=f"Призвана {caster.name}. {template['description']}"
        )
        
        for effect in template.get("effects", []):
            trap.add_effect(effect)
        
        # Магические ловушки имеют больший шанс срабатывания
        trap.trigger_chance = 0.6
        trap.uses_remaining = 2
        
        self.active_traps.append(trap)
        return trap
    
    def check_trap_trigger(self, target) -> List[str]:
        """
        Проверяет срабатывание ловушек для цели.
        Возвращает список сообщений.
        """
        messages = []
        
        for trap in self.active_traps[:]:  # Копируем для безопасного удаления
            if trap.is_active:
                triggered, message = trap.trigger(target)
                if triggered:
                    messages.append(message)
                    
                    # Наносим урон
                    if hasattr(target, 'take_damage'):
                        trap_template = self.templates.get(trap.trap_id.split('_')[0], {})
                        damage = trap_template.get("damage", 10)
                        
                        # Модифицируем урон статус-эффектами цели
                        if hasattr(target, 'status_system') and target.status_system:
                            damage = target.status_system.modify_damage(damage)
                        
                        # Применяем защиту
                        if hasattr(target, 'defense'):
                            actual_damage = max(1, damage - target.defense)
                        else:
                            actual_damage = damage
                        
                        target.health_current = max(0, target.health_current - actual_damage)
                        messages.append(f"{target.name} получает {actual_damage} урона от ловушки!")
                
                # Удаляем неактивные ловушки
                if not trap.is_active:
                    self.active_traps.remove(trap)
        
        return messages
    
    def detect_traps(self, detector, detection_skill: float = 0.0) -> List[str]:
        """
        Пытается обнаружить ловушки.
        detection_skill: 0.0-1.0, шанс обнаружения каждой ловушки.
        """
        messages = []
        
        for trap in self.active_traps:
            if not trap.detected:
                # Базовый шанс обнаружения + навык
                detect_chance = 0.1 + detection_skill
                
                if random.random() < detect_chance:
                    trap.detect()
                    messages.append(f"{detector.name} обнаружил {trap.name}!")
        
        return messages
    
    def get_active_traps_info(self) -> List[Dict]:
        """Возвращает информацию об активных ловушках"""
        info = []
        for trap in self.active_traps:
            status = "✅ Обнаружена" if trap.detected else "❓ Скрытая"
            info.append({
                "name": trap.name,
                "type": trap.trap_type.value,
                "status": status,
                "uses": trap.uses_remaining,
                "chance": f"{trap.trigger_chance*100:.0f}%"
            })
        return info
    
    def clear_all_traps(self):
        """Очищает все ловушки"""
        self.active_traps.clear()

# Глобальный экземпляр системы ловушек
trap_system = TrapSystem()