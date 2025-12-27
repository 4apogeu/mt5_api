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
│   └── main.py              # Entry point
├── mql5/
│   └── Experts/
│       └── MT5SocketClient.mq5   # MT5 Expert Advisor
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

## EA Input Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| ServerAddress | "192.168.1.100" | Python server IP |
| ServerPort | 1111 | TCP port |
| ReconnectDelayMs | 5000 | Reconnect delay on disconnect |
| HeartbeatIntervalMs | 10000 | Keep-alive interval |
| TimerIntervalMs | 100 | Socket polling interval |

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
