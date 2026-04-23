import { describe, it, expect, vi } from 'vitest';
import * as progressUtils from '../src/utils/progressTracking';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('Progress Tracking Utilities', () => {
  const mockPalaceId = 'palace-1';
  const mockPalaceName = 'Test Palace';

  const mockSession = {
    id: 'session-1',
    palaceId: 'palace-1',
    palaceName: 'Test Palace',
    exerciseType: 'spatial',
    startTime: '2024-01-15T10:00:00.000Z',
    endTime: '2024-01-15T10:05:00.000Z',
    duration: 300,
    score: 80,
    totalItems: 10,
    correctItems: 8,
    accuracy: 80,
    difficulty: 'medium',
  };

  describe('getExerciseSessions', () => {
    it('returns all exercise sessions for a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockSession]));

      const result = progressUtils.getExerciseSessions(mockPalaceId);

      expect(result).toHaveLength(1);
      expect(result[0].palaceId).toBe('palace-1');
    });

    it('returns empty array when no sessions exist', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getExerciseSessions(mockPalaceId);

      expect(result).toEqual([]);
    });

    it('handles invalid JSON gracefully', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue('invalid json');

      const result = progressUtils.getExerciseSessions(mockPalaceId);

      expect(result).toEqual([]);
    });

    it('filters sessions by palace ID', () => {
      const otherPalaceSession = { ...mockSession, palaceId: 'palace-2' };
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockSession, otherPalaceSession]));

      const result = progressUtils.getExerciseSessions('palace-2');

      expect(result).toHaveLength(1);
      expect(result[0].palaceId).toBe('palace-2');
    });
  });

  describe('saveExerciseSession', () => {
    it('saves an exercise session', () => {
      const result = progressUtils.saveExerciseSession(mockSession);

      expect(localStorage.setItem).toHaveBeenCalledWith('memoryExerciseSessions', expect.any(String));
      expect(result).toBe(true);
    });

    it('handles save errors gracefully', () => {
      localStorageMock.setItem = vi.fn(() => {
        throw new Error('Storage error');
      });

      const result = progressUtils.saveExerciseSession(mockSession);

      expect(result).toBe(false);
    });

    it('appends to existing sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockSession]));

      const newSession = {
        ...mockSession,
        id: 'session-2',
        accuracy: 90,
      };

      progressUtils.saveExerciseSession(newSession);

      expect(localStorage.setItem).toHaveBeenCalled();
    });
  });

  describe('getPalaceStats', () => {
    it('returns stats for a palace with sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockSession]));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.palaceId).toBe('palace-1');
      expect(result.palaceName).toBe('Test Palace');
      expect(result.totalSessions).toBe(1);
      expect(result.totalAttempts).toBe(10);
      expect(result.correctRecalls).toBe(8);
      expect(result.totalRooms).toBeUndefined();
    });

    it('returns default stats when no sessions exist', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.palaceId).toBe(mockPalaceId);
      expect(result.palaceName).toBe('Unknown Palace');
      expect(result.totalSessions).toBe(0);
      expect(result.totalAttempts).toBe(0);
      expect(result.correctRecalls).toBe(0);
      expect(result.totalRooms).toBe(0);
      expect(result.sessionHistory).toEqual([]);
    });

    it('calculates average accuracy correctly', () => {
      const sessions = [
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 90 },
        { ...mockSession, accuracy: 70 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.averageAccuracy).toBe(80);
    });

    it('calculates average duration correctly', () => {
      const sessions = [
        { ...mockSession, duration: 300 },
        { ...mockSession, duration: 240 },
        { ...mockSession, duration: 360 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.averageDuration).toBe(300);
    });

    it('calculates trend correctly (improving)', () => {
      const sessions = [
        { ...mockSession, accuracy: 70 },
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 90 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.trend).toBe('Improving');
    });

    it('calculates trend correctly (decreasing)', () => {
      const sessions = [
        { ...mockSession, accuracy: 90 },
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 70 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.trend).toBe('Decreasing');
    });

    it('calculates trend correctly (stable)', () => {
      const sessions = [
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 82 },
        { ...mockSession, accuracy: 78 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.trend).toBe('Stable');
    });

    it('includes session history', () => {
      const sessions = [mockSession];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.sessionHistory).toHaveLength(1);
      expect(result.sessionHistory[0].id).toBe('session-1');
    });

    it('handles missing palace name gracefully', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([
        { ...mockSession, palaceName: 'Unknown Palace' },
      ]));

      const result = progressUtils.getPalaceStats(mockPalaceId);

      expect(result.palaceName).toBe('Unknown Palace');
    });
  });

  describe('getAccuracyTrend', () => {
    it('returns trend type based on accuracy changes', () => {
      const sessions = [
        { ...mockSession, accuracy: 70 },
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 90 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getAccuracyTrend(mockPalaceId);

      expect(result).toBe('improving');
    });

    it('returns stable trend for minimal variance', () => {
      const sessions = [
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 82 },
        { ...mockSession, accuracy: 78 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getAccuracyTrend(mockPalaceId);

      expect(result).toBe('stable');
    });

    it('returns decreasing trend for declining accuracy', () => {
      const sessions = [
        { ...mockSession, accuracy: 90 },
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 70 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getAccuracyTrend(mockPalaceId);

      expect(result).toBe('decreasing');
    });

    it('returns stable for single session', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockSession]));

      const result = progressUtils.getAccuracyTrend(mockPalaceId);

      expect(result).toBe('stable');
    });

    it('returns stable for empty sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getAccuracyTrend(mockPalaceId);

      expect(result).toBe('stable');
    });
  });

  describe('getAverageAccuracy', () => {
    it('calculates average accuracy correctly', () => {
      const sessions = [
        { ...mockSession, accuracy: 80 },
        { ...mockSession, accuracy: 90 },
        { ...mockSession, accuracy: 70 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getAverageAccuracy(mockPalaceId);

      expect(result).toBe(80);
    });

    it('returns 0 for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getAverageAccuracy(mockPalaceId);

      expect(result).toBe(0);
    });
  });

  describe('getAverageDuration', () => {
    it('calculates average duration correctly', () => {
      const sessions = [
        { ...mockSession, duration: 300 },
        { ...mockSession, duration: 240 },
        { ...mockSession, duration: 360 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getAverageDuration(mockPalaceId);

      expect(result).toBe(300);
    });

    it('returns 0 for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getAverageDuration(mockPalaceId);

      expect(result).toBe(0);
    });
  });

  describe('getTotalAttempts', () => {
    it('calculates total attempts correctly', () => {
      const sessions = [
        { ...mockSession, totalItems: 10 },
        { ...mockSession, totalItems: 8 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getTotalAttempts(mockPalaceId);

      expect(result).toBe(18);
    });

    it('returns 0 for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getTotalAttempts(mockPalaceId);

      expect(result).toBe(0);
    });
  });

  describe('getTotalCorrectRecalls', () => {
    it('calculates total correct recalls correctly', () => {
      const sessions = [
        { ...mockSession, correctItems: 8 },
        { ...mockSession, correctItems: 6 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getTotalCorrectRecalls(mockPalaceId);

      expect(result).toBe(14);
    });

    it('returns 0 for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getTotalCorrectRecalls(mockPalaceId);

      expect(result).toBe(0);
    });
  });

  describe('getLastSessionTimestamp', () => {
    it('returns last session timestamp', () => {
      const sessions = [
        { ...mockSession, startTime: '2024-01-15T10:00:00.000Z' },
        { ...mockSession, startTime: '2024-01-14T10:00:00.000Z' },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getLastSessionTimestamp(mockPalaceId);

      expect(result).toBe('2024-01-15T10:00:00.000Z');
    });

    it('returns null for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getLastSessionTimestamp(mockPalaceId);

      expect(result).toBeNull();
    });
  });

  describe('getFirstSessionTimestamp', () => {
    it('returns first session timestamp', () => {
      const sessions = [
        { ...mockSession, startTime: '2024-01-15T10:00:00.000Z' },
        { ...mockSession, startTime: '2024-01-14T10:00:00.000Z' },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getFirstSessionTimestamp(mockPalaceId);

      expect(result).toBe('2024-01-14T10:00:00.000Z');
    });

    it('returns null for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getFirstSessionTimestamp(mockPalaceId);

      expect(result).toBeNull();
    });
  });

  describe('getExerciseTypeBreakdown', () => {
    it('returns breakdown of exercise types', () => {
      const sessions = [
        { ...mockSession, exerciseType: 'spatial' },
        { ...mockSession, exerciseType: 'recall' },
        { ...mockSession, exerciseType: 'spatial' },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.getExerciseTypeBreakdown(mockPalaceId);

      expect(result.spatial).toBe(2);
      expect(result.recall).toBe(1);
    });

    it('returns empty breakdown for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.getExerciseTypeBreakdown(mockPalaceId);

      expect(result).toEqual({ spatial: 0, recall: 0 });
    });
  });

  describe('calculateOverallAccuracy', () => {
    it('calculates overall accuracy from total items and correct', () => {
      const sessions = [
        { ...mockSession, totalItems: 10, correctItems: 8 },
        { ...mockSession, totalItems: 5, correctItems: 4 },
      ];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(sessions));

      const result = progressUtils.calculateOverallAccuracy(mockPalaceId);

      expect(result).toBe(80);
    });

    it('returns 0 for no sessions', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = progressUtils.calculateOverallAccuracy(mockPalaceId);

      expect(result).toBe(0);
    });
  });
});
