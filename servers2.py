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
                elif line.startswith("Tracker Port:"):
                    port = int(line.split("Tracker Port:")[1].strip())
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
        
        self.server_socket.bind((self.host, self.port))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.listen(self.MAX_WAITING)
        print("Server started on {}:{}".format(self.host, self.port))

        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Connection from {}.".format(client_address))
            self.connections.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                # Continuously try to read from the socket
                data = client_socket.recv(4096)
                if data:
                    # Decode and process data as long as it's being received
                    data_str = data.decode()
                    received_data = json.loads(data_str)
                    ip = received_data['ip']
                    files_list = received_data['files']
                    self.files_per_client[ip] = json.loads(files_list)  # Assume files_list is also a JSON string
                    print("Received updated file list from {}: {}".format(ip, self.files_per_client[ip]))

                    # Send the updated list to the client periodically or upon change
                    files_per_client_json = json.dumps(self.files_per_client)
                    client_socket.send(files_per_client_json.encode())
                else:
                    # If no data is received, assume the connection is closed
                    break
        except socket.error as e:
            print("Socket error:", e)
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
        finally:
            # Remove the client from the connections list and close the socket
            print("Connection closed by the client.")
            for ip,files in list(self.files_per_client.items()):
                if ip ==client_socket.getpeername()[0]:
                    del self.files_per_client[ip]
                    print("Removed {} from the file list".format(ip))
            self.connections.remove(client_socket)
            client_socket.close()
            


# Main function
def main():
   # print("This is the main function in this Python P2P Program. (Server Edition)")
    print("""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣦⡀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⢀⣴⣦⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣦⡀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣆⠀⠀⢀⣴⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⣷⡄⠘⣿⣿⣿⣿⣿⣿⣿⡿⠀⣴⣿⣿⣿⣿⣿⠀⠀⠀⠀
⠀⢸⣦⡀⠙⢿⣿⣿⣿⣿⠆⠈⠛⣋⣉⣉⡛⠛⠀⢾⣿⣿⣿⣿⡿⠟⢀⣤⡆⠀
⠀⢸⣿⣿⣷⣄⠙⢿⠟⢁⣴⣾⣿⠿⠛⠻⣿⣿⣦⣄⠙⢿⡿⠋⣀⣴⣿⣿⡇⠀
⠀⢸⣿⣿⣿⣿⣷⣄⠐⢿⣿⠟⢁⣴⣾⣦⡀⠙⢿⣿⡷⠀⣠⣾⣿⣿⣿⣿⡇⠀
⠀⢸⣿⣿⣿⣿⣿⣿⣦⡀⠁⣴⣿⣿⣿⣿⣿⣦⡈⠋⣠⣾⣿⣿⣿⣿⣿⣿⠃⠀         Welcome to Lotus Leaf (Server Edition)
⠀⠈⣿⣿⣿⣿⣿⣿⡟⢀⣾⣿⣿⣿⣿⣿⣿⣿⣷⡀⢻⣿⣿⣿⣿⣿⣿⡏⠀⠀
⠀⠀⠸⣿⣿⣿⣿⣿⠁⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠈⣿⣿⣿⣿⣿⡟⠀⠀⠀
⠀⠀⠀⠹⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⡟⠁⠀⠀⠀
⠀⠀⠀⠀⠈⠻⣿⣿⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢀⣿⣿⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠛⠧⠘⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠼⠋⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ """)

    server = Server()
    server.start()

if __name__ == "__main__":
    main()
    while True:
        pass
