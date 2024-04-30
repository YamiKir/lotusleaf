import socket
import threading
import json
import os
import sys

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
                elif line.startswith("File Path:"):
                    file_path = line.split("File Path:")[1].strip()
                    setup_info['File Path'] = file_path
            return setup_info
    except IOError:
        print("File not found.")
        return None

def files_in_dir(filepath):
    files_list = os.listdir(filepath)
    files_with_size = [(file, os.path.getsize(os.path.join(filepath, file))) for file in files_list]
    return files_with_size

class Client:
    def __init__(self):
        setup_info = read_setup("setup.txt")
        self.host = setup_info['Tracker IP']
        self.port = setup_info['Port']
        self.client_socket = None
        self.file_path = setup_info['File Path']
        self.files_per_client = {}
        self.lock = threading.Lock()

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print("Connected to server at {}:{}".format(self.host, self.port))
        self.send_file_list()
        self.start_reading_data()

    def close(self):
        with self.lock:
            self.client_socket.close()
            print("Connection closed")

    def send_file_list(self):
        file_list = files_in_dir(self.file_path)
        file_list_json = json.dumps(file_list)
        data_to_send = {'ip': self.get_local_ip(), 'files': file_list_json}
        with self.lock:
            self.client_socket.send(json.dumps(data_to_send).encode())

    def read_data(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    with self.lock:
                        files_per_client_json = data.decode()
                        self.files_per_client = json.loads(files_per_client_json)
            except Exception as e:
                print("Error while reading data:", e)
                break

    def get_local_ip(self):
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            return local_ip
        except socket.error:
            return None

    def start_reading_data(self):
        data_reading_thread = threading.Thread(target=self.read_data)
        data_reading_thread.daemon = True
        data_reading_thread.start()


    def download_list(self):
        unique_names = set()

        with self.lock:
            for files_json in self.files_per_client.values():
                files_list = json.loads(files_json)
                for file_info in files_list:
                    if len(file_info) >= 1:
                        file_name = file_info[0]
                        unique_names.add(file_name)

        return list(unique_names)




    



def read_user_input(client):
    while True:
        command = input("Enter a command (view, download, exit): ").strip().lower()
        if command == 'view':
            print(client.files_per_client)
        elif command == 'download':
            down_list=client.download_list()
            print(down_list)
            if len(down_list)>0: 
                chosen_file=input("Enter the name of the file you want to download: ").strip().lower()
                while chosen_file not in down_list:
                    chosen_file=input("Enter the name of the file you want to download: ").strip().lower()
                print("{} is about to be downloaded from your peers".format(chosen_file))
        elif command == 'exit':
            client.close()
            sys.exit()
        else:
            print("Invalid command. Type 'exit' to quit.")

def main():
    print("This is the main function in this Python P2P Program. (Client)")
    client = Client()
    client.connect()
    user_input_thread = threading.Thread(target=read_user_input, args=(client,))
    user_input_thread.start()
    user_input_thread.join()  # Wait for the user input thread to finish

if __name__ == "__main__":
    main()
