# ui.party_manager.py
from ui.ui_utils import print_header, press_enter_to_continue
from ui.visual_effects import VisualEffects

def view_party(game_state):
    """
    Просмотр информации о ТОЛЬКО ЖИВЫХ героях
    """
    print_header("Ваши героев")
    
    # Фильтруем только живых героев
    living_heroes = [h for h in game_state["heroes"] if h.is_alive]
    
    if not living_heroes:
        print("🎯 В вашем лобби отсутствуют герои")
        print("💡 Призовите новых героев в зале призыва героев")
        press_enter_to_continue()
        return
    
    dormitory = game_state["buildings"].get_building("dormitory")
    current_capacity = len(living_heroes)  # Используем только живых
    max_capacity = dormitory.get_capacity()
    
    print(f"👥 Героев: {current_capacity}/{max_capacity}")
    print("=" * 50)
    
    for i, hero in enumerate(living_heroes, 1):  # Используем living_heroes вместо game_state["heroes"]
        star_display = VisualEffects.get_star_display(hero.star)
        
        # Получаем роль героя
        hero_role = None
        if game_state.get("role_system"):
            hero_role = game_state["role_system"].get_hero_role(hero)
        
        # Проверяем, занят ли герой в группах
        in_party = False
        if "party_system" in game_state:
            parties = game_state["party_system"]["parties"]
            for party_data in parties.values():
                if id(hero) in party_data.get("heroes", []):
                    in_party = True
                    break
        
        # Формируем строку статуса
        if hero_role:
            status = f"👑 На роли | {hero_role}"
        elif in_party:
            status = "⚔️ В группе"
        else:
            status = "✅ Свободен"
        
        print(f"{i}. {hero.name} {star_display} | {status}")
        print(f"   📊 Уровень: {hero.level}")
        print(f"   ❤️ Здоровье: {hero.health_current}/{hero.health_max}")
        print(f"   🔵 Мана: {hero.mana_current}/{hero.mana_max}")
        exp_bar = hero.get_experience_bar(15)
        print(f"   📈 Опыт: {hero.experience}/{hero.exp_to_next_level}")
        print(f"   {exp_bar}")
        
        # Показываем скрытые статы, если изучено "Понимание героев"
        if game_state.get("hero_understanding") or game_state.get("flags", {}).get("hero_understanding"):
            print(f"   {hero.get_hidden_stats(game_state)}")
        
        print("-" * 50)
    
    press_enter_to_continue()