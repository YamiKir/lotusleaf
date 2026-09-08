# Lotus Leaf


The structure of Lotus Leaf requires three components: a tracking server, a set of peers, and the setup file.

The Tracking Server program file reads "setup.txt" fields "Tracker" for the ip of the server (check Google to determine the Public/Private IP of your server) and "Port" for the desired port to broadcast on.  

The Client program reads "setup.txt" for the file path fields (Downloads and File). The fields can be different or the same.  

After the tracker server starts, it starts waiting for incomming connections from the clients. The clients sends each file name and sizes of the contents of the their "File Path". When a file download is attempted, the clients with the file will send chunks of the entire file so the random disconnect of SOME peers won't result in the complete halting of the download in most cases.