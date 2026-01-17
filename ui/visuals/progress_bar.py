# ui.visuals.progress_bar.py

class ProgressBar:
    @staticmethod
    def draw_tower_progress(current_floor, max_floor=100, width=50):
        progress = min(current_floor / max_floor, 1.0)
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        
        # Маркеры боссов каждые 5 этажей
        markers = ""
        for floor in range(5, 101, 5):
            pos = int((floor / max_floor) * width)
            if pos < width:
                markers += f"\033[{pos}G👑"  # ANSI позиционирование
        
        return f"[{bar}] {current_floor}/100{markers}"