"""Configuration model for the Basanos engine."""

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Config(BaseModel):
    """Configuration for correlation-aware position optimization (Basanos engine).

    Example:
        >>> from pydantic import ValidationError
        >>> from tinycta.config import Config
        >>> cfg = Config(vola=32, corr=64, clip=4.2, shrink=0.5)
        >>> cfg.vola, cfg.corr, cfg.clip, cfg.shrink
        (32, 64, 4.2, 0.5)

        The model is frozen, so a validated config cannot drift after construction:

        >>> try:
        ...     cfg.vola = 16
        ... except ValidationError:
        ...     print("frozen")
        frozen

        ``corr`` must not be shorter than ``vola`` — a correlation window below the
        volatility window is numerically unstable:

        >>> try:
        ...     Config(vola=64, corr=32, clip=4.2, shrink=0.5)
        ... except ValidationError:
        ...     print("corr must be >= vola")
        corr must be >= vola

        Windows are strictly positive, ``shrink`` lies in ``[0, 1]``, and unknown
        keys are rejected rather than silently ignored:

        >>> for bad in ({"vola": 0}, {"shrink": 1.5}, {"typo": 1}):
        ...     kwargs = {"vola": 32, "corr": 64, "clip": 4.2, "shrink": 0.5} | bad
        ...     try:
        ...         Config(**kwargs)
        ...     except ValidationError:
        ...         print("rejected", sorted(bad))
        rejected ['vola']
        rejected ['shrink']
        rejected ['typo']
    """

    vola: int = Field(..., gt=0)
    corr: int = Field(..., gt=0)
    clip: float = Field(..., gt=0.0)
    shrink: float = Field(..., ge=0.0, le=1.0)

    model_config = {"frozen": True, "extra": "forbid"}

    @field_validator("corr")
    @classmethod  # pragma: no mutate - pydantic field_validator behaves identically without classmethod
    def corr_greater_than_vola(cls, v: int, info: ValidationInfo) -> int:
        """Enforce corr >= vola for numerical stability."""
        vola = info.data.get("vola") if hasattr(info, "data") else None
        if vola is not None and v < vola:
            msg = f"corr ({v}) must be >= vola ({vola}) for numerical stability"
            raise ValueError(msg)
        return v
