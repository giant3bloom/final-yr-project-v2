import os
from datetime import datetime

from config import GRAPHS_DIR, RESULTS_DIR, ensure_output_dirs


def save_as_file(data):
    ensure_output_dirs()
    file_path = RESULTS_DIR / "rec_data.txt"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    else:
        content = ""

    if content:
        content += ", " + str(data)
    else:
        content = str(data)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content + "\n")

    print(f"Data appended as comma-separated values to {file_path}")


def read_file(filename="rec_data.txt"):
    file_path = RESULTS_DIR / filename

    with open(file_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        if line:
            return [float(x.strip()) for x in line.split(",")]
        return []


def save_graph(fig, output_dir=None, prefix="line_graph"):
    ensure_output_dirs()
    output_dir = output_dir or GRAPHS_DIR
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(output_dir, f"{prefix}_{timestamp}.png")
    fig.savefig(save_path)
    print(f"Graph saved at {save_path}")


if __name__ == "__main__":
    for data in range(10):
        save_as_file(data)
    print(read_file("rec_data.txt"))
