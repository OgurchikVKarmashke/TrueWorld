# systems.combat_modifiers.weather.py

from systems.combat_modifiers import register_modifier
import random

class WeatherModifier:
    def __init__(self, weather_type):
        self.weather_type = weather_type
        self.modifiers = {
            "ясно": {"accuracy": 0.0, "description": "☀️ Ясно: обычная погода"},
            "облачно": {"accuracy": -0.05, "description": "⛅ Облачно: -5% точности"},
            "дождь": {"accuracy": -0.2, "evasion": 0.1, "description": "💧 Дождь: -20% точности, +10% уклонения"},
            "гроза": {"accuracy": -0.3, "stun_chance": 0.15, "description": "⚡ Гроза: -30% точности, 15% шанс оглушения"},
            "туман": {"accuracy": -0.4, "evasion": 0.2, "description": "🌫️ Туман: -40% точности, +20% уклонения"},
            "снег": {"speed": -0.25, "freeze_chance": 0.1, "description": "❄️ Снег: -25% скорости, 10% шанс заморозки"},
            "ветер": {"accuracy": -0.15, "critical_chance": 0.1, "description": "💨 Ветер: -15% точности, +10% шанс крита"},
            "жара": {"stamina": -0.2, "burn_chance": 0.12, "description": "🔥 Жара: -20% выносливости, 12% шанс поджога"}
        }
    
    def apply(self, combat_system):
        if self.weather_type in self.modifiers:
            mod = self.modifiers[self.weather_type]
            combat_system.weather_modifier = mod  # Сохраняем для использования в бою
            return mod
        return {}
    
    def apply_weather_effect(self, attacker, target, damage):
        """Применяет эффекты погоды к атаке"""
        if not hasattr(self, 'weather_modifier'):
            return damage
        
        mod = self.weather_modifier
        
        # Шанс промаха из-за погоды
        if random.random() < abs(mod.get("accuracy", 0)):
            return 0  # Промах
        
        # Дополнительные эффекты
        if "stun_chance" in mod and random.random() < mod["stun_chance"]:
            target.stunned = True  # Нужно добавить stunned атрибут в Hero/Monster
        
        if "freeze_chance" in mod and random.random() < mod["freeze_chance"]:
            target.frozen = True
        
        if "burn_chance" in mod and random.random() < mod["burn_chance"]:
            target.burning = True
        
        return damage

register_modifier("weather", WeatherModifier)