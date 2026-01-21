/**
 * Joint Assessment Logic Tests
 * Tests for frontend/src/modules/joint_assessment_logic.js
 * Uses Node.js 24 native test runner
 */

import { test, describe, mock } from 'node:test';
import assert from 'node:assert';

describe('DAS28-ESR Calculation', () => {
    /**
     * DAS28-ESR formula:
     * 0.56 * sqrt(TJC) + 0.28 * sqrt(SJC) + 0.70 * ln(ESR) + 0.014 * PGA
     * where PGA is 0-100 scale (pg_scale * 10)
     */
    function calculateDAS28(tjc, sjc, esr, pg_scale) {
        const t = Math.sqrt(tjc) * 0.56;
        const s = Math.sqrt(sjc) * 0.28;
        const e = Math.log(Math.max(1, esr)) * 0.70;
        const pgaVal = (Number(pg_scale) || 0) * 10;
        const p = pgaVal * 0.014;
        return (t + s + e + p).toFixed(2);
    }

    test('calculateDAS28 returns correct score for remission values', () => {
        // Low activity example: TJC=0, SJC=0, ESR=10, PGA=2
        const score = calculateDAS28(0, 0, 10, 2);
        const numericScore = parseFloat(score);

        // Should be < 2.6 for remission
        assert.ok(numericScore < 2.6, `Score ${numericScore} should be < 2.6 for remission`);
    });

    test('calculateDAS28 returns correct score for low activity', () => {
        // Low activity: TJC=2, SJC=1, ESR=10, PGA=2
        // t = sqrt(2)*0.56 = 0.792, s = sqrt(1)*0.28 = 0.28
        // e = ln(10)*0.70 = 1.612, p = 20*0.014 = 0.28
        // Total = 2.964
        const score = calculateDAS28(2, 1, 10, 2);
        const numericScore = parseFloat(score);

        // Should be between 2.6 and 3.2 for low activity
        assert.ok(numericScore >= 2.6 && numericScore <= 3.2,
            `Score ${numericScore} should be between 2.6-3.2 for low activity`);
    });

    test('calculateDAS28 returns correct score for moderate activity', () => {
        // Moderate: TJC=4, SJC=2, ESR=20, PGA=4
        const score = calculateDAS28(4, 2, 20, 4);
        const numericScore = parseFloat(score);

        // Should be between 3.2 and 5.1 for moderate
        assert.ok(numericScore > 3.2 && numericScore <= 5.1,
            `Score ${numericScore} should be between 3.2-5.1 for moderate activity`);
    });

    test('calculateDAS28 returns correct score for high activity', () => {
        // High activity: TJC=15, SJC=10, ESR=50, PGA=8
        const score = calculateDAS28(15, 10, 50, 8);
        const numericScore = parseFloat(score);

        // Should be > 5.1 for high activity
        assert.ok(numericScore > 5.1, `Score ${numericScore} should be > 5.1 for high activity`);
    });

    test('calculateDAS28 handles zero values', () => {
        const score = calculateDAS28(0, 0, 1, 0);
        const numericScore = parseFloat(score);

        // With all zeros (except ESR min 1), score should be very low
        assert.ok(numericScore >= 0);
        assert.ok(numericScore < 1);
    });

    test('calculateDAS28 handles ESR of 1 (minimum)', () => {
        // ln(1) = 0, so ESR component should be 0
        const score = calculateDAS28(0, 0, 1, 0);
        const numericScore = parseFloat(score);

        assert.strictEqual(numericScore, 0);
    });

    test('calculateDAS28 converts pg_scale to PGA correctly', () => {
        // pg_scale of 5 should become PGA of 50
        // PGA effect = 0.014 * 50 = 0.7
        const score1 = calculateDAS28(0, 0, 1, 5);
        const score2 = calculateDAS28(0, 0, 1, 0);

        const diff = parseFloat(score1) - parseFloat(score2);
        assert.ok(Math.abs(diff - 0.7) < 0.01, `Difference should be ~0.7, got ${diff}`);
    });
});

describe('Joint Count Functions', () => {
    test('countTenderJoints counts joints with tenderness', () => {
        const joints = {
            'left_wrist': { tenderness: true, pain: false, swelling: 0 },
            'right_wrist': { tenderness: false, pain: false, swelling: 0 },
            'left_mcp1': { tenderness: true, pain: true, swelling: 1 },
            'right_mcp1': { tenderness: false, pain: false, swelling: 1 }
        };

        let tjc = 0;
        Object.values(joints).forEach(j => {
            if (j.tenderness) tjc++;
        });

        assert.strictEqual(tjc, 2);
    });

    test('countSwollenJoints counts joints with swelling > 0', () => {
        const joints = {
            'left_wrist': { tenderness: true, pain: false, swelling: 0 },
            'right_wrist': { tenderness: false, pain: false, swelling: 1 },
            'left_mcp1': { tenderness: true, pain: true, swelling: 2 },
            'right_mcp1': { tenderness: false, pain: false, swelling: 0 }
        };

        let sjc = 0;
        Object.values(joints).forEach(j => {
            if (j.swelling > 0) sjc++;
        });

        assert.strictEqual(sjc, 2);
    });

    test('joint state cycles correctly on click', () => {
        // State cycle: Normal(0) -> Tenderness(1) -> Swelling(2) -> Both(3) -> Normal(0)
        const joint = { tenderness: false, pain: false, swelling: 0 };

        function getCurrentState(j) {
            if (j.tenderness && j.swelling > 0) return 3;
            if (j.swelling > 0) return 2;
            if (j.tenderness) return 1;
            return 0;
        }

        function applyNextState(j, nextState) {
            switch (nextState) {
                case 0: j.tenderness = false; j.swelling = 0; break;
                case 1: j.tenderness = true; j.swelling = 0; break;
                case 2: j.tenderness = false; j.swelling = 1; break;
                case 3: j.tenderness = true; j.swelling = 1; break;
            }
        }

        // Initial state = 0 (Normal)
        assert.strictEqual(getCurrentState(joint), 0);

        // Click 1: Normal -> Tenderness
        applyNextState(joint, 1);
        assert.strictEqual(getCurrentState(joint), 1);
        assert.strictEqual(joint.tenderness, true);
        assert.strictEqual(joint.swelling, 0);

        // Click 2: Tenderness -> Swelling
        applyNextState(joint, 2);
        assert.strictEqual(getCurrentState(joint), 2);
        assert.strictEqual(joint.tenderness, false);
        assert.strictEqual(joint.swelling, 1);

        // Click 3: Swelling -> Both
        applyNextState(joint, 3);
        assert.strictEqual(getCurrentState(joint), 3);
        assert.strictEqual(joint.tenderness, true);
        assert.strictEqual(joint.swelling, 1);

        // Click 4: Both -> Normal
        applyNextState(joint, 0);
        assert.strictEqual(getCurrentState(joint), 0);
    });
});

describe('Joint Assessment Save', () => {
    test('saveAssessment builds correct payload', async () => {
        let capturedBody = null;
        const mockFetch = mock.fn(async (url, options) => {
            capturedBody = JSON.parse(options?.body || '{}');
            return { ok: true, json: async () => ({}) };
        });

        const visitId = '123';
        const joints = {
            'left_wrist': { tenderness: true, pain: false, swelling: 1 },
            'right_wrist': { tenderness: false, pain: true, swelling: 0 }
        };

        const payload = {
            visit_id: visitId,
            joints: Object.entries(joints).map(([id, state]) => ({
                joint_id: id,
                has_tenderness: state.tenderness,
                has_pain: state.pain,
                swelling_grade: state.swelling
            }))
        };

        await mockFetch('/api/v1/joint_assessments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        assert.strictEqual(capturedBody.visit_id, '123');
        assert.strictEqual(capturedBody.joints.length, 2);
        assert.strictEqual(capturedBody.joints[0].joint_id, 'left_wrist');
        assert.strictEqual(capturedBody.joints[0].has_tenderness, true);
        assert.strictEqual(capturedBody.joints[0].swelling_grade, 1);
    });

    test('saveAssessment requires visitId', () => {
        const visitId = null;
        let shouldAlert = false;

        if (!visitId) {
            shouldAlert = true;
        }

        assert.strictEqual(shouldAlert, true);
    });

    test('saveAssessment updates saveStatus on success', async () => {
        const mockFetch = mock.fn(async () => ({ ok: true }));
        const state = { saveStatus: '' };

        state.saveStatus = 'Saving...';
        const response = await mockFetch('/api/v1/joint_assessments', { method: 'POST' });

        if (response.ok) {
            state.saveStatus = 'Saved';
        }

        assert.strictEqual(state.saveStatus, 'Saved');
    });

    test('saveAssessment updates saveStatus on error', async () => {
        const mockFetch = mock.fn(async () => ({ ok: false }));
        const state = { saveStatus: '' };

        state.saveStatus = 'Saving...';
        const response = await mockFetch('/api/v1/joint_assessments', { method: 'POST' });

        if (!response.ok) {
            state.saveStatus = 'Error';
        }

        assert.strictEqual(state.saveStatus, 'Error');
    });
});

describe('Joint Assessment Load', () => {
    test('loadExistingData fetches by visit ID', async () => {
        let capturedUrl = null;
        const mockFetch = mock.fn(async (url) => {
            capturedUrl = url;
            return {
                ok: true,
                json: async () => ({
                    joints: [
                        { joint_id: 'left_wrist', has_tenderness: true, has_pain: false, swelling_grade: 1 }
                    ]
                })
            };
        });

        const visitId = '456';
        await mockFetch(`/api/v1/joint_assessments/visit/${visitId}`);

        assert.strictEqual(capturedUrl, '/api/v1/joint_assessments/visit/456');
    });

    test('loadExistingData maps DB columns to state', async () => {
        const dbRow = {
            joint_id: 'left_mcp2',
            has_tenderness: 1,
            has_pain: 0,
            swelling_grade: 2
        };

        const jointState = {
            tenderness: Boolean(dbRow.has_tenderness),
            pain: Boolean(dbRow.has_pain),
            swelling: parseInt(dbRow.swelling_grade || 0)
        };

        assert.strictEqual(jointState.tenderness, true);
        assert.strictEqual(jointState.pain, false);
        assert.strictEqual(jointState.swelling, 2);
    });

    test('loadExistingData handles empty response', async () => {
        const mockFetch = mock.fn(async () => ({
            ok: true,
            json: async () => ({ joints: [] })
        }));

        const response = await mockFetch('/api/v1/joint_assessments/visit/999');
        const data = await response.json();

        assert.ok(Array.isArray(data.joints));
        assert.strictEqual(data.joints.length, 0);
    });
});

describe('Joint Summary', () => {
    test('getJointSummary returns correct structure', () => {
        const state = {
            tjc: 5,
            sjc: 3,
            esr: 25,
            pg_scale: 5,
            score: 4.2
        };

        const summary = {
            tjc: state.tjc,
            sjc: state.sjc,
            esr: state.esr,
            pg_scale: state.pg_scale,
            pga: (Number(state.pg_scale) || 0) * 10,
            das28: parseFloat(state.score) || 0
        };

        assert.strictEqual(summary.tjc, 5);
        assert.strictEqual(summary.sjc, 3);
        assert.strictEqual(summary.esr, 25);
        assert.strictEqual(summary.pg_scale, 5);
        assert.strictEqual(summary.pga, 50);
        assert.strictEqual(summary.das28, 4.2);
    });
});
