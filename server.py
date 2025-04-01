import socket
import threading
import json

def handle_device(conn, addr):
    """
    Handle communication with a connected device.
    """
    try:
        # Receive device info
        data = conn.recv(1024).decode('utf-8')
        device_info = json.loads(data)
        device_id = device_info['device_id']
        print(f"Device {device_id} connected from {addr}")
        print(f"Device specs: {device_info['specs']}")

        # Define the GPU-intensive task
        task_code = """
import tensorflow as tf

# Check for GPU availability
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        # Explicitly place computation on the first GPU
        with tf.device('/GPU:0'):
            # Define two matrices
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]], dtype=tf.float32)
            b = tf.constant([[1.0, 1.0], [0.0, 1.0]], dtype=tf.float32)
            # Perform matrix multiplication
            c = tf.matmul(a, b)
            print("GPU is available")
            print("Matrix A:\\n", a.numpy())
            print("Matrix B:\\n", b.numpy())
            print("Matrix multiplication result (A * B):\\n", c.numpy())
    except RuntimeError as e:
        print(f"GPU computation failed: {e}")
else:
    print("No GPU available")
"""

        # Package the task as JSON
        task = {
            "type": "run_python",
            "code": task_code.strip()
        }

        # Send the task to the device
        conn.send(json.dumps(task).encode('utf-8'))
        print(f"Sent task to {device_id}")

        # Receive the result
        result = conn.recv(4096).decode('utf-8')  # Increased buffer for larger output
        print(f"Result from {device_id}:\n{result}")

    except Exception as e:
        print(f"Error handling device {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {device_id} closed")

def start_server():
    """
    Start the server to listen for device connections.
    """
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind to all interfaces on port 5000
        s.bind(('0.0.0.0', 5000))
        s.listen()
        print("Server started, listening on port 5000...")

        # Accept connections indefinitely
        while True:
            conn, addr = s.accept()
            print(f"New connection from {addr}")
            # Handle each device in a separate thread
            thread = threading.Thread(target=handle_device, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
