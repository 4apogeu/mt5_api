# MT5-Python Socket Bridge

A socket-based bridge for trading on MetaTrader 5 from Python. Enables cross-platform integration between Python (Linux/Mac) and MT5 (Windows VM).

## Architecture

```
+------------------+          TCP/IP          +------------------+
|  Python Server   | <----------------------> |   MT5 EA Client  |
|  (Linux Host)    |      Port 1111           |  (Windows VM)    |
+------------------+                          +------------------+
```

> **Note**: MQL5 only supports client-side sockets. Python must be the TCP server, MT5 EA connects as client.

## Project Structure

```
mt5_third_parties/
├── mt5_bridge/              # Python package
│   ├── protocol/            # JSON message models & parsing
│   ├── server/              # TCP server & connection handling
│   ├── trading/             # MT5Bridge high-level API
│   ├── timing/              # Latency measurement & analysis
│   ├── ui/                  # Order panel UI (Tkinter)
│   └── main.py              # Entry point
├── mql5/
│   └── Experts/
│       └── MT5SocketClient.mq5   # MT5 Expert Advisor
├── run_panel.py             # Order panel runner
├── test_latency.py          # Latency benchmark script
└── example.py               # Usage example
```

## Quick Start

### 1. Start Python Server (Linux Host)

```bash
cd mt5_third_parties
python -m mt5_bridge.main --host 0.0.0.0 --port 1111
```

### 2. Setup MT5 EA (Windows VM)

1. Copy `mql5/Experts/MT5SocketClient.mq5` to your MT5 `MQL5/Experts/` folder
2. Open MetaEditor and compile the EA
3. In MT5: **Tools > Options > Expert Advisors**
   - Check "Allow WebRequest for listed URL"
   - Add your Python server IP (e.g., `192.168.1.100`)
4. Attach EA to any chart
5. Configure input parameters:
   - `ServerAddress`: Your Python server IP
   - `ServerPort`: 1111 (default)

### 3. Verify Connection

Python server will show:
```
MT5 EA connected from ('192.168.x.x', xxxxx)
```

## Python API Usage

```python
import asyncio
from mt5_bridge import MT5Bridge, Timeframe

async def main():
    bridge = MT5Bridge(host="0.0.0.0", port=1111)
    await bridge.start()

    # Wait for MT5 EA to connect
    await bridge.wait_for_connection(timeout=120)

    # Get account info
    account = await bridge.get_account()
    print(f"Balance: {account.balance}")

    # Get current price
    tick = await bridge.get_tick("EURUSD")
    print(f"EURUSD: Bid={tick.bid}, Ask={tick.ask}")

    # Get historical data
    rates = await bridge.get_rates("EURUSD", Timeframe.H1, 100)
    print(f"Got {len(rates)} candles")

    # Place a buy order
    result = await bridge.buy("EURUSD", 0.01, stop_loss=tick.bid - 0.0050)
    print(f"Order ticket: {result.ticket}")

    # Get open positions
    positions = await bridge.get_positions()
    for pos in positions:
        print(f"{pos.symbol} {pos.order_type} {pos.volume} lots")

    # Close a position
    close_result = await bridge.close_position(result.ticket)
    print(f"Closed with profit: {close_result.profit}")

    await bridge.stop()

asyncio.run(main())
```

## Available Commands

| Command | Python Method | Description |
|---------|---------------|-------------|
| TRADE | `buy()`, `sell()`, `place_pending_order()` | Execute orders |
| GET_DATA | `get_rates(symbol, timeframe, count)` | Historical OHLC data |
| GET_TICK | `get_tick(symbol)` | Current bid/ask |
| GET_ACCOUNT | `get_account()` | Balance, equity, margin |
| GET_POSITIONS | `get_positions()` | All open positions |
| CLOSE_POSITION | `close_position(ticket)` | Close position by ticket |
| HEARTBEAT | `heartbeat()` | Connection check |

## Order Types

- `BUY`, `SELL` - Market orders
- `BUY_LIMIT`, `SELL_LIMIT` - Limit orders
- `BUY_STOP`, `SELL_STOP` - Stop orders

## Timeframes

`M1`, `M5`, `M15`, `M30`, `H1`, `H4`, `D1`, `W1`, `MN1`

## Order Panel UI

A graphical trading panel with quick-access buttons for manual trading.

### Usage

```bash
python run_panel.py --symbol BTCUSD --volume 0.01 --port 5555
```

### Features

- **Buy/Sell/Close buttons** - Quick trade execution
- **SL/TP inputs** - Stop Loss and Take Profit with mode selection:
  - `%` - Percentage from entry price
  - `$` - Dollar amount risk
  - `Price` - Absolute price level
- **Positions Panel** - View and manage all open positions:
  - Editable SL/TP fields (press Enter to apply)
  - Close button per position
  - Trailing stop toggle with percentage input
- **Trailing Stops** - Automatic SL adjustment as price moves in your favor
- **Keyboard shortcuts**:
  - `B` - Buy
  - `S` - Sell
  - `C` - Close all positions for selected symbol
  - `R` - Refresh positions
  - `Esc` - Quit
- **Symbol dropdown** - BTCUSD, EURUSD, GBPUSD, USDJPY, XAUUSD
- **Volume input** - Adjustable with +/- buttons
- **Visual feedback** - Hover effects, success/error flash
- **Status bar** - Connection status and last action result
- **Auto-refresh** - Positions panel updates automatically

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--symbol` | BTCUSD | Initial trading symbol |
| `--volume` | 0.01 | Initial trade volume |
| `--port` | 5555 | Server port |

## Latency Measurement

Built-in execution speed measurement for performance analysis.

### Usage

```bash
python test_latency.py --iterations 50 --symbol BTCUSD --output latency.csv
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--iterations`, `-n` | 50 | Number of iterations per test |
| `--symbol`, `-s` | BTCUSD | Symbol for testing |
| `--output`, `-o` | (none) | Output CSV file for detailed samples |
| `--port`, `-p` | 5555 | Server port |
| `--timeout` | 60 | Connection timeout in seconds |

### Programmatic Usage

```python
from mt5_bridge import MT5Bridge, ConsoleReporter

# Enable timing collection
bridge = MT5Bridge(port=5555, enable_timing=True)
await bridge.start()
await bridge.wait_for_connection()

# Execute some commands...
await bridge.get_tick("BTCUSD")
await bridge.get_account()

# Get timing report
report = bridge.get_timing_report()
ConsoleReporter().print_report(report)

# Export to CSV
from mt5_bridge import CSVReporter
CSVReporter().write_samples(bridge.get_timing_samples(), "latency.csv")
```

### Benchmark Results

With 10ms polling interval (default):

| Metric | Min | Avg | P50 | P95 | P99 |
|--------|-----|-----|-----|-----|-----|
| Round-trip | 1.06ms | 13.64ms | 17.36ms | 22.64ms | 26.41ms |
| EA Processing | 0.01ms | 0.02ms | 0.02ms | 0.04ms | 0.06ms |
| Network (est.) | 0.52ms | 6.81ms | 8.67ms | 11.31ms | 13.20ms |

## EA Input Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| ServerAddress | "127.0.0.1" | Python server IP |
| ServerPort | 5555 | TCP port |
| ReconnectDelayMs | 5000 | Reconnect delay on disconnect |
| HeartbeatIntervalMs | 10000 | Keep-alive interval |
| TimerIntervalMs | 10 | Socket polling interval (lower = faster, higher CPU) |

## Troubleshooting

**EA can't connect:**
- Check firewall on Python host allows port 1111
- Verify Python server IP is correct in EA settings
- Ensure WebRequest is allowed for the IP in MT5 settings

**Orders fail:**
- Check symbol name matches broker's naming (e.g., "EURUSD" vs "EURUSDm")
- Verify account has sufficient margin
- Check if market is open

**Connection drops:**
- Increase `HeartbeatIntervalMs` if network is slow
- Check for network stability between VM and host

## License

MIT
