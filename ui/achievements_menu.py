# achievements_menu.py
# ui.achievements_menu.pyfrom ui.ui_utils import print_header, press_enter_to_continue, loading_screen
from ui.ui_utils import print_header, press_enter_to_continue

def achievements_menu(game_state):
    """Меню просмотра достижений"""
    achievement_system = game_state["achievement_system"]
    
    # Отмечаем все достижения как просмотренные при входе в меню
    achievement_system.mark_all_as_viewed()
    
    while True:
        completed_count = achievement_system.get_completed_count()
        total_count = achievement_system.get_total_count()
        
        print_header("🏆 Система достижений")
        print(f"📊 Прогресс: {completed_count}/{total_count} ({completed_count/total_count*100:.1f}%)")
        print()
        
        # Группируем достижения по статусу
        completed = []
        not_completed = []
        
        for achievement in achievement_system.achievements.values():
            if achievement.completed:
                completed.append(achievement)
            else:
                not_completed.append(achievement)
        
        # Показываем выполненные достижения
        if completed:
            print("✅ ВЫПОЛНЕННЫЕ ДОСТИЖЕНИЯ:")
            for achievement in completed:
                date_str = achievement.completed_date.strftime("%d.%m.%Y") if achievement.completed_date else ""
                reward_text = f"+{achievement.reward_value} {achievement.reward_type}"
                print(f"🏆 {achievement.name} - {reward_text} {date_str}")
                print(f"   {achievement.description}")
                print()
            
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
            
            if choice == 0:
                break
            else:
                print("❌ Неверный выбор. Доступна только опция '0' для возврата.")
                press_enter_to_continue()
                
        except ValueError:
            print("❌ Пожалуйста, введите 0 для возврата.")
            press_enter_to_continue()

def show_achievement_notification(new_achievements):
    """Показывает уведомление о новых достижениях"""
    if new_achievements:
        print("\n🎉 НОВЫЕ ДОСТИЖЕНИЯ!")
        print("═" * 30)
        for achievement in new_achievements:
            reward_text = f"+{achievement.reward_value} {achievement.reward_type}"
            print(f"🏆 {achievement.name}")
            print(f"   {achievement.description}")
            print(f"   Награда: {reward_text}")
            print()
        press_enter_to_continue()