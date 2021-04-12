from benchmark import Benchmark
from data import examples
from tools import tools


if __name__ == "__main__":
    bench = Benchmark(
        files=examples,
        tools=tools,
        timeout=(10 * 60),  # 10 minutes
    )

    result = bench.run()
    result.report(directory="results")
