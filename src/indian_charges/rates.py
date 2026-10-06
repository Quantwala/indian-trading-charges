"""Statutory rates and broker plans for NSE and BSE equity and F&O.

Rates are data, not logic: they change by circular a few times a year, so they live here with their sources.
Effective for FY2026-27, after the 1 April 2026 STT revision (futures 0.02% -> 0.05% of the sell side, options
0.10% -> 0.15% of the sell-side premium; Finance Act 2026, NSE/FATAX/73524 of 31 Mar 2026).

What differs by exchange is the exchange's own transaction charge. STT, stamp duty, the SEBI fee, GST and DP
charges are the same on NSE and BSE.

NSE, per crore each side (premium for options), transaction charge + IPFT, from 1 Mar 2026 (NSE/FA/73061):
  cash 306.99 + 0.01 = 307, futures 182.99 + 0.01 = 183, options 3,552.99 + 0.01 = 3,553.
BSE cash market, per crore each side, by scrip group, its Rs 1 Investor Protection Fund contribution included
  (bseindia.com/static/members/tfequity.aspx; notice 20221109-7, from 1 Dec 2022): see BSE_CASH_GROUPS.
STT: 0.1% on both sides of delivery, 0.025% on the intraday sell. Units of an equity-oriented fund (an equity ETF)
  pay none on the purchase, 0.001% on a delivery sale and 0.025% on an intraday one; other funds (gold, silver,
  debt, liquid, overseas-index ETFs) pay none (Finance (No.2) Act 2004 s.98).
Stamp duty (Indian Stamp Act as amended by the Finance Act 2019, from 1 Jul 2020): 0.015% delivery buy,
  0.003% intraday buy, 0.002% futures buy, 0.003% options buy.
SEBI turnover fee: Rs 10 per crore. GST: 18% on brokerage, exchange charge, SEBI fee and IPFT; never on STT or
  stamp duty.

Check against your broker's contract note and the current exchange circulars before relying on a figure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict

ZERO = Decimal("0")
EFFECTIVE_FROM = "2026-04-01"
SEGMENTS = ("delivery", "intraday", "futures", "options")
CASH = ("delivery", "intraday")
EXCHANGES = ("NSE", "BSE")


@dataclass(frozen=True)
class SegmentRates:
    stt_buy: Decimal
    stt_sell: Decimal
    exchange_txn: Dict[str, Decimal]
    stamp_buy: Decimal
    sebi_turnover: Decimal = Decimal("0.000001")  # Rs 10 per crore
    ipft: Dict[str, Decimal] = field(default_factory=dict)  # by exchange; BSE's cash-market IPF is inside its charge
    gst: Decimal = Decimal("0.18")


RATES: Dict[str, SegmentRates] = {
    "delivery": SegmentRates(
        stt_buy=Decimal("0.001"), stt_sell=Decimal("0.001"),
        exchange_txn={"NSE": Decimal("0.000030699"), "BSE": Decimal("0.0000375")},
        stamp_buy=Decimal("0.00015"), ipft={"NSE": Decimal("0.000000001"), "BSE": ZERO},
    ),
    "intraday": SegmentRates(
        stt_buy=ZERO, stt_sell=Decimal("0.00025"),
        exchange_txn={"NSE": Decimal("0.000030699"), "BSE": Decimal("0.0000375")},
        stamp_buy=Decimal("0.00003"), ipft={"NSE": Decimal("0.000000001"), "BSE": ZERO},
    ),
    "futures": SegmentRates(
        stt_buy=ZERO, stt_sell=Decimal("0.0005"),
        exchange_txn={"NSE": Decimal("0.000018299"), "BSE": ZERO},
        stamp_buy=Decimal("0.00002"), ipft={"NSE": Decimal("0.000000001"), "BSE": Decimal("0.0000005")},
    ),
    "options": SegmentRates(
        # Levied on PREMIUM turnover, not on the notional the contract controls.
        stt_buy=ZERO, stt_sell=Decimal("0.0015"),
        exchange_txn={"NSE": Decimal("0.000355299"), "BSE": Decimal("0.000325")},
        stamp_buy=Decimal("0.00003"), ipft={"NSE": Decimal("0.000000001"), "BSE": Decimal("0.000005")},
    ),
}

# STT on selling units of an equity-oriented fund; none on buying them since 2013. Other funds pay no STT at all.
FUND_STT_SELL: Dict[str, Decimal] = {"delivery": Decimal("0.00001"), "intraday": Decimal("0.00025")}

# BSE's equity-segment transaction charge by scrip group, each side (read 29 Sep 2026). Rs 375 per crore for A, B
# and the other non-exclusive scrips; SME (M, MT, TS, MS), InvIT/REIT (IF, IT) and rights (R) Rs 275; X, XT and Z
# Rs 10,000; P and ZP Rs 1,00,000. A group missing here is charged the A/B rate.
BSE_CASH_GROUPS: Dict[str, Decimal] = {
    **dict.fromkeys(("A", "B", "T", "E", "F", "FC", "G", "GC", "I", "W"), Decimal("0.0000375")),
    **dict.fromkeys(("M", "MT", "TS", "MS", "IF", "IT", "R"), Decimal("0.0000275")),
    **dict.fromkeys(("X", "XT", "Z"), Decimal("0.001")),
    **dict.fromkeys(("P", "ZP"), Decimal("0.01")),
}


@dataclass(frozen=True)
class BrokeragePlan:
    """A broker's plan: a percentage of turnover per segment, capped at a flat amount per order (options: the flat
    amount per order), plus a DP charge per scrip on delivery sells."""
    broker_id: str
    label: str
    percent: Dict[str, Decimal]
    flat_cap: Dict[str, Decimal]
    dp_charge_per_scrip: Decimal = ZERO


PLANS: Dict[str, BrokeragePlan] = {
    # zerodha.com/charges: free delivery; 0.03% or Rs 20 intraday and futures; Rs 20 per options order;
    # DP Rs 13 + GST = Rs 15.34 per scrip sold from demat.
    "zerodha": BrokeragePlan(
        "zerodha", "Zerodha",
        percent={"delivery": ZERO, "intraday": Decimal("0.0003"), "futures": Decimal("0.0003"), "options": ZERO},
        flat_cap={"delivery": ZERO, "intraday": Decimal("20"), "futures": Decimal("20"), "options": Decimal("20")},
        dp_charge_per_scrip=Decimal("15.34"),
    ),
    # groww.in/pricing: 0.1% capped at Rs 20 (min Rs 5 not modelled) per order; Rs 20 per options order.
    "groww": BrokeragePlan(
        "groww", "Groww",
        percent={"delivery": Decimal("0.001"), "intraday": Decimal("0.001"), "futures": Decimal("0.001"), "options": ZERO},
        flat_cap={"delivery": Decimal("20"), "intraday": Decimal("20"), "futures": Decimal("20"), "options": Decimal("20")},
        dp_charge_per_scrip=Decimal("18.50"),
    ),
    # Statutory charges only, for research runs that leave brokerage out.
    "none": BrokeragePlan(
        "none", "No brokerage",
        percent={k: ZERO for k in SEGMENTS}, flat_cap={k: ZERO for k in SEGMENTS},
    ),
}
