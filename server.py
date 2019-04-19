import socket
import select
import colorama
from colorama import Fore, Style
import config

header_length = 10
ip = "https://moonservo.netlify.com" 
port = 1234

# setup the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # 1 = True

server_socket.bind((ip, port))

server_socket.listen()

# do server management
sockets_list = [server_socket]

clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(header_length)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        message_data = client_socket.recv(message_length)

        return {"header": message_header, "data": message_data}
    except Exception as e:
        print("Receiving Error", str(e))
        return False


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user

            print(Fore.GREEN + f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}" + Style.RESET_ALL)
        else:
            message = receive_message(notified_socket)

            if message is False:
                print(Fore.RED + f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}" + Style.RESET_ALL)
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(Fore.BLUE + f"{user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}" + Style.RESET_ALL)

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
