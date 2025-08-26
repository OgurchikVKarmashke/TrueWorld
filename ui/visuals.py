# visuals.py
# ui/visuals.py
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
        color_code = VisualEffects.STAR_COLORS.get(star_level, "")
        filled_stars = "★" * star_level
        empty_stars = "☆" * (max_stars - star_level)
        return f"{color_code}{filled_stars}{empty_stars}{VisualEffects.RESET_COLOR}"
    
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
            
        bar = f"{color}[{'=' * filled_width}{'-' * empty_width}]{VisualEffects.RESET_COLOR} {percentage}%"
        return bar
    
    @staticmethod
    def format_hero_display(hero):
        """Форматирует отображение героя с цветами и прогресс-баром"""
        star_display = VisualEffects.get_star_display(hero.star)
        exp_bar = VisualEffects.get_exp_bar(hero.experience, hero.exp_to_next_level)
        
        return (f"{star_display} {hero.name} (Ур. {hero.level}) {hero.character}\n"
                f"❤️ {hero.health_current}/{hero.health_max} | ✨ {hero.mana_current}/{hero.mana_max}\n"
                f"EXP: {exp_bar}")