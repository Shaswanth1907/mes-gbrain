from pydantic import BaseModel


class MachineCreate(BaseModel):
    machine_ref: str
    machine_code: str
    name: str
    location: str
    status: str