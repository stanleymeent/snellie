from __future__ import annotations

import base64
import io
import os

import httpx
from fastapi import UploadFile, status

from src.api.common.exceptions import raise_http_exception
from src.api.schemas import OCRSource, PredictionOutput
from src.api.utils.time_decorator import timeit


async def get_items_prediction(file: UploadFile, prediction_source: str) -> PredictionOutput:
    """Get the items prediction from the prediction service."""
    if prediction_source == OCRSource.KLIPPA.value:
        return await run_klippa_prediction(file=file)
    if prediction_source == OCRSource.ASPRISE.value:
        return await run_asprise_prediction(file=file)
    raise ValueError(f"Invalid OCR source provided: {prediction_source}")


@timeit
async def run_asprise_prediction(file: UploadFile) -> PredictionOutput:
    """Process an image file using the Asprise OCR API and return the receipt data.

    Args:
        file (UploadFile): The image file to process.

    Returns:
        PredictionOutput: The receipt data.
    """
    contents = await file.read()
    image_file = io.BytesIO(contents)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://ocr.asprise.com/api/v1/receipt",
            data={
                "client_id": "TEST",
                "recognizer": "auto",
                "ref_no": "ocr_python_123",
            },
            files={"file": image_file},
            timeout=10,
        )
        if response.status_code != 200:
            raise_http_exception(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"{OCRSource.ASPRISE.name} prediction service failed to process the image",
            )
        response_output = response.json()

    if len(response_output["receipts"]) > 1:
        raise ValueError("More than one receipt found in the image")

    receipt_data = response_output["receipts"][0]
    return PredictionOutput(
        image_id=file.filename,
        line_items=receipt_data["items"],
        total_amount=receipt_data["total"],
    )


@timeit
async def run_klippa_prediction(file: UploadFile) -> PredictionOutput:
    """Process an image file using the Klippa OCR API and return the receipt data.

    Args:
        file (UploadFile): The image file to process.

    Returns:
        PredictionOutput: The receipt data.
    """
    contents = await file.read()

    base64_data = base64.b64encode(contents).decode("ascii")

    async with httpx.AsyncClient() as client:
        payload = {"preset": {"slug": "snellie"}, "documents": [{"data": base64_data}]}
        response = await client.post(
            os.environ["KLIPPA_API_URL"],
            headers={"x-api-key": os.environ["KLIPPA_API_KEY"], "Content-Type": "application/json"},
            json=payload,
            timeout=10,
        )
        if response.status_code != 200:
            raise_http_exception(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"{OCRSource.KLIPPA.name} prediction service failed to process the image",
            )
        response_output = response.json()["data"]["components"]

    if len(response_output["line_items"]) > 1 or len(response_output["line_items"]["line_item_sections"]) > 1:
        raise ValueError("More than one receipt found in the image")

    line_items = response_output["line_items"]["line_item_sections"][0]["items"]
    financial = response_output["financial"]
    return PredictionOutput(
        image_id=file.filename,
        line_items=line_items,
        total_amount=financial["total_amount"],
        brand_name=financial.get("merchant", {}).get("brand_name", {}),
    )
