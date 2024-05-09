from socket import *
import struct # To pack/unpack byte data
from datetime import datetime # To display current time
    
def now():
    '''
    Description:
        This function returns the current time
        Returns: Current time
    '''
    return datetime.now().time() # Gets current time in format HH:MM:SS.ms

def udp_client(server_ip, server_port, file, window):
    '''
    Description:
        Main client funtion
        Arguments: 
        server_ip (int): IP of the server you want to establish a connection to
        server_port (int): Port of the server
        file (file): File on client host you want to send to server
        window (int): Sliding window size of the sender (client)
        Returns: This function is void      
    '''
    
    # Set window size to default 3, or value of passed in window variable
    sliding_window_size = window if window else 3
    
    def update_window(lst, value):
        '''
        Description:
            This function adds a value to the end of a list and returns the last x elements of the list based on the passed in window size value
            Arguments:
            lst: The list you want to append the value to
            value: The value to append
            Returns: last x elements of the list depending on window size
        '''
        lst.append(value) # Adds new window value to end of list
        return lst[-sliding_window_size:] # Return only last elements according to window size
    
    # Initialize sliding window list
    sliding_window = []
    
    # Set flag bits
    SYNACK = 1 << 3 | 1 << 2
    SYN = 1 << 3
    ACK = 1 << 2
    FIN = 1 << 1
    R = 1 << 0
    
    # Initialize header values
    seq_num = 0
    ack_num = 0

    # Create an UDP socket at the client side
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    server_address = (server_ip, server_port)
    
    # Set socket timeout = 500ms
    clientSocket.settimeout(0.5)
        
    try:
        # Establish connection
        print(f"\nConnecting to server IP: {server_ip} port: {server_port}")
        print("Connection establishment phase:\n")
        
        if file:
            # Open the passed in binary file as f
            f = open(file, 'rb')
        
        # Pack header flagged SYN
        header = struct.pack('!HHH', 0, 0, SYN)
        # Send flagged SYN header packet to server to initiate connection 
        clientSocket.sendto(header, server_address)
        print("SYN packet is sent")
        
        # Recieve header packet from server
        data, server_address = clientSocket.recvfrom(6)
        # Unpack the header
        recv_seq_num, ack_num, flags = struct.unpack('!HHH', data)

        # Check if header is flagged SYN-ACK
        if flags == SYNACK:
            print("SYN-ACK packet is recieved")
            # Pack header flagged ACK
            header = struct.pack('!HHH', 0, 0, ACK)
            # Send flagged ACK header packet to server
            clientSocket.sendto(header, server_address)
            print("ACK packet is sent")
            print("Connection established\n")
            
            # Connection established -  send data packets
            print("Data Transfer:\n")
            
            while True and file:
                # Read 994 bytes of passed in file
                application_data = f.read(994)
                # Try for timeout
                try:
                    # If end of application data, wait for acknowledgement of last packets
                    if not application_data:
                        data, server_address = clientSocket.recvfrom(6)
                        recv_seq_num, ack_num, flags = struct.unpack('!HHH', data)
                        print(f"{now()} -- ACK for packet = {ack_num} is recieved")
                        # If all packets acknowledged, break loop and jump to connection teardown
                        if ack_num == sliding_window[-1]:
                            break
                    # Push initial packets up to sliding window limit
                    elif seq_num < sliding_window_size:
                        # Increment sequence number (Initialized as 0)
                        seq_num += 1
                        # Pack header with sequence number
                        header = struct.pack('!HHH', seq_num, 0, 0)
                        # Update sliding window
                        sliding_window = update_window(sliding_window, seq_num)
                        # Send header + data packet to server
                        clientSocket.sendto(header + application_data, server_address)
                        print(f"{now()} -- Packet with seq = {seq_num} is sent, sliding window = {sliding_window}")
                    # Send data packets inside sliding window
                    else:
                        data, server_address = clientSocket.recvfrom(6)
                        recv_seq_num, ack_num, flags = struct.unpack('!HHH', data)
                        print(f"{now()} -- ACK for packet = {ack_num} is recieved")
                        # Check if ack_num equals last sent packet
                        if ack_num == sliding_window[-sliding_window_size]:
                            # Increment sequence number
                            seq_num += 1
                            # Pack header with sequence number
                            header = struct.pack('!HHH', seq_num, 0, 0)
                            # Update sliding window
                            sliding_window = update_window(sliding_window, seq_num)
                            # Send header + data packet to server
                            clientSocket.sendto(header + application_data, server_address)
                            print(f"{now()} -- Packet with seq = {seq_num} is sent, sliding window = {sliding_window}")             
                # Timeout exception
                # Resend packets
                except timeout:
                    print(f"{now()} -- RTO occurred")
                    # Set ret_num to last acknowledged packet
                    ret_num = ack_num
                    i = 0
                    while i < sliding_window_size:
                        # Increment retransmission number
                        ret_num += 1
                        # Pack header with retransmission number
                        header = struct.pack('!HHH', ret_num, 0, 0)
                        # Find the file bytes that corresponds with the retransmission number
                        f.seek(994*(ret_num-1))
                        ret_data = f.read(994)
                        # Check if end of application data
                        if not ret_data:
                            break
                        # Send header + data packet to server
                        clientSocket.sendto(header + ret_data, server_address)
                        print(f"{now()} -- Retransmitting packet with seq = {ret_num}")
                        i += 1
                
                # General exception        
                except error as e:
                    print(f"Error : {e}")
                    return

            # Connection teardown    
            # End of data transfer    
            print("DATA Finished\n") 
            print("Connection teardown:\n")
            # Pack header flagged FIN
            header = struct.pack('!HHH', 0, 0, FIN)
            # Send FIN packet to server
            clientSocket.sendto(header, server_address)
            print("FIN packet is sent")    
            
            while True:
                #Try for timeout
                try:
                    # Listen for ACK from server
                    data, server_address = clientSocket.recvfrom(6)
                    recv_seq_num, ack_num, flags = struct.unpack('!HHH', data)
                    # Check if received header is flagged ACK 
                    if flags == ACK:
                        print("FIN ACK packet is recieved")
                        print("Connection closes\n")
                        # Exit
                        return  
                # Timeout exception
                # Resend FIN packet
                except timeout:
                    print("RTO occurred")
                    # Pack header flagged FIN
                    header = struct.pack('!HHH', 0, 0, FIN)
                    # Send FIN packet to server
                    clientSocket.sendto(header, server_address)
                    print("Resending FIN packet")
                # Exception server not available    
                except error:    
                    print("Server not available")
                    print("Connection closes\n")
                    # Exit
                    return                  
        
    except error:
        print("\nConnection failed\n")
        # Exit
        return
        
