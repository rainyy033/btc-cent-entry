#!/usr/bin/env python3
"""BTC 4h-ahead forecaster: shrunk 12h momentum drift over persistence.

guess = last_close + 0.6 * ((last - close_720min_ago) / 720) * 240

Fixed constants, fitted on no future data (chosen on the dev kit's
pseudo-backtests only); deterministic; stdlib only.
"""
import json
import math
import os
import sys

WIN = 720          # 12h momentum window (minutes)
SHRINK = 0.6       # shrink factor applied to the 240-minute drift
H = 240            # forecast horizon (minutes)
MIN_PRICE = 0.00001
MAX_PRICE = 9999999.99999


def clamp(x):
    """Keep x on the 5-decimal price grid and inside the scorer's bounds."""
    return float(f"{max(MIN_PRICE, min(MAX_PRICE, x)):.5f}")


def forecast(prices):
    """One case's guess from its price series; raises when it cannot be made.

    A missing/empty/non-finite series is raised rather than guessed: an
    invalid case is scored as the checkpoint's own close (persistence), which
    beats fabricating a price off no data.
    """
    if not isinstance(prices, list) or not prices:
        raise ValueError("market has no prices")
    last = prices[-1]
    if isinstance(last, bool) or not isinstance(last, (int, float)) or not math.isfinite(last):
        raise ValueError("market's last price is not a finite number")
    if len(prices) == 1:
        guess = last
    else:
        w = min(WIN, len(prices))
        drift = (last - prices[-w]) / w
        guess = last + SHRINK * drift * H
    if not math.isfinite(guess):
        raise ValueError("forecast is not finite")
    return clamp(guess)


def main():
    indir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    if len(sys.argv) == 3:
        indir, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    for name in sorted(os.listdir(indir)):
        if not name.endswith(".in"):
            continue
        cid = name[:-3]  # strip ".in"; the output names the case by its file id
        with open(os.path.join(indir, name)) as f:
            case = json.load(f)
        markets = case.get("markets") if isinstance(case, dict) else None
        if not isinstance(markets, list) or len(markets) != 1:
            raise ValueError(f"{name} does not hold exactly one market")
        prices = markets[0].get("prices") if isinstance(markets[0], dict) else None
        price = forecast(prices)
        with open(os.path.join(outdir, f"{cid}.out"), "w") as f:
            json.dump({"forecasts": [{"case": cid, "price": price}]}, f, separators=(",", ":"))
            f.write("\n")


if __name__ == "__main__":
    main()
