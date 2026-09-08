# lotusleaf'

a p2p solution

Network Overview:
Source Node: Holds the original file to be shared.
Chunk Nodes (3 Nodes): Download and temporarily store chunks of the file.
Aggregator Node: Aggregates downloaded chunks into the original file.
Tracker Node: Keeps track of node statuses, chunk distribution, and file assembly progress.
Step 1: Preparing the File for Distribution
The Source Node splits the file into chunks. The number of chunks can be based on the file size and the optimal chunk size for network transfer (e.g., 1MB).
Each chunk is hashed for integrity verification.
Step 2: Distributing File Chunks
The Source Node announces the availability of file chunks to the Tracker Node.
The Tracker Node manages the distribution logic, instructing the Chunk Nodes which chunks to download from the Source Node.
Chunk Nodes download their assigned chunks and notify the Tracker Node upon successful download.
Step 3: Aggregating Chunks into the Original File
Once all chunks are downloaded, the Tracker Node instructs the Chunk Nodes to send their chunks to the Aggregator Node.
The Aggregator Node reassembles the chunks in the correct order to recreate the original file. Integrity checks are performed using the chunk hashes.
Step 4: Tracking Node and Chunk Status
The Tracker Node maintains a dynamic list of online and offline nodes by periodically receiving heartbeat signals from each node.
It also keeps a record of which chunks are stored on which Chunk Nodes and tracks the aggregation progress on the Aggregator Node.
Implementing the System:
Communication Protocol:
Implement a simple communication protocol that supports messages for announcing file chunks, requesting downloads, sending heartbeats, and transferring chunks. JSON over TCP or a simple REST API are good choices for clarity and simplicity
