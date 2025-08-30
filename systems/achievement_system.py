# achievement_system.py
# systems.achievement_system.py
import json
import os
from datetime import datetime

class Achievement:
    def __init__(self, id, name, description, reward_type, reward_value, condition_type, condition_value):
        self.id = id
        self.name = name
        self.description = description
        self.reward_type = reward_type
        self.reward_value = reward_value
        self.condition_type = condition_type
        self.condition_value = condition_value
        self.completed = False
        self.completed_date = None
        self.viewed = False

class AchievementSystem:
    def __init__(self, save_path="saves/achievements.json"):
        self.save_path = save_path
        self.achievements = self.load_achievements()
        self.initialize_default_achievements()
    
    def initialize_default_achievements(self):
        """Инициализирует стандартные достижения по зданиям"""
        building_achievements = [
            # Достижения по строительству
            ("first_building", "Первый камень", "Постройте любое здание", "gold", 100, "build_any", 1),
            ("dormitory_lvl5", "Комфортное жильё", "Улучшите Общежитие до 5 уровня", "gold", 250, "building_level", ("dormitory", 5)),
            ("forge_lvl3", "Оружейный мастер", "Улучшите Кузницу до 3 уровня", "crystals", 10, "building_level", ("forge", 3)),
            ("all_buildings", "Великий архитектор", "Постройте все здания", "gold", 1000, "build_all", None),
            
            # Достижения по уровням
            ("total_lvl10", "Новичок строителя", "Достигните 10 общего уровня зданий", "gold", 150, "total_level", 10),
            ("total_lvl50", "Опытный строитель", "Достигните 50 общего уровня зданий", "gold", 500, "total_level", 50),
            
            # Специфические достижения
            ("max_dormitory", "Вместительный дом", "Максимально улучшите Общежитие", "crystals", 25, "building_max", "dormitory"),
            ("max_laboratory", "Гений науки", "Максимально улучшите Лабораторию", "crystals", 30, "building_max", "laboratory"),
            
            # Этажные достижения
            ("floor_10_buildings", "Небесный архитектор", "Имейте здания 10+ уровня на 10+ этаже", "gold", 300, "floor_building", (10, 10)),
        ]
        
        for ach_id, name, desc, reward_type, reward_val, cond_type, cond_val in building_achievements:
            if ach_id not in self.achievements:
                self.achievements[ach_id] = Achievement(ach_id, name, desc, reward_type, reward_val, cond_type, cond_val)
    
    def check_building_achievements(self, game_state):
        """Проверяет достижения, связанные со зданиями"""
        buildings = game_state["buildings"].buildings
        new_achievements = []
        
        for achievement in self.achievements.values():
            if not achievement.completed:
                if self.check_condition(achievement, buildings, game_state):
                    achievement.completed = True
                    achievement.completed_date = datetime.now()
                    self.apply_reward(game_state, achievement)
                    new_achievements.append(achievement)
        
        if new_achievements:
            self.save_achievements()
            
        return new_achievements
    
    def check_condition(self, achievement, buildings, game_state):
        """Проверяет условие достижения"""
        condition_type = achievement.condition_type
        condition_value = achievement.condition_value
        
        if condition_type == "build_any":
            # Проверяем, построено ли хотя бы одно НЕ изначальное здание
            return any(building.level > 0 and not building.initially_built 
                    for building in buildings.values())
            
        elif condition_type == "building_level":
            # Проверяем уровень конкретного здания
            building_id, required_level = condition_value
            if building_id in buildings:
                return buildings[building_id].level >= required_level
            return False
            
        elif condition_type == "build_all":
            # Проверяем, построены ли все здания
            return all(building.level > 0 for building in buildings.values())
            
        elif condition_type == "total_level":
            # Проверяем общий уровень всех зданий
            total_level = sum(building.level for building in buildings.values())
            return total_level >= condition_value
            
        elif condition_type == "building_max":
            # Проверяем, максимально ли улучшено здание
            if condition_value in buildings:
                building = buildings[condition_value]
                return building.level >= building.max_level
            return False
            
        elif condition_type == "floor_building":
            # Проверяем здания на определенном этаже
            required_level, required_floor = condition_value
            tower_level = game_state["tower_level"]
            if tower_level >= required_floor:
                return any(building.level >= required_level for building in buildings.values())
            return False
            
        return False
    
    def apply_reward(self, game_state, achievement):
        """Применяет награду за достижение"""
        wallet = game_state["wallet"]
        if achievement.reward_type == "gold":
            wallet.add_gold(achievement.reward_value)
        elif achievement.reward_type == "crystals":
            wallet.add_crystals(achievement.reward_value)
    
    def mark_all_as_viewed(self):
        """Отмечает все достижения как просмотренные"""
        for achievement in self.achievements.values():
            achievement.viewed = True
        self.save_achievements()
    
    def get_unviewed_achievements(self):
        """Возвращает непросмотренные достижения"""
        return [ach for ach in self.achievements.values() if ach.completed and not ach.viewed]
    
    def mark_as_viewed(self, achievement_id):
        """Отмечает конкретное достижение как просмотренное"""
        if achievement_id in self.achievements:
            self.achievements[achievement_id].viewed = True
            self.save_achievements()
    
    def get_recent_achievements(self, limit=3):
        """Возвращает последние выполненные достижения (только непросмотренные)"""
        unviewed = [ach for ach in self.achievements.values() if ach.completed and not ach.viewed]
        unviewed.sort(key=lambda x: x.completed_date or datetime.min, reverse=True)
        return unviewed[:limit]
    
    def get_completed_count(self):
        """Возвращает количество выполненных достижений"""
        return sum(1 for ach in self.achievements.values() if ach.completed)
    
    def get_total_count(self):
        """Возвращает общее количество достижений"""
        return len(self.achievements)
    
    def save_achievements(self):
        """Сохраняет достижения в файл"""
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        data = {}
        for ach_id, achievement in self.achievements.items():
            data[ach_id] = {
                'name': achievement.name,
                'description': achievement.description,
                'reward_type': achievement.reward_type,
                'reward_value': achievement.reward_value,
                'condition_type': achievement.condition_type,
                'condition_value': achievement.condition_value,
                'completed': achievement.completed,
                'completed_date': achievement.completed_date.isoformat() if achievement.completed_date else None,
                'viewed': achievement.viewed  # Сохраняем статус просмотра
            }
        
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_achievements(self):
        """Загружает достижения из файла"""
        achievements = {}
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for ach_id, ach_data in data.items():
                        achievement = Achievement(
                            ach_id, ach_data['name'], ach_data['description'],
                            ach_data['reward_type'], ach_data['reward_value'],
                            ach_data['condition_type'], ach_data['condition_value']
                        )
                        achievement.completed = ach_data.get('completed', False)
                        achievement.viewed = ach_data.get('viewed', False)  # Загружаем статус просмотра
                        if ach_data.get('completed_date'):
                            achievement.completed_date = datetime.fromisoformat(ach_data['completed_date'])
                        achievements[ach_id] = achievement
            except:
                achievements = {}
        return achievements