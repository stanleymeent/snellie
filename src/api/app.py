import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.auth import get_current_user
from src.api.common.exceptions import raise_http_exception
from src.api.common.predict import get_items_prediction
from src.api.schemas import OCRSource, PredictionOutput
from src.api.tags import tags_metadata
from src.config import settings
from src.utils import logger

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

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/predict-items", tags=["receipt-predictions"], status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_user)])
async def predict(
    file: UploadFile,
    prediction_source: str = OCRSource.KLIPPA,
    current_user: dict = Depends(get_current_user),  # noqa: B008
) -> PredictionOutput:
    """Predict items from a receipt image."""
    try:
        user_id = current_user["uid"]
        logger.info("Prediction request %s", user_id)

        if not file.content_type.startswith("image/"):
            raise_http_exception(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

        return await get_items_prediction(file=file, prediction_source=prediction_source)

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
            detail="Internal server error",
        )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> RedirectResponse:
    """Redirect to the favicon."""
    return RedirectResponse(url="static/favicon.ico")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to Snellie API!"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ["PORT"])
    logger.info(f"Running API on port: {port}")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)
