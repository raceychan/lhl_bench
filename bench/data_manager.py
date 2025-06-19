#!/usr/bin/env python3

"""
Data management module for benchmarking operations.

This module handles all file I/O operations including:
- Reading and writing JSON files
- Loading benchmark configurations
- Managing benchmark results
- Generating Lua scripts
"""

import json
import logging
from pathlib import Path
from typing import Any

from msgspec import Struct
from msgspec.json import decode, encode
from msgspec.structs import asdict

logger = logging.getLogger(__name__)

# ASGI compatible frameworks
ASGI_FRAMEWORKS = ["Lihil", "Starlette", "FastAPI", "Litestar", "Blacksheep", "Sanic"]

# Non-ASGI frameworks with custom commands
NON_ASGI_FRAMEWORKS = ["Robyn"]


class Base(Struct):
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FrameWorkConfig(Base):
    name: str  # e.g. FastAPI
    port: int = 8000

    @property
    def command(self) -> list[str]:
        return [
            "uv",
            "run",
            "uvicorn",
            f"src.{self.name.lower()}:app",
            "--interface",
            "asgi3",
            "--http",
            "httptools",
            "--no-access-log",
            "--log-level",
            "warning",
            "--port",
            str(self.port),
        ]


class NonASGIConfig(FrameWorkConfig):
    @property
    def command(self) -> list[str]:
        return ["uv", "run", "python", "-m", f"src.{self.name.lower()}"]


class FrameworkResult(Base):
    framework: str
    rps: float


class BenchmarkResults(Base):
    benchmark_name: str
    results: list[FrameworkResult]

    def to_dict_by_framework(self) -> dict[str, float]:
        """Convert to dict format for JSON serialization."""
        return {result.framework: result.rps for result in self.results}


# Framework configurations using structured data
FRAMEWORKS: dict[str, FrameWorkConfig | NonASGIConfig] = {
    **{
        framework.lower(): FrameWorkConfig(name=framework)
        for framework in ASGI_FRAMEWORKS
    },
    **{
        name.lower(): NonASGIConfig(
            name=name,
        )
        for name in NON_ASGI_FRAMEWORKS
    },
}


class BenchmarkConfig(Base):
    bench_name: str
    method: str
    url: str
    data: dict[str, Any] | None = None
    threads: int = 4
    connections: int = 64
    duration: str = "10s"

    @property
    def script_name(self) -> str:
        """Generate script filename based on test name and method."""
        return f"{self.bench_name}_{self.method.lower()}.lua"

    def wrk_command(self, script_path: str) -> list[str]:
        """Generate wrk command for this benchmark configuration."""
        return [
            "wrk",
            f"-t{self.threads}",
            f"-c{self.connections}",
            f"-d{self.duration}",
            self.url,
            "-s",
            script_path,
        ]

    def generate_lua_script(self, data_manager: "DataManager") -> Path:
        """Generate wrk Lua script content based on config."""
        script_lines = []

        # Set HTTP method
        script_lines.append(f'wrk.method = "{self.method}"')

        # Set body data if provided
        if self.data:
            body_json = encode(self.data).decode()
            script_lines.append(f"wrk.body = '{body_json}'")
            script_lines.append('wrk.headers["Content-Type"] = "application/json"')

        content = "\n".join(script_lines)
        script_path = data_manager.tests_dir / self.script_name

        with open(script_path, "w") as f:
            f.write(content)
        return script_path

    @classmethod
    def generate_lua_scripts(
        cls, data_manager: "DataManager", configs: list["BenchmarkConfig"]
    ) -> dict[str, str]:
        """Generate Lua scripts for all test configurations."""
        script_paths = {}

        for config in configs:
            script_path = config.generate_lua_script(data_manager)
            script_paths[config.bench_name] = str(script_path)
            logger.info(f"Generated {script_path} for {config.bench_name} test")

        return script_paths


class DataManager:
    """Handles all file I/O operations for benchmarking."""

    def __init__(
        self, project_root: Path, test_dir: str, result_file: str, test_file: str
    ):
        self.project_root = project_root
        self.tests_dir = project_root / test_dir
        self.results_path = project_root / result_file
        self.test_file = self.tests_dir / test_file

        # Load data eagerly during initialization
        self.benchmarks = self.load_benchmark_configs()
        self.script_paths = BenchmarkConfig.generate_lua_scripts(self, self.benchmarks)

    def load_benchmark_configs(self, config_file: Path | None = None) -> list[Any]:
        """Load benchmark configurations from JSON file."""
        if config_file is None:
            config_file = self.test_file

        with open(config_file, "r") as f:
            test_data = f.read()

        return decode(test_data, type=list[BenchmarkConfig], strict=False)

    def update_benchmark_results(
        self, benchmark_name: str, results: "BenchmarkResults"
    ) -> None:
        """Update benchmark results for a specific benchmark."""
        try:
            # Load existing results
            with open(self.results_path, "r") as f:
                data = f.read()

            all_results = decode(data, type=dict[str, BenchmarkResults])
            all_results[benchmark_name] = results

            with open(self.results_path, "w") as f:
                f.write(encode(all_results).decode())

            # Save back to file
            logger.info(f"Updated {benchmark_name} results in benchmark_results.json")

        except Exception as e:
            logger.error(f"Error updating results file: {e}")
