# indian-trading-charges

<p align="center"><img src="https://quantwala.in/brand/quantwala-icon-512.png" width="96" alt="Quantwala logo"></p>

[![Tests](https://github.com/Quantwala/indian-trading-charges/actions/workflows/tests.yml/badge.svg)](https://github.com/Quantwala/indian-trading-charges/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/indian-trading-charges)](https://pypi.org/project/indian-trading-charges/)
[![Python](https://img.shields.io/pypi/pyversions/indian-trading-charges)](https://pypi.org/project/indian-trading-charges/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**Estimate brokerage, STT, GST, stamp duty and exchange charges for NSE and BSE trades, in Python.**
Equity delivery, intraday, futures and options. Zero runtime dependencies. Decimal arithmetic with paise rounding. Rates current to the
**1 April 2026 STT revision**.

```bash
pip install indian-trading-charges
```

```python
from indian_charges import round_trip, net_pnl, breakeven_pct

c = round_trip(buy_price=1500, sell_price=1510, quantity=100, segment="intraday")
c.total            # Decimal('100.71')
c.as_dict()        # {'brokerage': 40.0, 'stt': 37.75, 'exchange_txn': 9.24, 'sebi_fee': 0.3, 'stamp_duty': 4.5, 'gst': 8.92, ...}

net_pnl(buy_price=120, sell_price=121, quantity=65, segment="options")
# {'gross': 65.0, 'charges': 65.81, 'net': -0.81}   <- a winning option trade that lost money

breakeven_pct(price=1500, quantity=100, segment="intraday")   # 0.0669 (% move needed just to pay charges)
```

Or from the terminal:

```text
$ indian-charges intraday 1500 1510 100

Intraday · NSE · Zerodha · 100 units · rates from 2026-04-01

                             Buy          Sell         Total
Brokerage                 ₹20.00        ₹20.00        ₹40.00
STT                        ₹0.00        ₹37.75        ₹37.75
Exchange charges           ₹4.60         ₹4.64         ₹9.24
SEBI fee                   ₹0.15         ₹0.15         ₹0.30
Stamp duty                 ₹4.50         ₹0.00         ₹4.50
GST                        ₹4.46         ₹4.46         ₹8.92
------------------------------------------------------------
Total charges             ₹33.71        ₹67.00       ₹100.71

Gross P&L        ₹1,000.00
Net P&L            ₹899.29
Breakeven          0.0669%  (move needed just to cover charges)
```

> **Don't want to code?** The same engine runs the free [trading charges calculator](https://quantwala.in/charges-calculator)
> (no login), and [Quantwala](https://quantwala.in) uses it to price every trade when it backtests a strategy you describe
> in plain English or Hinglish.

## Why this exists

Most backtests and P&L trackers for Indian markets either ignore charges or use one flat percentage. Real costs are
uneven: STT is 0.1% on *both* sides of delivery but only on the sell side of intraday; options STT and exchange charges
are levied on **premium**, not notional; stamp duty applies only to buys; GST is charged on brokerage and exchange fees
but never on STT or stamp duty; a BSE X-group stock pays a 0.1% exchange charge per side. Get one of these wrong and a
strategy that "works" stops working.

This library encodes each rule once, with the source circular next to the number.

## What's covered

| | Delivery | Intraday | Futures | Options |
|---|---|---|---|---|
| STT | 0.1% buy and sell | 0.025% sell | 0.05% sell | 0.15% sell (premium) |
| Stamp duty (buy only) | 0.015% | 0.003% | 0.002% | 0.003% (premium) |
| NSE transaction + IPFT (per side) | 0.00307% | 0.00307% | 0.00183% | 0.03553% (premium) |
| SEBI fee | ₹10 per crore | ₹10 per crore | ₹10 per crore | ₹10 per crore |
| GST | 18% of brokerage + exchange + SEBI + IPFT | same | same | same |
| DP charge | per scrip on the sell | – | – | – |

Also handled:

- **NSE and BSE** exchange charges, including BSE's per-scrip-group rates (A, B, X, Z, SME and others).
- **ETFs and fund units**: equity-oriented funds pay 0.001% STT on a delivery sale; gold, debt and other funds pay none.
- **Broker plans:** `zerodha` (default), `groww`, `none` (statutory only), or your own `BrokeragePlan`.
- **Single legs** with `leg(turnover=..., side="buy" | "sell", ...)`, so a strategy's fills can be priced one by one.

Every rate and its source is in [`rates.py`](src/indian_charges/rates.py). `indian_charges.EFFECTIVE_FROM` says which
schedule you're on.

## API

```python
round_trip(*, buy_price, sell_price, quantity, segment="intraday", exchange="NSE",
           broker="zerodha", bse_group="", fund="") -> Charges
leg(*, turnover, side, segment="intraday", exchange="NSE", broker="zerodha",
    dp_scrips=0, bse_group="", fund="") -> Charges
net_pnl(*, buy_price, sell_price, quantity, **same_options) -> {"gross", "charges", "net"}
breakeven_pct(*, price, quantity, segment="intraday", **same_options) -> float
```

`Charges` has `brokerage`, `stt`, `exchange_txn`, `sebi_fee`, `ipft`, `stamp_duty`, `gst`, `dp_charge`, `turnover`
(all `Decimal`, rounded to the paisa), `.total`, `.as_dict()`, and supports `+` to add legs.

**F&O quantity is total units** (lots × lot size). For options, prices are **premiums**.

## Accuracy

The test suite checks worked examples line by line against the published rates. A parity test in the Quantwala app checks this library against the same rates used by
[Quantwala's live calculator](https://quantwala.in/charges-calculator). Your contract note can still differ
by a few paise: brokers aggregate and round per contract note, not per trade. Not modelled: Groww's ₹5 minimum, option
exercise and assignment (STT on intrinsic value), physical settlement, call-and-trade and account fees.

## Keeping rates current

SEBI, the exchanges and the Budget change these numbers a few times a year. If a rate changes, please open an issue or
a pull request with a link to the circular. Every number in `rates.py` should carry its source.

## Disclaimer

An estimate for research and education, not tax, legal or investment advice. Check your broker's contract note before
relying on a figure.

## License

MIT. Built and maintained by [Quantwala](https://quantwala.in): honest backtests for Indian markets, with every charge
included.

## Contributing and support

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, tests and rate-change requirements.
[Report a bug or request a feature](https://github.com/Quantwala/indian-trading-charges/issues).
For vulnerability reports, see [SECURITY.md](SECURITY.md).
