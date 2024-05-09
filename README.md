# Final home exam - DATA2410

This submission is an implementation of a reliable data transfer protocol with Go-Back-N on top of UDP. The client sends a file to recieve and store on the server (as recieved.jpg)

## Contains (6 files)
Submission.pdf  
application.py - Python script to invoke either the server or the client  
udp_server.py - The server code  
udp_client.py - The client code  
iceland_safiqul.jpg - The test image to transfer over the network   
README.md

(recieved.jpg) - This jpg file will be created on the server side when the test image is recieved 

## To set up the server use this syntax
"python3 application.py -s -i 10.0.1.2 -p 8080 -d 1800"

#### Where:  
-s invokes server mode  
-i is the server ip  
-p is the server port  
-d is the recieved packet you want to manually discard (optional)

## To set up the client use this syntax
"python3 application.py -c -i 10.0.1.2 -p 8080 -f iceland_safiqul.jpg -w 3

#### Where:  
-c invokes client mode  
-i is the server ip  
-p is the server port  
-f is the file you want to send (optional)  
-w is the sliding window (optional, default 3)


## Author 
s356213 - Sigurd Omnes