"""Charges for one leg, a round trip, and the breakeven move. Exact to the paisa (Decimal, half-up)."""
from __future__ import annotations

from dataclasses import dataclass, fields
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Optional, Union

from .rates import BSE_CASH_GROUPS, CASH, EXCHANGES, FUND_STT_SELL, PLANS, RATES, SEGMENTS, ZERO, BrokeragePlan

Number = Union[int, float, str, Decimal]
LINES = ("brokerage", "stt", "exchange_txn", "sebi_fee", "ipft", "stamp_duty", "gst", "dp_charge")


def _d(v: Any) -> Decimal:
    return v if isinstance(v, Decimal) else Decimal(str(v or 0))


def _paisa(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class Charges:
    """Every charge on a trade, in rupees. Add two legs with ``+``."""
    turnover: Decimal = ZERO
    brokerage: Decimal = ZERO
    stt: Decimal = ZERO
    exchange_txn: Decimal = ZERO
    sebi_fee: Decimal = ZERO
    ipft: Decimal = ZERO
    stamp_duty: Decimal = ZERO
    gst: Decimal = ZERO
    dp_charge: Decimal = ZERO

    @property
    def total(self) -> Decimal:
        return _paisa(sum((getattr(self, f) for f in LINES), ZERO))

    def as_dict(self) -> Dict[str, float]:
        out = {"turnover": float(_paisa(self.turnover)), **{f: float(getattr(self, f)) for f in LINES}}
        out["total"] = float(self.total)
        return out

    def __add__(self, other: "Charges") -> "Charges":
        return Charges(**{f.name: getattr(self, f.name) + getattr(other, f.name) for f in fields(self)})


def exchange_rate(segment: str, exchange: str = "NSE", bse_group: str = "") -> Decimal:
    """The exchange transaction charge as a fraction of turnover. On BSE's cash market it depends on the scrip group
    (an X-group stock pays 0.1% a side, not 0.00375%)."""
    seg = _segment(segment)
    ex = _exchange(exchange)
    if ex == "BSE" and seg in CASH and bse_group:
        return BSE_CASH_GROUPS.get(bse_group.strip().upper(), RATES[seg].exchange_txn["BSE"])
    return RATES[seg].exchange_txn.get(ex, ZERO)


def _segment(segment: str) -> str:
    seg = (segment or "").lower()
    if seg not in SEGMENTS: raise ValueError(f"segment must be one of {', '.join(SEGMENTS)}")
    return seg


def _exchange(exchange: str) -> str:
    ex = (exchange or "NSE").upper()
    if ex not in EXCHANGES: raise ValueError("exchange must be NSE or BSE")
    return ex


def _plan(broker: Union[str, BrokeragePlan]) -> BrokeragePlan:
    if isinstance(broker, BrokeragePlan): return broker
    plan = PLANS.get((broker or "zerodha").lower())
    if plan is None: raise ValueError(f"unknown broker {broker!r}; use one of {', '.join(PLANS)} or pass a BrokeragePlan")
    return plan


def leg(*, turnover: Number, side: str, segment: str = "intraday", exchange: str = "NSE",
        broker: Union[str, BrokeragePlan] = "zerodha", dp_scrips: int = 0, bse_group: str = "", fund: str = "") -> Charges:
    """Charges for ONE order: ``side`` is "buy" or "sell", ``turnover`` is price × quantity.

    For options pass the PREMIUM turnover: STT and the exchange charge are levied on premium, not notional
    (passing notional overstates costs about a hundredfold). ``bse_group`` is a BSE stock's scrip group.
    ``fund`` is "" for a share, "equity" for units of an equity-oriented fund, "other" for any other fund.
    ``dp_scrips`` is the number of scrips debited from demat on a delivery sell (usually 1)."""
    seg, ex, plan = _segment(segment), _exchange(exchange), _plan(broker)
    rates = RATES[seg]
    s = (side or "").lower()
    if s not in ("buy", "sell"): raise ValueError('side must be "buy" or "sell"')
    is_buy = s == "buy"
    t = abs(_d(turnover))
    c = Charges(turnover=t)

    pct, cap = plan.percent.get(seg, ZERO), plan.flat_cap.get(seg, ZERO)
    if seg == "options":
        c.brokerage = cap if t > 0 else ZERO
    elif pct > 0:
        c.brokerage = min(t * pct, cap) if cap > 0 else t * pct

    if fund and seg in CASH:
        c.stt = t * FUND_STT_SELL[seg] if fund == "equity" and not is_buy else ZERO
    else:
        c.stt = t * (rates.stt_buy if is_buy else rates.stt_sell)
    c.exchange_txn = t * exchange_rate(seg, ex, bse_group)
    c.sebi_fee = t * rates.sebi_turnover
    c.ipft = t * rates.ipft.get(ex, ZERO)
    c.stamp_duty = t * rates.stamp_buy if is_buy else ZERO
    c.gst = (c.brokerage + c.sebi_fee + c.exchange_txn + c.ipft) * rates.gst  # never on STT or stamp duty
    if seg == "delivery" and not is_buy and dp_scrips > 0:
        c.dp_charge = plan.dp_charge_per_scrip * Decimal(int(dp_scrips))
    for f in LINES:
        setattr(c, f, _paisa(_d(getattr(c, f))))
    return c


def round_trip(*, buy_price: Number, sell_price: Number, quantity: Number, segment: str = "intraday",
               exchange: str = "NSE", broker: Union[str, BrokeragePlan] = "zerodha", bse_group: str = "",
               fund: str = "") -> Charges:
    """Charges for one buy and one sell of the same quantity (the order doesn't matter: a short trade is the
    same two legs). A delivery sell carries one DP charge."""
    q = _d(quantity)
    common = dict(segment=segment, exchange=exchange, broker=broker, bse_group=bse_group, fund=fund)
    return (leg(turnover=_d(buy_price) * q, side="buy", **common)
            + leg(turnover=_d(sell_price) * q, side="sell", dp_scrips=1 if _segment(segment) == "delivery" else 0, **common))


def net_pnl(*, buy_price: Number, sell_price: Number, quantity: Number, **kw: Any) -> Dict[str, float]:
    """Gross P&L, total charges and what is left."""
    gross = (_d(sell_price) - _d(buy_price)) * _d(quantity)
    c = round_trip(buy_price=buy_price, sell_price=sell_price, quantity=quantity, **kw)
    return {"gross": float(_paisa(gross)), "charges": float(c.total), "net": float(_paisa(gross - c.total))}


def breakeven_pct(*, price: Number, quantity: Number, segment: str = "intraday", **kw: Any) -> float:
    """How far the price must move, in percent, just to pay for the round trip. The first number to look at."""
    p, q = _d(price), _d(quantity)
    if p <= 0 or q <= 0: return 0.0
    c = round_trip(buy_price=p, sell_price=p, quantity=q, segment=segment, **kw)
    return float(c.total / (p * q) * 100)
