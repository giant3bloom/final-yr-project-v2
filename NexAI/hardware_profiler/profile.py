import json
import socket

import psutil

from config import STATUS_HOST, PROFILER_PORT


def send_system_data(host=STATUS_HOST, port=PROFILER_PORT):
    """Collect system metrics and send them as JSON over the network."""
    output_data = {
        "ball_position": {"x": 0, "y": 0},
        "possible_moves": ["up", "down", "left", "right"],
        "cpu_usage_percent": psutil.cpu_percent(interval=1),
        "memory_usage_percent": psutil.virtual_memory().percent,
    }

    json_string = json.dumps(output_data)
    print(json_string)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            sock.connect((host, port))
            sock.sendall(json_string.encode())
            print("✅ Profiler data sent successfully!")
    except OSError:
        pass  # no profiler listener running — expected during local runs


if __name__ == "__main__":
    send_system_data()
