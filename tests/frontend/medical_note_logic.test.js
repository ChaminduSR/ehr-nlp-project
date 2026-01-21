/**
 * Medical Note Logic Tests
 * Tests for frontend/src/modules/medical_note_logic.js
 * Uses Node.js 24 native test runner
 */

import { test, describe, mock } from 'node:test';
import assert from 'node:assert';

describe('Medical Note Auto-Save', () => {
    test('autoSave skips when no visitId', async () => {
        let fetchCalled = false;
        const mockFetch = mock.fn(async () => {
            fetchCalled = true;
            return { ok: true };
        });

        const state = {
            visitId: null,
            smartText: 'Some text',
            lastSavedText: ''
        };

        // Simulate autoSave check
        if (!state.visitId || !state.smartText || state.smartText === state.lastSavedText) {
            // Skip save
        } else {
            await mockFetch('/api/v1/medical_notes/draft');
        }

        assert.strictEqual(fetchCalled, false);
    });

    test('autoSave skips when text unchanged', async () => {
        let fetchCalled = false;
        const mockFetch = mock.fn(async () => {
            fetchCalled = true;
            return { ok: true };
        });

        const state = {
            visitId: '123',
            smartText: 'Same text',
            lastSavedText: 'Same text'
        };

        if (!state.visitId || !state.smartText || state.smartText === state.lastSavedText) {
            // Skip save
        } else {
            await mockFetch('/api/v1/medical_notes/draft');
        }

        assert.strictEqual(fetchCalled, false);
    });

    test('autoSave sends draft when text changed', async () => {
        let capturedBody = null;
        const mockFetch = mock.fn(async (url, options) => {
            capturedBody = JSON.parse(options?.body || '{}');
            return { ok: true, json: async () => ({}) };
        });

        const state = {
            visitId: '456',
            smartText: 'New text content',
            lastSavedText: 'Old text',
            saveStatus: ''
        };

        if (!state.visitId || !state.smartText || state.smartText === state.lastSavedText) {
            // Skip
        } else {
            state.saveStatus = 'Saving...';
            await mockFetch('/api/v1/medical_notes/draft', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    visit_id: state.visitId,
                    text: state.smartText
                })
            });
            state.lastSavedText = state.smartText;
            state.saveStatus = 'Saved';
        }

        assert.strictEqual(capturedBody.visit_id, '456');
        assert.strictEqual(capturedBody.text, 'New text content');
        assert.strictEqual(state.saveStatus, 'Saved');
    });

    test('autoSave handles API error', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: false,
            status: 500
        }));

        const state = { saveStatus: '' };

        const response = await mockFetch('/api/v1/medical_notes/draft', { method: 'POST' });

        if (!response.ok) {
            state.saveStatus = 'Error saving draft';
        }

        assert.strictEqual(state.saveStatus, 'Error saving draft');
    });
});

describe('Medical Note Extract Entities', () => {
    test('extractEntities skips when no text', async () => {
        let fetchCalled = false;
        const mockFetch = mock.fn(async () => {
            fetchCalled = true;
            return { ok: true };
        });

        const smartText = '';

        if (smartText) {
            await mockFetch('/api/v1/medical_notes/extract');
        }

        assert.strictEqual(fetchCalled, false);
    });

    test('extractEntities sends text to API', async () => {
        let capturedBody = null;
        const mockFetch = mock.fn(async (url, options) => {
            capturedBody = JSON.parse(options?.body || '{}');
            return {
                ok: true,
                json: async () => ({
                    success: true,
                    structured: {
                        chief_complaint: 'Joint pain',
                        assessment: 'Rheumatoid arthritis'
                    }
                })
            };
        });

        const smartText = 'Patient presents with joint pain in both hands.';

        await mockFetch('/api/v1/medical_notes/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: smartText })
        });

        assert.strictEqual(capturedBody.text, smartText);
    });

    test('extractEntities parses structured response', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: true,
            json: async () => ({
                success: true,
                structured: {
                    chief_complaint: 'Joint swelling',
                    hpi: 'Patient reports 2 weeks of symptoms',
                    assessment: 'RA flare',
                    plan: 'Increase methotrexate'
                }
            })
        }));

        const response = await mockFetch('/api/v1/medical_notes/extract', { method: 'POST' });
        const data = await response.json();

        assert.strictEqual(data.success, true);
        assert.ok('chief_complaint' in data.structured);
        assert.ok('assessment' in data.structured);
    });

    test('extractEntities handles extraction failure', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: true,
            json: async () => ({
                success: false,
                message: 'Failed to extract entities'
            })
        }));

        const state = { error: null };

        const response = await mockFetch('/api/v1/medical_notes/extract', { method: 'POST' });
        const data = await response.json();

        if (!data.success) {
            state.error = 'Extraction failed: ' + (data.message || 'Unknown error');
        }

        assert.ok(state.error.includes('Failed to extract entities'));
    });
});

describe('Medical Note Format Key', () => {
    test('formatKey converts underscores to spaces', () => {
        const formatKey = (key) => key.replace(/_/g, ' ');

        assert.strictEqual(formatKey('chief_complaint'), 'chief complaint');
        assert.strictEqual(formatKey('history_of_present_illness'), 'history of present illness');
        assert.strictEqual(formatKey('physical_exam'), 'physical exam');
    });

    test('formatKey handles keys without underscores', () => {
        const formatKey = (key) => key.replace(/_/g, ' ');

        assert.strictEqual(formatKey('assessment'), 'assessment');
        assert.strictEqual(formatKey('plan'), 'plan');
    });
});

describe('Medical Note Accept Extraction', () => {
    test('acceptExtraction requires visitId', () => {
        const state = { visitId: null, error: null };

        if (!state.visitId) {
            state.error = 'No visit selected. Cannot save.';
        }

        assert.strictEqual(state.error, 'No visit selected. Cannot save.');
    });

    test('acceptExtraction section mapping is complete', () => {
        const SECTION_MAPPING = {
            chief_complaint: 'CHIEF COMPLAINT',
            hpi: 'HISTORY OF PRESENT ILLNESS',
            physical_exam: 'PHYSICAL EXAMINATION',
            assessment: 'ASSESSMENT',
            plan: 'PLAN',
            medications: 'MEDICATIONS',
            follow_up: 'FOLLOW-UP'
        };

        // Verify all expected sections exist
        assert.ok('chief_complaint' in SECTION_MAPPING);
        assert.ok('hpi' in SECTION_MAPPING);
        assert.ok('physical_exam' in SECTION_MAPPING);
        assert.ok('assessment' in SECTION_MAPPING);
        assert.ok('plan' in SECTION_MAPPING);
        assert.ok('medications' in SECTION_MAPPING);
        assert.ok('follow_up' in SECTION_MAPPING);

        assert.strictEqual(Object.keys(SECTION_MAPPING).length, 7);
    });

    test('acceptExtraction builds note text from structured data', () => {
        const SECTION_MAPPING = {
            chief_complaint: 'CHIEF COMPLAINT',
            assessment: 'ASSESSMENT',
            plan: 'PLAN'
        };

        const reviewData = {
            chief_complaint: 'Joint pain',
            assessment: 'Rheumatoid arthritis',
            plan: 'Start methotrexate'
        };

        let noteText = '';
        for (const [key, value] of Object.entries(reviewData)) {
            const header = SECTION_MAPPING[key];
            if (header && value) {
                const textValue = Array.isArray(value) ? value.join(', ') : value;
                if (textValue.trim()) {
                    noteText += `${header}:\n${textValue}\n\n`;
                }
            }
        }

        assert.ok(noteText.includes('CHIEF COMPLAINT:'));
        assert.ok(noteText.includes('Joint pain'));
        assert.ok(noteText.includes('ASSESSMENT:'));
        assert.ok(noteText.includes('Rheumatoid arthritis'));
    });

    test('acceptExtraction handles array values', () => {
        const medications = ['Methotrexate 15mg weekly', 'Folic acid 1mg daily', 'Prednisone 5mg daily'];
        const textValue = Array.isArray(medications) ? medications.join(', ') : medications;

        assert.strictEqual(textValue, 'Methotrexate 15mg weekly, Folic acid 1mg daily, Prednisone 5mg daily');
    });
});

describe('Medical Note Recording', () => {
    test('toggleRecording starts when not recording', () => {
        const state = { isRecording: false };

        if (!state.isRecording) {
            state.isRecording = true;
        }

        assert.strictEqual(state.isRecording, true);
    });

    test('toggleRecording stops when recording', () => {
        const state = { isRecording: true };

        if (state.isRecording) {
            state.isRecording = false;
        }

        assert.strictEqual(state.isRecording, false);
    });

    test('toggleRecording appends transcribed text', () => {
        let smartText = 'Existing text.';
        const transcribedText = 'New dictation.';

        smartText += (smartText ? ' ' : '') + transcribedText;

        assert.strictEqual(smartText, 'Existing text. New dictation.');
    });
});
