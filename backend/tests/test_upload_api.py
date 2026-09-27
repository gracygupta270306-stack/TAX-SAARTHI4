import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.datastructures import UploadFile

from app.services.csv_processor import process_csv

SAMPLE_CSV = Path(__file__).parents[1] / "sample_data" / "sample_transactions.csv"


def test_sample_csv_is_validated_and_processed():
    with SAMPLE_CSV.open("rb") as sample_file:
        dataframe, preview = asyncio.run(
            process_csv(UploadFile(filename=SAMPLE_CSV.name, file=sample_file))
        )

    assert len(dataframe) > 0
    assert {"date", "description", "amount", "type"} <= set(dataframe.columns)
    assert len(preview) > 0


def test_csv_missing_required_columns_is_rejected():
    invalid_file = UploadFile(
        filename="invalid.csv",
        file=BytesIO(b"date,description\n2026-01-01,Salary\n"),
    )

    with pytest.raises(HTTPException) as error:
        asyncio.run(process_csv(invalid_file))

    assert error.value.status_code == 422
    assert "Missing required columns" in error.value.detail
