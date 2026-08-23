import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CollectorState(enum.StrEnum):
    HEALTHY = "HEALTHY"

class CollectorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    state: str
    created_at: datetime

class Collector:
    id: int
    state: CollectorState
    created_at: datetime

c = Collector()
c.id = 1
c.state = CollectorState.HEALTHY
c.created_at = datetime.now()

try:
    schema = CollectorSchema.model_validate(c)
    print("SUCCESS")
except Exception as e:
    print(e)
