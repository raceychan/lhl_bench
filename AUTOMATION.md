# Automated Benchmarking

This repository now includes fully automated benchmarking capabilities.

## Quick Start

### Run all framework benchmarks automatically:
```bash
make auto-bench
# OR
python auto_bench.py
```

### Run a single framework benchmark:
```bash
make bench-single FRAMEWORK=lhl
# OR  
python auto_bench.py lhl
```

Available frameworks: `lhl`, `ls`, `fa`, `slt`, `bs`, `rb`

## What it does

The automation script:

1. **Starts each framework server** - Uses the same commands as the Makefile
2. **Runs wrk benchmark** - Uses the same wrk command with post.lua script
3. **Extracts RPS values** - Parses wrk output automatically 
4. **Updates results** - Modifies `make_graph.py` with new benchmark data
5. **Generates graphs** - Creates updated PNG files in `./assets/`

## Output

- Results are automatically saved to `make_graph.py`
- Updated graphs are generated in `./assets/` 
- Console shows RPS for each framework

## Manual workflow (old way)
```bash
# 1. Start server
make lhl

# 2. In another terminal, run benchmark  
cd ~/myprojects/wrk
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua

# 3. Manually update make_graph.py with results
# 4. Generate graphs
make graph
```

## Automated workflow (new way)
```bash
make auto-bench
```

That's it! 🚀