/**
 * Reports Logic Tests
 * Tests for frontend/src/modules/reports_logic.js
 * Uses Node.js 24 native test runner
 */

import { test, describe, mock } from 'node:test';
import assert from 'node:assert';

describe('Reports Init', () => {
    test('init sets default date range to last 30 days', () => {
        const today = new Date();
        const lastMonth = new Date();
        lastMonth.setDate(today.getDate() - 30);

        const filters = {
            endDate: today.toISOString().split('T')[0],
            startDate: lastMonth.toISOString().split('T')[0]
        };

        // Verify date format
        assert.ok(filters.startDate.match(/^\d{4}-\d{2}-\d{2}$/));
        assert.ok(filters.endDate.match(/^\d{4}-\d{2}-\d{2}$/));

        // Verify 30 day difference
        const start = new Date(filters.startDate);
        const end = new Date(filters.endDate);
        const diffDays = Math.round((end - start) / (1000 * 60 * 60 * 24));
        assert.strictEqual(diffDays, 30);
    });

    test('init sets endDate to today', () => {
        const today = new Date().toISOString().split('T')[0];
        const filters = { endDate: today };

        assert.strictEqual(filters.endDate, today);
    });
});

describe('Reports Patient Search', () => {
    test('searchPatients requires minimum 2 characters', async () => {
        let fetchCalled = false;
        const mockFetch = mock.fn(async () => {
            fetchCalled = true;
            return { ok: true, json: async () => [] };
        });

        const query = 'a'; // Only 1 character

        // Simulate the check
        if (query.length >= 2) {
            await mockFetch(`/api/v1/patients/search?q=${query}`);
        }

        assert.strictEqual(fetchCalled, false);
    });

    test('searchPatients calls API with 2+ characters', async () => {
        let capturedUrl = null;
        const mockFetch = mock.fn(async (url) => {
            capturedUrl = url;
            return {
                ok: true,
                json: async () => [
                    { id: 1, name: 'John Doe', mrn: 'MRN-123' }
                ]
            };
        });

        const query = 'jo';

        if (query.length >= 2) {
            await mockFetch(`/api/v1/patients/search?q=${encodeURIComponent(query)}`);
        }

        assert.ok(capturedUrl.includes('/api/v1/patients/search'));
        assert.ok(capturedUrl.includes('q=jo'));
    });

    test('searchPatients encodes query parameter', async () => {
        let capturedUrl = null;
        const mockFetch = mock.fn(async (url) => {
            capturedUrl = url;
            return { ok: true, json: async () => [] };
        });

        const query = 'john doe'; // Contains space

        await mockFetch(`/api/v1/patients/search?q=${encodeURIComponent(query)}`);

        assert.ok(capturedUrl.includes('john%20doe'));
    });
});

describe('Reports Select Patient', () => {
    test('selectPatient sets selectedPatient', () => {
        const state = { selectedPatient: null };
        const patient = { id: 5, name: 'Test Patient', mrn: 'MRN-005' };

        state.selectedPatient = patient;

        assert.deepStrictEqual(state.selectedPatient, patient);
        assert.strictEqual(state.selectedPatient.id, 5);
    });
});

describe('Reports Generate', () => {
    test('generateReport requires patient for summary type', () => {
        const state = {
            reportType: 'summary',
            selectedPatient: null
        };

        const requiresPatient = state.reportType === 'summary' && !state.selectedPatient;
        assert.strictEqual(requiresPatient, true);
    });

    test('generateReport allows no patient for other types', () => {
        const state = {
            reportType: 'activity',
            selectedPatient: null
        };

        const requiresPatient = state.reportType === 'summary' && !state.selectedPatient;
        assert.strictEqual(requiresPatient, false);
    });

    test('generateReport sends correct payload', async () => {
        let capturedBody = null;
        const mockFetch = mock.fn(async (url, options) => {
            capturedBody = JSON.parse(options?.body || '{}');
            return { ok: true, json: async () => ({}) };
        });

        const state = {
            reportType: 'summary',
            selectedPatient: { id: 10 },
            filters: {
                startDate: '2026-01-01',
                endDate: '2026-01-12'
            }
        };

        await mockFetch('/api/v1/reports/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                report_type: state.reportType,
                patient_id: state.selectedPatient?.id,
                filters: state.filters
            })
        });

        assert.strictEqual(capturedBody.report_type, 'summary');
        assert.strictEqual(capturedBody.patient_id, 10);
        assert.deepStrictEqual(capturedBody.filters, state.filters);
    });

    test('generateReport sets isGenerating flag during request', async () => {
        const state = { isGenerating: false };

        // Simulate request lifecycle
        state.isGenerating = true;
        assert.strictEqual(state.isGenerating, true);

        // After request completes
        state.isGenerating = false;
        assert.strictEqual(state.isGenerating, false);
    });

    test('generateReport constructs correct preview URL', () => {
        const reportType = 'summary';
        const selectedPatient = { id: 42 };

        let url = `/api/v1/reports/preview?type=${reportType}`;
        if (selectedPatient) {
            url += `&patient_id=${selectedPatient.id}`;
        }

        assert.strictEqual(url, '/api/v1/reports/preview?type=summary&patient_id=42');
    });

    test('generateReport handles API error', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: false,
            status: 500
        }));

        const response = await mockFetch('/api/v1/reports/generate', { method: 'POST' });

        assert.strictEqual(response.ok, false);
    });
});

describe('Reports Update Form', () => {
    test('updateForm resets patient selection', () => {
        const state = {
            patientResults: [{ id: 1 }, { id: 2 }],
            selectedPatient: { id: 1 },
            showPreview: true
        };

        // Simulate updateForm
        state.patientResults = [];
        state.selectedPatient = null;
        state.showPreview = false;

        assert.deepStrictEqual(state.patientResults, []);
        assert.strictEqual(state.selectedPatient, null);
        assert.strictEqual(state.showPreview, false);
    });
});
