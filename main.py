#!/usr/bin/env python3
"""BTC 4h-ahead forecaster: shrunk 12h momentum drift over persistence.

guess = last_close + 0.6 * ((last - close_720min_ago) / 720) * 240

Fixed constants, fitted on no future data (chosen on the dev kit's
pseudo-backtests only); deterministic; stdlib only.
"""
import json, os, sys

WIN = 720          # 12h momentum window (minutes)
SHRINK = 0.6       # shrink factor applied to the 240-minute drift
H = 240            # forecast horizon (minutes)

def clamp(x):
    lo, hi = 0.00001, 9999999.99999
    x = max(lo, min(hi, x))
    return float(f"{x:.5f}")

def main():
    indir, outdir = "/input", "/output"
    if len(sys.argv) == 3:
        indir, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    for name in sorted(os.listdir(indir)):
        if not name.endswith(".in"):
            continue
        case = json.load(open(os.path.join(indir, name)))
        prices = case["markets"][0]["prices"]
        n = len(prices)
        last = prices[-1]
        w = min(WIN, n)
        drift = (last - prices[-w]) / w
        guess = clamp(last + SHRINK * drift * H)
        cid = case["case"]
        with open(os.path.join(outdir, f"{cid}.out"), "w") as f:
            json.dump({"forecasts": [{"case": cid, "price": guess}]}, f)

if __name__ == "__main__":
    main()
