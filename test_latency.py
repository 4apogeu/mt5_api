#!/usr/bin/env python3
"""Latency benchmark script for MT5-Python bridge.

This script measures execution speed and latency metrics for various
MT5 bridge operations.

Usage:
    python test_latency.py [--iterations N] [--symbol SYMBOL] [--output FILE]
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from mt5_bridge import MT5Bridge, ConsoleReporter, CSVReporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_benchmark(
    bridge: MT5Bridge,
    symbol: str,
    iterations: int
) -> None:
    """Run latency benchmark tests.

    Args:
        bridge: MT5Bridge instance with timing enabled
        symbol: Symbol to use for tests
        iterations: Number of iterations for each test
    """
    logger.info(f"Starting latency benchmark: {iterations} iterations on {symbol}")

    # Test GET_TICK (lightweight operation)
    logger.info("Testing GET_TICK latency...")
    for i in range(iterations):
        try:
            await bridge.get_tick(symbol)
            if (i + 1) % 10 == 0:
                logger.info(f"  GET_TICK: {i + 1}/{iterations}")
        except Exception as e:
            logger.error(f"GET_TICK failed: {e}")

    # Test GET_ACCOUNT (no symbol dependency)
    logger.info("Testing GET_ACCOUNT latency...")
    for i in range(iterations):
        try:
            await bridge.get_account()
            if (i + 1) % 10 == 0:
                logger.info(f"  GET_ACCOUNT: {i + 1}/{iterations}")
        except Exception as e:
            logger.error(f"GET_ACCOUNT failed: {e}")

    # Test GET_POSITIONS
    logger.info("Testing GET_POSITIONS latency...")
    for i in range(iterations):
        try:
            await bridge.get_positions()
            if (i + 1) % 10 == 0:
                logger.info(f"  GET_POSITIONS: {i + 1}/{iterations}")
        except Exception as e:
            logger.error(f"GET_POSITIONS failed: {e}")

    # Test HEARTBEAT
    logger.info("Testing HEARTBEAT latency...")
    for i in range(iterations):
        try:
            await bridge.heartbeat()
            if (i + 1) % 10 == 0:
                logger.info(f"  HEARTBEAT: {i + 1}/{iterations}")
        except Exception as e:
            logger.error(f"HEARTBEAT failed: {e}")


async def main():
    parser = argparse.ArgumentParser(description="MT5 Bridge Latency Benchmark")
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=50,
        help="Number of iterations per test (default: 50)"
    )
    parser.add_argument(
        "--symbol", "-s",
        type=str,
        default="BTCUSD",
        help="Symbol for testing (default: BTCUSD)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output CSV file for detailed samples"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=5555,
        help="Server port (default: 5555)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Connection timeout in seconds (default: 60)"
    )

    args = parser.parse_args()

    # Create bridge with timing enabled
    bridge = MT5Bridge(host="0.0.0.0", port=args.port, enable_timing=True)

    try:
        # Start server
        await bridge.start()
        logger.info(f"Server listening on port {args.port}")
        logger.info("Waiting for MT5 EA connection...")

        # Wait for connection
        await bridge.wait_for_connection(timeout=args.timeout)
        logger.info("MT5 EA connected!")

        # Run benchmark
        await run_benchmark(bridge, args.symbol, args.iterations)

        # Generate reports
        console_reporter = ConsoleReporter()

        # Overall report
        report = bridge.get_timing_report()
        if report:
            console_reporter.print_report(report, "Overall Latency Report")

        # Per-action report
        reports_by_action = bridge.get_timing_report_by_action()
        if reports_by_action:
            console_reporter.print_by_action(reports_by_action, "Latency by Action")

        # Save CSV if requested
        if args.output:
            csv_reporter = CSVReporter()
            samples = bridge.get_timing_samples()
            csv_reporter.write_samples(samples, args.output)
            logger.info(f"Detailed samples written to: {args.output}")

            # Also write summary
            summary_path = Path(args.output).with_suffix(".summary.csv")
            if report:
                csv_reporter.write_summary(report, summary_path)
                logger.info(f"Summary statistics written to: {summary_path}")

    except TimeoutError:
        logger.error("Connection timeout - ensure MT5 EA is running")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    finally:
        await bridge.stop()
        logger.info("Server stopped")


if __name__ == "__main__":
    asyncio.run(main())
