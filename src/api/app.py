import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.common.exceptions import raise_http_exception
from src.api.common.predict import get_items_prediction
from src.api.config import settings
from src.api.schemas import OCRSource, PredictionOutput
from src.api.services.s3_service import save_to_s3
from src.api.tags import tags_metadata
from src.api.utils.custom_logging import logger

load_dotenv()

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs" if settings.ENABLE_SWAGGER else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)


@app.post("/predict-items", tags=["receipt-predictions"], status_code=status.HTTP_200_OK)
async def predict(
    file: UploadFile,
    prediction_source: str = OCRSource.ASPRISE,
) -> PredictionOutput:
    """Predict items from a receipt image."""
    try:
        if not file.content_type.startswith("image/"):
            raise_http_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        prediction = await get_items_prediction(file=file, prediction_source=prediction_source)

        save_to_s3(file=file, prediction=prediction)
        return prediction  # noqa: TRY300

    except httpx.TimeoutException:
        logger.error("Timeout while calling prediction service")
        raise_http_exception(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Prediction service timed out",
        )
    except httpx.RequestError as e:
        logger.error(f"Error making prediction request: {e!s}")
        raise_http_exception(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Error connecting to prediction service",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e!s}")
        raise_http_exception(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {e!s}",
        )


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to Snellie API!"}
