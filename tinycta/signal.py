#    Copyright 2023 Thomas Schmelzer
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""signal"""

from __future__ import annotations

import numpy as np
import pandas as pd


# compute the oscillator
def osc(prices: pd.DataFrame, fast: int = 32, slow: int = 96, scaling: bool = True) -> pd.DataFrame:
    """
    oscillator

    Args:
        prices: a dataframe of prices
        fast: fast moving average factor, e.g. 32
        slow: slow moving average factor, e.g. 96
        scaling: true/false. If true scales with the standard deviation of the signal
        Strictly speacking this step is forward looking.

    Returns:
        oscillator as a DataFrame
    """
    diff = prices.ewm(com=fast - 1).mean() - prices.ewm(com=slow - 1).mean()
    if scaling:
        s = diff.std()
    else:
        s = 1

    return diff / s


def returns_adjust(price: pd.DataFrame, com: int = 32, min_periods: int = 300, clip: float = 4.2) -> pd.DataFrame:
    """
    volatility adjust the log-returns by a moving volatility, winsorize
    Args:
        price: a dataframe of prices
        com: center of mass for moving average for volatility
        min_periods: number of periods
        clip: winsorize at this level

    Returns:
        volatility adjusted and winsorized returns as a DataFrame
    """
    r = np.log(price).diff()
    return (r / r.ewm(com=com, min_periods=min_periods).std()).clip(-clip, +clip)


def shrink2id(matrix: np.ndarray, lamb: float = 1.0) -> np.ndarray:
    """
    Simple shrinkage towards the identity

    Args:
        matrix: the matrix A
        lamb: the shrinkage factor lambda

    Returns:
        A * lambda + (1 - lambda) * I
        where I is the identity matrix
    """
    return matrix * lamb + (1 - lamb) * np.eye(N=matrix.shape[0])
