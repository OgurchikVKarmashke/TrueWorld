# ui/color_utils.py
import re
from colorama import Fore, Style

def colorize_numbers(text, number_type="damage"):
    """Окрашивает все числа в тексте в зависимости от типа"""
    color_map = {
        "damage": Fore.RED,      # Урон - красный
        "blocked": Fore.BLUE,    # Заблокированный урон (защита) - синий
        "health": Fore.GREEN,    # Здоровье - зеленый
        "heal": Fore.GREEN,      # Лечение - зеленый
        "mana": Fore.CYAN,       # Мана - голубой
    }
    
    color = color_map.get(number_type, Style.RESET_ALL)
    
    # Находим все числа в тексте и окрашиваем их
    def replace_numbers(match):
        number = match.group(0)
        return f"{color}{number}{Style.RESET_ALL}"
    
    return re.sub(r'\b\d+\b', replace_numbers, text)

def colorize_text(text, color_name):
    """Окрашивает весь текст в указанный цвет"""
    color_map = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA
    }
    color = color_map.get(color_name, Style.RESET_ALL)
    return color + text + Style.RESET_ALL

def colorize_damage_message(message: str) -> str:
    """Окрашивает сообщение об уроне с учетом разных типов чисел"""
    # Если это сообщение о смерти, окрашиваем весь текст в красный
    if "повержен" in message.lower() or "вернулся в объятья" in message.lower():
        return f"{Fore.RED}{message}{Style.RESET_ALL}"
    
    # Для обычных сообщений об уроне
    result = message
    
    # Ищем все числа и их позиции
    numbers_with_positions = []
    for match in re.finditer(r'\b\d+\b', message):
        numbers_with_positions.append({
            'number': match.group(),
            'start': match.start(),
            'end': match.end()
        })
    
    if not numbers_with_positions:
        return result
    
    # Определяем, есть ли заблокированный урон
    has_blocked = "заблокировано" in message.lower()
    
    # Если есть заблокированный урон и минимум 3 числа
    if has_blocked and len(numbers_with_positions) >= 3:
        # Первое число - урон (красный)
        damage = numbers_with_positions[0]
        # Второе число - заблокированный урон (синий)
        blocked = numbers_with_positions[1]
        # Последнее число - здоровье (зеленый)
        health = numbers_with_positions[-1]
        
        # Заменяем в обратном порядке (от конца к началу), чтобы позиции не смещались
        # Сначала здоровье (последнее)
        result = result[:health['start']] + f"{Fore.GREEN}{health['number']}{Style.RESET_ALL}" + result[health['end']:]
        
        # Обновляем позиции после первой замены
        # Заблокированный урон может сместиться, если до него были числа
        # Но у нас заблокированный урон - второе число, а мы заменяем с конца, 
        # поэтому его позиция относительно начала не изменится
        
        # Теперь заменяем заблокированный урон (синий)
        # Находим его новую позицию в уже измененной строке
        # Ищем второе число в измененной строке
        temp_numbers = list(re.finditer(r'\b\d+\b', result))
        if len(temp_numbers) >= 2:
            blocked_new = temp_numbers[1]
            result = result[:blocked_new.start()] + f"{Fore.BLUE}{blocked_new.group()}{Style.RESET_ALL}" + result[blocked_new.end():]
        
        # Ищем первое число для урона (красный)
        temp_numbers = list(re.finditer(r'\b\d+\b', result))
        if temp_numbers:
            damage_new = temp_numbers[0]
            result = result[:damage_new.start()] + f"{Fore.RED}{damage_new.group()}{Style.RESET_ALL}" + result[damage_new.end():]
    
    elif not has_blocked and len(numbers_with_positions) >= 2:
        # Только урон и здоровье
        damage = numbers_with_positions[0]
        health = numbers_with_positions[-1]
        
        # Сначала заменяем здоровье (зеленый)
        result = result[:health['start']] + f"{Fore.GREEN}{health['number']}{Style.RESET_ALL}" + result[health['end']:]
        
        # Затем заменяем урон (красный)
        # Находим первое число в измененной строке
        temp_numbers = list(re.finditer(r'\b\d+\b', result))
        if temp_numbers:
            damage_new = temp_numbers[0]
            result = result[:damage_new.start()] + f"{Fore.RED}{damage_new.group()}{Style.RESET_ALL}" + result[damage_new.end():]
    
    return result

def get_health_color(current, max_hp):
    """Возвращает цвет для здоровья в зависимости от процента"""
    if max_hp <= 0:
        return Fore.RED
    percent = current / max_hp
    if percent > 0.5:
        return Fore.GREEN
    elif percent > 0.25:
        return Fore.YELLOW
    else:
        return Fore.RED

def colorize_skill_message(message: str) -> str:
    """Окрашивает сообщение от навыков"""
    # Разделяем сообщение на строки (если есть переносы)
    lines = message.split('\n')
    colored_lines = []
    
    for line in lines:
        # Для каждой строки применяем colorize_damage_message
        colored_lines.append(colorize_damage_message(line))
    
    return '\n'.join(colored_lines)