class GenericSkill:
    def __init__(self, skill_name, ap, mp, base_damage):
        self.skill_name = skill_name
        self.skill_description = ""
        
        self.ap_cost = ap
        self.mp_cost = mp
        self.base_damage = base_damage

        

    def some_func(self):
        pass

class Slap(GenericSkill):
    def __init__(self):
        super().__init__("Slap", 2, 4, 5)
        self.skill_description = "A gentleman's slap that strikes to their soul."

class Kick(GenericSkill):
    def __init__(self):
        super().__init__("Kick", 2, 6, 8)
        self.skill_description = "A strong kick to the mid-section of your opponent."

class Dropkick(GenericSkill):
    def __init__(self):
        super().__init__("Dropkick", 3, 10, 12)
        self.skill_description = "A powerful running dropkick combining your mass and inertia to deliver the mightiest of blows to topple the enemy."

class MegaBusterBlast(GenericSkill):
    def __init__(self):
        super().__init__("Mega Buster Blast", 3, 8, 11)
        self.skill_description = "A charged blast of energy from the Mega Buster of a legendary Maverick Hunter."

class DoubleDragonHeadbutt(GenericSkill):
    def __init__(self):
        super().__init__("Double Dragon NES Headbutt", 4, 12, 20)
        self.skill_description = "The most iconic headbutt."

class Hadouken(GenericSkill):
    def __init__(self):
        super().__init__("Hadouken", 3, 9, 14)
        self.skill_description = (
                "Imagine focusing your body\'s energy into a single focal point " 
                "in the palms of your hands, and then unleashing it at your " 
                "opponent as a large, blue ball of energy that\'s two to three " 
                "times the size of your head... Yep, that\'s a Hadouken!")

class ShiningFinger(GenericSkill):
    def __init__(self):
        super().__init__("Shining Finger", 5, 35, 60)
        self.skill_description = "SHINING FINGER~!"

class OmaeWaMouShindeiru(GenericSkill):
    def __init__(self):
        super().__init__("Omae wa mou shindeiru", 9, 60, 300)
        self.skill_description = "Omae wa mou shindeiru... (You are already dead...)"

class Powerbomb(GenericSkill):
    def __init__(self):
        super().__init__("Powerbomb", 4, 15, 25)
        self.skill_description = (
                "A devestating move where you lift your opponent over your head " 
                "by their hips and slam them onto the ground on their back. OooooOOOOAAAAHHH!~")

master_list_of_skills = [Slap, Kick, Dropkick, MegaBusterBlast, DoubleDragonHeadbutt, Hadouken, ShiningFinger, OmaeWaMouShindeiru, Powerbomb]