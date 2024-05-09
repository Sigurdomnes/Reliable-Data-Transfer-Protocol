import argparse # To parse passed in arguments
from ipaddress import ip_address, IPv4Address # To check if IP is valid
from udp_server import udp_server # Import server
from udp_client import udp_client # Import client
import os # To check if file exists


def main():
    '''
        Description:
        This function invokes a server or a client through command line arguments
        Arguments:
        -c: Client mode
        -s: Server mode
        -i: Server IP (Server/Client)
        -p: Server port (Server/Client)
        -f: File to transfer (Client, optional)
        -w: Sliding window (Client, optional, default 3)
        -d: Manually discard packet (Server, optional)
        Returns: void
    '''
    parser = argparse.ArgumentParser()

    try:
        # Arguments:
            # Stores client as true if passed argument -c:
        parser.add_argument('-c', '--client', action='store_true', help='Invoke client mode')
            # Stores server as true if passed argument -s:        
        parser.add_argument('-s', '--server', action='store_true', help='Invoke server mode')
            # Stores port as int if passed in with -p, default 8080:          
        parser.add_argument('-p' , '--port', type=int, default=8080, help='Port number')
            # Stores IP as string if passed in with -i, default 127.0.0.1:      
        parser.add_argument('-i' , '--ip', type=str, default='127.0.0.1', help='IP address')
            # Stores filename as string if passer in with -f:
        parser.add_argument('-f', '--file', type=str, help='Name of file to send')
            # Stores window size as int if passed in with -w, default 3:
        parser.add_argument('-w', '--window', type=int, help='Sliding window size, default 3')
            # Stores discard packet seq number:
        parser.add_argument('-d', '--discard', type=int, help='Packet to manually discard')

        args = parser.parse_args()  # Parses args to be accessible with args.xyz
        
    except:
        print(f"Cant parse arguments\n")
        return
    
    try:
        if args.server and args.client:
            print("You cannot use both client and server mode at the same time")
            return  # Return if passed both server and client
        elif not args.server and not args.client:
            print("You should run either in client or server mode")
            return  # Return if passed neither server nor client
        elif args.port < 1024 or args.port > 65535:
            print("Invalid port. It must be within the range [1024, 65535]")
            return  # Return if passed a port value not inside of range
        elif args.file:
            if args.server:
                print("Argument [-f FILE] is not recognized in server mode")
                return # Return if -f invoked with server mode
            elif not os.path.exists(args.file):
                print(f"File '{args.file}' does not exist in its given path")
                return # Return if file does not exist
        elif args.window:
            if args.server:
                print("Argument [-w WINDOW] is not recognized in server mode")
                return # Return if -w invoked with server mode
            elif not (0 < args.window <= 10):
                print("Sliding window must be inside 1 and 10")
                return # Return if sliding window is not inside 1 and 10
        elif args.client and args.discard:
            print("Argument [-d DISCARD] is not recognized in client mode")
            return # Return if -d is invoked with client mode
        try:
            if not type(ip_address(args.ip)) is IPv4Address: # Check if IP is valid but not IPv4
                print("Invalid IP. It must be an IPv4 address in this format: 10.1.2.3")
                return  # Return if not IPv4
        except:
            print("Invalid IP. It must be in this format: 10.1.2.3")
            return  # Return if IP not valid
    except:
        print(f"Couldn't validate arguments. Try again.\n")
        return
    
    # If all inputs passes tests, start the server or client:
    try:
        if args.server:
            udp_server(args.ip, args.port, args.discard)
        elif args.client:
            udp_client(args.ip, args.port, args.file, args.window)
    except:
        print(f"Could not start the {'server' if args.server else ''}{'client' if args.client else ''}. Please try again.\n")
 
if __name__ == "__main__":
    main()

    
    