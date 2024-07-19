from pydantic import BaseModel

class CronJob(BaseModel):
    job: str
    name: str
    state: str = "paused"  # Default state

