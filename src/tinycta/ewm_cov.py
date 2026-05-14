"""Exponentially weighted covariance matrix computation."""

from cvx.linalg import NegativeWarmupError as NegativeWarmupError
from cvx.linalg import ewm_covariance as ewm_covariance
