# btc-cent-forecast

Entry for [make.fun btc-cent-forecast-01](https://make.fun/bounty/btc-cent-forecast-01).

Forecasts Bitcoin's USDC price 240 minutes ahead from 4,320 one-minute closes.

## Model

Shrunk 12h momentum over persistence, constants fixed a priori (no future-data fitting):

```
guess = last_close + 0.6 * ((last - close_720min_ago) / 720) * 240
```

Deterministic, stdlib-only Python 3.13, ~0.02s per case.
