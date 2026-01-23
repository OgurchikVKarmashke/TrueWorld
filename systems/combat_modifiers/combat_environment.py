# systems/combat_modifiers/combat_environment.py
import random
from typing import List, Dict, Optional
from .locations import LocationManager, Location, LocationType
from .weather import WeatherSystem, Weather
from .traps import TrapSystem, Trap

"""
Комбинированная система окружения для боя.
Содержит локации, погоду и ловушки в одном экземпляре.
"""

class CombatEnvironment:
    """Окружение для конкретного боя (локация, погода, ловушки)"""
    
    def __init__(self):
        self.location_manager = LocationManager()
        self.weather_system = WeatherSystem()
        self.trap_system = TrapSystem()
        
        self.current_location: Optional[Location] = None
        self.current_weather: Optional[Weather] = None
        
    def generate_for_floor(self, floor: int) -> Dict:
        """Генерирует окружение для этажа"""
        # Локация
        self.current_location = self.location_manager.get_location_for_floor(floor)
        
        # Погода
        self.current_weather = self.weather_system.generate_weather(
            self.current_location.location_type.value,
            floor
        )
        
        # Ловушки
        traps = self.trap_system.generate_location_traps(
            self.current_location.location_type.value,
            self.current_location.trap_chance
        )
        
        return {
            "location": self.current_location,
            "weather": self.current_weather,
            "traps": traps
        }
    
    def clear(self):
        """Очищает окружение после боя"""
        self.trap_system.clear_all_traps()
        # location_manager и weather_system сохраняют историю для следующего боя
    
    def get_location_info(self) -> Dict:
        """Возвращает информацию о локации"""
        if not self.current_location:
            return {"name": "Неизвестно", "description": ""}
        
        return {
            "name": self.current_location.name,
            "description": self.current_location.description,
            "type": self.current_location.location_type.value
        }
    
    def get_weather_info(self) -> Dict:
        """Возвращает информацию о погоде"""
        if not self.current_weather:
            return self.weather_system.get_current_weather_info()
        return self.weather_system.get_current_weather_info()
    
    def get_traps_info(self) -> List[Dict]:
        """Возвращает информацию о ловушках"""
        return self.trap_system.get_active_traps_info()