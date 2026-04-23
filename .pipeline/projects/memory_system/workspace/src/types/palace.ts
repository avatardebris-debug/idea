export interface Room {
  id: string;
  name: string;
  description: string;
  items: string[];
}

export interface Palace {
  id: string;
  name: string;
  description: string;
  rooms: Room[];
  createdAt: string;
}

export interface PalaceStats {
  palaceId: string;
  palaceName: string;
  totalSessions: number;
  totalAttempts: number;
  correctRecalls: number;
  totalRooms: number;
  lastSessionTimestamp: string | null;
  firstSessionTimestamp: string | null;
  sessionHistory: PalaceExerciseSession[];
}

export interface PalaceExerciseStats {
  palaceId: string;
  palaceName: string;
  roomsVisited: number;
  timeElapsed: number;
  itemsPlaced: number;
}

/**
 * Exercise session record for progress tracking
 */
export interface PalaceExerciseSession {
  id: string;
  palaceId: string;
  palaceName: string;
  exerciseType: 'spatial' | 'recall';
  startTime: string;
  endTime: string;
  duration: number; // in seconds
  score: number;
  totalItems: number;
  correctItems: number;
  accuracy: number;
  difficulty: string;
}
