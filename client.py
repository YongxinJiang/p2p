import socket
import threading

class User:
    def __init__(self, name, connection):
        self.name = name
        self.connection = connection
        self.messages = []

    def receive_message(self, sender, message):
        print(f"Received a message from {sender}: {message}")
        self.messages.append((sender, message))

    def check_messages(self):
        if self.messages:
            print(f"Messages for {self.name}:")
            for sender, message in self.messages:
                print(f"{sender}: {message}")
            self.messages = []

class MessagingSystem:
    def __init__(self):
        self.users = {}

    def register_user(self, user):
        self.users[user.name] = user

    def initiate_session(self, sender, receiver_name, message):
        if receiver_name in self.users:
            receiver = self.users[receiver_name]
            receiver_conn = receiver.connection
            if receiver_conn:
                receiver_conn.send(f"{sender.name}: {message}".encode())
            else:
                print(f"{receiver_name} is currently offline. Message will be stored.")
                receiver.messages.append((sender.name, message))
        else:
            print(f"User {receiver_name} not found.")

def handle_client(client_socket, username, messaging_system):
    user = User(username, client_socket)
    messaging_system.register_user(user)
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            parts = message.split(": ", 1)
            if len(parts) == 2:
                receiver_name, message_text = parts
                messaging_system.initiate_session(user, receiver_name, message_text)
            else:
                print("Invalid message format")
        except Exception as e:
            print(f"Error: {e}")
            break
    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)
    print("Server started. Listening on port 5555...")

    messaging_system = MessagingSystem()

    while True:
        client_socket, addr = server.accept()
        print(f"Connection from {addr}")

        username = client_socket.recv(1024).decode()
        print(f"{username} connected")

        client_handler = threading.Thread(target=handle_client, args=(client_socket, username, messaging_system))
        client_handler.start()

if __name__ == "__main__":
    start_server()
