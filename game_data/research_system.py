# game_data/research_system.py

class Research:
    def __init__(self, key, name, description, base_cost, max_level=1, min_lab_level=1, reveal_floors=None):
        """
        reveal_floors: список этажей, после которых появляется возможность изучать уровни (по индексу -> уровень)
            пример: [5, 10, 15] означает:
                ур.1 появляется после этажа 5,
                ур.2 появляется после этажа 10,
                ур.3 появляется после этажа 15
        """
        self.key = key
        self.name = name
        self.description = description
        self.base_cost = base_cost  # {'gold': int, 'crystals': int}
        self.max_level = max_level
        self.min_lab_level = min_lab_level
        self.reveal_floors = reveal_floors or []
        self.level = 0
        self.is_researched = False  # True, когда level == max_level

    def next_level_available_by_floor(self, tower_level: int) -> bool:
        """
        Проверяем, доступен ли следующий уровень исследования по зачистке нужного этажа.
        Если список reveal_floors короче max_level, считаем, что оставшиеся уровни по этажу не ограничены.
        """
        next_level = self.level + 1
        if next_level > self.max_level:
            return False
        idx = next_level - 1
        if idx < len(self.reveal_floors):
            return tower_level >= self.reveal_floors[idx]
        return True

    def next_level_cost(self):
        """
        Стоимость следующего уровня. Стоимость скалируется линейно: base * (уровень)
        """
        next_level = self.level + 1
        return {
            "gold": self.base_cost["gold"] * next_level,
            "crystals": self.base_cost["crystals"] * next_level
        }


class ResearchManager:
    def __init__(self):
        # 1) Понимание героев (1 уровень, лаборатория 1, появляется после этажа 5)
        # 2) Расширение отрядов (до 3 уровней: ур.1 -> 2 группы, ур.2 -> 3 группы, ур.3 -> 4 группы),
        #    уровни появляются после этажей [5, 10, 15]
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

    # ===== ВИДИМОСТЬ / ПРОВЕРКИ =====

    def is_visible(self, key, game_state):
        """Показывать ли технологию в списке (если доступен следующий уровень по этажу)"""
        research = self.researches[key]
        tower_level = game_state["tower_level"]
        return (not research.is_researched) and research.next_level_available_by_floor(tower_level)

    def can_research(self, key, game_state):
        """
        Можно ли изучить следующий уровень:
        - технология не макс.
        - достигнут нужный этаж для след. уровня
        - уровень лаборатории
        - хватает ресурсов
        """
        research = self.researches[key]
        if research.level >= research.max_level:
            return False, "Исследование достигло максимального уровня"

        if not research.next_level_available_by_floor(game_state["tower_level"]):
            return False, "Недоступно: требуется зачистить более высокий этаж"

        lab = game_state["buildings"].get_building("laboratory")
        if lab is None or lab.level < research.min_lab_level:
            return False, f"Требуется Лаборатория ур. {research.min_lab_level}"

        cost = research.next_level_cost()
        if not game_state["wallet"].subtract_gold(cost["gold"], check_only=True):
            return False, "Недостаточно золота"
        if not game_state["wallet"].subtract_crystals(cost["crystals"], check_only=True):
            return False, "Недостаточно кристаллов"

        return True, "Можно исследовать"

    # ===== ЭФФЕКТЫ =====

    def _apply_effect(self, key, game_state):
        research = self.researches[key]
        if research.level <= 0:
            return

        if key == "hero_understanding":
            game_state["hero_understanding"] = True
            game_state.setdefault("flags", {})["hero_understanding"] = True

        elif key == "party_expansion":
            # 1 базовая группа + каждый уровень даёт +1
            max_parties = 1 + research.level
            ps = game_state["party_system"]
            ps["max_parties"] = max_parties

            # Создаём недостающие группы
            parties = ps["parties"]
            for i in range(2, max_parties + 1):
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

    # ===== СТАРТ ИССЛЕДОВАНИЯ =====

    def start_research(self, key, game_state):
        can, msg = self.can_research(key, game_state)
        if not can:
            return False, msg

        research = self.researches[key]
        cost = research.next_level_cost()

        game_state["wallet"].subtract_gold(cost["gold"])
        game_state["wallet"].subtract_crystals(cost["crystals"])

        research.level += 1
        if research.level >= research.max_level:
            research.is_researched = True

        self._apply_effect(key, game_state)

        return True, f"{research.name} ур.{research.level} изучено!"

    # ===== СЕРИАЛИЗАЦИЯ =====

    def export_state(self):
        """Сериализация уровней исследований"""
        data = {}
        for key, r in self.researches.items():
            data[key] = {
                "level": r.level,
                "is_researched": r.is_researched,
            }
        return data

    def import_state(self, saved_data):
        """Десериализация уровней (с обратной совместимостью по старым сейвам)"""
        if not saved_data:
            return
        for key, state in saved_data.items():
            if key in self.researches:
                r = self.researches[key]
                # Поддержка старых сейвов (когда был только is_researched)
                level = state.get("level", r.max_level if state.get("is_researched") else 0)
                r.level = max(0, min(level, r.max_level))
                r.is_researched = r.level >= r.max_level
