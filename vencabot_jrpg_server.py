#import pygame
import vencabot_jrpg_game_state
import vencabot_jrpg_leaders
import vencabot_jrpg_units
import vencabot_jrpg_combat_handler
import socket
import threading
import json
import time, math

# Initialize GameState class
# game_state = vencabot_jrpg_game_state.GameState()
# protagonist = vencabot_jrpg_leaders.GenericLeader()

HOST = ""
PORT = 1717

class ClientData:
    def __init__(self, connection, addr):
        self.connection = connection
        self.address = addr
        self.username = ""


def accept_connections_forever(server_socket, connections_list):
    while True:
        connection, address = server_socket.accept()
        print(f"Connection made with {address}")
        connections_list[connection] = ClientData(connection, address)
        client_thread = threading.Thread(target=lobby_core_server_forever, args=(connection, connections_list))
        client_thread.start()

def create_client_message(msg_type, msg_data):
    client_message = {"message_type": msg_type, "message_data": msg_data}
    return str(json.dumps(client_message)).encode()

def parse_client_message(received_message):
    return json.loads(received_message)

def run_command(received_message, assigned_connection):
    return CLIENT_COMMAND_LIST[received_message["message_type"]](received_message["message_data"], assigned_connection)

# def request_username(assigned_connection):
#     assigned_connection.sendall(create_client_message("username_prompt", {"sender_username": "server", "message_body": "What is your name?"}))
#     # decoded_client_message = parse_client_message(assigned_connection.recv(1024).decode())
#     # return run_command(decoded_client_message)

def echo_message(msg_data, assigned_connection):
    msg_body = msg_data["message_body"]
    print(f"ECHO Request from {list_of_client_connections[assigned_connection].username}: {msg_body}")
    msg = f"{list_of_client_connections[assigned_connection].username}: {msg_body}"
    print(f"Echoing {msg} to all clients")
    for connection in list_of_client_connections.keys():
        if assigned_connection != connection:
            print(f"    Sending {msg} to {connection}")
            connection.sendall(create_client_message("echo", {"sender_username": list_of_client_connections[assigned_connection].username, "message_body": msg_body}))

def username_request(msg_data, assigned_connection):
    print(f"Message received from: {assigned_connection}")
    print(f"Message Data: {msg_data['message_body']}")
    if list_of_client_connections[assigned_connection].username == "":
        print("    No username found --- Acknowledging and awaiting new nick")
        assigned_connection.sendall(create_client_message("username_prompt", {"sender_username": "server", "message_body": "What is your name?"}))

def username_response(msg_data, assigned_connection):
    name = str(msg_data["message_body"])
    print(f"Player has selected the name: {name}")
    list_of_client_connections[assigned_connection].username = name
    return name

def message_send_request(msg_data, assigned_connection):
    print(f"Message received from: {assigned_connection}")
    print(f"Message Data: {msg_data['message_body']}")
    assigned_connection.sendall(create_client_message("message_send_acknowledged", {"sender_username": "server", "message_body": "Awaiting message..."}))

def lobby_core_server_forever(assigned_connection, connections_list):
    # username = str(get_username(assigned_connection))
    # request_username(assigned_connection)
    while True:
        client_message = assigned_connection.recv(1024).decode()
        decoded_client_message = parse_client_message(client_message)
        run_command(decoded_client_message, assigned_connection)
        # echo_message = username + ": " + client_message
        # print(echo_message)
        # for connection in connections_list:
        #     connection.sendall(echo_message.encode())


list_of_client_connections = {}
CLIENT_COMMAND_LIST = {
        "echo_message"        : echo_message,
        "username_request"    : username_request,
        "username_response"   : username_response,
        "message_send_request": message_send_request}


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST,PORT))
    print("Awaiting Connections...")
    server_socket.listen()

    accept_connections_thread = threading.Thread(target=accept_connections_forever, args=(server_socket, list_of_client_connections))
    accept_connections_thread.start()

    input("Press Enter to End Main Thread")









# Main Game Loop

# while(not game_state.is_game_completed() and not game_state.is_game_over()):

#     print("this is a test")
#     game_state.set_game_completed_flag()

# if game_state.is_game_over():
#     print("the game ended - you died")
# elif game_state.is_game_completed():
#     print("the game ended - you won!")