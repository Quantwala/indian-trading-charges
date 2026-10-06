"""Worked examples, each checked line by line against the published rates (Zerodha plan unless stated)."""
from decimal import Decimal as D

import pytest

from indian_charges import BrokeragePlan, breakeven_pct, leg, net_pnl, round_trip
from indian_charges.cli import main, rupees


def test_intraday_round_trip_line_by_line():
    c = round_trip(buy_price=1500, sell_price=1510, quantity=100, segment="intraday")
    # Brokerage: 0.03% of 1.5L = 45 -> capped at 20, on both legs.
    assert c.brokerage == D("40.00")
    # STT 0.025% on the sell only: 151000 × 0.00025 = 37.75.
    assert c.stt == D("37.75")
    # Stamp duty 0.003% on the buy only: 150000 × 0.00003 = 4.50.
    assert c.stamp_duty == D("4.50")
    # NSE transaction charge 0.0030699% each side.
    assert c.exchange_txn == D("9.24")
    # GST 18% on brokerage + exchange + SEBI + IPFT; never on STT or stamp duty.
    assert c.gst == D("8.92")
    assert c.total == D("100.71")


def test_delivery_has_stt_both_sides_and_one_dp_charge():
    c = round_trip(buy_price=2400, sell_price=2500, quantity=50, segment="delivery")
    assert c.brokerage == 0 and c.stt == D("245.00") and c.dp_charge == D("15.34")
    assert c.total == D("287.50")


def test_options_use_premium_turnover_and_flat_brokerage():
    c = round_trip(buy_price=120, sell_price=140, quantity=65, segment="options")
    assert c.brokerage == D("40.00")
    assert c.stt == D("13.65")  # 0.15% of the 9,100 sell premium (from 1 Apr 2026)
    assert c.total == D("68.18")


def test_futures_stt_on_the_sell_side():
    c = round_trip(buy_price=24000, sell_price=24100, quantity=75, segment="futures")
    assert c.stt == D("903.75")  # 0.05% of 18.075L
    assert c.total == D("1069.11")


def test_bse_group_x_pays_a_much_higher_exchange_charge():
    a = round_trip(buy_price=240, sell_price=250, quantity=500, segment="delivery", exchange="BSE", bse_group="A")
    x = round_trip(buy_price=240, sell_price=250, quantity=500, segment="delivery", exchange="BSE", bse_group="X")
    assert x.exchange_txn > a.exchange_txn * 20


def test_equity_etf_pays_tiny_stt_and_other_funds_none():
    etf = round_trip(buy_price=250, sell_price=260, quantity=100, segment="delivery", fund="equity")
    gold = round_trip(buy_price=60, sell_price=62, quantity=100, segment="delivery", fund="other")
    assert etf.stt == D("0.26") and gold.stt == 0


def test_groww_and_custom_plans():
    g = round_trip(buy_price=1000, sell_price=1010, quantity=10, segment="delivery", broker="groww")
    assert g.brokerage == D("20.10")  # 0.1% of each leg, under the Rs 20 cap
    flat = BrokeragePlan("flat", "Flat ₹10", percent={s: D("1") for s in ("delivery", "intraday", "futures", "options")},
                         flat_cap={s: D("10") for s in ("delivery", "intraday", "futures", "options")})
    assert round_trip(buy_price=1500, sell_price=1510, quantity=100, broker=flat).brokerage == D("20.00")


def test_a_short_trade_costs_the_same_as_a_long_one():
    # Charges depend on which leg is the buy and which the sell, not on their order.
    assert leg(turnover=150000, side="buy").total + leg(turnover=151000, side="sell").total == \
        round_trip(buy_price=1500, sell_price=1510, quantity=100).total


def test_breakeven_and_net_pnl():
    assert 0.06 < breakeven_pct(price=1500, quantity=100) < 0.07
    assert net_pnl(buy_price=120, sell_price=121, quantity=65, segment="options") == {"gross": 65.0, "charges": 65.81, "net": -0.81}


def test_bad_inputs_are_rejected():
    with pytest.raises(ValueError): round_trip(buy_price=1, sell_price=1, quantity=1, segment="commodity")
    with pytest.raises(ValueError): round_trip(buy_price=1, sell_price=1, quantity=1, exchange="MCX")
    with pytest.raises(ValueError): round_trip(buy_price=1, sell_price=1, quantity=1, broker="nobody")
    with pytest.raises(ValueError): leg(turnover=100, side="hold")


def test_cli_prints_a_breakdown(capsys):
    assert main(["intraday", "1500", "1510", "100"]) == 0
    out = capsys.readouterr().out
    assert "₹100.71" in out and "Breakeven" in out
    assert rupees(D("12345678.9")) == "₹1,23,45,678.90"
