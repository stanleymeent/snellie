from __future__ import annotations

import io
import os

import httpx
from fastapi import UploadFile, status

from src.api.common.error_handling import raise_http_exception
from src.api.schemas import OCRSource, PredictionOutput
from src.utils import timeit


async def get_items_prediction(file: UploadFile, prediction_source: str) -> PredictionOutput:
    """Get the items prediction from the prediction service."""
    if prediction_source == OCRSource.KLIPPA.value:
        return await run_klippa_prediction(image_file=file)
    if prediction_source == OCRSource.ASPRISE.value:
        return await run_asprise_prediction(image_file=file)
    raise ValueError(f"Invalid OCR source provided: {prediction_source}")


@timeit
async def run_asprise_prediction(image_file: UploadFile) -> PredictionOutput:
    """Process an image file using the Asprise OCR API and return the receipt data.

    Args:
        image_file (UploadFile): The image file to process.

    Returns:
        Dict[str, Any]: A dictionary containing the receipt data.
    """
    contents = await image_file.read()
    image_file = io.BytesIO(contents)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            os.environ["ASPRISE_API_URL"],
            data={
                "client_id": "TEST",
                "recognizer": "auto",  # can be 'US', 'CA', 'JP', 'SG' or 'auto'
                "ref_no": "ocr_python_123",
            },
            files={"file": image_file},
            timeout=10,  # Adding a timeout to the request
        )
        if response.status_code != 200:
            raise_http_exception(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Prediction service failed to process the image",
            )
        response_output = response.json()

    if len(response_output["receipts"]) > 1:
        raise ValueError("More than one receipt found in the image")

    receipt_data = response_output["receipts"][0]
    return PredictionOutput(
        image_id=response_output["file_name"],
        line_items=receipt_data["items"],
        total_amount=receipt_data["total"],
        tax_amount=receipt_data["tax"],
    )


@timeit
async def run_klippa_prediction(image_file: UploadFile) -> PredictionOutput:
    """Process an image file using the Klippa OCR API and return the receipt data."""
    contents = await image_file.read()
    image_file = io.BytesIO(contents)
