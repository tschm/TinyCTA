"""Exponentially weighted covariance matrix computation."""

from cvx.linalg.ewm_cov import NegativeWarmupError, ewm_covariance

__all__ = ["NegativeWarmupError", "ewm_covariance"]
