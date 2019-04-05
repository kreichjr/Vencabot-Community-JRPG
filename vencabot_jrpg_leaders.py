import enum

# MOD_ATK = enum.auto()
# MOD_DEF = enum.auto()
# MOD_HP  = enum.auto()
# modifier_string = {MOD_ATK: "attack", MOD_DEF: "defense", MOD_HP: "HP"}


class GenericLeader:
    def __init__(self, name, mod_type, mod_stat, mod_string, mod_amount):
        self.leader_name = name
        self.modifier_type = mod_type # Valid options will be "flat" or "percentage"
        self.modifier_stat = mod_stat # What stat are we modifying - Uses the same stat types that units use
        self.modifier_stat_string = mod_string # Just a string representation of the stat
        self.modifier_amount = int(mod_amount) # The value that the stat is being changed by

    def adjust_stat_from_leader_buff(self, unit):
        if self.modifier_stat == "atk":  
            stat = unit.attack
            if self.modifier_type == "percentage":
                return stat + (stat * self.modifier_amount / 100)
            elif self.modifier_type == "flat":
                return stat + self.modifier_amount
        elif self.modifier_stat == "defense":
            stat = unit.defense
            if self.modifier_type == "percentage":
                return stat + (stat * self.modifier_amount / 100)
            elif self.modifier_type == "flat":
                return stat + self.modifier_amount
        elif self.modifier_stat == "hp":
            stat = unit.hp
            if self.modifier_type == "percentage":
                return stat + (stat * self.modifier_amount / 100)
            elif self.modifier_type == "flat":
                return stat + self.modifier_amount
