#synthesis_room_system.py
#systems.synthesis_room_system.py
import random

def get_available_heroes(heroes, base_hero, current_sacrifices):
    """Возвращает список доступных героев для синтеза"""
    return [h for h in heroes if h != base_hero and h not in current_sacrifices]

def calculate_synthesis_bonuses(sacrifices):
    """Рассчитывает бонусы от синтеза"""
    total_exp = sum(hero.level * 50 for hero in sacrifices)
    stat_bonus_chance = 0.1 * len(sacrifices)  # 10% за каждого героя
    return total_exp, stat_bonus_chance

def synthesize_heroes(game_state, base_hero, sacrifices):
    """
    Основная логика синтеза героев
    Возвращает: (результатное сообщение, была ли улучшена характеристика)
    """
    total_exp, stat_bonus_chance = calculate_synthesis_bonuses(sacrifices)
    
    # Применяем опыт
    result_message = base_hero.add_experience(total_exp)
    
    # Проверяем усиление характеристик
    stat_improved = False
    if random.random() < stat_bonus_chance:
        stat_improved = improve_random_stat(base_hero)
        if stat_improved:
            result_message += f"\n✨ {base_hero.name} получает +1 к {stat_improved}!"
    
    # Удаляем жертвенных героев
    remove_sacrificed_heroes(game_state, sacrifices)
    
    # Очищаем группы от удаленных героев
    cleanup_party_system(game_state)
    
    return result_message, stat_improved

def cleanup_party_system(game_state):
    """Очищает систему групп от удаленных героев"""
    if "party_system" in game_state:
        from systems.party_system import PartySystem
        party_system = PartySystem(game_state)
        party_system.cleanup_dead_heroes()

def improve_random_stat(hero):
    """Улучшает случайную характеристику героя"""
    stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
    chosen_stat = random.choice(stats)
    current_value = getattr(hero, chosen_stat)
    setattr(hero, chosen_stat, current_value + 1)
    
    stat_names = {
        'strength': 'Сила', 'dexterity': 'Ловкость', 
        'constitution': 'Выносливость', 'intelligence': 'Интеллект',
        'wisdom': 'Мудрость', 'charisma': 'Харизма'
    }
    
    return stat_names[chosen_stat]

def remove_sacrificed_heroes(game_state, sacrifices):
    """Удаляет жертвенных героев из игры"""
    for hero in sacrifices:
        if hero in game_state["heroes"]:
            game_state["heroes"].remove(hero)