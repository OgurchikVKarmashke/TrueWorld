# party_manager.py
from ui.ui_utils import print_header, press_enter_to_continue

def view_party(game_state):
    """
    Просмотр информации о героях
    """
    print_header("Ваши герои")
    
    if not game_state["heroes"]:
        print("🎯 Отряд пуст")
        print("➡️ Призовите героев в зале призыва героев")
        print("💡 Стоимость призыва: 50 золота")
        press_enter_to_continue()
        return
    
    dormitory = game_state["buildings"].get_building("dormitory")
    current_capacity = len(game_state["heroes"])
    max_capacity = dormitory.get_capacity()
    
    print(f"👥 Героев: {current_capacity}/{max_capacity}")
    print("=" * 50)
    
    for i, hero in enumerate(game_state["heroes"], 1):
        star_symbol = "★" * hero.star
        
        # Получаем роль героя
        role = ""
        if hasattr(game_state.get("role_system", None), 'get_hero_role'):
            hero_role = game_state["role_system"].get_hero_role(hero)
            if hero_role:
                role = f" | 👑 {hero_role}"
        
        # Проверяем, занят ли герой в группах
        in_party = False
        if "party_system" in game_state:
            parties = game_state["party_system"]["parties"]
            for party_data in parties.values():
                if id(hero) in party_data.get("heroes", []):
                    in_party = True
                    break
        
        status = "✅ Свободен"
        if role:
            status = f"👑 На роли"
        elif in_party:
            status = "⚔️ В группе"
        
        print(f"{i}. {hero.name} {star_symbol} | {status}{role}")
        print(f"   📊 Уровень: {hero.level}")
        print(f"   ❤️ Здоровье: {hero.health_current}/{hero.health_max}")
        print(f"   🔵 Мана: {hero.mana_current}/{hero.mana_max}")
        # Показываем скрытые статы, если изучено "Понимание героев"
        if game_state.get("hero_understanding") or game_state.get("flags", {}).get("hero_understanding"):
            print(f"   {hero.get_hidden_stats(game_state)}")
        print("-" * 50)
    
    press_enter_to_continue()