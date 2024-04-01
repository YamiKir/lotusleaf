import socket
import threading
class Client:

    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.server_socket=None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ##AF_INET=>IP4, SOCK_STREAM =>TCP (so that they continue to comminucate after a reply)
        self.client_socket.connect((self.host, self.port))  ##right now the server is localhost:9999
        print(f"Connected to server at {self.host}:{self.port}") ##right now the server is localhost:9999

    def close(self):
        self.client_socket.close()
        ##send a disconnect message on the server
        print("Connection closed")

    def read_data(self):
        while True: 
            try: 
                data = self.client_socket.recv(1024)
                if data:
                    print("Recieved:",data.decode())
            except ConnectionResetError:
                print("Connection closed by the server.")
                break


def main ():

    print("This is the main function in this Python P2P Program. (Client)")
    client = Client('localhost', 9999) 
    client.connect()
    client.read_data()
#    client.close()
   
    


if __name__ == "__main__":
    main()
    while True: ## so window doesnt disappear
        pass 
        
