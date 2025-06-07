from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid
import time


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AgentTask(BaseModel):
    id: str
    type: str
    input: Dict[str, Any]
    status: TaskStatus
    timestamp: float
    output: Optional[Any] = None

    def mark_completed(self, output: Any):
        self.status = TaskStatus.COMPLETED
        self.output = output

    @classmethod
    def create(cls, type: str, input: Dict[str, Any]):
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            input=input,
            status=TaskStatus.PENDING,
            timestamp=time.time(),
        )
