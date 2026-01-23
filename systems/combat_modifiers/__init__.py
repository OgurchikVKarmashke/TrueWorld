# systems.combat_modifiers.__init__.py
from systems.combat_modifiers.status_effects import (
    StatusEffect, StatusEffectType, StatusEffectSystem,
    create_poison_effect, create_burn_effect, create_stun_effect,
    create_freeze_effect, create_slow_effect, create_dot_effect,
    create_weakness_effect
)

from systems.combat_modifiers.locations import (
    Location, LocationType, LocationManager, location_manager
)

from systems.combat_modifiers.weather import (
    Weather, WeatherSystem, weather_system
)

from systems.combat_modifiers.traps import (
    Trap, TrapType, TrapSystem, trap_system
)

"""
Инициализация всех систем модификаторов боя.
Теперь включает статус-эффекты, локации, погоду и ловушки.
"""

# Для обратной совместимости (если где-то используется старый импорт)
COMBAT_MODIFIERS = {
    "weather": WeatherSystem,
    "trap": TrapSystem,
    "location": LocationManager,
    "status": StatusEffectSystem
}

__all__ = [
    # Статус-эффекты
    'StatusEffect', 'StatusEffectType', 'StatusEffectSystem',
    'create_poison_effect', 'create_burn_effect', 'create_stun_effect',
    'create_freeze_effect', 'create_slow_effect', 'create_dot_effect',
    'create_weakness_effect',
    
    # Локации
    'Location', 'LocationType', 'LocationManager', 'location_manager',
    
    # Погода
    'Weather', 'WeatherSystem', 'weather_system',
    
    # Ловушки
    'Trap', 'TrapType', 'TrapSystem', 'trap_system',
    
    # Обратная совместимость
    'COMBAT_MODIFIERS'
]