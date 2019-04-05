import time
import json
import socket
import threading

HOST = "localhost"
PORT = 1717

class ClientData:
    def __init__(self, my_connection):
        self.username = ""
        self.my_connection = my_connection

def lobby_core_client_forever(server_connection, serv_msg_queue):
    print("Sending request to select a username")
    server_message = create_server_message("username_request", {"message_body": "Requesting to update username"})
    server_connection.sendall(server_message)
    while True:
        if serv_msg_queue:
            command = serv_msg_queue.pop(0)
            run_command(command, server_connection)
        elif this_client.username != "":
            # No commands in queue - Request server to send acknowledgement to send message
            server_message = create_server_message("message_send_request", {"message_body": "Requesting to send message"})
            server_connection.sendall(server_message)
            time.sleep(1)
                
def run_command(cmd, server_connection):
    return SERVER_COMMAND_LIST[cmd["message_type"]](cmd["message_data"], server_connection)                

def receive_messages_forever(server_connection, serv_msg_queue):
    while True:
        server_message = server_connection.recv(1024).decode()
        decoded_message = decode_server_message(server_message)
        serv_msg_queue.append(decoded_message)

def create_server_message(msg_type, msg_data):
    server_message = {"message_type": msg_type, "message_data": msg_data}
    return str(json.dumps(server_message)).encode()

def decode_server_message(serv_message):
    return json.loads(serv_message)

def echo_message(msg_data, server_connection):
    username = msg_data["sender_username"]
    msg = msg_data["message_body"]
    print(f"{username}: {msg}")

def username_prompt(msg_data, server_connection):
    username = str(msg_data["sender_username"])
    msg = str(msg_data["message_body"])
    print(f"{username}: {msg}")
    user_input = input()
    this_client.username = user_input
    server_message = create_server_message("username_response", {"message_body": user_input})
    server_connection.sendall(server_message)

def message_send_acknowledged(msg_data, server_connection):
    user_input = input()
    server_message = create_server_message("echo_message", {"message_body": user_input})
    server_connection.sendall(server_message)


server_message_queue = []
SERVER_COMMAND_LIST = {
        "echo"                     : echo_message, 
        "username_prompt"          : username_prompt,
        "message_send_acknowledged": message_send_acknowledged}


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.connect((HOST,PORT))

    this_client = ClientData(server_socket)

    receive_messages_thread = threading.Thread(target=receive_messages_forever, args=(server_socket, server_message_queue))
    lobby_core_client_thread = threading.Thread(target=lobby_core_client_forever, args=(server_socket, server_message_queue))

    receive_messages_thread.start()
    lobby_core_client_thread.start()

    while True:
        time.sleep(3)
