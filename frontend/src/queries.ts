import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PatientListResponseSchema, PatientResponseSchema, type PatientResponse } from './schemas';

// Fetch patients
export const usePatients = () => {
  return useQuery({
    queryKey: ['patients'],
    queryFn: async (): Promise<PatientResponse[]> => {
      const res = await fetch('/api/v1/patients');
      if (!res.ok) throw new Error('Failed to fetch patients');
      const data = await res.json();
      return PatientListResponseSchema.parse(data);
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes cache (renamed from cacheTime in v5)
  });
};

// Create patient mutation
export const useCreatePatient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newPatient: { mrn: string; first_name: string; last_name: string; date_of_birth?: string }) => {
      const res = await fetch('/api/v1/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPatient),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail?.[0]?.msg || errorData.error || 'Failed to create patient');
      }
      return res.json();
    },
    onSuccess: () => {
      // Refresh patient list after creation
      queryClient.invalidateQueries({ queryKey: ['patients'] });
    },
  });
};

// Get single patient
export const usePatient = (id: number) => {
  return useQuery({
    queryKey: ['patients', id],
    queryFn: async (): Promise<PatientResponse> => {
      const res = await fetch(`/api/v1/patients/${id}`);
      if (!res.ok) throw new Error('Failed to fetch patient');
      const data = await res.json();
      return PatientResponseSchema.parse(data);
    },
  });
};
