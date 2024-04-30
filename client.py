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
        file_ip_mapping = {}

        with self.lock:
            for ip, files_json in self.files_per_client.items():
                files_list = json.loads(files_json)
                for file_info in files_list:
                    if len(file_info) >= 1:
                        file_name = file_info[0]
                        if file_name not in file_ip_mapping:
                            file_ip_mapping[file_name] = []
                        file_ip_mapping[file_name].append(ip)

        return file_ip_mapping

    def download_file_from_ips(self, file_name, ips):
        for ip in ips:
            try:
                print("Attempting to download {} from {}".format(file_name, ip))
                # Implement the code to connect to the IP and download the file here
            except Exception as e:
                print("Error while downloading from {}: {}".format(ip, e))

def read_user_input(client):
    while True:
        command = input("Enter a command (view, download, exit): ").strip().lower()
        if command == 'view':
            print(client.files_per_client)
        elif command == 'download':
            file_ip_mapping = client.download_list()
            print("Available files for download:")
            for file_name in file_ip_mapping.keys():
                print("- {}".format(file_name))
            chosen_file = input("Enter the name of the file you want to download: ").strip().lower()
            if chosen_file in file_ip_mapping:
                client.download_file_from_ips(chosen_file, file_ip_mapping[chosen_file])
            else:
                print("File not found.")
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
