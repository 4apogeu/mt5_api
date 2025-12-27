#!/usr/bin/env python3
"""Standalone runner for MT5 Order Panel."""

import argparse
import logging

from mt5_bridge import MT5Bridge
from mt5_bridge.ui import OrderPanel
from mt5_bridge.ui.config import PanelConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="MT5 Order Panel")
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=5555, help="Server port")
    parser.add_argument("--symbol", default="BTCUSD", help="Default symbol")
    parser.add_argument("--volume", type=float, default=0.01, help="Default volume")
    args = parser.parse_args()

    # Create bridge
    bridge = MT5Bridge(host=args.host, port=args.port)

    # Create config with CLI overrides
    config = PanelConfig(
        default_symbol=args.symbol,
        default_volume=args.volume,
        host=args.host,
        port=args.port,
    )

    # Create and run panel
    panel = OrderPanel(bridge=bridge, config=config)
    panel.run()


if __name__ == "__main__":
    main()
