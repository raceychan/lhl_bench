#!/usr/bin/env python3

"""
Automated benchmarking script for Python ASGI web frameworks.

This script:
1. Starts each web framework server
2. Runs wrk benchmark against it
3. Parses the results and extracts RPS
4. Updates the results in make_graph.py
5. Generates updated graphs
"""

import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

from msgspec import Struct
from msgspec.json import decode, encode
from msgspec.structs import asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ASGI compatible frameworks
ASGI_FRAMEWORKS = ["Lihil", "Starlette", "FastAPI", "Litestar", "Blacksheep", "Sanic"]

# Non-ASGI frameworks with custom commands
NON_ASGI_FRAMEWORKS = {"Robyn": ["uv", "run", "python", "-m", "src.robyn"]}


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


class NonASGIConfig(Base):
    name: str
    command: list[str]
    port: int = 8000


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

    def generate_lua_script(self, tests_dir: Path) -> Path:
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

        script_path = tests_dir / self.script_name

        # Generate and write script
        with open(script_path, "w") as f:
            f.write(content)
        return script_path

    @classmethod
    def from_file(cls, config_file: Path) -> list["BenchmarkConfig"]:
        # Benchmark configurations
        """Load test configurations from test.json file."""

        with open(config_file, "r") as f:
            test_data = f.read()

        configs = decode(test_data, type=list[BenchmarkConfig], strict=False)
        return configs


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
        name.lower(): NonASGIConfig(name=name, command=command)
        for name, command in NON_ASGI_FRAMEWORKS.items()
    },
}


def generate_lua_scripts(configs: list[BenchmarkConfig]) -> dict[str, str]:
    """Generate Lua scripts for all test configurations."""
    tests_dir = Path(__file__).parent / "tests"
    script_paths = {}

    for config in configs:

        script_path = config.generate_lua_script(tests_dir)
        script_paths[config.bench_name] = str(script_path)
        logger.info(f"Generated {script_path} for {config.bench_name} test")

    return script_paths


# Load benchmark configurations from test.json
TESTS_DIR = Path(__file__).parent / "tests"
TEST_FILE = TESTS_DIR / "test.json"

BENCHMARKS = BenchmarkConfig.from_file(TEST_FILE)
SCRIPT_PATHS = generate_lua_scripts(BENCHMARKS)


class BenchmarkRunner:
    def __init__(self):
        self.results: dict[str, BenchmarkResults] = {}
        self.project_root = Path(__file__).parent

    def run_wrk_benchmark(self, benchmark_config: BenchmarkConfig) -> Optional[float]:
        """Run wrk benchmark and extract RPS."""
        # Get the generated script path for this test
        test_name = benchmark_config.bench_name
        script_path = SCRIPT_PATHS[test_name]

        cmd = [
            "wrk",
            f"-t{benchmark_config.threads}",
            f"-c{benchmark_config.connections}",
            f"-d{benchmark_config.duration}",
            benchmark_config.url,
            "-s",
            script_path,
        ]

        try:
            logger.info(f"Running benchmark: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

            if result.returncode != 0:
                logger.error(f"wrk failed: {result.stderr}")
                return None

            # Parse RPS from output
            rps_match = re.search(r"Requests/sec:\s+(\d+\.?\d*)", result.stdout)
            if rps_match:
                rps = float(rps_match.group(1))
                logger.info(f"Extracted RPS: {rps}")
                return rps
            else:
                logger.error("Could not extract RPS from wrk output")
                logger.debug(f"Output: {result.stdout}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("wrk benchmark timed out")
            return None
        except Exception as e:
            logger.error(f"Error running wrk: {e}")
            return None

    def start_server(
        self, config: FrameWorkConfig | NonASGIConfig
    ) -> Optional[subprocess.Popen]:
        """Start a web framework server."""
        try:
            logger.info(f"Starting {config.name} server...")
            process = subprocess.Popen(
                config.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_root,
            )
            # Give server time to start
            time.sleep(3)

            # Check if server is running
            if process.poll() is not None:
                _, stderr = process.communicate()
                logger.error(f"Server failed to start: {stderr.decode()}")
                return None

            return process
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return None

    def stop_server(self, process: subprocess.Popen):
        """Stop a server process."""
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()

    def benchmark_framework(
        self, framework_key: str, benchmark_config: BenchmarkConfig
    ) -> Optional[float]:
        """Benchmark a single framework."""
        config = FRAMEWORKS[framework_key]

        logger.info(f"\n{'='*50}")
        logger.info(f"Benchmarking {config.name} ({framework_key})")
        logger.info(f"{'='*50}")

        # Start server
        server_process = self.start_server(config)
        if not server_process:
            return None

        try:
            # Run benchmark
            rps = self.run_wrk_benchmark(benchmark_config)
            return rps
        finally:
            # Always stop server
            self.stop_server(server_process)
            time.sleep(2)  # Cool down period

    def update_results_file(self, benchmark_name: str, results: BenchmarkResults):
        """Update benchmark_results.json with new results."""
        results_path = self.project_root / "benchmark_results.json"

        try:
            # Load existing results
            if results_path.exists():
                with open(results_path, "r") as f:

                    all_results = json.load(f)
            else:
                all_results = {}

            # Update results for this benchmark
            all_results[benchmark_name] = results

            # Save back to file
            with open(results_path, "w") as f:
                json.dump(all_results, f, indent=2)

            logger.info(f"Updated {benchmark_name} results in benchmark_results.json")

        except Exception as e:
            logger.error(f"Error updating results file: {e}")

    def generate_graphs(self):
        """Generate updated graphs."""
        try:
            subprocess.run(
                ["uv", "run", "python", "make_graph.py"],
                cwd=self.project_root,
                check=True,
            )
            logger.info("Generated updated graphs in ./assets/")
        except Exception as e:
            logger.error(f"Error generating graphs: {e}")

    def run_all_benchmarks(self):
        """Run benchmarks for all frameworks."""
        for benchmark_config in BENCHMARKS:
            benchmark_name = benchmark_config.bench_name
            logger.info(f"\n{'='*60}")
            logger.info(f"Running {benchmark_name.upper()} benchmark suite")
            logger.info(f"{'='*60}")

            framework_results = []

            for framework_key in FRAMEWORKS.keys():
                rps = self.benchmark_framework(framework_key, benchmark_config)
                framework_config = FRAMEWORKS[framework_key]
                if rps is not None:
                    framework_results.append(
                        FrameworkResult(framework=framework_config.name, rps=rps)
                    )
                    logger.info(f"✓ {framework_config.name}: {rps:.2f} RPS")
                else:
                    logger.warning(f"✗ {framework_config.name}: Failed")

            if framework_results:
                benchmark_results = BenchmarkResults(
                    benchmark_name=benchmark_name, results=framework_results
                )
                self.results[benchmark_name] = benchmark_results
                self.update_results_file(benchmark_name, benchmark_results)

            logger.info(f"\n{benchmark_name.capitalize()} benchmark results:")
            # Sort by RPS descending
            sorted_results = sorted(
                framework_results, key=lambda x: x.rps, reverse=True
            )
            for result in sorted_results:
                logger.info(f"  {result.framework}: {result.rps:.2f} RPS")

        # Generate graphs with all results
        if self.results:
            self.generate_graphs()
            logger.info(f"\n{'='*60}")
            logger.info("✓ Benchmarking complete! Check ./assets/ for updated graphs.")
            logger.info(f"{'='*60}")
