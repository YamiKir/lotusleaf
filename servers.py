import socket
import threading

## things needed to be added to Server class: 
#  tracking of what files are on which clients 
#  connecting clients together 
#  tracking the status of clients 
## 

class Server:

    MAX_WAITING=3 ##var for the max number of waiting connections

    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.connections=[]
        self.server_socket=None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ##AF_INET=>IP4, SOCK_STREAM =>TCP (so that they continue to comminucate after a reply) (INET6 is IP6)
        self.server_socket.bind((self.host, self.port)) ##sets the server socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) ##allows for the same socket to be connected again
        self.server_socket.listen(self.MAX_WAITING) ##allows for number of waiting connection 
        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept() ## socket.accept() returns the socket and address information of the accepted socket.
            print(f"Connection from {client_address}")
            self.connections.append(client_socket) ## adds the current connection to the connections list
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,)) ##please please please dont elimate the ,. (needed as Thread expects a tuple)
            client_thread.start()
    def handle_client(self, client_socket):
        print(f"Handling client @ {client_socket}")
        while True:
            try:
                message = input("Enter message to send to client: ")  # Get message from user
                client_socket.send(message.encode())  # Send message to client
            except ConnectionResetError:
                print("Connection closed by the client.")
                self.connections.remove(client_socket)
                break

def main ():

        print("This is the main function in this Python P2P Program. (Server Edition)")
        server=Server('localhost',9999)
        server.start()
        

if __name__ == "__main__":
    main()
    while True: ## so window doesnt disappear
        pass