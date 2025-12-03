// Match backend schema exactly
export interface Patient {
  id: number;
  mrn: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  created_at: string;
}

export interface Visit {
  id: number;
  patient_id: number;
  visit_date: string;
  visit_type: string;
  created_at: string;
}

export interface MedicalNote {
  id: number;
  visit_id: number;
  note_text: string;
  status: 'draft' | 'finalized';
  draft_saved_at?: string;
  signed_at?: string;
  signed_by?: number;
  entity_count?: number;
  processing_time_ms?: number;
  created_at: string;
}

export interface JointAssessment {
  id?: number;
  visit_id: number;
  joint_id: string;
  has_tenderness: boolean;
  has_pain: boolean;
  swelling_grade: 0 | 1 | 2 | 3;
  assessed_at?: string;
}

export interface APIError {
  error: string;
  message?: string;
}
