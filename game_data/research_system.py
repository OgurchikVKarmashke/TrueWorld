# game_data/research_system.py
class Research:
    def __init__(self, key, name, description, base_cost, max_level=1, min_lab_level=1, reveal_floors=None):
        self.key = key
        self.name = name
        self.description = description
        self.base_cost = base_cost
        self.max_level = max_level
        self.min_lab_level = min_lab_level
        self.reveal_floors = reveal_floors or []
        self.level = 0
        self.is_researched = False

    def next_level_available_by_floor(self, max_tower_floor: int) -> bool:
        """Проверяет, доступен ли следующий уровень на основе МАКСИМАЛЬНОГО достигнутого этажа"""
        next_level = self.level + 1
        if next_level > self.max_level:
            return False
        idx = next_level - 1
        if idx < len(self.reveal_floors):
            return max_tower_floor >= self.reveal_floors[idx]
        return True

    def next_level_cost(self):
        next_level = self.level + 1
        return {
            "gold": self.base_cost["gold"] * next_level,
            "crystals": self.base_cost["crystals"] * next_level
        }


class ResearchManager:
    def __init__(self):
        self.researches = {
            "hero_understanding": Research(
                key="hero_understanding",
                name="Понимание героев",
                description="Позволяет видеть характеристики и статусы героев",
                base_cost={"gold": 500, "crystals": 50},
                max_level=1,
                min_lab_level=1,
                reveal_floors=[5]
            ),
            "party_expansion": Research(
                key="party_expansion",
                name="Расширение отрядов",
                description="Позволяет создавать дополнительные боевые группы",
                base_cost={"gold": 100, "crystals": 10},
                max_level=3,
                min_lab_level=1,
                reveal_floors=[5, 10, 15]
            ),
        }

    def is_visible(self, key, game_state):
        """Показываем исследование, если оно еще не исследовано и МАКСИМАЛЬНЫЙ этаж позволяет"""
        research = self.researches[key]
        max_tower_floor = game_state.get("max_tower_floor", game_state.get("tower_level", 1))
        
        # Если исследование уже исследовано, не показываем
        if research.is_researched:
            return False
        
        # Если есть уровни исследования, проверяем доступность по МАКСИМАЛЬНОМУ этажу
        return research.next_level_available_by_floor(max_tower_floor)

    def can_research(self, key, game_state):
        """Проверяет возможность исследования"""
        research = self.researches[key]
        if research.level >= research.max_level:
            return False, "Исследование достигло максимального уровня"

        # Используем МАКСИМАЛЬНЫЙ достигнутый этаж
        max_tower_floor = game_state.get("max_tower_floor", game_state.get("tower_level", 1))
        if not research.next_level_available_by_floor(max_tower_floor):
            required_floor = research.reveal_floors[research.level] if research.level < len(research.reveal_floors) else "?"
            return False, f"Недоступно: требуется достичь этажа {required_floor}"

        lab = game_state["buildings"].get_building("laboratory")
        if lab is None or lab.level < research.min_lab_level:
            return False, f"Требуется Лаборатория ур. {research.min_lab_level}"

        # ПРОВЕРКА НА НАЗНАЧЕННОГО ИССЛЕДОВАТЕЛЯ
        if "role_system" in game_state:
            role_system = game_state["role_system"]
            assigned_heroes = role_system.get_assigned_heroes()
            if "laboratory" not in assigned_heroes or assigned_heroes["laboratory"] is None:
                return False, "Требуется назначить исследователя в Лабораторию"
        else:
            # Если системы ролей нет, тоже требуем исследователя
            lab = game_state["buildings"].get_building("laboratory")
            if lab is None or not hasattr(lab, 'assigned_hero') or lab.assigned_hero is None:
                return False, "Требуется назначить исследователя в Лабораторию"

        cost = research.next_level_cost()
        if not game_state["wallet"].subtract_gold(cost["gold"], check_only=True):
            return False, "Недостаточно золота"
        if not game_state["wallet"].subtract_crystals(cost["crystals"], check_only=True):
            return False, "Недостаточно кристаллов"

        return True, "Можно исследовать"

    def _apply_effect(self, key, game_state):
        """Применяет эффект исследования"""
        research = self.researches[key]
        if research.level <= 0:
            return

        if key == "hero_understanding":
            # Устанавливаем флаг, что исследование изучено
            game_state["hero_understanding"] = True
            if "flags" not in game_state:
                game_state["flags"] = {}
            game_state["flags"]["hero_understanding"] = True

        elif key == "party_expansion":
            # ПРОСТОЙ СПОСОБ: устанавливаем max_parties
            target_max_parties = 1 + research.level
            
            # Убедимся что party_system существует
            if "party_system" not in game_state:
                game_state["party_system"] = {
                    "max_parties": 1,
                    "parties": {
                        "party_1": {
                            "name": "Основная группа",
                            "heroes": [],
                            "is_unlocked": True
                        }
                    },
                    "current_party": "party_1"
                }
            
            # Устанавливаем новое максимальное количество групп
            game_state["party_system"]["max_parties"] = target_max_parties
            
            # Создаем недостающие группы
            parties = game_state["party_system"]["parties"]
            for i in range(len(parties) + 1, target_max_parties + 1):
                pid = f"party_{i}"
                if pid not in parties:
                    parties[pid] = {
                        "name": f"Боевая группа №{i}",
                        "heroes": [],
                        "is_unlocked": True
                    }

    def apply_all_effects(self, game_state):
        """Применить эффекты всех исследований (используется после загрузки сейва)."""
        for key in self.researches.keys():
            self._apply_effect(key, game_state)

    def start_research(self, key, game_state):
        """Запускает исследование"""
        can, msg = self.can_research(key, game_state)
        if not can:
            return False, msg

        research = self.researches[key]
        cost = research.next_level_cost()
        
        # Позже можно добавить бонусы от исследователя
        researcher_bonus = 1.0
        if "role_system" in game_state:
            role_system = game_state["role_system"]
            assigned_heroes = role_system.get_assigned_heroes()
            if "laboratory" in assigned_heroes and assigned_heroes["laboratory"] is not None:
                researcher = assigned_heroes["laboratory"]
                # Здесь позже будет логика бонусов от навыков героя
                pass
        
        actual_cost = {
            "gold": int(cost["gold"] * researcher_bonus),
            "crystals": int(cost["crystals"] * researcher_bonus)
        }

        game_state["wallet"].subtract_gold(actual_cost["gold"])
        game_state["wallet"].subtract_crystals(actual_cost["crystals"])

        research.level += 1
        if research.level >= research.max_level:
            research.is_researched = True

        self._apply_effect(key, game_state)

        return True, f"{research.name} ур.{research.level} изучено!"

    def export_state(self):
        data = {}
        for key, r in self.researches.items():
            data[key] = {
                "level": r.level,
                "is_researched": r.is_researched,
            }
        return data

    def import_state(self, saved_data):
        if not saved_data:
            return
        for key, state in saved_data.items():
            if key in self.researches:
                r = self.researches[key]
                level = state.get("level", r.max_level if state.get("is_researched") else 0)
                r.level = max(0, min(level, r.max_level))
                r.is_researched = r.level >= r.max_level