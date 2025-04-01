import socket
import threading
import torch
import time

# Server configuration
HOST = ''        # Listen on all available interfaces (0.0.0.0)
PORT = 12345     # Port number to listen on

# Determine if we have a GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[Server] Using device: {device}")

def handle_client(client_socket, client_address):
    """
    Handles communication with a single connected client.
    Receives commands, processes them on GPU/CPU, and sends back results.
    """
    print(f"[Server] Client connected: {client_address}")
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                # Client closed the connection
                print(f"[Server] Client {client_address} disconnected.")
                break

            message = data.decode('utf-8').strip()
            print(f"[Server] Received from {client_address}: {message}")

            # Special case: client wants to exit
            if message.lower() == "exit":
                response = "Goodbye!\n"
                client_socket.sendall(response.encode('utf-8'))
                break

            # Example commands:
            #   "compute 2+3*4"
            #   "gpu_matmul 1000"
            #   "exit"
            tokens = message.split()
            if len(tokens) == 0:
                response = "No command provided.\n"
                client_socket.sendall(response.encode('utf-8'))
                continue

            command = tokens[0].lower()

            if command == "compute":
                # e.g. "compute 2+3*4"
                expression = message[len("compute"):].strip()
                result = cpu_compute(expression)
                response = f"{result}\n"
                client_socket.sendall(response.encode('utf-8'))

            elif command == "gpu_matmul":
                # e.g. "gpu_matmul 1000"
                if len(tokens) < 2:
                    response = "Usage: gpu_matmul <size>\n"
                else:
                    try:
                        size = int(tokens[1])
                        result_sum, elapsed = gpu_matmul(size)
                        response = (f"Matrix multiplication sum: {result_sum}\n"
                                    f"Time taken: {elapsed:.4f}s\n")
                    except ValueError:
                        response = "Invalid size for gpu_matmul.\n"
                client_socket.sendall(response.encode('utf-8'))

            else:
                response = "Unrecognized command.\n"
                client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        print(f"[Server] Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"[Server] Connection closed: {client_address}")

def cpu_compute(expression):
    """
    Evaluate a Python arithmetic expression on the CPU.
    Caution: 'eval' is dangerous with untrusted input.
    In production, use a safer parser or sandbox.
    """
    try:
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return f"Error evaluating expression: {e}"

def gpu_matmul(size):
    """
    Example of a GPU-based computation (or CPU fallback).
    Generates two random tensors (size x size), multiplies them, and returns:
      1) The sum of all elements in the result
      2) The elapsed time
    """
    start = time.time()

    # Create random tensors on the chosen device (CPU or GPU)
    a = torch.randn((size, size), device=device)
    b = torch.randn((size, size), device=device)

    # Perform matrix multiplication
    c = torch.matmul(a, b)

    # Sum of all elements in matrix 'c'
    result_sum = torch.sum(c).item()

    elapsed = time.time() - start
    print(f"[Server] Performed {size}x{size} matmul on {device} in {elapsed:.4f}s")
    return result_sum, elapsed

def start_server():
    """
    Creates a socket, binds to HOST:PORT, and listens for incoming clients.
    Spawns a thread for each connected client.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"[Server] Listening on port {PORT}...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("[Server] Shutting down due to KeyboardInterrupt.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()