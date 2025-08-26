# relationship_system.py
# systems/relationship_system.py
class RelationshipSystem:
    # Матрица совместимости черт характера
    COMPATIBILITY_MATRIX = {
        "Храбрый": {"Храбрый": 1.15, "Трусливый": 0.8, "Мудрый": 1.1, "Добрый": 1.05, "Злой": 0.9},
        "Трусливый": {"Храбрый": 0.8, "Трусливый": 1.0, "Хитрый": 1.1, "Ленивый": 1.05},
        "Мудрый": {"Храбрый": 1.1, "Мудрый": 1.1, "Хитрый": 1.05, "Творческий": 1.15},
        "Хитрый": {"Трусливый": 1.1, "Мудрый": 1.05, "Хитрый": 1.0, "Злой": 1.1},
        "Добрый": {"Храбрый": 1.05, "Добрый": 1.1, "Мудрый": 1.05, "Злой": 0.7},
        "Злой": {"Храбрый": 0.9, "Злой": 1.0, "Хитрый": 1.1, "Добрый": 0.7},
        "Ленивый": {"Трусливый": 1.05, "Ленивый": 1.0, "Медлительный": 1.1},
        "Везучий": {"Храбрый": 1.1, "Везучий": 1.2, "Все": 1.05},
        "Сильный": {"Храбрый": 1.1, "Сильный": 1.1, "Слабый": 0.9},
        "Слабый": {"Сильный": 0.9, "Слабый": 1.0, "Хитрый": 1.05},
        "Быстрый": {"Храбрый": 1.05, "Быстрый": 1.1, "Медлительный": 0.8},
        "Медлительный": {"Быстрый": 0.8, "Медлительный": 1.0, "Ленивый": 1.1},
        "Творческий": {"Мудрый": 1.15, "Творческий": 1.1, "Практичный": 0.9},
        "Практичный": {"Мудрый": 1.05, "Практичный": 1.1, "Творческий": 0.9}
    }
    
    # Бонусы за наборы одинаковых черт
    SET_BONUSES = {
        3: 1.15,  # +15% за 3 одинаковых черты
        4: 1.25,  # +25% за 4 одинаковых черты  
        5: 1.4    # +40% за 5+ одинаковых черт
    }
    
    @staticmethod
    def calculate_party_bonus(heroes):
        """Рассчитывает бонусы группы на основе совместимости черт"""
        if not heroes or len(heroes) < 2:
            return 1.0  # Нет бонуса для одиночек или пустых групп
        
        total_bonus = 1.0
        trait_counts = {}
        
        # Считаем количество каждой черты
        for hero in heroes:
            trait = hero.character
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        # Применяем бонусы за наборы одинаковых черт
        for trait, count in trait_counts.items():
            if count >= 3:
                set_bonus = RelationshipSystem.SET_BONUSES.get(count, 1.0)
                total_bonus *= set_bonus
        
        # Применяем бонусы совместимости между всеми героями
        for i, hero1 in enumerate(heroes):
            for j, hero2 in enumerate(heroes):
                if i != j:  # Не сравниваем героя с самим собой
                    trait1 = hero1.character
                    trait2 = hero2.character
                    
                    compatibility = RelationshipSystem.COMPATIBILITY_MATRIX.get(
                        trait1, {}).get(trait2, 1.0)
                    
                    total_bonus *= compatibility
        
        # Ограничиваем бонус разумными пределами
        return max(0.5, min(2.0, total_bonus))
    
    @staticmethod
    def get_relationship_description(bonus):
        """Возвращает текстовое описание отношения бонуса"""
        if bonus >= 1.5:
            return "🎉 Идеальная синергия! (+{:.0f}%)".format((bonus-1)*100)
        elif bonus >= 1.2:
            return "👍 Отличная совместимость (+{:.0f}%)".format((bonus-1)*100)
        elif bonus >= 1.0:
            return "✅ Нормальные отношения (+{:.0f}%)".format((bonus-1)*100)
        elif bonus >= 0.8:
            return "⚠️ Напряжённые отношения ({:.0f}%)".format((bonus-1)*100)
        else:
            return "❌ Конфликт в группе ({:.0f}%)".format((bonus-1)*100)
    
    @staticmethod
    def get_party_synergy_details(heroes):
        """Возвращает детализированную информацию о синергии группы"""
        if not heroes:
            return "Группа пуста"
        
        details = []
        trait_counts = {}
        
        for hero in heroes:
            trait = hero.character
            trait_counts[trait] = trait_counts.get(trait, 0) + 1
        
        # Информация о наборах черт
        for trait, count in trait_counts.items():
            if count >= 3:
                bonus = RelationshipSystem.SET_BONUSES.get(count, 1.0)
                details.append(f"🎯 {count}x {trait}: +{int((bonus-1)*100)}%")
        
        # Информация о парных отношениях
        for i, hero1 in enumerate(heroes):
            for j, hero2 in enumerate(heroes):
                if i < j:  # Чтобы не дублировать пары
                    trait1 = hero1.character
                    trait2 = hero2.character
                    compat = RelationshipSystem.COMPATIBILITY_MATRIX.get(trait1, {}).get(trait2, 1.0)
                    
                    if compat != 1.0:
                        arrow = "↑" if compat > 1.0 else "↓"
                        details.append(f"🔗 {trait1} ↔ {trait2}: {arrow}{abs(int((compat-1)*100))}%")
        
        return details