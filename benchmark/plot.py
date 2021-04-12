import matplotlib.pyplot as plt
import matplotlib.style as style
import matplotlib.cm as cm


def scatter(data, xlabel, ylabel, output):
    style.use("seaborn-paper")
    style.use("ggplot")

    palette = [
        "#9861bc",
        "#61bc6d",
        "#6171bc",
        "#bcb061",
        "#61bcbc",
        "#bc9261",
        "#0D160B",
        "#f4f7f5",
        "#2b8c99",
        "#992b5f",
        "#2b9948",
        "#752b99",
        "#93992b",
        "#2b3a99",
        "#995b2b",
    ]

    for i, (label, (xs, ys)) in enumerate(data.items()):
        plt.scatter(
            xs, ys,
            label=label,
            marker=".",
            linewidths=2,
            color=palette[i % len(palette)],
        )

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()

    plt.savefig(output, dpi=150)
    plt.clf()
