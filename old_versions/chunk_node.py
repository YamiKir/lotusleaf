# chunk_node.py
import asyncio

async def request_chunk(chunk_id):
    reader, writer = await asyncio.open_connection('127.0.0.1', 9999)
    request_message = f'request,{chunk_id}'
    writer.write(request_message.encode())
    await writer.drain()

    # Assuming the chunk is less than 10KB for simplicity
    chunk_data = await reader.read(10240)
    if chunk_data.startswith(b'Error'):
        print("Failed to download chunk:", chunk_data.decode())
    else:
        # Save the chunk to a file
        with open(f'downloaded_chunk_{chunk_id}.dat', 'wb') as file:
            file.write(chunk_data)
        print(f"Chunk {chunk_id} downloaded successfully.")

    writer.close()

if __name__ == "__main__":
    chunk_id = '1'  # Example for requesting the first chunk
    asyncio.run(request_chunk(chunk_id))
