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


def test_corr_less_than_vola_message_is_exact():
    """The corr<vola error carries the exact, unwrapped message text.

    Compared exactly (including pydantic's ``Value error,`` prefix) so that a
    mutated message string or a dropped message is detected.
    """
    with pytest.raises(ValidationError) as exc:
        Config(vola=200, corr=100, clip=4.2, shrink=0.5)
    assert exc.value.errors()[0]["msg"] == "Value error, corr (100) must be >= vola (200) for numerical stability"


def test_small_positive_bounds_are_valid():
    """vola, corr and clip accept any value strictly greater than 0.

    Pins the lower bounds at 0 (not 1): ``vola=1``, ``corr=1`` and ``clip=0.5``
    are all valid.
    """
    cfg = Config(vola=1, corr=1, clip=0.5, shrink=0.0)
    assert cfg.vola == 1
    assert cfg.corr == 1
    assert cfg.clip == 0.5


def test_corr_is_required():
    """Corr is a required field (no default); omitting it raises."""
    with pytest.raises(ValidationError):
        Config(vola=50, clip=4.2, shrink=0.5)  # type: ignore[call-arg]


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
        Config(vola=50, corr=200, clip=4.2, shrink=0.5, aum=1e6)  # ty: ignore[unknown-argument]
