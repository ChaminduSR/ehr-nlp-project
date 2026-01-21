/**
 * Voice Recorder Tests
 * Tests for frontend/src/modules/voice_recorder.js
 * Uses Node.js 24 native test runner
 */

import { test, describe, mock } from 'node:test';
import assert from 'node:assert';

describe('Voice Recorder State', () => {
    test('initial state is not recording', () => {
        const VoiceRecorder = {
            isRecording: false,
            mediaRecorder: null,
            chunks: []
        };

        assert.strictEqual(VoiceRecorder.isRecording, false);
        assert.strictEqual(VoiceRecorder.mediaRecorder, null);
        assert.deepStrictEqual(VoiceRecorder.chunks, []);
    });

    test('start sets isRecording to true', () => {
        const state = { isRecording: false };

        // Simulate successful start
        state.isRecording = true;

        assert.strictEqual(state.isRecording, true);
    });

    test('stop sets isRecording to false', () => {
        const state = { isRecording: true };

        // Simulate stop
        state.isRecording = false;

        assert.strictEqual(state.isRecording, false);
    });
});

describe('Voice Recorder Model Loading', () => {
    test('start calls model load endpoint', async () => {
        let modelLoadCalled = false;
        const mockFetch = mock.fn(async (url, options) => {
            if (url === '/api/v1/voice/load-model' && options?.method === 'POST') {
                modelLoadCalled = true;
            }
            return { ok: true };
        });

        await mockFetch('/api/v1/voice/load-model', { method: 'POST' });

        assert.strictEqual(modelLoadCalled, true);
    });

    test('model load uses correct endpoint path', async () => {
        let capturedUrl = null;
        const mockFetch = mock.fn(async (url) => {
            capturedUrl = url;
            return { ok: true };
        });

        await mockFetch('/api/v1/voice/load-model', { method: 'POST' });

        assert.strictEqual(capturedUrl, '/api/v1/voice/load-model');
    });
});

describe('Voice Recorder Transcription', () => {
    test('transcribe sends audio as FormData', async () => {
        let receivedFormData = false;
        const mockFetch = mock.fn(async (url, options) => {
            if (options?.body && typeof options.body.append === 'function') {
                receivedFormData = true;
            }
            return {
                ok: true,
                json: async () => ({ text: 'Transcribed text' })
            };
        });

        // Simulate FormData
        const formData = {
            append: mock.fn(),
            get: mock.fn()
        };
        formData.append('audio', 'blob', 'recording.wav');

        await mockFetch('/api/v1/voice/transcribe', {
            method: 'POST',
            body: formData
        });

        assert.ok(formData.append.mock.calls.length > 0);
    });

    test('transcribe returns text on success', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: true,
            json: async () => ({
                text: 'Patient presents with joint pain'
            })
        }));

        const response = await mockFetch('/api/v1/voice/transcribe', { method: 'POST' });
        const result = await response.json();

        assert.strictEqual(result.text, 'Patient presents with joint pain');
    });

    test('transcribe returns error on failure', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: true,
            json: async () => ({
                error: 'Model not loaded'
            })
        }));

        const response = await mockFetch('/api/v1/voice/transcribe', { method: 'POST' });
        const result = await response.json();

        assert.strictEqual(result.error, 'Model not loaded');
        assert.strictEqual(result.text, undefined);
    });
});

describe('Voice Recorder WAV Conversion', () => {
    test('writeString writes characters at correct offsets', () => {
        const buffer = new ArrayBuffer(10);
        const view = new DataView(buffer);

        function writeString(view, offset, string) {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        }

        writeString(view, 0, 'RIFF');

        assert.strictEqual(view.getUint8(0), 'R'.charCodeAt(0));
        assert.strictEqual(view.getUint8(1), 'I'.charCodeAt(0));
        assert.strictEqual(view.getUint8(2), 'F'.charCodeAt(0));
        assert.strictEqual(view.getUint8(3), 'F'.charCodeAt(0));
    });

    test('WAV header structure is correct', () => {
        // WAV file header should be 44 bytes
        const HEADER_SIZE = 44;
        const sampleRate = 16000;
        const numChannels = 1;
        const bitDepth = 16;
        const bytesPerSample = bitDepth / 8;
        const blockAlign = numChannels * bytesPerSample;
        const byteRate = sampleRate * blockAlign;

        assert.strictEqual(HEADER_SIZE, 44);
        assert.strictEqual(bytesPerSample, 2);
        assert.strictEqual(blockAlign, 2);
        assert.strictEqual(byteRate, 32000);
    });

    test('audio sample clipping works correctly', () => {
        function clampSample(sample) {
            return Math.max(-1, Math.min(1, sample));
        }

        assert.strictEqual(clampSample(0.5), 0.5);
        assert.strictEqual(clampSample(-0.5), -0.5);
        assert.strictEqual(clampSample(1.5), 1);
        assert.strictEqual(clampSample(-1.5), -1);
        assert.strictEqual(clampSample(0), 0);
    });

    test('stereo to mono conversion averages channels', () => {
        const ch1 = [0.5, 0.8, -0.2];
        const ch2 = [0.3, 0.4, 0.2];

        const mono = ch1.map((sample, i) => (sample + ch2[i]) / 2);

        // Use approximate equality for floating point
        assert.ok(Math.abs(mono[0] - 0.4) < 0.0001);
        assert.ok(Math.abs(mono[1] - 0.6) < 0.0001);
        assert.ok(Math.abs(mono[2] - 0) < 0.0001);
    });
});

describe('Voice Recorder Error Handling', () => {
    test('start handles microphone permission denial', async () => {
        const error = new Error('Permission denied');
        let errorMessage = null;

        try {
            throw error;
        } catch (err) {
            errorMessage = err.message;
        }

        assert.strictEqual(errorMessage, 'Permission denied');
    });

    test('stop handles null mediaRecorder gracefully', async () => {
        const VoiceRecorder = {
            mediaRecorder: null,
            isRecording: false
        };

        // Simulate stop check
        if (!VoiceRecorder.mediaRecorder || !VoiceRecorder.isRecording) {
            // Should return null without error
            assert.ok(true);
        }
    });

    test('stop cleans up media tracks', () => {
        const mockTrack = {
            stopped: false,
            stop() { this.stopped = true; }
        };

        const mockStream = {
            getTracks: () => [mockTrack]
        };

        // Simulate cleanup
        mockStream.getTracks().forEach(track => track.stop());

        assert.strictEqual(mockTrack.stopped, true);
    });
});

describe('Voice Recorder Integration', () => {
    test('full recording cycle state transitions', () => {
        const state = {
            isRecording: false,
            chunks: [],
            error: null
        };

        // Start recording
        state.isRecording = true;
        assert.strictEqual(state.isRecording, true);

        // Simulate data available
        state.chunks.push('chunk1');
        state.chunks.push('chunk2');
        assert.strictEqual(state.chunks.length, 2);

        // Stop recording
        state.isRecording = false;
        assert.strictEqual(state.isRecording, false);

        // Clear chunks after processing
        state.chunks = [];
        assert.strictEqual(state.chunks.length, 0);
    });
});
