from pydantic import BaseModel


class IssueCreate(BaseModel):
    issue_ref: str
    machine_id: int
    title: str
    description: str
    severity: str
    status: str