from enum import Enum


class ProcessStatus(Enum):
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"