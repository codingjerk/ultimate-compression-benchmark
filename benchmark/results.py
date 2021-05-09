import os
from collections import defaultdict
from dataclasses import dataclass
from textwrap import dedent
from typing import List, Union

from tabulate import tabulate

import plot
from tools import Tool


@dataclass
class RunResult:
    tool: Tool
    file: str
    level: int

    compression_time: float
    decompression_time: float
    original_size: int
    compressed_size: int

    is_ok: bool = True

    def ratio(self) -> float:
        return self.original_size / max(self.compressed_size, 1)


@dataclass
class RunError:
    tool: Tool
    file: str
    level: int

    reason: Exception

    is_ok: bool = False


@dataclass
class BenchmarkResult:
    tools: List[Tool]
    files: List[str]
    runs: List[Union[RunResult, RunError]]

    def print_table(self) -> None:
        data = []
        for result in self.runs:
            if result.is_ok:
                data.append([
                    f"{result.tool.name} (v{result.tool.gather_version()}) (level {result.level})",
                    int(result.compressed_size / max(result.original_size, 1) * 1000),
                    int(result.compression_time * 1000),
                    int(result.decompression_time * 1000),
                    "Ok",
                ])
            else:
                data.append([
                    f"{result.tool.name} (v{result.tool.gather_version()}) (level {result.level})",
                    "-",
                    "-",
                    "-",
                    result.reason,
                ])

        print(tabulate(data, headers=["Tool", "RT", "CT", "DT", "Result"]))

    def as_table(self, file: str) -> str:
        data = []
        for result in self.runs:
            if result.file != file:
                continue

            if result.is_ok:
                data.append([
                    f"{result.tool.name} (v{result.tool.gather_version()}) (level {result.level})",
                    result.compressed_size,
                    int(result.compression_time * 1000),
                    int(result.decompression_time * 1000),
                    "Ok",
                ])
            else:
                data.append([
                    f"{result.tool.name} (v{result.tool.gather_version()}) (level {result.level})",
                    "-",
                    "-",
                    "-",
                    result.reason,
                ])

        return tabulate(data, headers=["Tool", "CS", "CT", "DT", "Result"])

    def plot_time_to_ratio(self, file, output) -> None:
        tools = defaultdict(lambda: ([], []))
        for run in self.runs:
            if run.file != file: continue
            if not run.is_ok: continue

            tools[run.tool.identity()][0].append(run.compression_time)
            tools[run.tool.identity()][1].append(run.ratio())

        plot.scatter(
            data=tools,
            xlabel="Compression time",
            ylabel="Compression ratio",
            output=output,
        )

    def plot_time_to_time(self, file, output) -> None:
        tools = defaultdict(lambda: ([], []))
        for run in self.runs:
            if run.file != file: continue
            if not run.is_ok: continue

            tools[run.tool.identity()][0].append(run.compression_time)
            tools[run.tool.identity()][1].append(run.decompression_time)

        plot.scatter(
            data=tools,
            xlabel="Compression time",
            ylabel="Decompression time",
            output=output,
        )

    def report(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)

        result  = "# Ultimate compression benchmark results\n"
        result += "\n## Benchmarked tools\n\n"

        for tool in self.tools:
            result += f"* {tool.identity()}\n"

        result += "\n## Datasets\n\n"
        for file in self.files:
            result += f"* {file}\n"

        for file in self.files:
            result += f"\n## Results for `{file}`\n"
            result += "\n### Table\n\n"
            result += "| Tool | Compression level | Compressed size (kB) | Compression time (s) | Decompression time (s) |\n"
            result += "| --- | --- | --- | --- | --- |\n"

            for run in self.runs:
                if run.file != file: continue
                if not run.is_ok: continue

                result += "| {} | {} | {} | {} | {} |\n".format(
                    run.tool.identity(),
                    run.level if run.level is not None else "—",
                    "{:.2f}".format(run.compressed_size / 1024),
                    "{:.2f}".format(run.compression_time),
                    "{:.2f}".format(run.decompression_time),
                )

            escaped_name = file.replace("/", "_").replace("\\", "_")

            result += f"\n### Compression time vs compression ratio\n\n"
            plot = os.path.join(directory, f"{escaped_name}_ttr.png")
            self.plot_time_to_ratio(file, plot)
            result += f"![]({escaped_name}_ttr.png)\n"

            result += f"\n### Compression time vs decompression time\n\n"
            plot = os.path.join(directory, f"{escaped_name}_ttt.png")
            self.plot_time_to_time(file, plot)
            result += f"![]({escaped_name}_ttt.png)\n"

        report_path = os.path.join(directory, "report.md")
        with open(report_path, "w") as report:
            report.write(result)

        report_path = os.path.join(directory, "report.txt")
        with open(report_path, "w") as report:
            report.write("# Ultimate compression benchmark\n\n")

            for file in self.files:
                report.write(f"## Results for {file}:\n\n")

                report.write(self.as_table(file))
                report.write("\n\n")
