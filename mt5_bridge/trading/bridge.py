"""High-level MT5 trading bridge API."""

import logging
from typing import Optional

from ..server import MT5Server, MT5Connection
from ..protocol import (
    Action,
    OrderType,
    Timeframe,
    Request,
    TradeParams,
    DataParams,
    OrderResult,
    TickData,
    AccountInfo,
    Position,
    CloseResult,
)

logger = logging.getLogger(__name__)


class MT5BridgeError(Exception):
    """Base exception for MT5 bridge errors."""
    pass


class NotConnectedError(MT5BridgeError):
    """Raised when no MT5 EA is connected."""
    pass


class TradeError(MT5BridgeError):
    """Raised when a trade operation fails."""

    def __init__(self, message: str, error_code: int = 0):
        super().__init__(message)
        self.error_code = error_code


class MT5Bridge:
    """High-level API for MT5 trading operations."""

    def __init__(self, host: str = "0.0.0.0", port: int = 1111):
        self._server = MT5Server(
            host=host,
            port=port,
            on_connect=self._on_connect,
            on_disconnect=self._on_disconnect
        )

    def _on_connect(self, connection: MT5Connection) -> None:
        logger.info(f"MT5 EA connected: {connection.client_address}")

    def _on_disconnect(self, connection: MT5Connection) -> None:
        logger.info("MT5 EA disconnected")

    @property
    def is_connected(self) -> bool:
        return self._server.is_connected

    async def start(self) -> None:
        """Start the bridge server."""
        await self._server.start()

    async def stop(self) -> None:
        """Stop the bridge server."""
        await self._server.stop()

    async def wait_for_connection(self, timeout: float = 60.0) -> None:
        """Wait for an MT5 EA to connect."""
        await self._server.wait_for_connection(timeout)

    def _get_connection(self) -> MT5Connection:
        """Get the current connection or raise error."""
        connection = self._server.connection
        if connection is None or not connection.is_connected:
            raise NotConnectedError("No MT5 EA connected")
        return connection

    async def _send_command(self, action: Action, params: dict) -> dict:
        """Send a command and return the response data."""
        connection = self._get_connection()
        request = Request(action=action, params=params)
        response = await connection.send_request(request)

        if not response.success:
            raise TradeError(
                response.error_message or f"Command {action.value} failed",
                response.error_code
            )
        return response.data

    async def buy(
        self,
        symbol: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        magic: int = 0,
        comment: str = ""
    ) -> OrderResult:
        """Execute a market buy order."""
        params = TradeParams(
            symbol=symbol,
            order_type=OrderType.BUY,
            volume=volume,
            stop_loss=stop_loss,
            take_profit=take_profit,
            magic=magic,
            comment=comment
        )
        data = await self._send_command(Action.TRADE, params.to_dict())
        return OrderResult.from_response_data(data)

    async def sell(
        self,
        symbol: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        magic: int = 0,
        comment: str = ""
    ) -> OrderResult:
        """Execute a market sell order."""
        params = TradeParams(
            symbol=symbol,
            order_type=OrderType.SELL,
            volume=volume,
            stop_loss=stop_loss,
            take_profit=take_profit,
            magic=magic,
            comment=comment
        )
        data = await self._send_command(Action.TRADE, params.to_dict())
        return OrderResult.from_response_data(data)

    async def place_pending_order(
        self,
        symbol: str,
        order_type: OrderType,
        price: float,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        magic: int = 0,
        comment: str = ""
    ) -> OrderResult:
        """Place a pending order (limit or stop)."""
        if order_type in (OrderType.BUY, OrderType.SELL):
            raise ValueError("Use buy() or sell() for market orders")

        params = TradeParams(
            symbol=symbol,
            order_type=order_type,
            volume=volume,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            magic=magic,
            comment=comment
        )
        data = await self._send_command(Action.TRADE, params.to_dict())
        return OrderResult.from_response_data(data)

    async def get_rates(
        self,
        symbol: str,
        timeframe: Timeframe,
        count: int
    ) -> list[dict]:
        """Get historical OHLC data."""
        params = DataParams(symbol=symbol, timeframe=timeframe, count=count)
        data = await self._send_command(Action.GET_DATA, params.to_dict())
        return data.get("rates", [])

    async def get_tick(self, symbol: str) -> TickData:
        """Get current bid/ask for a symbol."""
        data = await self._send_command(Action.GET_TICK, {"symbol": symbol})
        return TickData.from_response_data(data)

    async def get_account(self) -> AccountInfo:
        """Get account information."""
        data = await self._send_command(Action.GET_ACCOUNT, {})
        return AccountInfo.from_response_data(data)

    async def get_positions(self) -> list[Position]:
        """Get all open positions."""
        data = await self._send_command(Action.GET_POSITIONS, {})
        positions_data = data.get("positions", [])
        return [Position.from_response_data(p) for p in positions_data]

    async def close_position(self, ticket: int) -> CloseResult:
        """Close an open position by ticket."""
        data = await self._send_command(Action.CLOSE_POSITION, {"ticket": ticket})
        return CloseResult.from_response_data(data)

    async def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """Modify stop loss and take profit of a position."""
        params = {"ticket": ticket}
        if stop_loss is not None:
            params["sl"] = stop_loss
        if take_profit is not None:
            params["tp"] = take_profit

        data = await self._send_command(Action.TRADE, {
            "action": "MODIFY",
            **params
        })
        return data.get("success", False)

    async def heartbeat(self) -> bool:
        """Send heartbeat to check connection."""
        try:
            await self._send_command(Action.HEARTBEAT, {})
            return True
        except Exception:
            return False
