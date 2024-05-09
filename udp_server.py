from socket import *
import struct # To pack/unpack byte data
from datetime import datetime # To display current time
import time # To calculate throughput

def now():
    '''
    Description:
        This function returns the current time
        Returns: current time
    '''
    return datetime.now().time() # Gets current time in format HH:MM:SS.ms
        
def udp_server(server_ip, server_port, discard):
    '''
    Description:
        Main server function
        Arguments: 
        server_ip (int): IP the server should bind to
        server_port (int): Port of the server
        discard (int): A packet that should be discarded on first try by the server
        Returns: This function is void 
    '''
    # Prepare an UDP server socket
    server_ip = server_ip
    server_port = server_port
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    
    try:
    # Bind server address
        serverSocket.bind((server_ip, server_port))
    except error as e:
        print(f"Bind error: {e}")
        return
        
    # Set flag bits
    SYNACK = 1 << 3 | 1 << 2
    SYN = 1 << 3
    ACK = 1 << 2
    FIN = 1 << 1
    R = 1 << 0
    
    # Initialize recieved application data as bytes object
    application_data = b''
          
    while True:
    # Establish the connection
        print(f"\nServer ready to serve on ip: {server_ip} and port: {server_port}...")
        # Listen for flagged SYN header packet
        data, addr = serverSocket.recvfrom(6)
        # Unpack header
        seq_num, ack_num, flags = struct.unpack('!HHH', data)
        
        # Set timeout 10 seconds to prevent server from waiting indefinetly on the client
        serverSocket.settimeout(10) 
        try:
            # Check if packet flagged SYN
            if flags == SYN:
                print("SYN packet recieved")
                # Pack header flagged SYNACK
                header = struct.pack('!HHH', 0, 0, SYNACK)
                # Send flagged SYNACK header packet to client
                serverSocket.sendto(header, addr)
                print("SYN-ACK packet is sent")
            while True:
                # Listen for flagged ACK header packet
                data, addr = serverSocket.recvfrom(6)
                # Unpack header
                seq_num, ack_num, flags = struct.unpack('!HHH', data)
                # Check if packet flagged ACK
                if flags == ACK:
                    print("ACK packet is recieved")
                    print("Connection established")
                    # Initialize control sequence number to assure received packets are in order
                    ctrl_seq_num = 1
                    # Connection established - listen for data packets
                    # Set start time of data transfer
                    transfer_start_time = time.time()
                    while True:
                        # Listen for packets
                        data, addr = serverSocket.recvfrom(1000)
                        # Unpack header
                        seq_num, ack_num, flags = struct.unpack('!HHH', data[:6])
                        # Check that FIN flag is not set
                        if flags == FIN:
                            # Set end time of data transfer
                            transfer_end_time = time.time()
                            print("\nFIN packet is recieved")
                            # Pack header flagged ACK
                            header = struct.pack('!HHH', 0, 0, ACK)
                            # Send to client
                            serverSocket.sendto(header, addr)
                            print("FIN ACK packet sent\n")
                            # Write recieved data to file on server
                            try:
                                with open('recieved.jpg', 'wb') as f:
                                    f.write(application_data)
                            except:
                                print("Couldn't write to file 'recieved.jpg' on server")
                            # Calculate throughput
                            try:
                                transfer_time = transfer_end_time - transfer_start_time
                                throughput = (len(application_data) / transfer_time) / 1000000
                                print(f"The throughput is {throughput:.2f} Mbps")
                            except:
                                print("Couldn't calculate throughput")
                            print("Connection closes\n")
                            # Exit
                            return
                        # If FIN flag is not set, recieve data
                        # Check if recieved packet is in order or else discard
                        elif seq_num == ctrl_seq_num:
                            # Check that packet should not be manually discarded
                            if seq_num != discard:
                                # Concatenate application data as bytes object
                                application_data += data[6:]
                                print(f"{now()} -- packet {seq_num} is recieved")
                                # Pack header with ack_num set as seq_num of last recieved packet in order
                                header = struct.pack('!HHH', 0, seq_num, 0)
                                # Send to client
                                serverSocket.sendto(header, addr)
                                print(f"{now()} -- sending ack for the recieved packet {seq_num}")
                                # Increment control sequence number
                                ctrl_seq_num += 1
                            # If packet is manually discarded
                            else:
                                print(f"Discarding packet {seq_num}")
                                discard = -1
                        # Display packets recieved out of order
                        else:
                            print(f"{now()} -- out-of-order packet {seq_num} is received")
                        
        # Timeout exception             
        except timeout:
            print("Connection timed out (10 seconds)")
            # Exit
            return
        
        # General exception            
        except error as e:
            print (f"Connection error: {e}")
            # Exit
            return