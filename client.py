import socket
import json
import subprocess
import tempfile
import os

# Device-specific information (customize as needed)
device_id = "device_1"
specs = {
    "cpu": "4 cores",
    "memory": "16GB",
    "gpu": "NVIDIA GTX 1660"  # Replace with actual GPU if known
}

def run_task(task):
    """
    Execute the received task and return the output.
    """
    if task['type'] != "run_python":
        return "Error: Unknown task type"

    code = task['code']

    # Create a temporary file for the Python code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name

    try:
        # Execute the script and capture output
        result = subprocess.run(
            ['python', temp_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
    except subprocess.CalledProcessError as e:
        output = f"Execution failed:\n{e.output}\n{e.stderr}"
    except Exception as e:
        output = f"Error running task: {e}"
    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

    return output

def connect_to_server():
    """
    Connect to the server and process tasks.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server (replace 'localhost' with server IP if remote)
        server_address = ('localhost', 5000)
        s.connect(server_address)
        print(f"Connected to server at {server_address}")

        # Send device info
        device_info = {"device_id": device_id, "specs": specs}
        s.send(json.dumps(device_info).encode('utf-8'))
        print("Sent device info to server")

        # Receive the task
        task_data = s.recv(1024).decode('utf-8')
        task = json.loads(task_data)
        print("Received task from server")
 
        # Execute the task and get the result
        result = run_task(task)
        print("Task executed, sending result back")

        # Send the result back to the server
        s.send(result.encode('utf-8'))
        print("Result sent, closing connection")

if __name__ == "__main__":
    try:
        connect_to_server()
    except Exception as e:
        print(f"Failed to connect or process task: {e}")
