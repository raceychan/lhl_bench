# Ping

Test a get request with path `ping` with text response `pong`

## Lihil

### source code

```python
app.static("/ping", "pong")
```

### Result
```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.13ms  227.40us  17.31ms   94.15%
    Req/Sec    14.28k     1.65k   31.32k    90.00%
  568144 requests in 10.08s, 74.23MB read
Requests/sec:  56359.57
Transfer/sec:      7.36MB
```

## Blacksheep


### Source code

```bash
@get("/ping")
async def pong():
    return Response(status=200, content=TextContent("pong"))
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.28ms    1.10ms  52.17ms   99.36%
    Req/Sec    12.92k     1.51k   34.21k    90.27%
  515406 requests in 10.10s, 67.34MB read
Requests/sec:  51031.89
Transfer/sec:      6.67MB
```

## Starlette

### source code

```python
async def ping(r: Request):
    return PlainTextResponse("pong")
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.46ms    1.32ms  60.98ms   99.43%
    Req/Sec    11.40k     1.03k   26.58k    86.53%
  454862 requests in 10.10s, 59.43MB read
Requests/sec:  45039.65
Transfer/sec:      5.88MB
```


## litestar

### Source

```python
@get("/ping")
async def ping() -> Literal["pong"]:
    return "pong"
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     1.88ms    1.06ms  60.79ms   96.80%
    Req/Sec     8.72k   564.72    13.39k    77.50%
  347119 requests in 10.05s, 42.37MB read
Requests/sec:  34523.74
Transfer/sec:      4.21MB
```

## FastAPI

### Source code

```python
@ping_route.get("/ping")
async def ping():
    return PlainTextResponse("pong")
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.30ms    4.05ms  93.26ms   99.20%
    Req/Sec     7.97k   801.00    14.12k    91.75%
  317395 requests in 10.06s, 41.47MB read
Requests/sec:  31539.92
Transfer/sec:      4.12MB
```

## Robyn

### Source Code

```python
@app.get("/ping")
async def ping():
    return "pong"
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/ping'
Running 10s test @ http://localhost:8000/ping
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     3.27ms    3.92ms 114.97ms   99.46%
    Req/Sec     5.27k   608.97    14.46k    98.00%
  209966 requests in 10.06s, 21.03MB read
Requests/sec:  20874.14
Transfer/sec:      2.09MB
```


