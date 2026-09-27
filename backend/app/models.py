from typing import Any

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    row_count: int
    columns: list[str]
    preview: list[dict[str, Any]]
    message: str
