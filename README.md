# Python ASGI Web Framework Benchmarks

This repository contains an automated micro-benchmarking framework for Python ASGI web frameworks. It automatically runs performance tests, collects results, and generates comparison graphs.

## 🏆 Latest Results

You might see different results in absolute value of RPS on your computer as hardware might differ, but the ranking should stay the same.

### Complex POST Request Test
Tests a POST request with path parameters, query parameters, request body, and dependency injection.

![Complex Test Results](/assets/bench_complex.png)

[View detailed results](/docs/test_complex.md)

### Simple GET Request Test  
Tests a simple GET request with static path and static text response.

![Simple Test Results](/assets/bench_ping.png)

[View detailed results](/docs/test_ping.md)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- [wrk](https://github.com/wg/wrk) HTTP benchmarking tool

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd lhl_bench

# Install dependencies
uv sync
```

### Running Benchmarks

#### Run All Tests on All Frameworks (Recommended)
```bash
# Automatically runs all benchmarks and generates graphs
python -m bench
```

#### Run Specific Framework
```bash
# Test a single framework with all tests
python -m bench fastapi
python -m bench lihil
python -m bench starlette
python -m bench blacksheep
python -m bench litestar
python -m bench robyn
```

#### Run Specific Test
```bash
# Run a single test across all frameworks
python -m bench --test=complex  # POST request test
python -m bench --test=simple   # GET request test
```

#### Run Specific Framework + Test
```bash
# Test specific framework with specific test
python -m bench fastapi --test=complex
python -m bench lihil --test=simple
```

#### Additional Options
```bash
# List all available frameworks
python -m bench --list-frameworks

# List all available tests  
python -m bench --list-tests

# Enable verbose logging
python -m bench --verbose
```

## 🏗️ How It Works

This automated benchmarking framework:

1. **Starts each web framework server** using their optimal configuration
2. **Runs wrk HTTP benchmarks** against standardized endpoints
3. **Collects performance metrics** (requests per second, latency, etc.)
4. **Stores results** in JSON format for historical tracking
5. **Generates comparison graphs** automatically in the `/assets/` directory

### Framework Architecture

```
bench/
├── auto_bench.py      # Main benchmarking automation
├── data_manager.py    # Result storage and configuration
├── models.py          # Data models for benchmarks
├── src/               # Framework implementations
│   ├── fastapi.py
│   ├── lihil.py
│   ├── starlette.py
│   └── ...
└── tests/             # Test configurations and Lua scripts
    ├── test.json      # Test definitions
    ├── complex_post.lua
    └── simple_get.lua
```

### Test Definitions

Tests are defined in `/bench/tests/test.json`:

```json
[
  {
    "bench_name": "complex",
    "method": "POST", 
    "url": "http://localhost:8000/profile/p?q=5",
    "data": {
      "id": 1,
      "name": "user", 
      "email": "user@email.com"
    }
  },
  {
    "bench_name": "simple",
    "method": "GET",
    "url": "http://localhost:8000/health"
  }
]
```

### Adding New Frameworks

1. Create a new implementation in `/bench/src/your_framework.py`
2. Add the framework configuration to `FRAMEWORKS` in `/bench/data_manager.py`
3. Implement the required endpoints matching the test definitions
4. Run the benchmarks to see results

### Adding New Tests

1. Add test definition to `/bench/tests/test.json`
2. Create corresponding Lua script in `/bench/tests/` if needed
3. Implement the endpoints in all framework implementations
4. Run benchmarks to generate results

## PRs are welcome !

It is natural that people would think this benchmark is biased given it is created by the author of lihil, which makes makes PR even more valuable and appreciated.

If you would like to see your test results shown here or if you have better idea for testing/benchmarking, please feel free to submit a PR.

## Context

### OS
Ubuntu 20.04.6 LTS

### packages

- python == 3.12
- uvloop==0.21.0
- httptools==0.6.4
- uvicorn==0.34.0

- lihil==0.1.12
- fastapi==0.115.8
- litestar==2.15.1
- robyn==0.37.0
- blacksheep==2.0.8,
- starlette==0.46.1
