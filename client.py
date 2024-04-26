import socket
import sys
import threading
import os
import time
from collections import defaultdict

class Client:
    def __init__(self, discovery_server=('localhost', 12345)):
        self.blocked_users = set()
        self.discovery_server = discovery_server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_active = False
        self.messages_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_socket.bind(('localhost', 0))
        self.listen_port = self.messages_socket.getsockname()[1]
        self.username = None
        self.offline_messages = defaultdict(list)
        self.is_active = True

    def get_listening_port(self):
        return self.listen_port

    def listen_for_messages(self):
        self.messages_socket.listen()
        print(f"{self.username} is listening for messages on {self.listen_port}.")

        while self.is_active:
            try:
                conn, addr = self.messages_socket.accept()
                client_ip, client_port = addr  # 获取客户端的IP和端口信息
                threading.Thread(target=self.handle_incoming_connection, args=(conn, client_ip, client_port)).start()
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def handle_incoming_connection(self, conn, client_ip, client_port):
        with conn:
            while self.is_active:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                sender = message.split(':')[0]
                if sender in self.blocked_users:
                    print(f"\nMessage from {sender} blocked.\n")
                else:
                    print(f"\n{self.username} received message: {message}\n")
                print(
                    f"{self.username}, enter your command (REGISTER, SEND <PeerName> <Message>, BLOCK <UserName>, UNBLOCK <UserName>, LIST, EXIT): ",
                    end='')

    def save_message_to_file(self, message):
        with open(f"{self.username}_messages.txt", "a") as file:
            file.write(message + "\n")

    def send_message(self, peer_name, message):
        try:
            peer_ip = self.get_peer_ip(peer_name)
            if peer_ip == "NOT FOUND":
                raise ConnectionError(f"{peer_name} is offline.")

            peer_port = self.get_peer_port(peer_name)
            if not peer_port:
                raise ConnectionError(f"{peer_name}'s port not found.")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((peer_ip, peer_port))
                s.sendall(message.encode('utf-8'))
                print(f"Message sent to {peer_name} successfully.")

            self.send_offline_messages(peer_name, peer_ip)

        except ConnectionError as e:
            print(e)
            self.offline_messages[peer_name].append(message)

    def send_online_message(self, peer_name, peer_ip, message):
        peer_port = self.get_peer_port(peer_name)
        if peer_port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_ip, peer_port))
                    s.sendall(message.encode('utf-8'))
                    print(f"Message sent to {peer_name} successfully.")
            except Exception as e:
                print(f"Error: Could not send message to {peer_name}. {e}")

    def send_offline_messages(self, peer_name, peer_ip):
        if peer_name in self.offline_messages:
            for msg in self.offline_messages[peer_name]:
                print(f"Sending stored message to {peer_name}: {msg}")
                self.send_online_message(peer_name, peer_ip, msg)
            del self.offline_messages[peer_name]

    def get_peer_ip(self, peer_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            sock.sendall(f"GET_IP {peer_name}".encode('utf-8'))
            peer_ip = sock.recv(1024).decode('utf-8')
        if peer_ip == "NOT FOUND":
            print(f"{peer_name}'s IP not found on discovery server.")
            return None
        else:
            return peer_ip


    def get_peer_port(self, peer_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            sock.sendall(f"GET_PORT {peer_name}".encode('utf-8'))
            port = sock.recv(1024).decode('utf-8')
        if port.isdigit():
            return int(port)
        else:
            print(f"Error: {peer_name}'s port not found on discovery server.")
            return None

    def register_with_discovery_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            register_command = f"REGISTER {self.username} {self.listen_port}"
            sock.sendall(register_command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print(f"{self.username}: {response}")
            if "Registered" in response:
                self.is_registered = True
            else:
                print("Error: Registration failed.")

    def command_line_interface(self):
        self.is_active = True  # 控制命令行界面循环
        while self.is_active:
            command_input = input(f"{self.username}, enter your command (REGISTER, SEND <PeerName> <Message>, LIST, EXIT): ").strip()
            commands = command_input.split(maxsplit=2)
            if commands[0] == "REGISTER":
                self.register_with_discovery_server()
            elif commands[0] == "SEND":
                if len(commands) < 3:
                    print("Error: SEND command format is 'SEND <PeerName> <Message>'.")
                    continue
                _, peer_name, message = commands
                self.send_message(peer_name, message)
            else:
                print("Unknown command or incorrect format.")
    def send_to_server(self, message):
        self.socket.connect(self.discovery_server)
        self.socket.sendall(message.encode('utf-8'))
        response = self.socket.recv(1024).decode('utf-8')
        print(f"Server response: {response}")
        self.socket.close()
        return response

    def register_new_user(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        # Removed the part where the client's port is retrieved and sent to the server.
        listening_port = self.get_listening_port()
        message = f"REGISTER {username} {password} {listening_port}"
        response = self.send_to_server(message)
        if "Registered" in response:
            self.username = username
            self.is_active = True

    def login_user(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        listening_port = self.get_listening_port()
        message = f"LOGIN {username} {password} {listening_port}"
        response = self.send_to_server(message)
        if "successful" in response:
            self.username = username
            self.is_active = True
        else:
            print("Login failed.")

    def user_choice(self):
        while True:
            choice = input("Do you want to (1) Register or (2) Login? Enter 1 or 2: ")
            if choice == '1':
                self.register_new_user()
                break
            elif choice == '2':
                self.login_user()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

    def start(self):
        self.user_choice()
        if self.is_active:
            print(f"Welcome {self.username}. You are now logged in.")
            # 创建一个新的线程来运行 listen_for_messages 方法
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
            self.command_line_interface()  # 添加命令行界面循环
        print("Client stopped")

    def stop(self):
        self.is_active = False
        self.messages_socket.close()
        self.socket.close()

if __name__ == "__main__":
    client = Client()
    client.start()
