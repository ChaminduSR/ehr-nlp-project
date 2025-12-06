import { z } from 'zod';

// =========================
// API Response Schemas
// =========================

// Patient response from API
export const PatientResponseSchema = z.object({
  id: z.number(),
  mrn: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  date_of_birth: z.string().nullable(),
  latest_visit_id: z.number().nullable().optional(),
  created_at: z.string().optional(),
});

export type PatientResponse = z.infer<typeof PatientResponseSchema>;

// Patient list response
export const PatientListResponseSchema = z.array(PatientResponseSchema);

// Visit response from API
export const VisitResponseSchema = z.object({
  id: z.number(),
  patient_id: z.number(),
  visit_date: z.string(),
  visit_type: z.string().nullable().optional(),
  chief_complaint: z.string().nullable().optional(),
  created_at: z.string().optional(),
});

export type VisitResponse = z.infer<typeof VisitResponseSchema>;

// Medical note response
export const MedicalNoteResponseSchema = z.object({
  id: z.number(),
  visit_id: z.number(),
  raw_text: z.string().nullable().optional(),
  status: z.enum(['draft', 'finalized']).optional(),
  created_at: z.string().optional(),
  updated_at: z.string().optional(),
});

export type MedicalNoteResponse = z.infer<typeof MedicalNoteResponseSchema>;

// NLP extraction response
export const NLPExtractionResponseSchema = z.object({
  success: z.boolean(),
  entities: z.array(z.object({
    text: z.string(),
    type: z.string(),
    start: z.number(),
    end: z.number(),
    is_negated: z.boolean().optional(),
  })),
  entity_count: z.number(),
  processing_time_ms: z.number(),
  model_version: z.string(),
});

export type NLPExtractionResponse = z.infer<typeof NLPExtractionResponseSchema>;

// Joint assessment item
export const JointAssessmentItemSchema = z.object({
  id: z.number().optional(),
  joint_id: z.string(),
  tenderness: z.number().min(0).max(3),
  pain: z.number().min(0).max(3),
  swelling: z.number().min(0).max(3),
});

export type JointAssessmentItem = z.infer<typeof JointAssessmentItemSchema>;

// Joint assessment response
export const JointAssessmentResponseSchema = z.object({
  visit_id: z.number(),
  joints: z.array(JointAssessmentItemSchema),
  das28_score: z.number().nullable().optional(),
  created_at: z.string().optional(),
});

export type JointAssessmentResponse = z.infer<typeof JointAssessmentResponseSchema>;

// Analytics stats response
export const AnalyticsStatsResponseSchema = z.object({
  total_patients: z.number(),
  total_visits: z.number(),
  total_notes: z.number(),
  avg_das28: z.number().nullable().optional(),
});

export type AnalyticsStatsResponse = z.infer<typeof AnalyticsStatsResponseSchema>;

// =========================
// Form Validation Schemas (legacy)
// =========================

// Patient form validation (for creating/editing)
export const PatientFormSchema = z.object({
  mrn: z.string().min(1, 'MRN is required'),
  first_name: z.string().min(2, 'First name must be at least 2 characters'),
  last_name: z.string().min(2, 'Last name must be at least 2 characters'),
  date_of_birth: z.string().optional(),
});

export type PatientFormData = z.infer<typeof PatientFormSchema>;

// DAS28 scoring validation
export const DAS28Schema = z.object({
  tender_joints: z.number().int().min(0).max(28),
  swollen_joints: z.number().int().min(0).max(28),
  esr: z.number().positive('ESR must be positive'),
  vas: z.number().min(0).max(100, 'VAS must be 0-100'),
});

export type DAS28Data = z.infer<typeof DAS28Schema>;

// =========================
// Validation Helpers
// =========================

// Safe parse helper that returns typed result or throws
export function parseOrThrow<T>(schema: z.ZodSchema<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error('Validation failed:', result.error.errors);
    throw new Error(`Validation failed: ${result.error.errors[0]?.message}`);
  }
  return result.data;
}

// Safe parse helper that returns result with error info
export function safeParse<T>(schema: z.ZodSchema<T>, data: unknown): { success: true; data: T } | { success: false; error: string } {
  const result = schema.safeParse(data);
  if (!result.success) {
    return { success: false, error: result.error.errors[0]?.message ?? 'Validation failed' };
  }
  return { success: true, data: result.data };
}
