import socket
import threading
import json
import time

## things needed to be added to Server class: 
#  tracking of what files are on which clients 
#  connecting clients together 
#  tracking the status of clients 
## 
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
    
class Server:

    MAX_WAITING=3 ##var for the max number of waiting connection
    def print_connections(self):
        print("Active Connections:")
        for connection in self.connections:
            print(connection)
        
    def __init__(self,host,port):
        setup_info=read_setup("setup.txt")
        self.host= setup_info['Tracker IP']
        self.port=setup_info['Port']
        self.connections=[]
        self.server_socket=None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ##AF_INET=>IP4, SOCK_STREAM =>TCP (so that they continue to comminucate after a reply) (INET6 is IP6)
        self.server_socket.bind((self.host, self.port)) ##sets the server socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ##allows for the same socket to be connected again
        self.server_socket.listen(self.MAX_WAITING) ##allows for number of waiting connection 
        print("Server started on {}:{}".format(self.host, self.port))

        while True:
            client_socket, client_address = self.server_socket.accept() ## socket.accept() returns the socket and address information of the accepted socket.
            print("Connection from {}.".format(client_address))
            self.connections.append(client_socket) ## adds the current connection to the connections list
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,)) ##please please please dont elimate the ,. (needed as Thread expects a tuple)
            client_thread.start()
    def handle_client(self, client_socket):
        print("Handling client @ {}".format(client_socket))
        while True:
            try:
                ##message = input("Enter message to send to client: ")  # Get message from user
                ##client_socket.send(message.encode())  # Send message to client
                connection_list = [str(addr.getpeername()) for addr in self.connections]
                connection_list_json = json.dumps(connection_list)
                time.sleep(5)
                client_socket.send(connection_list_json.encode())
                self.print_connections() ## development line
            except ConnectionResetError:
                print("Connection closed by the client.")
                self.connections.remove(client_socket)
                break
   

def main ():
    try:
        print("This is the main function in this Python P2P Program. (Server Edition)")
        server=Server('169.254.132.175',80)
        server.start()
    except Exception as e:
        print("An error occurred: " + str(e))
        

if __name__ == "__main__":
    main()
    while True: ## so window doesnt disappear
        pass
