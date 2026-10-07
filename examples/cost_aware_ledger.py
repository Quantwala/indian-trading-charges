"""Reproducible, synthetic trades. Run after pip install indian-trading-charges.

Not historical backtest results. Slippage and exercise costs are excluded.
Rates/model assumptions are documented in the package README.
"""
from indian_charges import net_pnl


def main():
    trades = [
        dict(buy_price=120, sell_price=121, quantity=65, segment="options"),
        dict(buy_price=1500, sell_price=1510, quantity=100, segment="intraday"),
    ]
    totals = dict(gross=0.0, charges=0.0, net=0.0)
    for trade in trades:
        result = net_pnl(**trade)
        print(trade, result)
        for key in totals:
            totals[key] = round(totals[key] + result[key], 2)
    print("Synthetic ledger totals:", totals)
    assert net_pnl(**trades[0]) == dict(gross=65.0, charges=65.81, net=-0.81)
    assert net_pnl(**trades[1]) == dict(gross=1000.0, charges=100.71, net=899.29)
    assert totals == dict(gross=1065.0, charges=166.52, net=898.48)


if __name__ == "__main__":
    main()
