from pydantic import BaseModel
from datetime import date
from typing import Optional, List, Union

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Union[date, str]  # Accept both date and string from DB
    mrn: str

class PatientCreate(PatientBase):
    pass

class PatientResponse(PatientBase):
    id: int
    latest_visit_id: Optional[int] = None

    class Config:
        from_attributes = True
