"""indian-charges: print the full charge breakdown for one round trip.

    indian-charges intraday 1500 1510 100
    indian-charges options 120 140 65 --broker groww
    indian-charges delivery 240 250 500 --exchange BSE --bse-group X
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal

from . import __version__
from .core import LINES, breakeven_pct, leg
from .rates import EFFECTIVE_FROM, PLANS, SEGMENTS

LABELS = {"brokerage": "Brokerage", "stt": "STT", "exchange_txn": "Exchange charges", "sebi_fee": "SEBI fee",
          "ipft": "IPFT", "stamp_duty": "Stamp duty", "gst": "GST", "dp_charge": "DP charge"}


def rupees(x) -> str:
    """₹1,23,456.78: Indian digit grouping."""
    neg, x = x < 0, abs(Decimal(str(x))).quantize(Decimal("0.01"))
    whole, frac = str(x).split(".")
    head, tail = whole[:-3], whole[-3:]
    while len(head) > 2: tail, head = head[-2:] + "," + tail, head[:-2]
    return ("-" if neg else "") + "₹" + (head + "," if head else "") + tail + "." + frac


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="indian-charges", description="Exact charges for one buy and one sell on NSE/BSE.")
    p.add_argument("segment", choices=SEGMENTS)
    p.add_argument("buy_price", type=Decimal, help="buy price per unit (premium for options)")
    p.add_argument("sell_price", type=Decimal, help="sell price per unit (premium for options)")
    p.add_argument("quantity", type=Decimal, help="total units (lots × lot size for F&O)")
    p.add_argument("--exchange", default="NSE", choices=("NSE", "BSE"))
    p.add_argument("--broker", default="zerodha", choices=sorted(PLANS))
    p.add_argument("--bse-group", default="", help="BSE scrip group, e.g. A, B, X, Z")
    p.add_argument("--fund", default="", choices=("", "equity", "other"), help="for ETF / fund units")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__} (rates from {EFFECTIVE_FROM})")
    a = p.parse_args(argv)
    kw = dict(segment=a.segment, exchange=a.exchange, broker=a.broker, bse_group=a.bse_group, fund=a.fund)
    buy = leg(turnover=a.buy_price * a.quantity, side="buy", **kw)
    sell = leg(turnover=a.sell_price * a.quantity, side="sell", dp_scrips=1 if a.segment == "delivery" else 0, **kw)
    total = buy + sell
    gross = (a.sell_price - a.buy_price) * a.quantity
    be = breakeven_pct(price=a.buy_price, quantity=a.quantity, **kw)
    if a.json:
        print(json.dumps({"buy": buy.as_dict(), "sell": sell.as_dict(), "total": total.as_dict(), "gross": float(gross),
                          "net": float(gross - total.total), "breakeven_pct": round(be, 4), "rates_effective": EFFECTIVE_FROM}, indent=2))
        return 0
    print(f"{a.segment.title()} · {a.exchange} · {PLANS[a.broker].label} · {a.quantity} units · rates from {EFFECTIVE_FROM}\n")
    print(f"{'':18}{'Buy':>14}{'Sell':>14}{'Total':>14}")
    for f in LINES:
        if getattr(total, f): print(f"{LABELS[f]:18}{rupees(getattr(buy, f)):>14}{rupees(getattr(sell, f)):>14}{rupees(getattr(total, f)):>14}")
    print("-" * 60)
    print(f"{'Total charges':18}{rupees(buy.total):>14}{rupees(sell.total):>14}{rupees(total.total):>14}\n")
    print(f"Gross P&L   {rupees(gross):>14}")
    print(f"Net P&L     {rupees(gross - total.total):>14}")
    print(f"Breakeven   {be:>13.4f}%  (move needed just to cover charges)\n")
    print("Estimate, not a contract note. Free web version and backtests with these charges: https://quantwala.in")
    return 0


if __name__ == "__main__":
    sys.exit(main())
