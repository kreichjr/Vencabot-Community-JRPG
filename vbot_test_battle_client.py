import socket
import json
import os

HOST = "localhost"
PORT = 1717

class ClientSetup:
    def __init__(self, socket_connection, player_name, master_leader_and_unit_list):
        self.connection = socket_connection
        self.player_name = player_name
        
        self.master_leader_and_unit_list_json = master_leader_and_unit_list
        
        self.master_leader_list = []
        self.selected_leader = None
        
        self.master_unit_list = []
        self.selected_unit_list = []
        
        self.opponent_selected_units = []
        self.initiative_type = ""
        self.opponent_initiative_type = ""

        self._populate_master_lists()

    def _populate_master_lists(self):
        self.master_leader_list = self.master_leader_and_unit_list_json["leader_list"]
        self.master_unit_list = self.master_leader_and_unit_list_json["unit_list"]

        
def run_server_message(message):
    decoded_protocol = json.loads(message)
    command = decoded_protocol["message_type"]
    data = decoded_protocol["message_data"]
    command_list[command](data)

def clear_console(*_):
    os.system("cls")

def get_valid_input(prompt, func):
    pass



def create_match(msg_data):
    clear_console()
    
    my_character.selected_leader = None
    my_character.selected_unit_list = []
    my_character.opponent_selected_units = []
    my_character.initiative_type = ""
    my_character.opponent_initiative_type = ""

    initiative_player_name = msg_data["initiative"]
    secondary_player_name = msg_data["secondary"]
    if initiative_player_name == my_character.player_name:
        print(f"You've been matched up with {secondary_player_name}! You've got the first attack!")
        print("Waiting for the opponent to select their first unit...")
        my_character.initiative_type = "initiative"
        my_character.opponent_initiative_type = "secondary"
    else:
        print(f"You've been matched up with {initiative_player_name}! You'll be going second.")
        print("You get to choose your unit first.")
        my_character.initiative_type = "secondary"
        my_character.opponent_initiative_type = "initiative"


def rps_tie(msg_data):
    rps_type = msg_data["rps_type"]
    print(f"You both chose {rps_type} and tied! Try again!\n")

def rps_won(msg_data):
    winner = msg_data["winner"]
    winning_rps_type = msg_data["rps_type"]
    rps_beats_map = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

    if winner == my_character.player_name:
        print(f"You won by throwing {winning_rps_type} against their {rps_beats_map[winning_rps_type]}! Congrats!")
    else:
        print(f"You lost this match when you threw {rps_beats_map[winning_rps_type]} against their {winning_rps_type}. D= Bummer!")

def request_rps_choice(msg_data):
    user_choice = input('Please enter "rock", "paper", or "scissors" as your choice.\n')
    my_character.connection.sendall(user_choice.encode())

def invalid_rps_choice(msg_data):
    print("Error: The choice you selected was invalid.\n\n")

def request_rematch(msg_data):
    user_choice = input('\n\nDo you want to rematch? Type "yes" to rematch. Any other input will end the game.\n')
    my_character.connection.sendall(user_choice.encode())





# def request_unit(msg_data):
#     valid_choice = False
#     while not valid_choice:
#         print("Please select one of the units displayed using their number:")
#         for index, name in enumerate(msg_data["unit_name_list"]):
#             print(f"{index + 1}) {name}")
        
#         user_choice = input("Your choice?  ")
        
#         try:
#             if int(user_choice) in range(1, len(msg_data["unit_name_list"]) + 1):
#                 valid_choice = True
#         except ValueError: 
#             print("An invalid choice was selected\n")
#     adjusted_choice = str(int(user_choice) - 1)
#     my_character.connection.sendall(adjusted_choice.encode())

# Start of Combat Arena code

def select_leader(msg_data):
    clear_console()
    leader_not_picked = True

    while leader_not_picked:

        print("Select the leader you want to use: ")
        valid_choice = False
        confirmed_choice = False

        while not valid_choice:
            for index, leader in enumerate(my_character.master_leader_list):
                if leader["modifier_type"] == "percentage":
                    print(f'{index + 1}) {leader["leader_name"]} - Increases your {leader["modifier_stat_string"]} by {leader["modifier_amount"]}%.')
                elif leader["modifier_type"] == "flat":
                    print(f'{index + 1}) {leader["leader_name"]} - Increases your {leader["modifier_stat_string"]} by a flat {leader["modifier_amount"]} points.')

            unit_choice = input("\nYour choice?  ")

            try:
                if int(unit_choice) in range(1, len(my_character.master_leader_list) + 1):
                    valid_choice = True
            except ValueError: 
                print("An invalid choice was selected\n")
            
        adjusted_choice = int(unit_choice) - 1
        while not confirmed_choice:
            user_choice = input(f'\nDo you want to have {my_character.master_leader_list[adjusted_choice]["leader_name"]} as your leader?  Type \'y\' or \'n\'.  ')
            if user_choice in ['y','n']:
                confirmed_choice = True
            else:
                clear_console()
                print("Please select \'y\' or \'n\'.")

        if user_choice == 'y':
            leader_not_picked = False

    my_character.selected_leader = my_character.master_leader_list[adjusted_choice]
    my_character.connection.sendall(json.dumps(my_character.selected_leader).encode())


            

def request_units_and_skills(msg_data):
    
    # unit_attributes = ["unit_name", "hp", "atk", "defense", "mp", "lp", "skills"]
    skill_attributes = ["skill_name", "ap", "mp", "base_damage", "skill_description"]

    prompt_dict = {
            0: "Select the first unit from your deck list:",
            1: "Select the second unit from your deck list:",
            2: "Select the third unit from your deck list:",
            3: "Select the final unit from your deck list:"}

    unit_picked_and_confirmed = False

    while not unit_picked_and_confirmed:
        valid_choice = False
        confirmed_choice = False
        
        while not valid_choice:
            print(prompt_dict[len(my_character.selected_unit_list)])
            for index, unit in enumerate(my_character.master_unit_list):
                print(f"{index + 1}) {unit['unit_name']}")
            unit_choice = input("\nYour choice?  ")

            try:
                if int(unit_choice) in range(1, len(my_character.master_unit_list) + 1):
                    valid_choice = True
            except ValueError: 
                print("An invalid choice was selected\n")
            
        adjusted_choice = int(unit_choice) - 1
        potential_unit = my_character.master_unit_list[adjusted_choice]
        print(f'{potential_unit["unit_name"]}\'s Stats')
        for key in potential_unit:
            if key != "unit_name" and key != "skills":
                print(f'  {key}: {potential_unit[key]}')
            elif key == "skills":
                print(f'  {key}:')
                for skill in potential_unit[key]:
                    print()
                    for skill_attribute in skill_attributes:
                        print(f'    {skill_attribute}: {skill[skill_attribute]}')
        print()

        while not confirmed_choice:
            user_choice = input("\nDo you want to use this unit?  Type \'y\' or \'n\'.  ")
            if user_choice in ['y','n']:
                confirmed_choice = True
            else:
                clear_console()
                print("Please select \'y\' or \'n\'.")

        if user_choice == 'y':
            unit_picked_and_confirmed = True

        
    my_character.selected_unit_list.append(my_character.master_unit_list[adjusted_choice])
    
    selected_unit_return_json = json.dumps(my_character.selected_unit_list[-1])
    my_character.connection.sendall(selected_unit_return_json.encode())
        
def display_stats_confirmation(msg_data):
    print()
    print(f'{msg_data["name"]}\'s Stats')
    for key in msg_data:
        if key != "name":
            print(f'  {key}: {msg_data[key]}')

    valid_choice = False
    while not valid_choice:
        user_choice = input("\nDo you want to use this unit?  Type \'Y\' or \'N\'. ")
        if user_choice in ['Y','N']:
            valid_choice = True
        else:
            print("Please select \'Y\' or \'N\'.")
    
    my_character.connection.sendall(user_choice.encode())
    print(f"You've selected {msg_data['name']}!")

def player_unit_choice(msg_data):
    if len(my_character.selected_unit_list) > 0:
        clear_console()
    my_character.opponent_selected_units.append(msg_data['unit'])
    print(f"Your opponent has selected these units:")
    for unit in my_character.opponent_selected_units:
        print(unit)
    print()

def select_start_unit(msg_data):
    clear_console()
    

    valid_choice = False
    while not valid_choice:
        print("Select which unit you want to start with:")
        for index, unit_name in enumerate(msg_data):
            print(f"  {index + 1}) {unit_name}")
    
        unit_choice = input("Your choice?  ")

        try:
            if int(unit_choice) in range(1, len(msg_data) + 1):
                valid_choice = True
        except ValueError: 
            print("An invalid choice was selected\n")
            
    adjusted_choice = int(unit_choice) - 1
    my_character.connection.sendall(str(adjusted_choice).encode())

def update_match_state(msg_data):
    clear_console()
    my_info = msg_data[my_character.initiative_type]
    opponent_info = msg_data[my_character.opponent_initiative_type]

    print(f'Your unit {my_info["unit"]} has {my_info["unit_hp"]} HP. {opponent_info["name"]}\'s {opponent_info["unit"]} has {opponent_info["unit_hp"]} HP.')
    print(f'Remaining AP for this turn: {msg_data["ap"]}')
    if my_character.initiative_type == "secondary":
        print("Waiting for the opponent to end their turn...")

def request_battle_option(msg_data):
    BATTLE_OPTIONS = ["[F]ight","[I]tem (Not yet implemented)","[S]wap","[E]nd Turn"]
    valid_choices = {"f": "Fight", "i": "Item", "s": "Swap", "e": "End Turn"}
    
    valid_choice = False
    while not valid_choice:
        print("Select the action you want to take:")
        for option in BATTLE_OPTIONS:
            print("  ", option)
        
        user_choice = input("Your choice?  ")

        valid_choice = user_choice in valid_choices.keys()
    my_character.connection.sendall(valid_choices[user_choice].encode())    
    
def request_swap(msg_data):
    clear_console()
    
    valid_choice = False
    while not valid_choice:
        print("What unit did you want to swap to? Cost: 3 AP")
        print("Selecting the currently active unit will not swap any units and your AP will not be used.")
        for index, unit in enumerate(msg_data):
            print(f'  {index + 1}) {unit["name"]} --- HP: {unit["hp"]} / {unit["max_hp"]}')

        unit_choice = input("Your choice?  ")

        try:
            if int(unit_choice) in range(1, len(msg_data) + 1):
                valid_choice = True
        except ValueError: 
            print("An invalid choice was selected\n")
                
    adjusted_choice = int(unit_choice) - 1
    my_character.connection.sendall(str(adjusted_choice).encode())

def not_enough_ap(msg_data):
    print("You don't have enough AP to perform that action!")
    input("Press enter to continue...")
    
    

def attack_with_request(msg_data):
    
    valid_choice = False
    while not valid_choice:
        print(f'You have {msg_data["unit_mp"]}. What ability/skill do you want to use?')
        for index, skill in enumerate(msg_data["skill_info"]):
            print(f'  {index + 1}) {skill["skill_name"]}')
            print(f'    AP Cost: {skill["ap"]}')
            print(f'    MP Cost: {skill["mp"]}')
            print(f'    Skill Description: {skill["description"]}')
        print(f'  {len(msg_data)+1}) Go back')
        unit_choice = input("Your choice?  ")

        try:
            if int(unit_choice) in range(1, len(msg_data) + 2):
                valid_choice = True
        except ValueError: 
            print("An invalid choice was selected\n")
                
    adjusted_choice = int(unit_choice) - 1
    my_character.connection.sendall(str(adjusted_choice).encode())


command_list = {
        "create_match": create_match,
        "rps_tie": rps_tie,
        "rps_won": rps_won,
        "request_rps_choice": request_rps_choice,
        "invalid_rps_choice": invalid_rps_choice,
        "request_rematch": request_rematch,
        #"request_unit": request_unit,
        "clear_console": clear_console,
        "display_stats_confirmation": display_stats_confirmation,
        "player_unit_choice": player_unit_choice,
        "select_leader": select_leader,
        "request_units_and_skills": request_units_and_skills,
        "select_start_unit": select_start_unit,
        "update_match_state": update_match_state,
        "request_battle_option": request_battle_option,
        "request_swap": request_swap,
        "not_enough_ap": not_enough_ap,
        "attack_with_request": attack_with_request
        
}

# Start of program

try:
    with open("master_units.json") as read_json:
        master_unit_list_json = json.load(read_json)
except FileNotFoundError:
    print("You must get the master_units.json file.")
    exit()





with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_connection:
    socket_connection.connect((HOST,PORT))

    chosen_name = input("Connection complete! \nWhat username do you want to use?\n")

    my_character = ClientSetup(socket_connection, chosen_name, master_unit_list_json)
    socket_connection.sendall(chosen_name.encode())

    print("\nAwaiting acknowledgement from server\n")

    while True:
        
        server_message = ""
        while "END_OF_MESSAGE" not in server_message:
            server_message += socket_connection.recv(2048).decode()
            
        message_list = server_message.split("END_OF_MESSAGE")
        for command in message_list:
            if command != "":
                run_server_message(command)

        #input("End of Program")


