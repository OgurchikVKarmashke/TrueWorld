# sound_system.py
# ui.sound_system.py
import os
import platform
import subprocess
import time

class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.system = platform.system()
    
    def load_sounds(self):
        """Загрузка звуковых эффектов (заглушка)"""
        # В реальной реализации здесь можно загружать звуковые файлы
        # но для простоты сделаем заглушку
        sound_files = {
            'button_click': 'sounds/click.wav',
            'achievement': 'sounds/achievement.wav',
            'build': 'sounds/build.wav',
            'error': 'sounds/error.wav'
        }
        
        for name, path in sound_files.items():
            self.sounds[name] = path
    
    def play_sound(self, sound_name, volume=0.3):
        """Воспроизведение звука (заглушка)"""
        # Вместо реального воспроизведения просто выводим сообщение
        sound_messages = {
            'button_click': '🔊',
            'achievement': '🎵',
            'build': '🔨',
            'error': '❌'
        }
        
        if sound_name in sound_messages:
            print(sound_messages[sound_name], end=" ", flush=True)
            time.sleep(0.1)
    
    def play_music(self, music_file, volume=0.1, loop=-1):
        """Воспроизведение музыки (заглушка)"""
        print("🎶 Фоновая музыка включена")
        self.music_playing = True
    
    def stop_music(self):
        """Остановка музыки"""
        print("🎶 Музыка выключена")
        self.music_playing = False
    
    def toggle_music(self):
        """Переключение музыки"""
        if self.music_playing:
            self.stop_music()
        else:
            self.play_music('sounds/background.mp3')