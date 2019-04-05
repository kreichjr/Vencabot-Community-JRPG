import vencabot_jrpg_units
import vencabot_jrpg_skills
import vencabot_jrpg_leaders

import socket
import json
import random
import time
import math

HOST = ""
PORT = 1717

class PlayerData:
    def __init__(self, connection, address, player_name):
        self.connection = connection
        self.address = address
        self.player_name = player_name
        self.selected_leader = None
        self.selected_unit_list = []
        self.starting_unit = None
        self.point_unit = None
        

class GameOfRPS:
    rps_beats = {"rock":"scissors", "paper":"rock", "scissors":"paper"}
    
    def __init__(self, initiative, secondary):
        self.initiative_player = initiative
        self.secondary_player = secondary
    
    def do_match(self):
        is_a_tie = True
        while is_a_tie:
            init_choice = self._get_choice(self.initiative_player)
            sec_choice = self._get_choice(self.secondary_player)

            if init_choice != sec_choice:
                is_a_tie = False
            else:
                msg = create_protocol_string("rps_tie", {"rps_type": init_choice})
                self._alert_players(msg)
        
        winning_player, winning_rps_type = self._determine_winner(init_choice, sec_choice)
        msg = create_protocol_string("rps_won", {"winner": winning_player, "rps_type": winning_rps_type})
        self._alert_players(msg)
        
    def _get_choice(self, player):
        valid_choice = False
        while not valid_choice:
            msg = create_protocol_string("request_rps_choice",{})
            player.connection.sendall(msg)
            choice = player.connection.recv(1024).decode()
            valid_choice = choice in ["rock", "paper", "scissors"]
            if not valid_choice:
                msg = create_protocol_string("invalid_rps_choice",{})
                player.connection.sendall(msg)
        return choice
    
    def _alert_players(self, message):
        self.initiative_player.connection.sendall(message)
        self.secondary_player.connection.sendall(message)

    def _determine_winner(self, init_choice, sec_choice):
        if self.rps_beats[init_choice] == sec_choice:
            return self.initiative_player.player_name, init_choice
        else:
            return self.secondary_player.player_name, sec_choice

    def request_rematch(self):
        init_player_wants_rematch = self._request_rematch(self.initiative_player)
        sec_player_wants_rematch = self._request_rematch(self.secondary_player)

        return init_player_wants_rematch and sec_player_wants_rematch

    def _request_rematch(self, player):
        msg = create_protocol_string("request_rematch",{})
        player.connection.sendall(msg)
        choice = player.connection.recv(1024).decode()
        if choice == "yes":
            return True
        else: 
            return False



    

class BattleArena:
    def __init__(self, initiative, secondary):
        self.initiative_player = initiative
        self.secondary_player = secondary

        self.initiative_player.selected_leader = None
        self.secondary_player.selected_leader = None

        self.initiative_player.selected_unit_list = []
        self.secondary_player.selected_unit_list = []
        
        self.initiative_player.starting_unit = None
        self.secondary_player.starting_unit = None

        self.initiative_player.point_unit = None
        self.secondary_player.point_unit = None

        self.continuing_turn = True
        self.current_ap = 0

        self._setup()

    # Once the game has determined who gets initiative, we need to decide what units 
    # the players want to use

    # We have a few options on how to proceed with determining each player's units and skills
    #     1) We could have the server pull the list of units and skills that we've pre-made and 
    #        have both players selecte them in alternating order, one at a time
    #     2) We could have a json file on the client that references the units and skills
    #        that we've pre-made and load them that way
    #     3) We could have a json file on the client side that provides brand new units and skills
    #        along with their stats and other data, and create the units and skills that way

    # The problem with option 1 was that it will take a lot of time, and 
    # it'll get really old, really fast. Additionally, it doesn't allow for testers
    # with the client to be able to make tweaks for further testing. 
    # 
    # Option 2 would speed up the process with creating teams, but it would require knowing what 
    # units and skills would be available for use, and it still would not allow for tweaking the values.
    # Vencabot also calls out that loading an entire team at once would not allow for counterpicking.
    #
    # Option 3 provides the most flexibility, but on the other hand, if we load everything at once,
    # this also wouldn't allow for counterpicking. 
    # 
    # Venca mentions that the game may eventually be programmed to download the most up-to-date
    # version of our sanctioned units, such as "master_units.json" and they may be able to provide
    # a "custom_units.json" with their own personal creations.
    #
    # We're going to go with option 3 to give us the most flexibility. Let's talk about the JSON format
    # that the client will have.

    # The JSON client file, at least for the time being, will basically be a list of units with
    # a predetermined set of skills/abilities

    def _setup(self):

        select_leader_msg = create_protocol_string("select_leader", {})

        self._select_leader(self.initiative_player, select_leader_msg)
        self._select_leader(self.secondary_player, select_leader_msg)
        
        request_units_and_skills_msg = create_protocol_string("request_units_and_skills", {})
        
        while len(self.initiative_player.selected_unit_list) < 4 and len(self.secondary_player.selected_unit_list) < 4:
            self._request_units_and_skills(self.secondary_player, request_units_and_skills_msg)
            secondary_player_unit_choice_msg = create_protocol_string("player_unit_choice", {"unit": self.secondary_player.selected_unit_list[-1].unit_name})
            self.initiative_player.connection.sendall(secondary_player_unit_choice_msg)
            
            self._request_units_and_skills(self.initiative_player, request_units_and_skills_msg)
            initiative_player_unit_choice_msg = create_protocol_string("player_unit_choice", {"unit": self.initiative_player.selected_unit_list[-1].unit_name})
            self.secondary_player.connection.sendall(initiative_player_unit_choice_msg)

        print("The initiative player selected these units:")
        for unit in self.initiative_player.selected_unit_list:
            print(unit)

        print("The secondary player selected these units:")
        for unit in self.secondary_player.selected_unit_list:
            print(unit)

        self._determine_starting_unit(self.initiative_player)
        self._determine_starting_unit(self.secondary_player)

    def _select_leader(self, player, request_msg):
        player.connection.sendall(request_msg)
        received_leader_json = player.connection.recv(1024).decode()

        player.selected_leader = self._create_leader(json.loads(received_leader_json))

    def _create_leader(self, leader_json):
        created_leader = vencabot_jrpg_leaders.GenericLeader(
                leader_json["leader_name"], 
                leader_json["modifier_type"], 
                leader_json["modifier_stat"], 
                leader_json["modifier_stat_string"], 
                leader_json["modifier_amount"])
        return created_leader

    def _request_units_and_skills(self, player, request_msg):
        player.connection.sendall(request_msg)
        received_unit_and_skill_json = player.connection.recv(1024).decode()
        
        player.selected_unit_list.append(self._create_unit(json.loads(received_unit_and_skill_json)))

    def _create_unit(self, unit_json):
        created_unit = vencabot_jrpg_units.GenericUnit(unit_json["unit_name"], unit_json["hp"], unit_json["atk"], unit_json["defense"], unit_json["mp"], unit_json["lp"])
        for skill in unit_json["skills"]:
            created_unit.skill_list.append(self._create_skill(skill))
        return created_unit
        
    def _create_skill(self, skill_json):
        created_skill = vencabot_jrpg_skills.GenericSkill(skill_json["skill_name"], skill_json["ap"], skill_json["mp"], skill_json["base_damage"])
        created_skill.skill_description = skill_json["skill_description"]
        return created_skill
        
    def _determine_starting_unit(self, player):
        unit_list = []
        for unit in player.selected_unit_list:
            unit_list.append(unit.unit_name)

        unit_list_msg = create_protocol_string("select_start_unit", unit_list)
        player.connection.sendall(unit_list_msg)

        selection = int(player.connection.recv(1024).decode())
        player.starting_unit = player.selected_unit_list[selection]
        player.point_unit = player.starting_unit
        print(f"{player.player_name} selected {player.starting_unit.unit_name} as their starting unit.")

    def do_battle(self):
        # This will be the function containing the start of all of the battle logic
        while len(self.initiative_player.selected_unit_list) > 0 and len(self.secondary_player.selected_unit_list) > 0:
            self._do_turn(self.initiative_player, self.secondary_player)
            self._do_turn(self.secondary_player, self.initiative_player)

    def _do_turn(self, player, opponent):
        MAX_TURN_AP = 10
        self.current_ap = MAX_TURN_AP
        BATTLE_OPTIONS = {"Fight": self._use_fight, "Item": self._use_item, "Swap": self._use_swap, "End Turn": self._end_turn}
        self.continuing_turn = True

        while self.continuing_turn:
            match_state_msg = create_protocol_string("update_match_state", {
                    "initiative": {"name": self.initiative_player.player_name, "unit": self.initiative_player.point_unit.unit_name, "unit_hp": self.initiative_player.point_unit.hp},
                    "secondary": {"name": self.secondary_player.player_name, "unit": self.secondary_player.point_unit.unit_name, "unit_hp": self.secondary_player.point_unit.hp},
                    "ap": self.current_ap})
                    
            self.initiative_player.connection.sendall(match_state_msg)
            self.secondary_player.connection.sendall(match_state_msg)
            
            request_battle_option = create_protocol_string("request_battle_option", {})
            player.connection.sendall(request_battle_option)
            
            user_selection = ""
            while user_selection == "":
                user_selection += player.connection.recv(1024).decode()
            BATTLE_OPTIONS[user_selection](player, opponent)
            
            





    def _use_fight(self, player, opponent):
        skill_info = []
        for skill in player.point_unit.skill_list:
            skill_info.append({"skill_name": skill.skill_name, "mp": skill.mp_cost, "ap": skill.ap_cost, "description": skill.skill_description})
        attack_with_request = create_protocol_string("attack_with_request", {"skill_info": skill_info,"unit_mp": str(player.point_unit.mp) + " / " + str(player.point_unit.max_mp)})

        player.connection.sendall(attack_with_request)
        chosen_attack = int(player.connection.recv(1024).decode())
        if chosen_attack >= len(player.point_unit.skill_list):
            return None
        
        if player.point_unit.skill_list[chosen_attack].ap_cost <= self.current_ap and player.point_unit.skill_list[chosen_attack].mp_cost <= player.point_unit.mp:
            # Alias for the selected skill
            attack_skill = player.point_unit.skill_list[chosen_attack]
            
            self.current_ap -= attack_skill.ap_cost
            player.point_unit.mp -= attack_skill.mp_cost

            # Calculate damage based on stats via a function call
            # Let's talk this for a bit...
            # The leader skill, to my knowledge, is going to be potentially permanent for the fight.
            # What I mean is that there likely may not be any skills/abilities that could negate the leader effect
            # This this is the case, there's no reason why we shouldn't be able to adjust the unit's affected stat
            # in a more permanent way. The way I was originally thinking of doing it was to have the leader effect 
            # be a part of the general damage calculation. The pros of this is that it would allow for a more... I
            # guess a modular kind of fight where the leader skill could be altered or appended to. The downside of 
            # doing it that way would be that it has to run that calculation every single time damage is dealt. In
            # thinking about this, I'm currently not that worried about performance, so I think I may stick with
            # my original plan and just get 'er goin'

            damage_dealt = self._calculate_damage_dealt(player, attack_skill, opponent)
            opponent.point_unit.hp -= damage_dealt

            print(f'{player.player_name}\'s {player.point_unit.unit_name} did {damage_dealt} to {opponent.player_name}\'s {opponent.point_unit.unit_name}!')
            print(f'{opponent.player_name}\'s {opponent.point_unit.unit_name} has {opponent.point_unit.hp} HP left!')
        else:
            not_enough_ap_msg = create_protocol_string("not_enough_ap", {})
            player.connection.sendall(not_enough_ap_msg)
            return None

    def _calculate_damage_dealt(self, player, attack_skill, opponent):
        if player.selected_leader.modifier_stat == "atk":
            player_atk = player.selected_leader.adjust_stat_from_leader_buff(player.point_unit)
            player_defense = player.point_unit.defense
            player_hp = player.point_unit.hp
        elif player.selected_leader.modifier_stat == "defense":
            player_atk = player.point_unit.attack
            player_defense = player.selected_leader.adjust_stat_from_leader_buff(player.point_unit)
            player_hp = player.point_unit.hp
        else:
            player_atk = player.point_unit.attack
            player_defense = player.point_unit.defense
            player_hp = player.selected_leader.adjust_stat_from_leader_buff(player.point_unit)

        if opponent.selected_leader.modifier_stat == "atk":
            opponent_atk = opponent.selected_leader.adjust_stat_from_leader_buff(opponent.point_unit)
            opponent_defense = opponent.point_unit.defense
            opponent_hp = opponent.point_unit.hp
        elif opponent.selected_leader.modifier_stat == "defense":
            opponent_atk = opponent.point_unit.attack
            opponent_defense = opponent.selected_leader.adjust_stat_from_leader_buff(opponent.point_unit)
            opponent_hp = opponent.point_unit.hp
        else:
            opponent_atk = opponent.point_unit.attack
            opponent_defense = opponent.point_unit.defense
            opponent_hp = opponent.selected_leader.adjust_stat_from_leader_buff(opponent.point_unit)

        skill_damage = attack_skill.base_damage
        
        # Prevents damage from being completely zero'd out
        if opponent_defense >= 128:
            opponent_defense = 127

        total_damage = math.floor(player_atk / 8 * skill_damage * (1 - (opponent_defense / 128)))

        print(f"DEBUG: player_atk: {player_atk}")
        print(f"DEBUG: skill_damage: {skill_damage}")
        print(f"DEBUG: opponent_defense: {opponent_defense}")
        print(f"DEBUG: total_damage: {total_damage}")
        print("DEBUG: ")
        
        return total_damage



    def _use_item(self, player, opponent):
        pass

    def _use_swap(self, player, opponent):
        if self.current_ap < 3:
            not_enough_ap_msg = create_protocol_string("not_enough_ap", {})
            player.connection.sendall(not_enough_ap_msg)
            
            return 1
        
        unit_name_list = []
        for unit in player.selected_unit_list:
            if unit is player.point_unit:
                unit_name_list.append({"name": unit.unit_name + " (Currently Active)", "hp": unit.hp, "max_hp": unit.max_hp})
            else:
                unit_name_list.append({"name": unit.unit_name, "hp": unit.hp, "max_hp": unit.max_hp})
        swap_msg = create_protocol_string("request_swap", unit_name_list)
        player.connection.sendall(swap_msg)
        
        user_choice = int(player.connection.recv(1024).decode())

        if player.selected_unit_list[user_choice] is not player.point_unit:
            self.current_ap -= 3
            player.point_unit = player.selected_unit_list[user_choice]



        

    def _end_turn(self, player, opponent):
        self.continuing_turn = False

    # This code below was the old code using "Option 1" - May still be good for the final version of the game, but
    # for the test version, we're commenting this out for now

    # def _setup(self):
    #     while len(self.initiative_player.selected_unit_list) < 4 and len(self.secondary_player.selected_unit_list) < 4:
    #         self.initiative_player.selected_unit_list.append(self._select_unit(self.initiative_player))
    #         initiative_player_unit_choice_msg = create_protocol_string("player_unit_choice", {"unit": self.initiative_player.selected_unit_list[-1].unit_name})
    #         self.secondary_player.connection.sendall(initiative_player_unit_choice_msg)

    #         self.secondary_player.selected_unit_list.append(self._select_unit(self.secondary_player))
    #         secondary_player_unit_choice_msg = create_protocol_string("player_unit_choice", {"unit": self.secondary_player.selected_unit_list[-1].unit_name})
    #         self.initiative_player.connection.sendall(secondary_player_unit_choice_msg)

    #     for player in [self.initiative_player, self.secondary_player]:
    #         print(f"{player.player_name}\'s Selected Units")
    #         for index, unit in enumerate(player.selected_unit_list):
    #             unit_number = index + 1
    #             print(f"  {unit_number}) {unit.unit_name}")
    #         print()

    
    # def _select_unit(self, player):
    #     # Instead of sending multiple protocol messages with the text and available units...
    #     # Why not just send everything to the client, and let it sort it all out

    #     #Create a dict to store the unit classes as values and the po
    #     unit_list = vencabot_jrpg_units.master_list_of_units
    #     instantiated_unit_list = []
    #     for unit_class in unit_list:
    #         instantiated_unit_list.append(unit_class())
    #     unit_names_list = [unit.unit_name for unit in instantiated_unit_list]
        
    #     unit_selected = False
    #     while not unit_selected:
    #         request_unit_msg = create_protocol_string("request_unit", {"unit_name_list": unit_names_list})
        
    #         player.connection.sendall(request_unit_msg)
    #         choice = player.connection.recv(1024).decode()

    #         # Now that they've selected a unit, show them their stats, and make them verify their choice
    #         unit = instantiated_unit_list[int(choice)]
    #         stat_list = {"name": unit.unit_name, "hp": unit.max_hp, "mp": unit.max_mp, "attack": unit.attack, "defense": unit.defense, "lp": unit.max_life_points}
    #         display_stats_msg = create_protocol_string("display_stats_confirmation", stat_list)
    #         player.connection.sendall(display_stats_msg)
    #         confirm_choice = player.connection.recv(1024).decode()

    #         if confirm_choice == "Y":
    #             unit_selected = True
    #             print(f"{player.player_name} has confirmed their selection of {unit.unit_name}")
    #         else:
    #             print(f"Restarting selection loop for {player.player_name}")
        
    #     return instantiated_unit_list[int(choice)]


def create_protocol_string(msg_type, msg_data):
    protocol = {"message_type": msg_type, "message_data": msg_data}
    protocol_string = json.dumps(protocol)
    protocol_string += "END_OF_MESSAGE"
    return protocol_string.encode()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST,PORT))
    
    print("Listening for connections")
    server_socket.listen()

    #####################
    # Awaiting Player 1 #
    #####################
    
    p1_connection, p1_address = server_socket.accept()
    print(f"Connection made with {p1_address}")

    # After player 1 connection, await for their username
    p1_username = p1_connection.recv(1024).decode()
    print(f"Received Player 1 - Chosen name: {p1_username}")

    # Player 1 object created
    player_one = PlayerData(p1_connection, p1_address, p1_username)
    
    #####################
    # Awaiting Player 2 #
    #####################

    p2_connection, p2_address = server_socket.accept()
    print(f"Connection made with {p2_address}")

    # After player 2 connection, await for their username
    p2_username = p2_connection.recv(1024).decode()
    print(f"Received Player 2 - Chosen name: {p2_username}")

    # Player 2 object created
    player_two = PlayerData(p2_connection, p2_address, p2_username)
    

    ###########################################
    # Received two connections - CREATE MATCH #
    ###########################################

    still_playing = True
    while still_playing:
        
        # Notify that two players have connected and the match will be between them
        # Let's create a protocol like I did earlier using the format we decided on previously
        # That format will be {"message_type": <type>, "message_data": {"data_1": value, "data_2": value}}
        random_initiative_player = random.choice([player_one,player_two])
        random_secondary_player = player_two if random_initiative_player is player_one else player_one
        print(random_initiative_player.player_name, "has won the initative --- Sending notification to both players")

        initiative_message = create_protocol_string("create_match", {"initiative": random_initiative_player.player_name, "secondary": random_secondary_player.player_name})
        random_initiative_player.connection.sendall(initiative_message)
        random_secondary_player.connection.sendall(initiative_message)
        
        # rps_game = GameOfRPS(initiative_player, secondary_player)
        # rps_game.do_match()
        # still_playing = rps_game.request_rematch()

        # Create an object that passes the initiative_player and the secondary_player class instances to start the game
        battle_arena_match = BattleArena(random_initiative_player, random_secondary_player)
        battle_arena_match.do_battle()

    
    input("End of program")
