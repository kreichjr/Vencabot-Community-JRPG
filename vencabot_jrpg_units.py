class GenericUnit:
    def __init__(self, name, hp, atk, defense, mp, lp):
        self.unit_name = name
        self.attack = int(atk)
        self.defense = int(defense)
        self.hp = int(hp)
        self.max_hp = int(hp)
        self.mp = int(mp)
        self.max_mp = int(mp)
        self.life_points = int(lp)
        self.max_life_points = int(lp)
        self.exhaustion = 0
        self.skill_list = []
        self.status_effect_list = []

    def __str__(self):
        return_string = (
                f"{self.unit_name}\n"
                f"HP: {self.hp} / {self.max_hp}\n"
                f"ATK: {self.attack}\n"
                f"DEF: {self.defense}\n"
                f"MP: {self.mp} / {self.max_mp}\n"
                f"LP: {self.life_points} / {self.max_life_points}\n"
                f"Exhaustion: {self.exhaustion}")
        return return_string

class IvanOoze(GenericUnit):
    def __init__(self):
        super().__init__("Ivan Ooze", 300, 30, 15, 80, 3)

class MegaMan(GenericUnit):
    def __init__(self):
        super().__init__("Mega Man", 280, 25, 24, 60, 3)

class Ryu(GenericUnit):
    def __init__(self):
        super().__init__("Ryu", 330, 35, 18, 50, 3)

master_list_of_units = [IvanOoze, MegaMan, Ryu]