from fastapi import APIRouter, File, UploadFile

from app.models import UploadResponse
from app.services.csv_processor import process_csv
from app.services.session_store import save_transactions

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)) -> UploadResponse:
    dataframe, preview = await process_csv(file)
    save_transactions(dataframe)
    return UploadResponse(
        filename=file.filename or "uploaded.csv",
        row_count=len(dataframe),
        columns=list(dataframe.columns),
        preview=preview,
        message="CSV validated successfully. Analysis is ready to run.",
    )
