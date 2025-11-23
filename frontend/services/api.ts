import { API_CONFIG } from '../config/api';
import type { Patient, Visit, MedicalNote, JointAssessment, APIError } from '../types';

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error: APIError = await response.json();
        throw new Error(error.error || 'API request failed');
      }

      return response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Patients
  async createPatient(data: Omit<Patient, 'id' | 'created_at'>) {
    return this.request<{ id: number; message: string }>('/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPatient(id: number) {
    return this.request<Patient>(`/patients/${id}`);
  }

  // Visits
  async createVisit(data: Omit<Visit, 'id' | 'created_at'>) {
    return this.request<{ id: number; message: string }>('/visits', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getVisit(id: number) {
    return this.request<Visit>(`/visits/${id}`);
  }

  // Medical Notes
  async saveDraft(visitId: number, text: string) {
    return this.request<{
      success: boolean;
      note_id: number;
      status: string;
      draft_saved_at: string;
      message: string;
    }>('/medical_notes/draft', {
      method: 'POST',
      body: JSON.stringify({ visit_id: visitId, text }),
    });
  }

  async finalizeNote(noteId: number, text: string) {
    return this.request<{
      success: boolean;
      note_id: number;
      status: string;
      signed_at: string;
      entities_extracted: number;
      processing_time_ms: number;
      entities: any[];
      message: string;
    }>('/medical_notes/finalize', {
      method: 'POST',
      body: JSON.stringify({ note_id: noteId, text }),
    });
  }

  async getNote(id: number) {
    return this.request<MedicalNote>(`/medical_notes/${id}`);
  }

  // Joint Assessments
  async saveJointAssessment(visitId: number, joints: Omit<JointAssessment, 'id' | 'assessed_at'>[]) {
    return this.request<{
      success: boolean;
      visit_id: number;
      joints_saved: number;
      message: string;
    }>('/joint_assessments', {
      method: 'POST',
      body: JSON.stringify({ visit_id: visitId, joints }),
    });
  }

  async getJointAssessmentsByVisit(visitId: number) {
    return this.request<{
      visit_id: number;
      joints: JointAssessment[];
      total_joints: number;
    }>(`/joint_assessments/visit/${visitId}`);
  }

  // Voice Recognition
  async loadVoskModel() {
    return this.request<{ status: string; message: string }>('/voice/load-model', {
      method: 'POST',
    });
  }

  async transcribeAudio(audioFile: File) {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const url = `${this.baseURL}/voice/transcribe`;
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Transcription failed');
    }

    return response.json();
  }

  // Health Check
  async healthCheck() {
    return this.request<{ status: string; environment: string; version: string }>('/health');
  }
}

export const api = new APIClient();
