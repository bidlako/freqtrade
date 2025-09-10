"""Coinmate exchange subclass"""

import logging

from freqtrade.enums import MarginMode, TradingMode
from freqtrade.exceptions import OperationalException
from freqtrade.exchange import Exchange
from freqtrade.exchange.exchange_types import FtHas


logger = logging.getLogger(__name__)


class Coinmate(Exchange):
    """
    Coinmate exchange class. Contains adjustments needed for Freqtrade to work
    with this exchange.
    
    Coinmate is a European cryptocurrency exchange that supports spot trading only.
    Key limitations:
    - No OHLCV data support (no fetchOHLCV)
    - Spot trading only (no margin, futures, or derivatives)
    - Rate limited to 600ms between requests
    """

    _ft_has: FtHas = {
        "ohlcv_has_history": False,  # Coinmate doesn't provide OHLCV data
        "trades_pagination": "time",  # Uses time-based pagination for trades
        "trades_pagination_arg": "timestampFrom",
        "order_time_in_force": ["GTC", "IOC", "FOK", "PO"],  # Supports various TIF options
        "l2_limit_range": [1, 10, 50, 100],  # Order book depth options
        "stoploss_on_exchange": False,  # No native stop-loss support
    }

    _supported_trading_mode_margin_pairs: list[tuple[TradingMode, MarginMode]] = [
        # Coinmate only supports spot trading
        (TradingMode.SPOT, MarginMode.NONE),
    ]

    def get_tickers(self, symbols: list[str] | None = None, *, cached: bool = False) -> dict:
        """
        Fetch tickers for the given symbols.
        Override to handle any Coinmate-specific ticker format if needed.
        """
        return super().get_tickers(symbols=symbols, cached=cached)

    def additional_exchange_init(self) -> None:
        """
        Additional exchange initialization logic.
        """
        # Log that we're using a spot-only exchange
        logger.info("Coinmate exchange initialized - spot trading only")
        
        # Verify we're not trying to use unsupported trading modes
        if self.trading_mode != TradingMode.SPOT:
            raise OperationalException(
                f"Trading mode '{self.trading_mode}' is not supported by Coinmate. "
                "Only spot trading is available."
            )

    def validate_ordertypes(self, order_types: dict) -> None:
        """
        Validate order types for Coinmate.
        Override to add exchange-specific validations.
        """
        super().validate_ordertypes(order_types)
        
        # Coinmate doesn't support stoploss orders natively
        if order_types.get("stoploss_on_exchange", False):
            logger.warning(
                "Coinmate doesn't support stop-loss orders on exchange. "
                "Stop-loss will be handled by freqtrade locally."
            )
