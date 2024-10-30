from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from src.utils import timeit


@timeit
def run(image_filename: str) -> dict[str, Any]:
    """Process an image file using the Asprise OCR API and return the receipt data.

    Args:
        image_filename (str): The path to the image file.

    Returns:
        Dict[str, Any]: A dictionary containing the receipt data.
    """
    receiptOcrEndpoint = "https://ocr.asprise.com/api/v1/receipt"
    with Path(image_filename).open("rb") as image_file:
        receipt_data = requests.post(
            receiptOcrEndpoint,
            data={
                "client_id": "TEST",
                "recognizer": "auto",  # can be 'US', 'CA', 'JP', 'SG' or 'auto'
                "ref_no": "ocr_python_123",
            },
            files={"file": image_file},
            timeout=10,  # Adding a timeout to the request
        )
    response = receipt_data.json()

    if len(response["receipts"]) > 1:
        raise ValueError("More than one receipt found in the image")

    receipt_data = response["receipts"][0]
    return {
        "image_id": response["file_name"],
        "line_items": receipt_data["items"],  # type: ignore[index]
        "total": receipt_data["total"],  # type: ignore[index]
        "tax": receipt_data["tax"],  # type: ignore[index]
    }


if __name__ == "__main__":
    folder_path = Path("data/custom")

    receipt_data_collection = [
        run(str(filename))
        for filename in sorted(folder_path.iterdir())
        if filename.suffix in (".jpg", ".jpeg", ".png")
    ]
