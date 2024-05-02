import socket
import threading
import json
import os
import sys
import time
#Parses for Tracker IP:Port and file paths (File Path and Download Path) given a filename
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
                elif line.startswith("Download Path:"):
                    file_path = line.split("Download Path:")[1].strip()
                    setup_info['Download Path'] = file_path
            return setup_info
    except IOError:
        print("File not found.")
        return None
#returns all elements in a path alongside their sizes
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
        self.download = setup_info['Download Path']
        self.files_per_client = {} #holds a dictonary of {'ip':[files:size]}
        self.lock = threading.Lock()
        self.ear=False

    #connects to the Tracker
    def connect(self):
        self.start_listening()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        print("Connected to server at {}:{}".format(self.host, self.port))
        self.start_file_list()
        self.start_reading_data()
        
    #closes the connection to the Tracker
    def close(self):
        with self.lock:
            self.client_socket.close()
            print("Connection closed")
    
    #sends the files this pc has in File Path
    def send_file_list(self):
        while True:
            try:
                #print("Preparing to send file list...")
                file_list = files_in_dir(self.file_path)
                file_list_json = json.dumps(file_list)
                data_to_send = {'ip': self.get_local_ip(), 'files': file_list_json}
                #print(f"Sending data: {data_to_send}")
                with self.lock:
                    self.client_socket.send(json.dumps(data_to_send).encode())
               # print("Data sent successfully.")
                time.sleep(5)
            except Exception as e:
                print("Failed to send file list: ", e)
                break  # Optionally remove the break if you want the loop to continue even after a failure

    #recieves the files_per_client
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

    #returns this system's IP
    def get_local_ip(self):
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            return local_ip
        except socket.error:
            return None
        
    #file_per_client reading thread
    def start_reading_data(self):
        data_reading_thread = threading.Thread(target=self.read_data)
        data_reading_thread.daemon = True
        data_reading_thread.start()

    #filters files_per_client by filename
    def download_list(self):
        file_ip_mapping = {}
        local_ip = self.get_local_ip()

        with self.lock:
           for ip, files in self.files_per_client.items():
                if ip != local_ip:
                    files_list = files  # Assuming 'files' is already a list
                    for file_info in files_list:
                        if len(file_info) >= 2:
                            file_name, file_size = file_info
                            if file_name not in file_ip_mapping:
                                file_ip_mapping[file_name] = {'ips': [], 'size': file_size}
                            file_ip_mapping[file_name]['ips'].append(ip)

        return file_ip_mapping

    
    #downloads from each IP the entire file (Development Function OLD)
    def download_file_from_ips(self, file_name, ips):
        download_location=self.download
        for ip in ips:
            try:
                print("Attempting to download {} from {}".format(file_name, ip))
                # Connect to the IP on self.port
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as download_socket:
                    download_socket.connect((ip, self.port))

                    # Send the file name to request the file
                    download_socket.send(file_name.encode())

                    # Receive the file data
                    received_data = b""
                    while True:
                        data = download_socket.recv(4096)
                        if not data:
                            break
                        received_data += data

                    # Save the received file data to the specified download location
                    file_path = os.path.join(download_location, file_name)
                    with open(file_path, 'wb') as file:
                        file.write(received_data)

                    print("Download of {} from {} completed. Saved to {}".format(file_name, ip, file_path))

            except Exception as e:
                print("Error while downloading from {}: {}".format(ip, e))



    #downloads chunks from each peer with the file and aggreates it back together
    def download_file_chunks_from_ips(self, file_name, ips):
        download_location = self.download
        file_path = os.path.join(download_location, file_name)

        # Retrieve the total file size from download_list
        file_info = self.download_list().get(file_name)
        if file_info is None:
            print("File {} not found in download list.".format(file_name))
            return

        total_file_size = file_info['size']
        chunk_size = max(1024, total_file_size // 100)  # Determine chunk size based on file size
        print("chunk size={}, file size={}".format(chunk_size, total_file_size))

        with open(file_path, 'wb') as file:
            downloaded_size = 0
            ip_index = 0  # Start with the first IP in the list

            while downloaded_size < total_file_size:
                ip = ips[ip_index]  # Select IP based on current index
                ip_index = (ip_index + 1) % len(ips)  # Move to the next IP, wrap around if at the end

                try:
                    print("Attempting to download {} from {}".format(file_name, ip))
                    # Connect to the current IP on self.port
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as download_socket:
                        download_socket.connect((ip, self.port))
                        
                        # Prepare and send the request for a chunk
                        file_chunk_info = {
                            'name': file_name,
                            'start': downloaded_size,
                            'size': chunk_size
                        }
                        download_socket.send(json.dumps(file_chunk_info).encode())

                        # Receive the chunk of the file
                        while True:
                            data = download_socket.recv(chunk_size)
                            if not data:
                                break
                            file.write(data)
                            downloaded_size += len(data)

                            # Check if the file is fully downloaded
                            if downloaded_size >= total_file_size:
                                break

                    print("Download of {} chunk from {} completed. Chunk size ={}".format(file_name, ip, chunk_size))

                except Exception as e:
                    print("Error while downloading chunk from {}: {}".format(ip, e))

            print("File reconstruction completed. Saved to {}. Size={}".format(file_path, downloaded_size))



    #listening for peer connections
    def listening(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind((self.get_local_ip(), self.port))
        listen_socket.listen(5)
        print("Listening for incoming connections on {}:{}".format(self.get_local_ip(), self.port))
        self.ear=True

        while True:
            client_socket, client_address = listen_socket.accept()
            #print("Connection from {}:{}".format(client_address[0], client_address[1]))

            # Handle the connection in a separate thread
            client_thread = threading.Thread(target=self.handle_incoming_connection, args=(client_socket,))
            client_thread.start()

    #starts listening thread
    def start_listening(self):
        data_listening_thread = threading.Thread(target=self.listening)
        data_listening_thread.daemon = True
        data_listening_thread.start()

    #sends file list periodically on this thread
    def start_file_list(self):
        data_file_thread = threading.Thread(target=self.send_file_list)
        data_file_thread.daemon = True
        data_file_thread.start()
    
    #sends the requested file chunks 
    def handle_incoming_connection(self, client_socket):
        try:
            # Receive data from the client
            data = client_socket.recv(4096)

            if data:
                file_chunk_info=json.loads(data.decode())
                
                
                file_name=file_chunk_info['name']
                chunk_start=file_chunk_info['start']
                chunk_size=file_chunk_info['size']
                
                # Check if the requested file exists
                file_path = os.path.join(self.file_path, file_name)
                if os.path.exists(file_path):
                    # Open the file and send its contents to the client
                    with open(file_path, 'rb') as file:
                        file.seek(chunk_start)
                        chunk_data=file.read(chunk_size)
                        client_socket.sendall(chunk_data)
                        #print("Chunk {} sent to {}".format(file_name, client_socket.getpeername()))
                else:
                    # Send a message indicating that the file doesn't exist
                    error_message = "File {} not found".format(file_name)
                    client_socket.sendall(error_message.encode())
        except Exception as e:
            print("Error handling incoming connection:", e)
        finally:
            # Close the client socket
            client_socket.close()

#menu system for the client
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
            chosen_file = input("Enter the name of the file you want to download: ").strip()
            if chosen_file in file_ip_mapping:
                client.download_file_chunks_from_ips(chosen_file, file_ip_mapping[chosen_file]['ips'])
            else:
                print("File not found.")
        elif command == 'exit':
            client.close()
            sys.exit()
        else:
            print("Invalid command. Type 'exit' to quit.")

        

def main():

    #FOUND NOT ORIGINAL ASCII https://emojicombos.com/lotus-ascii-art
    print("""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢰⣦⡀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⢀⣴⣦⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣦⡀⠀⠀⣼⣿⣿⣿⣿⣿⣿⣆⠀⠀⢀⣴⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⣿⣿⣿⣿⣷⡄⠘⣿⣿⣿⣿⣿⣿⣿⡿⠀⣴⣿⣿⣿⣿⣿⠀⠀⠀⠀
⠀⢸⣦⡀⠙⢿⣿⣿⣿⣿⠆⠈⠛⣋⣉⣉⡛⠛⠀⢾⣿⣿⣿⣿⡿⠟⢀⣤⡆⠀
⠀⢸⣿⣿⣷⣄⠙⢿⠟⢁⣴⣾⣿⠿⠛⠻⣿⣿⣦⣄⠙⢿⡿⠋⣀⣴⣿⣿⡇⠀
⠀⢸⣿⣿⣿⣿⣷⣄⠐⢿⣿⠟⢁⣴⣾⣦⡀⠙⢿⣿⡷⠀⣠⣾⣿⣿⣿⣿⡇⠀
⠀⢸⣿⣿⣿⣿⣿⣿⣦⡀⠁⣴⣿⣿⣿⣿⣿⣦⡈⠋⣠⣾⣿⣿⣿⣿⣿⣿⠃⠀         Welcome to Lotus Leaf (Client Edition)
⠀⠈⣿⣿⣿⣿⣿⣿⡟⢀⣾⣿⣿⣿⣿⣿⣿⣿⣷⡀⢻⣿⣿⣿⣿⣿⣿⡏⠀⠀
⠀⠀⠸⣿⣿⣿⣿⣿⠁⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠈⣿⣿⣿⣿⣿⡟⠀⠀⠀
⠀⠀⠀⠹⣿⣿⣿⣿⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⣿⣿⣿⣿⡟⠁⠀⠀⠀
⠀⠀⠀⠀⠈⠻⣿⣿⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢀⣿⣿⡿⠋⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠛⠧⠘⣿⣿⣿⣿⣿⣿⣿⣿⡿⠁⠼⠋⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠛⠛⠛⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

         """)
    

    client = Client()
    client.connect()
    while not client.ear:
        time.sleep(1)
    user_input_thread = threading.Thread(target=read_user_input, args=(client,))
    user_input_thread.start()
    user_input_thread.join()  # Wait for the user input thread to finish

if __name__ == "__main__":
    main()
