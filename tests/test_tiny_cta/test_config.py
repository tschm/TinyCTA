"""Tests for tinycta.config.Config."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from tinycta.config import Config


def test_valid_config():
    """Config accepts valid field values."""
    cfg = Config(vola=50, corr=200, clip=4.2, shrink=0.5)
    assert cfg.vola == 50
    assert cfg.corr == 200


def test_corr_equal_to_vola_is_valid():
    """Corr == vola is allowed."""
    cfg = Config(vola=50, corr=50, clip=4.2, shrink=0.0)
    assert cfg.corr == cfg.vola


def test_corr_less_than_vola_raises():
    """Config rejects corr < vola."""
    with pytest.raises(ValidationError):
        Config(vola=200, corr=100, clip=4.2, shrink=0.5)


def test_vola_zero_raises():
    """Config rejects vola <= 0."""
    with pytest.raises(ValidationError):
        Config(vola=0, corr=10, clip=4.2, shrink=0.5)


def test_clip_zero_raises():
    """Config rejects clip <= 0."""
    with pytest.raises(ValidationError):
        Config(vola=50, corr=50, clip=0.0, shrink=0.5)


def test_shrink_above_one_raises():
    """Config rejects shrink > 1."""
    with pytest.raises(ValidationError):
        Config(vola=50, corr=50, clip=4.2, shrink=1.1)


def test_config_is_frozen():
    """Config is immutable after creation."""
    cfg = Config(vola=50, corr=200, clip=4.2, shrink=0.5)
    with pytest.raises(ValidationError):
        cfg.vola = 99  # type: ignore[misc]


def test_extra_fields_forbidden():
    """Config rejects unknown extra fields."""
    with pytest.raises(ValidationError):
        Config(vola=50, corr=200, clip=4.2, shrink=0.5, aum=1e6)  # type: ignore[call-arg]
