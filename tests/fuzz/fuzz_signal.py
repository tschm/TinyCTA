"""Fuzz the tinycta signal pipeline against arbitrary price series.

The signal functions (``osc``, ``ma_cross``, ``moving_absolute_deviation``,
``vol_adj``, ``adj_log_prices``) transform a polars price expression, and
``shrink2id`` shrinks a numpy matrix toward the identity. None should crash with
an unexpected exception on adversarial prices/parameters — they should compute a
result (possibly null/NaN) or raise a documented error. This harness exercises
that contract with coverage-guided input.

Run locally:
    pip install atheris numpy polars
    python tests/fuzz/fuzz_signal.py -atheris_runs=20000

Run in ClusterFuzzLite: this file is built by .clusterfuzzlite/build.sh.
"""

from __future__ import annotations

import contextlib
import sys

import atheris

# Pre-import the native dependencies OUTSIDE the instrumentation block. Atheris's
# import hook miscompiles parts of polars' Python machinery, so we let it load
# uninstrumented and instrument only the first-party package under test.
import numpy as np
import polars as pl

with atheris.instrument_imports():
    from tinycta.ewma import ma_cross
    from tinycta.osc import osc
    from tinycta.signal import moving_absolute_deviation, shrink2id
    from tinycta.util import adj_log_prices, vol_adj

_ALLOWED = (ValueError, TypeError, ZeroDivisionError, pl.exceptions.PolarsError)


def test_one_input(data: bytes) -> None:
    """Apply each signal transform to a fuzzed price series and matrix."""
    fdp = atheris.FuzzedDataProvider(data)
    n = fdp.ConsumeIntInRange(0, 24)
    prices = pl.DataFrame({"price": [fdp.ConsumeFloat() for _ in range(n)]})

    fast = fdp.ConsumeIntInRange(0, 8)
    slow = fdp.ConsumeIntInRange(0, 32)
    com = fdp.ConsumeIntInRange(1, 16)
    clip = fdp.ConsumeFloat()

    for build_expr in (
        lambda: osc(pl.col("price"), fast=fast, slow=slow),
        lambda: ma_cross(pl.col("price"), fast=fast, slow=slow),
        lambda: moving_absolute_deviation(pl.col("price"), com=com),
        lambda: vol_adj(pl.col("price"), vola=com, clip=clip),
        lambda: adj_log_prices(pl.col("price"), vola=com, clip=clip),
    ):
        with contextlib.suppress(_ALLOWED):
            prices.select(build_expr())

    # Pure-numpy path: shrink a fuzzed square matrix toward the identity.
    m = fdp.ConsumeIntInRange(0, 6)
    matrix = np.array([fdp.ConsumeFloat() for _ in range(m * m)], dtype=np.float64).reshape(m, m)
    with contextlib.suppress(_ALLOWED):
        shrink2id(matrix, fdp.ConsumeProbability())


def main() -> None:
    """Run the Atheris fuzz loop."""
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
