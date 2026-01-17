# ui/icons.py
# ASCII-совместимые иконки для Windows
ICONS = {
    "tower": "[T]",
    "gold": "[G]",
    "crystal": "[C]",
    "crystals": "[C]",
    "hero": "[H]",
    "heroes": "[H]",
    "party": "[P]",
    "save": "[S]",
    "achievement": "[A]",
    "exit": "[X]",
    "health": "[HP]",
    "mana": "[MP]",
    "attack": "[ATK]",
    "defense": "[DEF]",
    "experience": "[XP]",
    "new": "[NEW]",
    "load": "[LOAD]",
    "floor": "[F]",
    "time": "[T]",
    "arrow": "->",
    "bullet": "*",
    "check": "[V]",
    "cross": "[X]",
    "warning": "[!]",
    "info": "[i]"
}

# Функция для замены
def replace_emoji(text):
    """Заменяет эмодзи на ASCII символы"""
    replacements = {
        "🏰": ICONS["tower"],
        "💰": ICONS["gold"],
        "💎": ICONS["crystal"],
        "💠": ICONS["crystal"],
        "👤": ICONS["hero"],
        "👥": ICONS["party"],
        "💾": ICONS["save"],
        "🏆": ICONS["achievement"],
        "🚪": ICONS["exit"],
        "❤️": ICONS["health"],
        "🔵": ICONS["mana"],
        "⚔️": ICONS["attack"],
        "🛡️": ICONS["defense"],
        "⭐": ICONS["experience"],
        "🎯": "[TARGET]",
        "🌀": "[WAIT]",
        "🔄": "[LOAD]",
        "📁": "[FILE]",
        "🕒": ICONS["time"],
        "↩️": "[BACK]",
        "👋": "[BYE]",
        "✨": "[*]",
        "✅": ICONS["check"],
        "❌": ICONS["cross"],
        "⚠️": ICONS["warning"],
        "ℹ️": ICONS["info"],
        "🎉": "[!]"
    }
    
    for emoji, ascii_char in replacements.items():
        text = text.replace(emoji, ascii_char)
    
    return text