import io

import boto3
from fastapi import UploadFile
from PIL import Image

from src.api.config import settings
from src.api.schemas import PredictionOutput

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


def save_to_s3(file: UploadFile, prediction: PredictionOutput) -> None:
    """Save the prediction output and compressed photo to S3."""
    prediction_key = f"predictions/{file.filename}.json"
    s3_client.put_object(
        Bucket=settings.AWS_S3_BUCKET_NAME,
        Key=prediction_key,
        Body=prediction.json(),
        ContentType="application/json",
    )

    image = Image.open(file.file)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=50)
    buffer.seek(0)
    compressed_key = f"compressed/{file.filename}"
    s3_client.put_object(
        Bucket=settings.AWS_S3_BUCKET_NAME,
        Key=compressed_key,
        Body=buffer,
        ContentType="image/jpeg",
    )
