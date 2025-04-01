import socket

# Change this to the server's IP or hostname
HOST = "172.20.101.233"
PORT = 12345

def main():
    """
    Simple client that connects to the server, sends commands, and prints responses.
    """
    print(f"[Client] Connecting to {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((HOST, PORT))
            print("[Client] Connected successfully!")
        except Exception as e:
            print(f"[Client] Failed to connect: {e}")
            return

        while True:
            command = input("Enter command (compute <expr>, gpu_matmul <size>, exit): ").strip()
            if not command:
                continue

            # Send the command to the server
            sock.sendall((command + "\n").encode('utf-8'))

            if command.lower() == "exit":
                print("[Client] Exiting.")
                break

            # Receive the response
            response = sock.recv(4096)
            if not response:
                print("[Client] Server closed the connection.")
                break

            print("[Client] Response:")
            print(response.decode('utf-8').strip())

if __name__ == "__main__":
    main()