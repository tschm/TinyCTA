"""Configuration model for the Basanos engine."""

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class Config(BaseModel):
    """Configuration for correlation-aware position optimization (Basanos engine)."""

    vola: int = Field(..., gt=0)
    corr: int = Field(..., gt=0)
    clip: float = Field(..., gt=0.0)
    shrink: float = Field(..., ge=0.0, le=1.0)

    model_config = {"frozen": True, "extra": "forbid"}

    @field_validator("corr")
    @classmethod
    def corr_greater_than_vola(cls, v: int, info: ValidationInfo) -> int:
        """Enforce corr >= vola for numerical stability."""
        vola = info.data.get("vola") if hasattr(info, "data") else None
        if vola is not None and v < vola:
            raise ValueError
        return v
