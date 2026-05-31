import matplotlib.pyplot as plt

from demo_engine.io import file_op as f_op


def draw_graph():
    import matplotlib

    matplotlib.use("Qt5Agg")
    values = f_op.read_file("rec_data.txt")

    if not values:
        print("No data available to plot.")
        return

    x = list(range(1, len(values) + 1))
    fig = plt.figure(figsize=(8, 5))
    plt.plot(x, values, marker="o", linestyle="-", color="b")
    plt.xlabel("code generation")
    plt.ylabel("code accuracy")
    plt.title("code accuracy change over generation")
    plt.grid(True)

    f_op.save_graph(fig)
    plt.show()


if __name__ == "__main__":
    draw_graph()
