"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Union


# =========================
# Patient Schemas
# =========================

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    date_of_birth: Optional[Union[date, str]] = None
    mrn: str = Field(..., min_length=1)


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    date_of_birth: Optional[Union[date, str]] = None


class PatientResponse(PatientBase):
    id: int
    latest_visit_id: Optional[int] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# Visit Schemas
# =========================

class VisitCreate(BaseModel):
    patient_id: int
    visit_date: str
    visit_type: Optional[str] = None
    chief_complaint: Optional[str] = None


# =========================
# Medical Note Schemas
# =========================

class MedicalNoteExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)


class MedicalNoteDraftRequest(BaseModel):
    visit_id: int
    text: Optional[str] = None
    raw_text: Optional[str] = None

    def get_text(self) -> str:
        return self.text or self.raw_text or ''


class MedicalNoteFinalizeRequest(BaseModel):
    note_id: int
    text: Optional[str] = None
    final_text: Optional[str] = None

    def get_text(self) -> str:
        return self.text or self.final_text or ''


# =========================
# Joint Assessment Schemas
# =========================

class JointAssessmentItem(BaseModel):
    joint_id: str = Field(..., min_length=1)
    has_tenderness: Optional[bool] = None
    has_pain: Optional[bool] = None
    swelling_grade: Optional[int] = Field(None, ge=0, le=3)
    tenderness: Optional[int] = Field(None, ge=0, le=3)
    pain: Optional[int] = Field(None, ge=0, le=3)
    swelling: Optional[int] = Field(None, ge=0, le=3)

    def get_tenderness(self) -> int:
        if self.tenderness is not None:
            return self.tenderness
        return 1 if self.has_tenderness else 0

    def get_pain(self) -> int:
        if self.pain is not None:
            return self.pain
        return 1 if self.has_pain else 0

    def get_swelling(self) -> int:
        if self.swelling is not None:
            return self.swelling
        return self.swelling_grade or 0


class JointAssessmentCreate(BaseModel):
    visit_id: int
    joints: List[JointAssessmentItem]
