#!/usr/bin/env python3
"""
CLI interface for Python ASGI web framework benchmarking.

Usage:
    python -m bench                    # Run all benchmarks
    python -m bench fastapi             # Run specific framework
    python -m bench --test=complex      # Run specific test on all frameworks
    python -m bench fastapi --test=complex  # Run specific test on specific framework
"""

import argparse
import sys

from bench.auto_bench import BenchmarkRunner, DATA_MANAGER, logger
from bench.data_manager import FRAMEWORKS


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the benchmark CLI."""
    parser = argparse.ArgumentParser(
        prog="bench",
        description="Benchmark Python ASGI web frameworks using wrk",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m bench                      Run all frameworks with all tests
  python -m bench lihil              Run Lihil with all tests  
  python -m bench --test=complex       Run all frameworks with complex test
  python -m bench lihil --test=complex  Run Lihil with complex test

Available frameworks: """
        + ", ".join(sorted(FRAMEWORKS.keys()))
        + """
Available tests: """
        + ", ".join([b.bench_name for b in DATA_MANAGER.benchmarks]),
    )

    # Optional positional argument for framework
    parser.add_argument(
        "framework",
        nargs="?",
        help="Framework to benchmark (optional). If not provided, runs all frameworks.",
        choices=list(FRAMEWORKS.keys()),
        metavar="FRAMEWORK",
    )

    # Optional keyword argument for test
    parser.add_argument(
        "--test",
        choices=[b.bench_name for b in DATA_MANAGER.benchmarks],
        help="Specific test to run (optional). If not provided, runs all tests.",
        metavar="TEST",
    )

    # Optional arguments for customization
    parser.add_argument(
        "--list-frameworks",
        action="store_true",
        help="List all available frameworks and exit",
    )

    parser.add_argument(
        "--list-tests", action="store_true", help="List all available tests and exit"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle list options
    if args.list_frameworks:
        print("Available frameworks:")
        for framework_key in sorted(FRAMEWORKS.keys()):
            framework_config = FRAMEWORKS[framework_key]
            print(f"  {framework_key:<12} - {framework_config.name}")
        return

    if args.list_tests:
        print("Available tests:")
        for benchmark in DATA_MANAGER.benchmarks:
            print(f"  {benchmark.bench_name}")
        return

    # Set up logging level
    if args.verbose:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    # Create benchmark runner
    runner = BenchmarkRunner(DATA_MANAGER)

    # Determine what to run
    if args.framework and args.test:
        # Run specific framework with specific test
        logger.info(f"Running {args.framework} with {args.test} test")
        # Find the benchmark config
        benchmark_config = next((b for b in DATA_MANAGER.benchmarks if b.bench_name == args.test), None)
        if benchmark_config:
            rps = runner.benchmark_framework(args.framework, benchmark_config)
            if rps:
                logger.info(f"Result: {rps:.2f} RPS")
            else:
                logger.error("Benchmark failed")
                sys.exit(1)
        else:
            logger.error(f"Test '{args.test}' not found")
            sys.exit(1)

    elif args.framework:
        # Run specific framework with all tests
        logger.info(f"Running {args.framework} with all tests")
        for benchmark_config in DATA_MANAGER.benchmarks:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running {benchmark_config.bench_name} test on {args.framework}")
            logger.info(f"{'='*50}")

            rps = runner.benchmark_framework(args.framework, benchmark_config)
            if rps:
                logger.info(f" {benchmark_config.bench_name}: {rps:.2f} RPS")
            else:
                logger.warning(f" {benchmark_config.bench_name}: Failed")

    elif args.test:
        # Run all frameworks with specific test
        logger.info(f"Running all frameworks with {args.test} test")

        # Find the benchmark config
        benchmark_config = next((b for b in DATA_MANAGER.benchmarks if b.bench_name == args.test), None)
        if not benchmark_config:
            logger.error(f"Test '{args.test}' not found")
            sys.exit(1)

        framework_results = []
        for framework_key in FRAMEWORKS.keys():
            rps = runner.benchmark_framework(framework_key, benchmark_config)
            framework_config = FRAMEWORKS[framework_key]
            if rps is not None:
                framework_results.append((framework_config.name, rps))
                logger.info(f"✓ {framework_config.name}: {rps:.2f} RPS")
            else:
                logger.warning(f"✗ {framework_config.name}: Failed")

        # Show sorted results
        if framework_results:
            logger.info(f"\n{args.test.capitalize()} test results (sorted by RPS):")
            framework_results.sort(key=lambda x: x[1], reverse=True)
            for framework, rps in framework_results:
                logger.info(f"  {framework}: {rps:.2f} RPS")

    else:
        # Run all frameworks with all tests (default behavior)
        logger.info("Running all benchmarks")
        runner.run_all_benchmarks()


if __name__ == "__main__":
    main()
