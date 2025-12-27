"""Example usage of MT5 Bridge."""

import asyncio
from mt5_bridge import MT5Bridge, Timeframe, OrderType


async def main():
    bridge = MT5Bridge(host="0.0.0.0", port=1111)

    await bridge.start()
    print("Server started. Waiting for MT5 EA to connect...")

    await bridge.wait_for_connection(timeout=120)
    print("MT5 EA connected!")

    # Get account info
    account = await bridge.get_account()
    print(f"Balance: {account.balance}")
    print(f"Equity: {account.equity}")

    # Get current price
    tick = await bridge.get_tick("EURUSD")
    print(f"EURUSD Bid: {tick.bid}, Ask: {tick.ask}")

    # Get historical data
    rates = await bridge.get_rates("EURUSD", Timeframe.H1, 100)
    print(f"Got {len(rates)} candles")

    # Place a buy order (uncomment to execute)
    # result = await bridge.buy("EURUSD", 0.01, stop_loss=tick.bid - 0.0050)
    # print(f"Order placed: ticket={result.ticket}")

    # Get open positions
    positions = await bridge.get_positions()
    for pos in positions:
        print(f"Position: {pos.symbol} {pos.order_type} {pos.volume} lots, profit={pos.profit}")

    await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
