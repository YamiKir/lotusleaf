# tracker.py
import asyncio

class TrackerNode:
    def __init__(self):
        self.peer_info = {}  # Maps peer name to (host, port)
        self.chunk_locations = {}  # Maps chunk IDs to a list of peers that hold them

    async def handle_peer(self, reader, writer):
        data = await reader.read(1024)
        message = data.decode()
        parts = message.split(',')
        command = parts[0]
        
        if command == "register":
            # Registration request format: "register,peer_name,host,port"
            _, peer_name, host, port = parts
            self.peer_info[peer_name] = (host, int(port))
            print(f"Registered {peer_name} at {host}:{port}")
        elif command == "update":
            # Chunk update format: "update,peer_name,chunk_id"
            _, peer_name, chunk_id = parts
            if chunk_id not in self.chunk_locations:
                self.chunk_locations[chunk_id] = []
            self.chunk_locations[chunk_id].append(peer_name)
            print(f"Updated {peer_name} holds chunk {chunk_id}")
        elif command == "locate":
            # Locate request format: "locate,chunk_id"
            _, chunk_id = parts
            holders = self.chunk_locations.get(chunk_id, [])
            response = ",".join(holders)
            writer.write(response.encode())
            await writer.drain()
            print(f"Responded with locations for chunk {chunk_id}")

        writer.close()

    async def main(self, host='127.0.0.1', port=8888):
        server = await asyncio.start_server(self.handle_peer, host, port)
        print("Tracker Node started...")
        await server.serve_forever()

if __name__ == "__main__":
    tracker = TrackerNode()
    asyncio.run(tracker.main())
