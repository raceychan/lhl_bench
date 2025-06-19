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

import logging
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

from .data_manager import (
    FRAMEWORKS,
    BenchmarkConfig,
    BenchmarkResults,
    DataManager,
    FrameWorkConfig,
    FrameworkResult,
    NonASGIConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initialize data manager
project_root = Path(__file__).parent
DATA_MANAGER = DataManager(project_root, "tests", "benchmark_results.json", "test.json")


class BenchmarkRunner:
    def __init__(self, data_manager: DataManager):
        self.results: dict[str, BenchmarkResults] = {}
        self.data_manager = data_manager
        self.project_root = data_manager.project_root
    
    @property
    def benchmarks(self) -> list[BenchmarkConfig]:
        """Get benchmark configurations."""
        return self.data_manager.benchmarks
    
    @property
    def script_paths(self) -> dict[str, str]:
        """Get script paths."""
        return self.data_manager.script_paths

    def run_wrk_benchmark(self, benchmark_config: BenchmarkConfig) -> Optional[float]:
        """Run wrk benchmark and extract RPS."""
        # Get the generated script path for this test
        test_name = benchmark_config.bench_name
        script_path = self.script_paths[test_name]

        cmd = benchmark_config.wrk_command(script_path)

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
        for benchmark_config in self.benchmarks:
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
                self.data_manager.update_benchmark_results(benchmark_name, benchmark_results)

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


def main():
    """Main entry point for the benchmark script."""
    runner = BenchmarkRunner(DATA_MANAGER)
    runner.run_all_benchmarks()


if __name__ == "__main__":
    main()
