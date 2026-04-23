import React from 'react';
import { PalaceExerciseSession, PalaceStats, getPalaceStats } from '../utils/progressTracking';
import './ProgressTracker.css';

interface ProgressTrackerProps {
  palaceId: string;
}

/**
 * ProgressTracker Component
 * Displays progress metrics and session history for a specific palace
 */
const ProgressTracker: React.FC<ProgressTrackerProps> = ({ palaceId }) => {
  const stats: PalaceStats = getPalaceStats(palaceId);
  const sessionHistory: PalaceExerciseSession[] = stats.sessionHistory || [];

  const calculateAccuracy = (): number => {
    if (stats.totalAttempts === 0) return 0;
    return Math.round((stats.correctRecalls / stats.totalAttempts) * 100);
  };

  const calculateAverageDuration = (): number => {
    if (stats.totalSessions === 0) return 0;
    const totalDuration = stats.sessionHistory.reduce((sum, session) => sum + session.duration, 0);
    return Math.round(totalDuration / stats.totalSessions);
  };

  const getAccuracyColor = (accuracy: number): string => {
    if (accuracy >= 80) return 'var(--success-color)';
    if (accuracy >= 60) return 'var(--warning-color)';
    return 'var(--error-color)';
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const getTrend = (sessions: PalaceExerciseSession[]): string => {
    if (sessions.length < 2) return 'Stable';
    
    const recent = sessions.slice(0, 3);
    const older = sessions.slice(3, 6);
    
    if (recent.length === 0) return 'Stable';
    
    const recentAvg = recent.reduce((sum, s) => sum + (s.correctItems / s.totalItems), 0) / recent.length;
    const olderAvg = older.length > 0 
      ? older.reduce((sum, s) => sum + (s.correctItems / s.totalItems), 0) / older.length
      : recentAvg;
    
    if (recentAvg > olderAvg + 0.1) return 'Improving';
    if (recentAvg < olderAvg - 0.1) return 'Declining';
    return 'Stable';
  };

  return (
    <div className="progress-tracker">
      <div className="progress-header">
        <h3>📊 Progress Tracking</h3>
        <p className="palace-name">{stats.palaceName}</p>
      </div>

      {/* Main Statistics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <div className="stat-label">Accuracy</div>
            <div 
              className="stat-value" 
              style={{ color: getAccuracyColor(calculateAccuracy()) }}
            >
              {calculateAccuracy()}%
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-label">Avg Duration</div>
            <div className="stat-value">{formatDuration(calculateAverageDuration())}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-label">Sessions</div>
            <div className="stat-value">{stats.totalSessions}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-label">Trend</div>
            <div className="stat-value trend-badge">{getTrend(sessionHistory)}</div>
          </div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="detailed-stats">
        <div className="stat-row">
          <div className="stat-label">Correct Recalls</div>
          <div className="stat-value">{stats.correctRecalls}</div>
        </div>
        <div className="stat-row">
          <div className="stat-label">Total Attempts</div>
          <div className="stat-value">{stats.totalAttempts}</div>
        </div>
        <div className="stat-row">
          <div className="stat-label">First Session</div>
          <div className="stat-value">
            {stats.sessionHistory.length > 0 
              ? formatDate(stats.firstSessionTimestamp || '')
              : 'No sessions yet'}
          </div>
        </div>
        <div className="stat-row">
          <div className="stat-label">Last Activity</div>
          <div className="stat-value">
            {stats.lastSessionTimestamp 
              ? formatDate(stats.lastSessionTimestamp)
              : 'No sessions yet'}
          </div>
        </div>
      </div>

      {/* Session History */}
      <div className="session-history">
        <h4>Recent Sessions</h4>
        {sessionHistory.length === 0 ? (
          <p className="no-sessions">No exercise sessions yet. Start practicing!</p>
        ) : (
          <div className="sessions-list">
            {sessionHistory.slice(0, 10).reverse().map((session, index) => (
              <div key={index} className="session-item">
                <div className="session-info">
                  <span className="session-date">{formatDate(session.startTime)}</span>
                  <span className="session-type">{session.exerciseType}</span>
                </div>
                <div className="session-stats">
                  <span className="session-accuracy">
                    {Math.round((session.correctItems / session.totalItems) * 100)}%
                  </span>
                  <span className="session-duration">
                    {formatDuration(session.duration)}
                  </span>
                </div>
              </div>
            ))}
            {sessionHistory.length > 10 && (
              <div className="more-sessions">
                And {sessionHistory.length - 10} more sessions
              </div>
            )}
          </div>
        )}
      </div>

      {/* Progress Chart Placeholder */}
      <div className="progress-chart">
        <h4>Accuracy Over Time</h4>
        <div className="chart-container">
          {sessionHistory.length >= 2 ? (
            <div className="chart-bars">
              {sessionHistory.slice(-10).map((session, index) => {
                const accuracy = (session.correctItems / session.totalItems) * 100;
                return (
                  <div 
                    key={index} 
                    className="chart-bar"
                    style={{ 
                      height: `${accuracy}%`,
                      backgroundColor: getAccuracyColor(accuracy)
                    }}
                    title={`${formatDate(session.startTime)}: ${Math.round(accuracy)}%`}
                  />
                );
              })}
            </div>
          ) : (
            <p className="chart-placeholder">Complete at least 2 sessions to see your progress chart</p>
          )}
        </div>
      </div>

      {/* Reset Button */}
      <div className="progress-actions">
        <button className="btn btn-danger btn-small" onClick={() => window.confirm('Are you sure you want to reset all progress for this palace?')}>
          Reset Progress
        </button>
        <button className="btn btn-secondary btn-small" onClick={() => {
          const progressData = {
            palaceName: stats.palaceName,
            palaceId: palaceId,
            exportedAt: new Date().toISOString(),
            stats,
            sessionHistory
          };
          const jsonString = JSON.stringify(progressData, null, 2);
          const blob = new Blob([jsonString], { type: 'application/json' });
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `palace_progress_${palaceId}.json`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }}>
          Export Progress
        </button>
      </div>
    </div>
  );
};

export default ProgressTracker;
