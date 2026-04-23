import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProgressTracker } from '../src/components/MemoryPalace/ProgressTracker';

// Mock the progress tracking functions
vi.mock('../src/utils/progressTracking', () => ({
  getPalaceStats: vi.fn(),
  saveExerciseSession: vi.fn(),
}));

describe('ProgressTracker', () => {
  const mockPalaceId = 'palace-1';

  const mockStats = {
    palaceId: 'palace-1',
    palaceName: 'Test Palace',
    totalSessions: 5,
    totalAttempts: 50,
    correctRecalls: 40,
    totalRooms: 3,
    lastSessionTimestamp: '2024-01-15T10:00:00.000Z',
    firstSessionTimestamp: '2024-01-01T10:00:00.000Z',
    sessionHistory: [
      {
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
      },
      {
        id: 'session-2',
        palaceId: 'palace-1',
        palaceName: 'Test Palace',
        exerciseType: 'recall',
        startTime: '2024-01-14T10:00:00.000Z',
        endTime: '2024-01-14T10:04:00.000Z',
        duration: 240,
        score: 75,
        totalItems: 8,
        correctItems: 6,
        accuracy: 75,
        difficulty: 'medium',
      },
    ],
  };

  const renderComponent = (palaceId: string = mockPalaceId, stats = mockStats) => {
    vi.mocked(require('../src/utils/progressTracking').getPalaceStats).mockReturnValue(
      stats as any
    );

    return render(
      <ProgressTracker palaceId={palaceId} />
    );
  };

  it('renders the progress tracker header', () => {
    renderComponent();
    expect(screen.getByText('📊 Progress Tracking')).toBeInTheDocument();
    expect(screen.getByText('Test Palace')).toBeInTheDocument();
  });

  it('displays accuracy statistic', () => {
    renderComponent();
    expect(screen.getByText('Accuracy')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('displays average duration statistic', () => {
    renderComponent();
    expect(screen.getByText('Avg Duration')).toBeInTheDocument();
    expect(screen.getByText('5m 0s')).toBeInTheDocument();
  });

  it('displays sessions count', () => {
    renderComponent();
    expect(screen.getByText('Sessions')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('displays trend indicator', () => {
    renderComponent();
    expect(screen.getByText('Trend')).toBeInTheDocument();
    expect(screen.getByText('Improving')).toBeInTheDocument();
  });

  it('displays correct recalls count', () => {
    renderComponent();
    expect(screen.getByText('Correct Recalls')).toBeInTheDocument();
    expect(screen.getByText('40')).toBeInTheDocument();
  });

  it('displays total attempts count', () => {
    renderComponent();
    expect(screen.getByText('Total Attempts')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });

  it('displays first session date', () => {
    renderComponent();
    expect(screen.getByText('First Session')).toBeInTheDocument();
    expect(screen.getByText('Jan 1')).toBeInTheDocument();
  });

  it('displays last activity date', () => {
    renderComponent();
    expect(screen.getByText('Last Activity')).toBeInTheDocument();
    expect(screen.getByText('Jan 15')).toBeInTheDocument();
  });

  it('displays session history', () => {
    renderComponent();
    expect(screen.getByText('Recent Sessions')).toBeInTheDocument();
    expect(screen.getByText('spatial')).toBeInTheDocument();
    expect(screen.getByText('recall')).toBeInTheDocument();
  });

  it('handles no sessions gracefully', () => {
    const emptyStats = { ...mockStats, totalSessions: 0, sessionHistory: [] };
    renderComponent(mockPalaceId, emptyStats);
    expect(screen.getByText('No exercise sessions yet. Start practicing!')).toBeInTheDocument();
  });

  it('displays accuracy color correctly for good performance', () => {
    const goodStats = {
      ...mockStats,
      totalAttempts: 10,
      correctRecalls: 9,
    };
    renderComponent(mockPalaceId, goodStats);
    const accuracyElement = screen.getByText('90%');
    expect(accuracyElement).toHaveStyle('color: var(--success-color)');
  });

  it('displays accuracy color correctly for poor performance', () => {
    const poorStats = {
      ...mockStats,
      totalAttempts: 10,
      correctRecalls: 3,
    };
    renderComponent(mockPalaceId, poorStats);
    const accuracyElement = screen.getByText('30%');
    expect(accuracyElement).toHaveStyle('color: var(--error-color)');
  });

  it('displays accuracy color correctly for moderate performance', () => {
    const moderateStats = {
      ...mockStats,
      totalAttempts: 10,
      correctRecalls: 6,
    };
    renderComponent(mockPalaceId, moderateStats);
    const accuracyElement = screen.getByText('60%');
    expect(accuracyElement).toHaveStyle('color: var(--warning-color)');
  });

  it('handles empty session history', () => {
    const noSessionsStats = {
      ...mockStats,
      totalSessions: 0,
      sessionHistory: [],
    };
    renderComponent(mockPalaceId, noSessionsStats);
    expect(screen.getByText('No sessions yet')).toBeInTheDocument();
  });

  it('handles negative test case - no data', () => {
    const noDataStats = {
      palaceId: 'palace-1',
      palaceName: 'Unknown Palace',
      totalSessions: 0,
      totalAttempts: 0,
      correctRecalls: 0,
      totalRooms: 0,
      lastSessionTimestamp: null,
      firstSessionTimestamp: null,
      sessionHistory: [],
    };
    renderComponent(mockPalaceId, noDataStats);
    expect(screen.getByText('Unknown Palace')).toBeInTheDocument();
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('renders reset progress button', () => {
    renderComponent();
    expect(screen.getByText('Reset Progress')).toBeInTheDocument();
  });

  it('renders export progress button', () => {
    renderComponent();
    expect(screen.getByText('Export Progress')).toBeInTheDocument();
  });
});
