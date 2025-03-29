## TLDR

### Test a post request with path, query, body param, and a dependency

![res](/assets/bench_complex.png)

[check details here](/bench_results/test_complex.md)

### Test a get request with only static path param and return a static text response

![res](/assets/bench_ping.png)

[check details here](/bench_results/test_ping.md)

## Context

### Hardware

- CPU:
 AMD Ryzen 9 7950X 16-Core Processor 4.50 GHz

- RAM 
64.0 GB (63.1 GB usable)

- internet ethernet controller i225v

### OS
Ubuntu 20.04.6 LTS
packages

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
