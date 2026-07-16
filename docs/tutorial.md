# End-to-end CTA tutorial

This walkthrough takes you from raw prices all the way to **cash positions** using the
full TinyCTA pipeline:

```
prices ──▶ signal (osc / ma_cross) ──▶ mu ──▶ Engine ──▶ cash_position
```

Every Python block on this page is executed and its output checked in the test suite
(`tests/tinycta/test_tutorial.py`), so the walkthrough stays runnable as the code
evolves. The illustrative table dumps (marked `+RHIZA_SKIP`) show representative output
and are not part of the validated run.

## 1. Build a price panel

The engine consumes a **wide** Polars frame: one `date` column plus one numeric column per
asset. Here we synthesise three correlated-looking price series from a seeded random
generator so the walkthrough is fully reproducible.

```python
import datetime

import numpy as np
import polars as pl

rng = np.random.default_rng(0)
n_days = 60
dates = [datetime.date(2020, 1, 1) + datetime.timedelta(days=i) for i in range(n_days)]

data = {"date": dates}
for asset in ["A", "B", "C"]:
    daily_returns = rng.normal(0.0003, 0.01, size=n_days)
    data[asset] = (100 * np.exp(np.cumsum(daily_returns))).tolist()

prices = pl.DataFrame(data)
print(prices.shape)
```

```result
(60, 4)
```

A peek at the first rows (illustrative):

```python +RHIZA_SKIP
print(prices.head(3))
# shape: (3, 4)
# ┌────────────┬───────────┬───────────┬───────────┐
# │ date       ┆ A         ┆ B         ┆ C         │
# │ ---        ┆ ---       ┆ ---       ┆ ---       │
# │ date       ┆ f64       ┆ f64       ┆ f64       │
# ╞════════════╪═══════════╪═══════════╪═══════════╡
# │ 2020-01-01 ┆ 100.5106  ┆ 99.9...   ┆ 100.1...  │
# │ 2020-01-02 ┆ 100.9...  ┆ 99.7...   ┆ 100.5...  │
# │ 2020-01-03 ┆ 101.2...  ┆ 100.1...  ┆ 100.9...  │
# └────────────┴───────────┴───────────┴───────────┘
```

## 2. Turn prices into a signal

`osc` is an analytically scaled EWMA-difference oscillator: positive when the fast EWMA is
above the slow one (an up-trend), negative otherwise. We compute it for every asset with a
single `with_columns` call. The same shape works with `ma_cross` if you prefer a discrete
`-1 / 0 / +1` crossover signal.

```python
from tinycta.osc import osc

signal = prices.with_columns(osc(pl.col(asset), fast=8, slow=24).alias(asset) for asset in ["A", "B", "C"])
print(signal.columns)
```

```result
['date', 'A', 'B', 'C']
```

## 3. Use the signal as expected returns (`mu`)

The `Engine` expects a `mu` frame — the per-asset expected returns that drive position
sizing — **aligned to `prices`**: identical shape and identical column names. A trend
follower simply feeds the signal in as `mu`, so the oscillator frame from step 2 is exactly
what we need.

```python
mu = signal
print(mu.shape == prices.shape and mu.columns == prices.columns)
```

```result
True
```

## 4. Configure and run the Engine

`Config` is a frozen, validated model: `vola` and `corr` are EWMA lookbacks (`corr >= vola`),
`clip` bounds the volatility-adjusted returns, and `shrink ∈ [0, 1]` pulls the correlation
matrix towards the identity for numerical stability. The `Engine` then walks forward through
time and, at each timestamp, solves a correlation-shrinkage-optimised system to produce a
cash position per asset.

```python
from tinycta.config import Config
from tinycta.engine import Engine

cfg = Config(vola=20, corr=20, clip=4.2, shrink=0.5)
engine = Engine(prices=prices, mu=mu, cfg=cfg)
print(engine.assets)
```

```result
['A', 'B', 'C']
```

## 5. Read off the cash positions

`cash_position` returns the original frame (keeping `date`) with each asset column replaced
by its per-timestamp cash position. The first `corr` rows are warmup and come back as `NaN`;
every date **after** the warmup — including the most recent one — carries a position.

```python
positions = engine.cash_position
print(positions.shape)

# Warmup leaves the first `corr` dates as NaN; the rest are populated.
n_finite = positions.filter(pl.col("A").is_finite()).height
print(n_finite, n_finite == n_days - cfg.corr)

# The latest date always has a position you could trade on.
print(bool(np.isfinite(positions["A"][-1])))
```

```result
(60, 4)
40 True
True
```

A peek at the most recent positions (illustrative values):

```python +RHIZA_SKIP
print(positions.tail(3))
# shape: (3, 4)
# ┌────────────┬───────────┬───────────┬──────────┐
# │ date       ┆ A         ┆ B         ┆ C        │
# │ ---        ┆ ---       ┆ ---       ┆ ---      │
# │ date       ┆ f64       ┆ f64       ┆ f64      │
# ╞════════════╪═══════════╪═══════════╪══════════╡
# │ 2020-02-27 ┆ ...       ┆ ...       ┆ ...      │
# │ 2020-02-28 ┆ ...       ┆ ...       ┆ ...      │
# │ 2020-02-29 ┆ 106.0518  ┆ 11.8771   ┆ 3.5441   │
# └────────────┴───────────┴───────────┴──────────┘
```

## Where to go next

- Swap `osc` for [`ma_cross`](api/ewma.md) to use a discrete crossover signal.
- Inspect the intermediate quantities the engine exposes: `engine.ret_adj`,
  `engine.vola`, and `engine.cor` (see the [Engine API](api/engine.md)).
- Tune `fast` / `slow` / `Config` parameters automatically with the
  [hyperparameter-optimisation layer](api/hyper.md).
