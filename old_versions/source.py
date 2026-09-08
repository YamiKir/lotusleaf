# source.py
import asyncio
import os

async def handle_client(reader, asyncio_writer):
    # Wait to receive a chunk request 
    data = await reader.read(100)  # Assuming the request is less than 100 bytes
    message = data.decode()
    action, chunk_id = message.split(',')

    if action == "request":
        # Assuming chunks are stored in a directory named 'chunks'
        chunk_path = os.path.join('chunks', f'chunk_{chunk_id}.dat')
        if os.path.exists(chunk_path):
            with open(chunk_path, 'rb') as chunk_file:
                while True:
                    chunk_data = chunk_file.read(1024)  # Read in chunks of 1024 bytes
                    if not chunk_data:
                        break  # End of file
                    asyncio_writer.write(chunk_data)
                await asyncio_writer.drain()  # Ensure all data is sent
        else:
            asyncio_writer.write(b'Error: Chunk not found')

    asyncio_writer.close()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 9999)
    await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
