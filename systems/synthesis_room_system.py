# systems/synthesis_room_system.py
import random

def get_available_heroes(heroes, base_hero, current_sacrifices):
    """Возвращает список доступных героев для синтеза"""
    return [h for h in heroes if h != base_hero and h not in current_sacrifices]

def calculate_synthesis_bonuses(base_hero, sacrifices):
    """Рассчитывает бонусы от синтеза с учетом звездности"""
    total_exp = 0
    for hero in sacrifices:
        # УВЕЛИЧИМ ФОРМУЛУ: опыт = (уровень героя)^2 * 50 * модификатор звезды
        star_multiplier = 1.0 + (hero.star - 1) * 0.5  # 50% за каждую звезду
        hero_exp = int((hero.level ** 2) * 50 * star_multiplier)
        total_exp += hero_exp
    
    # Базовый шанс 10% за героя, увеличивается на 5% за каждую звезду выше 1
    base_chance = 0.1
    star_bonus = sum((hero.star - 1) * 0.05 for hero in sacrifices)
    stat_bonus_chance = base_chance * len(sacrifices) + star_bonus
    
    # Ограничиваем максимальный шанс 80%
    stat_bonus_chance = min(stat_bonus_chance, 0.8)
    
    return total_exp, stat_bonus_chance

def synthesize_heroes(game_state, base_hero, sacrifices):
    """
    Основная логика синтеза героев
    Возвращает: (результатное сообщение, была ли улучшена характеристика)
    """
    total_exp, stat_bonus_chance = calculate_synthesis_bonuses(base_hero, sacrifices)
    
    # Применяем опыт
    old_level = base_hero.level
    result_message = base_hero.add_experience(total_exp)
    
    # Убираем дублирование в сообщении об уровне
    if f"достиг {old_level + 1} уровня" in result_message:
        result_message = f"{base_hero.name} достиг {base_hero.level} уровня!"
    
    # Проверяем усиление характеристик
    stat_improved = False
    stat_name = None
    if random.random() < stat_bonus_chance:
        stat_name = improve_random_stat(base_hero)
        stat_improved = True
    
    # Удаляем жертвенных героев
    remove_sacrificed_heroes(game_state, sacrifices)
    
    # Очищаем группы от удаленных героев
    cleanup_party_system(game_state)
    
    # АВТОСОХРАНЕНИЕ: Сохраняем игру без уведомления игрока
    if "save_system" in game_state:
        try:
            game_state["save_system"].save_game(game_state, 1)
        except Exception:
            pass  # Игнорируем ошибки сохранения, чтобы не прерывать процесс
    
    return result_message, stat_improved, stat_name

def cleanup_party_system(game_state):
    """Очищает систему групп от удаленных героев"""
    if "party_system" in game_state:
        from systems.party_system import PartySystem
        party_system = PartySystem(game_state)
        party_system.cleanup_dead_heroes()

def improve_random_stat(hero):
    """Улучшает случайную характеристику героя (ТОЛЬКО 4 основные)"""
    # ТОЛЬКО 4 характеристики, без мудрости и харизмы
    stats = ['strength', 'dexterity', 'constitution', 'intelligence']
    chosen_stat = random.choice(stats)
    current_value = getattr(hero, chosen_stat)
    setattr(hero, chosen_stat, current_value + 1)
    
    # Пересчитываем производные характеристики (HP, MP, атака, защита)
    hero.calculate_derived_stats(hero.level)
    
    stat_names = {
        'strength': 'Сила', 
        'dexterity': 'Ловкость', 
        'constitution': 'Выносливость', 
        'intelligence': 'Интеллект'
    }
    
    return stat_names[chosen_stat]

def remove_sacrificed_heroes(game_state, sacrifices):
    """Удаляет жертвенных героев из игры"""
    for hero in sacrifices:
        if hero in game_state["heroes"]:
            game_state["heroes"].remove(hero)