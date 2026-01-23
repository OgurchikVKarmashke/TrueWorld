# systems.combat_modifiers.weather.py

import random
from typing import Dict, List, Optional, Tuple
from systems.combat_modifiers.status_effects import (
    StatusEffect, StatusEffectType, 
    create_dot_effect, create_slow_effect, create_weakness_effect
)

"""
Система погоды, зависящая от локаций.
Использует систему статус-эффектов для воздействия на бой.
"""

class Weather:
    """Класс погоды"""
    
    def __init__(self, weather_type: str, location_type: str):
        self.weather_type = weather_type
        self.location_type = location_type
        self.name, self.description, self.effects = self._get_weather_info()
        self.turn_counter = 0
    
    @property
    def is_dangerous(self):
        """Определяет, является ли погода опасной"""
        dangerous_weathers = ["гроза", "жара", "снег", "песчаная буря", "магическая буря"]
        return self.weather_type in dangerous_weathers
    
    
    def _get_weather_info(self) -> Tuple[str, str, List[StatusEffect]]:
        """Возвращает информацию о погоде"""
        weather_data = {
            # Обычные погоды (без эффектов)
            "ясно": {
                "name": "☀️ Ясная погода",
                "description": "Без особых эффектов.",
                "effects": []
            },
            "облачно": {
                "name": "⛅ Облачно",
                "description": "Слегка пасмурно, но без особых эффектов.",
                "effects": []
            },
            "дождь": {
                "name": "🌧️ Дождь",
                "description": "Идет дождь. Вода повсюду.",
                "effects": []
            },
            "ветер": {
                "name": "💨 Ветрено",
                "description": "Сильный ветер.",
                "effects": []
            },
            
            # Опасные погоды (с эффектами)
            "гроза": {
                "name": "⚡ Гроза",
                "description": "Молнии бьют с неба! Шанс получить удар молнией каждый ход.",
                "effects": [
                    create_dot_effect(
                        damage_per_turn=10, 
                        duration=999,  # На весь бой
                        element="электрический"
                    )
                ]
            },
            
            "жара": {
                "name": "🔥 Аномальная жара",
                "description": "Невыносимая жара. Наносит тепловой урон каждый ход.",
                "effects": [
                    create_dot_effect(
                        damage_per_turn=8,
                        duration=999,
                        element="огненный"
                    )
                ]
            },
            
            "снег": {
                "name": "❄️ Снежный буран",
                "description": "Метель и сильный холод. Замедляет всех и наносит холодный урон.",
                "effects": [
                    create_slow_effect(duration=999, power=0.5),  # 50% замедление
                    create_dot_effect(
                        damage_per_turn=5,
                        duration=999,
                        element="ледяной"
                    )
                ]
            },
            
            "песчаная буря": {
                "name": "🌪️ Песчаная буря",
                "description": "Слепящая песчаная буря. Наносит урон и снижает точность.",
                "effects": [
                    create_dot_effect(
                        damage_per_turn=6,
                        duration=999,
                        element="земляной"
                    )
                ]
            },
            
            "туман": {
                "name": "🌫️ Густой туман",
                "description": "Плотный туман ограничивает видимость.",
                "effects": [
                    create_slow_effect(duration=999, power=0.3)  # 30% замедление
                ]
            },
            
            "магическая буря": {
                "name": "🌀 Магическая буря",
                "description": "Нестабильные потоки магии бьют по всем.",
                "effects": [
                    create_dot_effect(
                        damage_per_turn=12,
                        duration=999,
                        element="магический"
                    )
                ]
            }
        }
        
        # Проверяем специальные ограничения для локаций
        if self.location_type == "desert":
            # В пустыне не может быть снега
            if self.weather_type == "снег":
                self.weather_type = "жара"
        
        if self.location_type in ["castle", "dungeon", "cave"]:
            # В закрытых локациях ограниченный набор погоды
            if self.weather_type not in ["ясно", "туман", "магическая буря"]:
                self.weather_type = "ясно"
        
        data = weather_data.get(self.weather_type, weather_data["ясно"])
        
        # Добавляем случайный элемент опасным погодам
        effects = data["effects"]
        if self.weather_type in ["гроза", "жара", "снег", "песчаная буря", "магическая буря"]:
            # Маленький шанс дополнительного эффекта
            if random.random() < 0.2:
                if self.weather_type == "гроза":
                    effects.append(create_weakness_effect("электрический", duration=999))
                elif self.weather_type == "жара":
                    effects.append(create_weakness_effect("огненный", duration=999))
                elif self.weather_type == "снег":
                    effects.append(create_weakness_effect("ледяной", duration=999))
        
        return data["name"], data["description"], effects
    
    def apply_to_targets(self, heroes: List, monsters: List) -> List[str]:
        """Применяет погодные эффекты ко всем целям. Возвращает сообщения."""
        messages = []
        self.turn_counter += 1
        
        # Только опасные погоды наносят урон
        if self.weather_type in ["гроза", "жара", "снег", "песчаная буря", "магическая буря"]:
            # Наносим урон всем участникам
            all_targets = heroes + monsters
            
            for target in all_targets:
                if hasattr(target, 'status_system') and target.status_system:
                    for effect in self.effects:
                        target.status_system.add_effect(effect)
                    
                    # Применяем эффекты начала хода
                    turn_messages = target.status_system.process_turn_start()
                    messages.extend(turn_messages)
        
        return messages
    
    def get_turn_announcement(self) -> Optional[str]:
        """Возвращает объявление о погоде в начале хода"""
        if self.turn_counter == 1:
            return f"{self.name}\n{self.description}"
        
        # Особые объявления для опасных погод
        if self.weather_type == "гроза" and self.turn_counter % 3 == 0:
            return "⚡ Молнии сверкают на небе!"
        elif self.weather_type == "жара" and self.turn_counter % 2 == 0:
            return "🔥 Жара становится невыносимой!"
        elif self.weather_type == "снег" and self.turn_counter % 4 == 0:
            return "❄️ Ветер усиливается, метель становится сильнее!"
        
        return None

class WeatherSystem:
    """Система управления погодой"""
    
    def __init__(self):
        self.current_weather: Optional[Weather] = None
        self.weather_history: List[str] = []
    
    def generate_weather(self, location_type: str, floor: int) -> Weather:
        """Генерирует погоду для локации и этажа"""
        from systems.combat_modifiers.locations import location_manager
        
        # Получаем возможные погоды для локации
        possible_weather = location_manager.get_possible_weather(location_type)
        
        if not possible_weather:
            possible_weather = ["ясно"]
        
        # Веса для разных типов погоды
        weather_weights = {
            "ясно": 40,
            "облачно": 20,
            "дождь": 15,
            "ветер": 10,
            "туман": 8,
            "гроза": 3,
            "жара": 2,
            "снег": 1,
            "песчаная буря": 0.5,
            "магическая буря": 0.5
        }
        
        # Ограничиваем по локации
        available_weather = [w for w in possible_weather if w in weather_weights]
        if not available_weather:
            available_weather = ["ясно"]
        
        # Увеличиваем шанс опасной погоды на высоких этажах
        weights = {}
        for weather in available_weather:
            base_weight = weather_weights.get(weather, 1)
            
            # Увеличиваем вес опасной погоды на высоких этажах
            if weather in ["гроза", "жара", "снег", "песчаная буря", "магическая буря"]:
                danger_bonus = min(floor // 10, 5)  # +5% за каждые 10 этажей
                adjusted_weight = base_weight + danger_bonus
            else:
                adjusted_weight = base_weight
            
            weights[weather] = adjusted_weight
        
        # Выбираем погоду по весам
        total_weight = sum(weights.values())
        r = random.uniform(0, total_weight)
        current = 0
        
        for weather, weight in weights.items():
            current += weight
            if r <= current:
                self.current_weather = Weather(weather, location_type)
                self.weather_history.append(weather)
                
                # Ограничиваем историю
                if len(self.weather_history) > 20:
                    self.weather_history = self.weather_history[-20:]
                
                return self.current_weather
        
        # Фолбэк
        self.current_weather = Weather("ясно", location_type)
        return self.current_weather
    
    def get_current_weather_info(self) -> Dict:
        """Возвращает информацию о текущей погоде"""
        if not self.current_weather:
            return {
                "name": "☀️ Ясная погода",
                "description": "Без погодных эффектов.",
                "is_dangerous": False
            }
        
        is_dangerous = self.current_weather.weather_type in [
            "гроза", "жара", "снег", "песчаная буря", "магическая буря"
        ]
        
        return {
            "name": self.current_weather.name,
            "description": self.current_weather.description,
            "is_dangerous": is_dangerous,
            "effects": [effect.get_description() for effect in self.current_weather.effects]
        }
    
    def apply_weather_effects(self, heroes: List, monsters: List) -> List[str]:
        """Применяет эффекты текущей погоды. Возвращает сообщения."""
        if not self.current_weather:
            return []
        
        return self.current_weather.apply_to_targets(heroes, monsters)
    
    def get_turn_announcement(self) -> Optional[str]:
        """Возвращает объявление о погоде для текущего хода"""
        if not self.current_weather:
            return None
        
        return self.current_weather.get_turn_announcement()

# Глобальный экземпляр системы погоды
weather_system = WeatherSystem()