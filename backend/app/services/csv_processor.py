from io import BytesIO

import pandas as pd
from fastapi import HTTPException, UploadFile

REQUIRED_COLUMNS = {"date", "description", "amount", "type"}


async def process_csv(file: UploadFile) -> tuple[pd.DataFrame, list[str]]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        dataframe = pd.read_csv(BytesIO(contents))
    except Exception as error:
        raise HTTPException(status_code=400, detail=f"Could not read CSV file: {error}") from error

    dataframe.columns = [str(column).strip().lower() for column in dataframe.columns]
    missing_columns = sorted(REQUIRED_COLUMNS - set(dataframe.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise HTTPException(
            status_code=422,
            detail=f"Missing required columns: {missing}. Required columns are date, description, amount, type.",
        )

    dataframe["amount"] = pd.to_numeric(dataframe["amount"], errors="coerce")
    invalid_rows = dataframe[dataframe["amount"].isna()].index.tolist()
    if invalid_rows:
        row_numbers = ", ".join(str(index + 2) for index in invalid_rows[:5])
        raise HTTPException(
            status_code=422,
            detail=f"Amount must be numeric. Check CSV row(s): {row_numbers}.",
        )

    dataframe["description"] = dataframe["description"].fillna("").astype(str).str.strip()
    dataframe["type"] = dataframe["type"].fillna("").astype(str).str.strip().str.lower()
    dataframe["date"] = dataframe["date"].fillna("").astype(str).str.strip()

    missing_details = dataframe[
        (dataframe["description"] == "") | (dataframe["date"] == "") | (dataframe["type"] == "")
    ]
    if not missing_details.empty:
        row_numbers = ", ".join(str(index + 2) for index in missing_details.index[:5])
        raise HTTPException(
            status_code=422,
            detail=f"Date, description, and type are required. Check CSV row(s): {row_numbers}.",
        )

    return dataframe, dataframe.head(10).to_dict(orient="records")
