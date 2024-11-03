from __future__ import annotations

from enum import Enum
from typing import Any, NewType

from pydantic import BaseModel

ImageID = NewType("ImageID", str)


class OCRSource(Enum):
    """The OCR source to use for the prediction."""

    KLIPPA = "klippa"
    ASPRISE = "asprise"


class PredictionOutput(BaseModel):
    """The output of the prediction service."""

    image_id: ImageID
    line_items: list[dict[str, Any]]
    total_amount: float
    brand_name: str | None = None
