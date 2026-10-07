"""indian-trading-charges: exact brokerage, STT, GST, stamp duty and exchange charges for NSE and BSE trades.

    >>> from indian_charges import round_trip
    >>> round_trip(buy_price=1500, sell_price=1510, quantity=100, segment="intraday").total
    Decimal('100.71')

Maintained by Quantwala (https://quantwala.in), where the same engine prices every backtest.
"""
from .core import Charges, breakeven_pct, exchange_rate, leg, net_pnl, round_trip
from .rates import EFFECTIVE_FROM, PLANS, RATES, SEGMENTS, BrokeragePlan

__version__ = "0.1.1"
__all__ = ["Charges", "BrokeragePlan", "leg", "round_trip", "net_pnl", "breakeven_pct", "exchange_rate",
           "RATES", "PLANS", "SEGMENTS", "EFFECTIVE_FROM", "__version__"]
