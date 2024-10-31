import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.common.error_handling import raise_http_exception
from src.api.common.predict import get_items_prediction
from src.api.schemas import OCRSource, PredictionOutput
from src.api.tags import tags_metadata
from src.utils import logger

load_dotenv()

app = FastAPI(openapi_tags=tags_metadata)

origins = ["http://localhost", "http://localhost:3000", "http://localhost:3003"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post(
    "/predict-items",
    tags=["receipt-predictions"],
    status_code=status.HTTP_200_OK,
)
async def predict(
    file: UploadFile,
    prediction_source: str = OCRSource.ASPRISE,
) -> PredictionOutput:
    """Predict items from a receipt image."""
    try:
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

    from src.api.utils import find_free_port

    port = find_free_port()
    logger.info(f"Running API on port: {port}")
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)
