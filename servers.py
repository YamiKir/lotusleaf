import socket
import threading
import json
import time

def read_setup(file_name):
    try:
        with open(file_name, 'r') as file:
            setup_info = {}
            for line in file:
                if line.startswith("Tracker:"):
                    tracker_ip = line.split("Tracker:")[1].strip()
                    setup_info['Tracker IP'] = tracker_ip
                elif line.startswith("Port:"):
                    port = int(line.split("Port:")[1].strip())
                    setup_info['Port'] = port
            return setup_info
        print("Tracker IP or Port not found in the file.")
        return None
    except FileNotFoundError:
        print("File not found.")
        return None
    
# Define the Server class
class Server:
    MAX_WAITING = 3  # Max number of waiting connections

    def __init__(self):
        setup_info = read_setup("setup.txt")
        self.host = setup_info['Tracker IP']
        self.port = setup_info['Port']
        self.connections = []
        self.files_per_client = {}  # Dictionary to store files per client
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_WAITING)
        print("Server started on {}:{}".format(self.host, self.port))

        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Connection from {}.".format(client_address))
            self.connections.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        data = client_socket.recv(4096)
        if data:
            data_str = data.decode()
            received_data = json.loads(data_str)
            ip = received_data['ip']
            files_list = received_data['files']
            self.files_per_client[ip] = files_list  # Update files_per_client dictionary
            print("Received file list from {}: {}".format(ip, files_list))

        while True:
            try:
                # Send files_per_client to client
                files_per_client_json = json.dumps(self.files_per_client)
                client_socket.send(files_per_client_json.encode())
                time.sleep(5)
            except socket.error:
                print("Connection closed by the client.")
                self.connections.remove(client_socket)
                break

# Main function
def main():
    print("This is the main function in this Python P2P Program. (Server Edition)")
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
    while True:
        pass
