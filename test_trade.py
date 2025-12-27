"""Test trading with BTCUSD."""

import asyncio
from mt5_bridge import MT5Bridge, Timeframe

async def test_btcusd_trade():
    bridge = MT5Bridge(host="127.0.0.1", port=5555)
    await bridge.start()

    print("Waiting for MT5 EA connection...")
    await bridge.wait_for_connection(timeout=60)
    print("Connected!\n")

    # Get BTCUSD tick
    print("Getting BTCUSD price...")
    tick = await bridge.get_tick("BTCUSD")
    print(f"BTCUSD: Bid={tick.bid}, Ask={tick.ask}\n")

    # Get account info
    account = await bridge.get_account()
    print(f"Account: Balance={account.balance}, Free Margin={account.free_margin}\n")

    # Place a buy order
    print("Placing BUY order for BTCUSD 0.01 lots...")
    try:
        result = await bridge.buy("BTCUSD", 0.01)
        print(f"ORDER SUCCESS!")
        print(f"  Ticket: {result.ticket}")
        print(f"  Price: {result.price_executed}")
        print(f"  Volume: {result.volume_executed}\n")
    except Exception as e:
        print(f"ORDER FAILED: {e}\n")

    # Check positions
    positions = await bridge.get_positions()
    print(f"Open positions: {len(positions)}")
    for pos in positions:
        print(f"  {pos.symbol} {pos.order_type} {pos.volume} lots @ {pos.open_price}, profit={pos.profit}")

    await bridge.stop()

if __name__ == "__main__":
    asyncio.run(test_btcusd_trade())
