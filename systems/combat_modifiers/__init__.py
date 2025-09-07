# systems.combat_modifiers.__init__.py

# Система плагинов для модификаторов боя

COMBAT_MODIFIERS = {}

def register_modifier(name, modifier_class):
    COMBAT_MODIFIERS[name] = modifier_class

def get_modifier(name):
    return COMBAT_MODIFIERS.get(name)

# Импортируем и регистрируем все модификаторы
from systems.combat_modifiers.weather import WeatherModifier
from systems.combat_modifiers.traps import TrapModifier

register_modifier("weather", WeatherModifier)
register_modifier("trap", TrapModifier)