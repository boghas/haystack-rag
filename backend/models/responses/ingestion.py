from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from pathlib import Path
from models.statuses.process_status import ProcessStatus


class IngestionResponseModel(BaseModel):
    status: Literal[ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.RUNNING]
    nr_of_files: int
    files: List[Path]
    documents_written: Optional[float] = None
    error_message: Optional[str] = None