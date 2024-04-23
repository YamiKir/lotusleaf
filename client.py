import socket
import threading
import ast

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
    except IOError:
        print("File not found.")
        return None
    
class Client:
    def get_local_ip(self):
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            return local_ip
        except socket.error:
            return None

    def __init__(self):
        setup_info = read_setup("setup.txt")
        self.host = setup_info['Tracker IP']
        self.port = setup_info['Port']
        self.client_socket = None
        

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print("Connected to server at {}:{}".format(self.host, self.port))

    def close(self):
        self.client_socket.close()
        print("Connection closed")

    def connect_to_ip(self, ip):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, 20))
            print("Connected to {} on port 20".format(ip))
            return True
        except Exception as e:
            print("Failed to connect to {}: {}".format(ip, e))
            return False

    def connect_to_all(self, connection_list):
        for ip, _ in connection_list:
            self.connect_to_ip(ip)
            

    def read_data(self):
        system_ip = self.get_local_ip()
        while True: 
            try: 
                data = self.client_socket.recv(1024)  # Reads the sent connection list
                if data:
                    data_str = data.decode()  # Convert bytes to string
                    received_connections = ast.literal_eval(data_str)  # Safely parse string into list of tuples
                
                # Filter out own IP address
                    #print("Recieved Connection List:", received_connections)
                    connection_list = []
                    for conn_str in received_connections:
                        ip, port = conn_str.strip("('')").split("', ")
                    
                        if ip != system_ip:
                            print(system_ip, " vs ", ip)
                            connection_list.append((ip, int(port)))

                    print("Filtered Connection List:", connection_list)
                    #if len(connection_list) > 0:
                        #self.connect_to_all(connection_list)
                    #print(system_ip + " is this machine")
            except Exception:
                print("Connection closed by the server.")
                break
    


def main():
    print("This is the main function in this Python P2P Program. (Client)")
    client = Client() 
    client.connect()
    client.read_data()

if __name__ == "__main__":
    main()
    while True:  # so the window doesn't disappear
        pass 
