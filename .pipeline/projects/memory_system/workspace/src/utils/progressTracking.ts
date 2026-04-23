import { PalaceExerciseSession } from '../types/palace';

const STORAGE_KEY = 'memory_palace_sessions';

/**
 * Load all exercise sessions from localStorage
 */
export const loadExerciseSessions = (): PalaceExerciseSession[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading exercise sessions from localStorage:', error);
  }
  return [];
};

/**
 * Save an exercise session to localStorage
 */
export const saveExerciseSession = (session: PalaceExerciseSession): void => {
  try {
    const sessions = loadExerciseSessions();
    sessions.push(session);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Error saving exercise session:', error);
  }
};

/**
 * Load exercise sessions for a specific palace
 */
export const loadPalaceSessions = (palaceId: string): PalaceExerciseSession[] => {
  const allSessions = loadExerciseSessions();
  return allSessions.filter((session) => session.palaceId === palaceId);
};

/**
 * Get recent exercise sessions
 */
export const getRecentSessions = (limit: number = 5): PalaceExerciseSession[] => {
  const allSessions = loadExerciseSessions();
  return allSessions
    .sort((a, b) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())
    .slice(0, limit);
};

/**
 * Reset exercise progress for a specific palace
 */
export const resetPalaceProgress = (palaceId: string): void => {
  try {
    const sessions = loadExerciseSessions();
    const filtered = sessions.filter((s) => s.palaceId !== palaceId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error resetting palace progress:', error);
  }
};

/**
 * Clear all exercise progress
 */
export const clearAllProgress = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Error clearing all progress:', error);
  }
};
