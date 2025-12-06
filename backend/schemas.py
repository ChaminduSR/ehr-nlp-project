from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional, List, Union

# =========================
# Patient Schemas
# =========================

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    date_of_birth: Optional[Union[date, str]] = None  # Accept both date and string from DB
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
    visit_date: str  # ISO date string
    visit_type: Optional[str] = None
    chief_complaint: Optional[str] = None


class VisitResponse(BaseModel):
    id: int
    patient_id: int
    visit_date: str
    visit_type: Optional[str] = None
    chief_complaint: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# Medical Note Schemas
# =========================

class MedicalNoteExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw clinical text to extract entities from")


class MedicalNoteDraftRequest(BaseModel):
    visit_id: int
    text: Optional[str] = Field(None, description="Note text (alternative to raw_text)")
    raw_text: Optional[str] = Field(None, description="Note text")

    @field_validator('raw_text', mode='before')
    @classmethod
    def set_raw_text_from_text(cls, v, info):
        # If raw_text not provided, it will be set from text in model_validator
        return v

    def get_text(self) -> str:
        """Get the note text from either field"""
        return self.text or self.raw_text or ''


class MedicalNoteFinalizeRequest(BaseModel):
    note_id: int
    text: Optional[str] = Field(None, description="Final note text (alternative to final_text)")
    final_text: Optional[str] = None

    def get_text(self) -> str:
        """Get the note text from either field"""
        return self.text or self.final_text or ''


class MedicalNoteResponse(BaseModel):
    id: int
    visit_id: int
    raw_text: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# Joint Assessment Schemas
# =========================

class JointAssessmentItem(BaseModel):
    joint_id: str = Field(..., min_length=1)
    # Accept both naming conventions from frontend
    has_tenderness: Optional[bool] = None
    has_pain: Optional[bool] = None
    swelling_grade: Optional[int] = Field(None, ge=0, le=3)
    # Also accept the simplified integer format
    tenderness: Optional[int] = Field(None, ge=0, le=3)
    pain: Optional[int] = Field(None, ge=0, le=3)
    swelling: Optional[int] = Field(None, ge=0, le=3)

    def get_tenderness(self) -> int:
        """Get tenderness as int (0 or 1+)"""
        if self.tenderness is not None:
            return self.tenderness
        return 1 if self.has_tenderness else 0

    def get_pain(self) -> int:
        """Get pain as int (0 or 1+)"""
        if self.pain is not None:
            return self.pain
        return 1 if self.has_pain else 0

    def get_swelling(self) -> int:
        """Get swelling grade"""
        if self.swelling is not None:
            return self.swelling
        return self.swelling_grade or 0


class JointAssessmentCreate(BaseModel):
    visit_id: int
    joints: List[JointAssessmentItem]


class JointAssessmentResponse(BaseModel):
    visit_id: int
    joints: List[JointAssessmentItem]
    das28_score: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# =========================
# NLP Response Schemas
# =========================

class EntityItem(BaseModel):
    text: str
    type: str
    start: int
    end: int
    is_negated: bool = False


class NLPExtractionResponse(BaseModel):
    model_config = {'protected_namespaces': ()}

    success: bool
    entities: List[EntityItem]
    entity_count: int
    processing_time_ms: float
    model_version: str
