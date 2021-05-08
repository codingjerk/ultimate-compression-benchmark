from dataclasses import dataclass
from pathlib import Path
from typing import Any, IO, List, Optional
import re
import subprocess
import time


@dataclass
class Tool:
    name: str
    binary: str
    compression_levels: List[int]
    version_arguments: List[str]
    compression_arguments: List[str]
    decompression_arguments: List[str]

    def identity(self) -> str:
        result = self.name
        if version := self.gather_version():
            result += f" v{version}"

        return result

    def exists(self) -> bool:
        return Path(self.binary).exists()

    def gather_version(self) -> Optional[str]:
        try:
            output = subprocess.check_output([self.binary] + self.version_arguments, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
        except Exception:
            return None

        matches = re.findall(r"((\d+\.\d+)(\.\d+)?)", output)

        if len(matches) == 0:
            return None

        if len(matches[0]) == 0:
            return None

        return matches[0][0]

    def compress(self, source: IO[Any], destination: IO[Any], level: int, timeout: float) -> float:
        return self.timed_run([self.binary] + self.format_arguments(self.compression_arguments, level), source, destination, timeout)

    def decompress(self, source: IO[Any], destination: IO[Any], timeout: float) -> float:
        return self.timed_run([self.binary] + self.decompression_arguments, source, destination, timeout)

    def timed_run(self, command: List[str], stdin: IO[Any], stdout: IO[Any], timeout: float) -> float:
        start_time = time.time()
        process = subprocess.Popen(command, stdin=stdin, stdout=stdout)
        process.wait(timeout=timeout)
        end_time = time.time()

        stdout.flush()

        return end_time - start_time

    def format_arguments(self, arguments, level) -> List[str]:
        return [
            arg.format(level=level)
            for arg in arguments
        ]


def lrange(from_value: int, to_value: int) -> List[int]:
    """
    Returns list of numbers in range [`from_value`, `to_value`]
    """

    return list(range(from_value, to_value + 1))


tools = [
    Tool(
        "cat",
        "/usr/bin/cat",
        [0],
        ["--version"],
        [],
        []
    ),
    Tool(
        "brotli",
        "/usr/bin/brotli",
        lrange(0, 11),
        ["--version"],
        ["--quality={level}"],
        ["-d"]
    ),
    Tool(
        "brotli (long)",
        "/usr/bin/brotli",
        lrange(0, 11),
        ["--version"],
        ["--quality={level}", "--lgwin=24"],
        ["-d"]
    ),
    Tool(
        "bzip2",
        "/usr/bin/bzip2",
        lrange(1, 9),
        ["--version", "--help"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "gzip",
        "/usr/bin/gzip",
        lrange(1, 9),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "lizard",
        "/usr/bin/lizard",
        lrange(10, 49),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "lz4",
        "/usr/bin/lz4",
        lrange(1, 12),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "lzf",
        "/usr/bin/lzf",
        lrange(1, 12),
        ["--help"],
        [],
        ["-d"]
    ),
    Tool(
        "lzma",
        "/usr/bin/lzma",
        lrange(1, 9),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "lzop",
        "/usr/bin/lzop",
        lrange(1, 9),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "lzturbo",
        "/usr/bin/lzturbo",
        [10, 11, 12, 19, 20, 21, 22, 29, 30, 31, 32, 39, 49],
        ["--help"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "xz",
        "/usr/bin/xz",
        lrange(1, 9),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "zstd",
        "/usr/bin/zstd",
        lrange(1, 19),
        ["--version"],
        ["-{level}"],
        ["-d"]
    ),
    Tool(
        "zstd (long)",
        "/usr/bin/zstd",
        lrange(1, 19),
        ["--version"],
        ["-{level}", "--long"],
        ["-d"]
    ),
    Tool(
        "zstd (ultra)",
        "/usr/bin/zstd",
        lrange(1, 22),
        ["--version"],
        ["-{level}", "--long", "--ultra"],
        ["-d"]
    ),
    Tool(
        "zstd (fast)",
        "/usr/bin/zstd",
        lrange(1, 19) + [50, 100, 1000],
        ["--version"],
        ["--fast={level}"],
        ["-d"]
    ),
]
