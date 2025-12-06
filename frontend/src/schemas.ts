import { z } from 'zod';

// Patient validation
export const PatientSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  age: z.number().int().min(1).max(150, 'Invalid age'),
  gender: z.enum(['M', 'F'], { message: 'Must select gender' }),
  email: z.string().email('Invalid email'),
  phone: z.string().regex(/^\+?[0-9\s-]+$/, 'Invalid phone'),
});

// DAS28 scoring validation
export const DAS28Schema = z.object({
  tender_joints: z.number().int().min(0).max(28),
  swollen_joints: z.number().int().min(0).max(28),
  esr: z.number().positive('ESR must be positive'),
  vas: z.number().min(0).max(100, 'VAS must be 0-100'),
});

// Form submission handler
export function validatePatientForm(data: unknown) {
  try {
    return PatientSchema.parse(data);
  } catch (error: any) {
    if (error instanceof z.ZodError) {
      return { error: (error as any).errors[0].message };
    }
    throw error;
  }
}
