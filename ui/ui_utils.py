# ui_utils.py
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_screen(duration=2, message="Загрузка"):
    """
    Создает анимированный экран загрузки с точками
    """
    clear_screen()
    end_time = time.time() + duration
    dot_stages = [".", "..", "..."]
    
    while time.time() < end_time:
        for dots in dot_stages:
            if time.time() >= end_time:
                break
            print(f"{message}{dots}")
            time.sleep(0.3)
            clear_screen()
    
    clear_screen()

def press_enter_to_continue():
    input("\nНажмите Enter чтобы продолжить...")

def print_header(title):
    """
    Красиво отображает заголовок
    """
    clear_screen()
    print("=" * 50)
    print(f"=== {title.upper()} ===")
    print("=" * 50)
    print()