import sys
from dataclasses import dataclass
from tempfile import TemporaryFile
from typing import List, Union

from tools import Tool
from results import BenchmarkResult, RunError, RunResult


@dataclass
class Benchmark:
    files: List[str]
    tools: List[Tool]
    timeout: float

    def single_run(
        self,
        tool: Tool,
        file: str,
        level: int,
        check_output: bool,
    ) -> RunResult:
        with open(file, "rb") as original:
            original.seek(0, 2)
            original_size = original.tell()
            original.seek(0)

            with TemporaryFile("wb") as compressed:
                compression_time = tool.compress(original, compressed, level, self.timeout)
                compressed_size = compressed.tell()
                compressed.seek(0)

                with TemporaryFile("wb") as decompressed:
                    decompression_time = tool.decompress(compressed, decompressed, self.timeout)
                    decompressed_size = decompressed.tell()

                    assert original_size == decompressed_size, "decompressed size is not equal to original size"

                    return RunResult(
                        tool=tool,
                        file=file,
                        level=level,

                        compression_time=compression_time,
                        decompression_time=decompression_time,
                        original_size=original_size,
                        compressed_size=compressed_size,
                    )

    def protected_single_run(
        self,
        tool: Tool,
        file: str,
        level: int,
        check_output: bool,
    ) -> Union[RunResult, RunError]:
        try:
            print(f"[{tool.identity()} ({level})]: {file}")
            sys.stdout.flush()
            return self.single_run(tool, file, level, check_output)
        except Exception as exception:
            return RunError(tool, file, level, exception)

    def run_file(self, file: str):
        for tool in self.tools:
            for level in tool.compression_levels:
                yield self.protected_single_run(tool, file, level=level, check_output=True)

    def run(self) -> BenchmarkResult:
        return BenchmarkResult(
            tools=self.tools,
            files=self.files,
            runs=[
                run
                for file in self.files
                for run in self.run_file(file)
            ],
        )
