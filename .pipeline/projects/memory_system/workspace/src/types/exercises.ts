/**
 * Exercise types and interfaces for memory palace exercises
 */

import { Room } from './palace';

export interface ExerciseItem {
  id: string;
  text: string;
}

export interface RoomExerciseState {
  roomId: string;
  roomName: string;
  items: ExerciseItem[];
  revealed: boolean;
  correctRecall: boolean;
}

export interface RecallExerciseState {
  roomId: string;
  roomName: string;
  items: ExerciseItem[];
  revealed: boolean;
  correctRecall: boolean;
  incorrectRecall: boolean;
}

export interface ExerciseSession {
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
  difficulty: 'easy' | 'medium' | 'hard';
}

export interface ExerciseState {
  isPlaying: boolean;
  isPaused: boolean;
  isCompleted: boolean;
  currentMode: 'placement' | 'recall' | 'review' | 'exercise';
  timer: number;
  score: number;
  correctRecalls: number;
  incorrectRecalls: number;
  feedback: { message: string; type: 'info' | 'success' | 'error' } | null;
}

export interface DifficultyConfig {
  timerDuration: number;
  roomsPerExercise: number;
  revealDelay: number;
}

export const DIFFICULTY_CONFIG: Record<string, DifficultyConfig> = {
  easy: {
    timerDuration: 120,
    roomsPerExercise: 2,
    revealDelay: 2000,
  },
  medium: {
    timerDuration: 90,
    roomsPerExercise: 3,
    revealDelay: 1500,
  },
  hard: {
    timerDuration: 60,
    roomsPerExercise: 4,
    revealDelay: 1000,
  },
};

export type ExerciseType = 'spatial' | 'recall';
export type ExerciseDifficulty = 'easy' | 'medium' | 'hard';
