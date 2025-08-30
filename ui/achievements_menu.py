# achievements_menu.py
# ui.achievements_menu.pyf
from ui.ui_utils import print_header, press_enter_to_continue
from ui.visual_effects import VisualEffects
from ui.sound_system import SoundSystem

def achievements_menu(game_state):
    """Меню просмотра достижений"""
    achievement_system = game_state["achievement_system"]
    
    # Инициализация звуковой системы
    sound_system = SoundSystem()
    sound_system.load_sounds()
    
    while True:
        completed_count = achievement_system.get_completed_count()
        total_count = achievement_system.get_total_count()
        
        print_header(VisualEffects.glowing_text("🏆 Система достижений"))
        print(f"📊 Прогресс: {VisualEffects.progress_bar(completed_count, total_count)}")
        print()
        
        # Группируем достижения по статусу
        completed = []
        not_completed = []
        
        for achievement in achievement_system.achievements.values():
            if achievement.completed:
                completed.append(achievement)
            else:
                not_completed.append(achievement)
        
        # Показываем выполненные достижения с эффектами
        if completed:
            print(VisualEffects.glowing_text("✅ ВЫПОЛНЕННЫЕ ДОСТИЖЕНИЯ"))
            for achievement in completed:
                date_str = achievement.completed_date.strftime("%d.%m.%Y") if achievement.completed_date else ""
                reward_text = f"+{achievement.reward_value} {achievement.reward_type}"
                print(f"🏆 {achievement.name} - {reward_text} {date_str}")
                print(f"   {achievement.description}")
            print()

        # Показываем недостигнутые достижения
        if not_completed:
            print("🔒 ПРЕДСТОЯЩИЕ ДОСТИЖЕНИЯ:")
            for achievement in not_completed:
                print(f"🔒 {achievement.name}")
                print(f"   {achievement.description}")
                print(f"   Награда: +{achievement.reward_value} {achievement.reward_type}")
                print()
            
            print()

        print("0. ↩️ Назад")
        print()

        try:
            choice = int(input("🎯 Ваш выбор: "))
            sound_system.play_sound('button_click')
            
            if choice == 0:
                break
            else:
                print("❌ Неверный выбор.")
                press_enter_to_continue()
                
        except ValueError:
            sound_system.play_sound('error')
            print("❌ Пожалуйста, введите число.")
            press_enter_to_continue()

def show_achievement_notification(new_achievements):
    """Показывает уведомление о новых достижениях с эффектами"""
    if new_achievements:
        sound_system = SoundSystem()
        sound_system.load_sounds()
        sound_system.play_sound('achievement')
        
        VisualEffects.achievement_unlock_effect("НОВЫЕ ДОСТИЖЕНИЯ!")
        print("═" * 40)
        
        for i, achievement in enumerate(new_achievements):
            reward_text = f"+{achievement.reward_value} {achievement.reward_type}"
            print(f"🏆 {VisualEffects.glowing_text(achievement.name)}")
            print(f"   {achievement.description}")
            print(f"   Награда: {reward_text}")
            if i == 0:  # Только для первого достижения
                VisualEffects.sparkle_effect()
            print()
        
        press_enter_to_continue()