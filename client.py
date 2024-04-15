import socket
import threading

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
    
class Client:

    def __init__(self):
        setup_info=read_setup("setup.txt")
        self.host= setup_info['Tracker IP']
        self.port=setup_info['Port']
        self.server_socket=None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ##AF_INET=>IP4, SOCK_STREAM =>TCP (so that they continue to comminucate after a reply)
        self.client_socket.connect((self.host, self.port))  ##right now the server is localhost:9999
        print("Connected to server at {}:{}".format(self.host,self.port)) ##right now the server is localhost:9999
        

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
    client = Client() 
    client.connect()
    client.read_data()
#    client.close()
   

if __name__ == "__main__":
    main()
    while True: ## so window doesnt disappear
        pass 
        
