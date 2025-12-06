import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch patients
export const usePatients = () => {
  return useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const res = await fetch('/api/v1/patients');
      if (!res.ok) throw new Error('Failed to fetch patients');
      return res.json();
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes cache (renamed from cacheTime in v5)
  });
};

// Create patient mutation
export const useCreatePatient = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newPatient) => {
      const res = await fetch('/api/v1/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newPatient),
      });
      if (!res.ok) throw new Error('Failed to create patient');
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
    queryFn: async () => {
      const res = await fetch(`/api/v1/patients/${id}`);
      if (!res.ok) throw new Error('Failed to fetch patient');
      return res.json();
    },
  });
};
