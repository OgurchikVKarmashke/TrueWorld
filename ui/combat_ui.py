# ui/combat_ui.py
import time
import colorama
from ui.ui_utils import clear_screen, print_header
from ui.color_utils import colorize_damage_message, colorize_text, get_health_color
from colorama import Fore, Back, Style
from typing import List, Dict, Optional
from systems.hero_system import Hero
from systems.combat_system import Monster

"""
Интерфейс боя, победы и поражения.
Отделен от логики боевой системы.
"""

# Инициализируем colorama в начале файла
colorama.init()


def show_damage_message(message: str, is_heavy_damage: bool = False):
    """Показывает сообщение об уроне с цветом"""
    from ui.color_utils import colorize_damage_message
    
    colored_message = colorize_damage_message(message)
    print(colored_message)

def show_turn_divider(side: str = "monsters"):
    """Показывает разделитель между ходами сторон"""
    if side == "monsters":
        print("\n" + "-"*50 + " [ХОД МОНСТРОВ] " + "-"*50)
    else:
        print("\n" + "-"*50 + " [ХОД ГЕРОЕВ] " + "-"*50)
    time.sleep(0.3)

def show_combat_intro(heroes: List[Hero], monsters: List[Monster], floor: int) -> None:
    """Показывает вводную информацию о бое"""
    print("=" * 60)
    print(f"🏰 БАШНЯ ИСПЫТАНИЙ - ЭТАЖ {floor}")
    print("=" * 60)
    time.sleep(1)

def get_location_icon(location_name: str) -> str:
    """Возвращает иконку для локации"""
    icons = {
        "Равнина": "🏞️",
        "Лес": "🌲",
        "Пустыня": "🏜️",
        "Горный перевал": "⛰️",
        "Замок": "🏰",
        "Подземелье": "🕳️",
        "Болото": "🐊",
        "Пещера": "🕸️",
        "Деревня гоблинов": "👺",
        "Некрополь": "💀"
    }
    return icons.get(location_name, "🗺️")

def get_weather_icon(weather_name: str) -> str:
    """Возвращает иконку для погоды"""
    icons = {
        "Ясная погода": "☀️",
        "Облачно": "⛅",
        "Дождь": "🌧️",
        "Ветрено": "💨",
        "Гроза": "⚡",
        "Аномальная жара": "🔥",
        "Снежный буран": "❄️",
        "Песчаная буря": "🌪️",
        "Густой туман": "🌫️",
        "Магическая буря": "🌀"
    }
    return icons.get(weather_name, "🌤️")

def show_location_and_weather(location_name: str, location_desc: str, 
                             weather_name: str, weather_desc: str, is_dangerous: bool) -> None:
    """Показывает информацию о локации и погоде"""
    print("\n" + "="*60)
    print(f"🗺️ Локация: {location_name}")
    print(f"   {location_desc}")
    print(f"\n🌤️ Погода: {weather_name}")
    print(f"   {weather_desc}")
    if is_dangerous:
        print("   ⚠️ ОПАСНАЯ ПОГОДА!")
    print("="*60)
    time.sleep(1.5)

def show_enemies_info(monsters: List[Monster]) -> None:
    """Показывает информацию о противниках"""
    print("\n👹 ПРОТИВНИКИ:")
    for monster in monsters:
        status = "❤️" if monster.is_alive else "💀"
        # с эмодзи
        print(f"  {status} {monster.name} (Ур. {monster.level}) | ❤️{int(monster.health_max)} ⚔️{int(monster.attack)} 🛡️{int(monster.defense)}")
    print("="*60)
    time.sleep(1.5)

def show_traps_info(traps_info: List[Dict]) -> None:
    """Показывает информацию о ловушках"""
    if traps_info:
        print("\n⚠️ ОБНАРУЖЕННЫЕ ЛОВУШКИ:")
        for trap in traps_info:
            status_icon = "✅" if trap["status"] == "✅ Обнаружена" else "❓"
            print(f"   {status_icon} {trap['name']} (шанс срабатывания: {trap['chance']})")
        print("="*60)
    else:
        print("\n✅ Ловушки не обнаружены")
    print("="*60)
    time.sleep(1)

def show_round_start(round_number: int, heroes: List[Hero], monsters: List[Monster]) -> None:
    """Показывает начало раунда"""
    print(f"\n{'='*40}")
    print(f"📯 РАУНД {round_number}")
    print(f"{'='*40}")
    
    # Показываем сгруппированные эффекты
    effect_messages = show_active_effects_before_round(heroes, monsters)
    if effect_messages:
        print("\n💫 АКТИВНЫЕ ЭФФЕКТЫ:")
        for msg in effect_messages:
            print(f"  {msg}")
        print("-"*40)
    
    time.sleep(0.5)

def show_hero_action(hero: Hero, action_text: str) -> None:
    """Показывает действие героя"""
    print(f"👤 {hero.name}: {action_text}")
    time.sleep(0.8)

def show_monster_action(monster: Monster, action_text: str) -> None:
    """Показывает действие монстра"""
    print(f"👹 {monster.name}: {action_text}")
    time.sleep(0.8)

def show_trap_activation(message: str) -> None:
    """Показывает активацию ловушки"""
    print(f"⚠️ {message}")
    time.sleep(0.6)

def show_weather_effect(message: str) -> None:
    """Показывает эффект погоды"""
    if message:  # Показываем только если есть сообщение
        print(f"🌤️ {message}")
        time.sleep(0.5)

def show_status_effect(message: str) -> None:
    """Показывает статус-эффект"""
    if message:
        print(f"💫 {message}")
        time.sleep(0.4)

def show_kill_message(monster: Monster, exp: int) -> None:
    """Показывает сообщение об убийстве монстра"""
    colored_exp = Fore.YELLOW + f"+{exp} опыта" + Style.RESET_ALL
    print(f"💀 {monster.name} повержен! {colored_exp}")
    time.sleep(0.8)

def show_combat_timeout() -> None:
    """Показывает сообщение о таймауте боя"""
    print("\n⏰ Бой затянулся! Обе стороны истощены...")
    time.sleep(1)

def show_active_effects_before_round(heroes: List[Hero], monsters: List[Monster]) -> List[str]:
    """Показывает активные эффекты перед началом раунда. Возвращает сообщения для лога."""
    messages = []
    
    # Проверяем героев
    for hero in heroes:
        if hasattr(hero, 'status_system') and hero.status_system and hero.is_alive:
            effects = hero.status_system.get_active_effects()
            if effects:
                effect_str = ", ".join(effects)
                messages.append(f"👤 {hero.name}: {effect_str}")
    
    # Проверяем монстров
    for monster in monsters:
        if hasattr(monster, 'status_system') and monster.status_system and monster.is_alive:
            effects = monster.status_system.get_active_effects()
            if effects:
                effect_str = ", ".join(effects)
                messages.append(f"👹 {monster.name}: {effect_str}")
    
    return messages

def show_round_results(heroes_alive: int, monsters_alive: int) -> None:
    """Показывает результаты раунда"""
    print(f"\n📊 После раунда: Герои: {heroes_alive} | Монстры: {monsters_alive}")
    print("-"*40)
    time.sleep(0.5)

def show_combat_result(victory: bool) -> None:
    """Показывает результат боя - ТОЛЬКО надпись"""
    print("\n" + "="*60)
    if victory:
        print("🎉 ПОБЕДА!")
    else:
        print("💥 ПОРАЖЕНИЕ")
    print("="*60)
    time.sleep(1)
    
    print("\nНажмите Enter чтобы продолжить...")
    input()

def show_combat_log(log: List[str]) -> None:
    """Показывает полный лог боя (опционально)"""
    if not log:
        return
        
    print("\n" + "="*60)
    print("📝 ПОЛНЫЙ ЛОГ БОЯ")
    print("="*60)
    
    for entry in log:
        print(entry)
    
    print("="*60)
    print("\nНажмите Enter чтобы продолжить...")
    input()