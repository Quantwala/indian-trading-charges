# Add Indian trading costs to a trade ledger

A gross gain can disappear after brokerage and statutory charges. This example
shows the arithmetic using two synthetic trades, not a historical strategy or
a claim about returns.

```sh
pip install indian-trading-charges==0.1.1
python examples/cost_aware_ledger.py
```

The options example buys at ₹120 and sells at ₹121 for 65 units. The model's
NSE Zerodha defaults estimate ₹65.81 in charges against ₹65 of gross profit:
net P&L is −₹0.81. Quantity is illustrative, not a current contract lot size.

The intraday equity example buys at ₹1,500 and sells at ₹1,510 for 100 shares.
Gross P&L is ₹1,000, estimated charges ₹100.71, net P&L ₹899.29.

## Using your own completed trade pairs

For a simple long-only ledger, call `net_pnl` on each matched entry and exit.
Use the actual quantity, segment and broker plan. Aggregate the returned
`gross`, `charges` and `net` fields separately. Retain those columns next to
the original orders so another person can inspect the calculation.

Do not apply these long-entry/exit examples directly to short positions,
partial fills or complex option legs. Reconcile orders first and model each
side correctly. Add slippage separately; this library does not model market
impact. Rates are effective 1 April 2026 and must be checked against exchange
circulars and your broker's contract note. Exercise is not modeled here.

## Explore without Python

[Check a trade with Quantwala's free calculator](https://quantwala.in/charges-calculator?utm_source=github&utm_medium=referral&utm_campaign=charges-calculator).
To test written rules against historical data, [read the backtesting workflow](https://quantwala.in/backtesting-indian-stocks?utm_source=github&utm_medium=referral&utm_campaign=backtesting-guide).

Maintained by Quantwala. The package is MIT licensed and can be used independently
of the hosted product.
