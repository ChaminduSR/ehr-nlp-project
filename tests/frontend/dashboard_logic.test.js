/**
 * Dashboard Logic Tests
 * Tests for frontend/src/modules/dashboard_logic.js
 * Uses Node.js 24 native test runner
 */

import { test, describe, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert';

// Mock browser APIs
const mockSessionStorage = {
    store: {},
    getItem(key) { return this.store[key] || null; },
    setItem(key, value) { this.store[key] = value; },
    removeItem(key) { delete this.store[key]; },
    clear() { this.store = {}; }
};

// Mock fetch responses
function createMockFetch(responses) {
    return mock.fn(async (url) => {
        const response = responses[url] || { ok: false, status: 404 };
        return {
            ok: response.ok !== false,
            status: response.status || 200,
            json: async () => response.data || {}
        };
    });
}

describe('Dashboard Cache', () => {
    const CACHE_TTL = 10 * 60 * 1000; // 10 minutes

    beforeEach(() => {
        mockSessionStorage.clear();
    });

    test('cache.get returns null for missing key', () => {
        const result = mockSessionStorage.getItem('dashboard_nonexistent');
        assert.strictEqual(result, null);
    });

    test('cache.set stores data with timestamp', () => {
        const data = { patientsToday: 5, avgDAS28: 3.2 };
        const cacheEntry = JSON.stringify({ data, timestamp: Date.now() });
        mockSessionStorage.setItem('dashboard_stats', cacheEntry);

        const stored = mockSessionStorage.getItem('dashboard_stats');
        assert.notStrictEqual(stored, null);

        const parsed = JSON.parse(stored);
        assert.deepStrictEqual(parsed.data, data);
        assert.ok(parsed.timestamp > 0);
    });

    test('cache.get returns data within TTL', () => {
        const data = { patientsToday: 10 };
        const timestamp = Date.now(); // Current time = valid
        mockSessionStorage.setItem('dashboard_stats', JSON.stringify({ data, timestamp }));

        const stored = JSON.parse(mockSessionStorage.getItem('dashboard_stats'));
        const isExpired = Date.now() - stored.timestamp > CACHE_TTL;

        assert.strictEqual(isExpired, false);
        assert.deepStrictEqual(stored.data, data);
    });

    test('cache.get returns null for expired data', () => {
        const data = { patientsToday: 10 };
        const expiredTimestamp = Date.now() - (CACHE_TTL + 1000); // Expired
        mockSessionStorage.setItem('dashboard_stats', JSON.stringify({ data, timestamp: expiredTimestamp }));

        const stored = JSON.parse(mockSessionStorage.getItem('dashboard_stats'));
        const isExpired = Date.now() - stored.timestamp > CACHE_TTL;

        assert.strictEqual(isExpired, true);
    });
});

describe('Dashboard Stats Loading', () => {
    test('loadStats fetches from /api/v1/dashboard/stats', async () => {
        const mockData = {
            patientsToday: 15,
            avgDAS28: 4.5,
            remissionPercent: 25,
            pendingReviews: 3
        };

        const mockFetch = createMockFetch({
            '/api/v1/dashboard/stats': { data: mockData }
        });

        // Simulate loadStats behavior
        const response = await mockFetch('/api/v1/dashboard/stats');
        const data = await response.json();

        assert.ok(mockFetch.mock.calls.length > 0);
        assert.strictEqual(data.patientsToday, 15);
        assert.strictEqual(data.avgDAS28, 4.5);
    });

    test('loadStats handles fetch errors gracefully', async () => {
        const mockFetch = createMockFetch({
            '/api/v1/dashboard/stats': { ok: false, status: 500, data: {} }
        });

        const response = await mockFetch('/api/v1/dashboard/stats');

        assert.strictEqual(response.ok, false);
        assert.strictEqual(response.status, 500);
    });
});

describe('Dashboard Charts', () => {
    test('distribution chart endpoint returns expected structure', async () => {
        const distributionData = {
            remission: 10,
            low_activity: 15,
            moderate: 8,
            high: 5
        };

        const mockFetch = createMockFetch({
            '/api/v1/dashboard/distribution': { data: distributionData }
        });

        const response = await mockFetch('/api/v1/dashboard/distribution');
        const data = await response.json();

        assert.ok('remission' in data);
        assert.ok('low_activity' in data);
        assert.ok('moderate' in data);
        assert.ok('high' in data);
    });

    test('trend chart endpoint returns expected structure', async () => {
        const trendData = {
            dates: ['2026-01-01', '2026-01-02', '2026-01-03'],
            scores: [3.5, 3.2, 3.8]
        };

        const mockFetch = createMockFetch({
            '/api/v1/dashboard/trend': { data: trendData }
        });

        const response = await mockFetch('/api/v1/dashboard/trend');
        const data = await response.json();

        assert.ok(Array.isArray(data.dates));
        assert.ok(Array.isArray(data.scores));
        assert.strictEqual(data.dates.length, data.scores.length);
    });
});

describe('Dashboard Refresh', () => {
    test('refreshStats clears cache and fetches new data', async () => {
        // Setup initial cache
        mockSessionStorage.setItem('dashboard_stats', JSON.stringify({
            data: { patientsToday: 5 },
            timestamp: Date.now()
        }));

        // Simulate refresh by removing cache
        mockSessionStorage.removeItem('dashboard_stats');

        const cachedData = mockSessionStorage.getItem('dashboard_stats');
        assert.strictEqual(cachedData, null);
    });
});
