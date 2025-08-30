# ui.visual_effects.py
import time
import random

class VisualEffects:
    # Цветовые коды для звёзд
    STAR_COLORS = {
        1: "",          # обычный (без цвета)
        2: "\033[92m",  # зелёный
        3: "\033[94m",  # синий  
        4: "\033[95m",  # фиолетовый
        5: "\033[93m",  # золотой
        6: "\033[96m",  # бирюзовый (радужный упрощённо)
        7: "\033[91m",  # красный
    }
    
    RESET_COLOR = "\033[0m"
    
    @staticmethod
    def get_star_display(star_level, max_stars=7):
        """Возвращает цветные звёзды с правильным форматированием"""
        if star_level < 1:
            star_level = 1
        if star_level > max_stars:
            star_level = max_stars
        
        color_code = VisualEffects.STAR_COLORS.get(star_level, "")
        filled_stars = "★" * star_level
        empty_stars = "☆" * (max_stars - star_level)
        
        # Правильное применение цветов
        if color_code:
            return f"{color_code}{filled_stars}{VisualEffects.RESET_COLOR}{empty_stars}"
        else:
            return f"{filled_stars}{empty_stars}"
    
    @staticmethod
    def get_exp_bar(current_exp, exp_needed, width=20):
        """Создаёт текстовый прогресс-бар опыта"""
        if exp_needed <= 0:
            return "[" + "=" * width + "] 100%"
        
        percentage = min(100, int((current_exp / exp_needed) * 100))
        filled_width = int(width * percentage / 100)
        empty_width = width - filled_width
        
        # Цвет меняется от красного к зелёному
        if percentage < 30:
            color = "\033[91m"  # красный
        elif percentage < 70:
            color = "\033[93m"  # жёлтый
        else:
            color = "\033[92m"  # зелёный
            
        # Используем разные символы для заполненной и пустой части
        filled_char = "█"
        empty_char = "░"
        
        bar = f"{color}[{filled_char * filled_width}{empty_char * empty_width}]{VisualEffects.RESET_COLOR} {percentage}%"
        return bar
    
    @staticmethod
    def format_hero_display(hero):
        """Форматирует отображение героя с цветами и прогресс-баром"""
        star_display = VisualEffects.get_star_display(hero.star)
        exp_bar = VisualEffects.get_exp_bar(hero.experience, hero.exp_to_next_level)
        
        # Добавляем цвет для уровня
        level_color = ""
        if hero.level >= 50:
            level_color = "\033[93m"  # золотой для высоких уровней
        elif hero.level >= 20:
            level_color = "\033[94m"  # синий для средних уровней
        
        level_display = f"{level_color}Ур. {hero.level}{VisualEffects.RESET_COLOR}" if level_color else f"Ур. {hero.level}"
        
        return (f"{star_display} {hero.name} ({level_display}) {hero.character}\n"
                f"❤️ {hero.health_current}/{hero.health_max} | ✨ {hero.mana_current}/{hero.mana_max}\n"
                f"EXP: {exp_bar}")

    @staticmethod
    def achievement_unlock_effect(achievement_name):
        """Эффект разблокировки достижения"""
        print("\n" + "✨" * 30)
        print(f"🎉 ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО: {achievement_name}")
        print("✨" * 30)
        
        # Простая анимация
        for i in range(2):
            print("🌟 " * 8)
            time.sleep(0.2)
            print("⭐ " * 8)
            time.sleep(0.2)
    
    @staticmethod
    def glowing_text(text, glow_char="✨"):
        """Текст с свечением"""
        return f"{glow_char} {text} {glow_char}"
    
    @staticmethod
    def progress_bar(completed, total, width=20):
        """Визуальная полоса прогресса"""
        progress = completed / total if total > 0 else 0
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {completed}/{total} ({progress*100:.1f}%)"