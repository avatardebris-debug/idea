import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Palace, Room } from '../types/palace';
import {
  RecallExerciseState,
  ExerciseState,
  ExerciseSession,
  DIFFICULTY_CONFIG,
  ExerciseItem,
  ExerciseDifficulty,
} from '../types/exercises';
import { saveExerciseSession } from '../utils/progressTracking';
import './RecallExercise.css';

export interface RecallExerciseProps {
  palace: Palace;
  onExerciseComplete?: (session: ExerciseSession) => void;
}

const RecallExercise: React.FC<RecallExerciseProps> = ({
  palace,
  onExerciseComplete,
}) => {
  // Initialize rooms with exercise state
  const [rooms, setRooms] = useState<RecallExerciseState[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [userInput, setUserInput] = useState<string>('');
  
  // Exercise state
  const [exerciseState, setExerciseState] = useState<ExerciseState>({
    isPlaying: false,
    isPaused: false,
    isCompleted: false,
    currentMode: 'review',
    timer: 0,
    score: 0,
    correctRecalls: 0,
    incorrectRecalls: 0,
    feedback: null,
  });

  // Difficulty settings
  const [difficulty, setDifficulty] = useState<ExerciseDifficulty>('medium');
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize exercise rooms from palace
  const initializeExerciseRooms = useCallback((palace: Palace): RecallExerciseState[] => {
    return palace.rooms.map((room) => ({
      roomId: room.id,
      roomName: room.name,
      items: room.items.map((item, index) => ({
        id: `item-${index}`,
        text: item,
      })),
      revealed: false,
      correctRecall: false,
      incorrectRecall: false,
    }));
  }, []);

  useEffect(() => {
    setRooms(initializeExerciseRooms(palace));
  }, [palace, initializeExerciseRooms]);

  // Timer logic
  useEffect(() => {
    if (exerciseState.isPlaying && !exerciseState.isPaused && !exerciseState.isCompleted) {
      timerRef.current = setInterval(() => {
        setExerciseState((prev) => {
          const timeLeft = prev.timer - 1;
          if (timeLeft <= 0) {
            handleTimeUp();
            return { ...prev, timer: 0, isCompleted: true };
          }
          return { ...prev, timer: timeLeft };
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [exerciseState.isPlaying, exerciseState.isPaused, exerciseState.isCompleted]);

  // Calculate difficulty settings
  const getDifficultySettings = useCallback(() => {
    const settings = DIFFICULTY_CONFIG[difficulty];
    const totalItems = palace.rooms.reduce((sum, room) => sum + room.items.length, 0);
    return {
      itemsPerRoom: Math.floor(totalItems / settings.roomsPerExercise),
      timeLimit: settings.timerDuration,
      revealDelay: settings.revealDelay,
    };
  }, [difficulty, palace.rooms]);

  const handleStartExercise = () => {
    setExerciseState({
      isPlaying: true,
      isPaused: false,
      isCompleted: false,
      currentMode: 'exercise',
      timer: getDifficultySettings().timeLimit,
      score: 0,
      correctRecalls: 0,
      incorrectRecalls: 0,
      feedback: null,
    });
  };

  const handlePauseExercise = () => {
    setExerciseState((prev) => ({
      ...prev,
      isPaused: !prev.isPaused,
    }));
  };

  const handleResumeExercise = () => {
    setExerciseState((prev) => ({
      ...prev,
      isPaused: false,
    }));
  };

  const handleTimeUp = () => {
    setExerciseState((prev) => ({
      ...prev,
      isCompleted: true,
      feedback: {
        message: 'Time is up!',
        type: 'info',
      },
    }));
    completeExercise();
  };

  const handleSelectRoom = (roomId: string) => {
    if (exerciseState.isCompleted) return;
    setSelectedRoom(roomId);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(e.target.value);
  };

  const handleReveal = () => {
    if (!selectedRoom) return;

    setRooms((prevRooms) =>
      prevRooms.map((room) =>
        room.roomId === selectedRoom ? { ...room, revealed: true } : room
      )
    );

    setExerciseState((prev) => ({
      ...prev,
      feedback: {
        message: 'Items revealed',
        type: 'info',
      },
    }));
  };

  const handleRecall = () => {
    if (!selectedRoom) return;

    const currentRoom = rooms.find((room) => room.roomId === selectedRoom);
    if (!currentRoom) return;

    const expectedItems = currentRoom.items.map((item) => item.text);
    const userItems = userInput.trim().split('\n').filter((item) => item.trim() !== '');

    const isCorrect = expectedItems.length === userItems.length &&
      expectedItems.every((item) => userItems.includes(item));

    // Update room state
    setRooms((prevRooms) =>
      prevRooms.map((room) =>
        room.roomId === selectedRoom
          ? {
              ...room,
              correctRecall: isCorrect,
              incorrectRecall: !isCorrect,
            }
          : room
      )
    );

    // Update score
    setExerciseState((prev) => ({
      ...prev,
      score: isCorrect ? prev.score + 100 : prev.score,
      correctRecalls: isCorrect ? prev.correctRecalls + 1 : prev.correctRecalls,
      incorrectRecalls: !isCorrect ? prev.incorrectRecalls + 1 : prev.incorrectRecalls,
      feedback: isCorrect ? { message: 'Correct!', type: 'success' } : { message: 'Incorrect', type: 'error' },
    }));

    setUserInput('');
  };

  const handleBackToReview = () => {
    setExerciseState((prev) => ({
      ...prev,
      currentMode: 'review',
    }));
  };

  const handleNextRoom = () => {
    if (!selectedRoom) return;

    const currentIndex = rooms.findIndex((room) => room.roomId === selectedRoom);
    const nextIndex = currentIndex + 1;

    if (nextIndex < rooms.length) {
      setSelectedRoom(rooms[nextIndex].roomId);
      setUserInput('');
    } else {
      // All rooms completed
      completeExercise();
    }
  };

  const completeExercise = () => {
    if (exerciseState.isPlaying) {
      // Save session to localStorage
      const session: ExerciseSession = {
        id: `recall-${Date.now()}`,
        palaceId: palace.id,
        palaceName: palace.name,
        exerciseType: 'recall',
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        duration: getDifficultySettings().timeLimit - exerciseState.timer,
        score: exerciseState.score,
        totalItems: palace.rooms.reduce((sum, room) => sum + room.items.length, 0),
        correctItems: exerciseState.correctRecalls,
        accuracy: exerciseState.correctRecalls > 0
          ? Math.round((exerciseState.correctRecalls / (exerciseState.correctRecalls + exerciseState.incorrectRecalls)) * 100)
          : 0,
        difficulty,
      };

      saveExerciseSession(session);
      onExerciseComplete?.(session);

      setExerciseState((prev) => ({
        ...prev,
        isCompleted: true,
        isPlaying: false,
      }));
    }
  };

  const handleRestart = () => {
    setRooms(initializeExerciseRooms(palace));
    setSelectedRoom(null);
    setUserInput('');
    setExerciseState({
      isPlaying: false,
      isPaused: false,
      isCompleted: false,
      currentMode: 'review',
      timer: 0,
      score: 0,
      correctRecalls: 0,
      incorrectRecalls: 0,
      feedback: null,
    });
  };

  const handleBackToPractice = () => {
    handleRestart();
  };

  // Render room card
  const renderRoomCard = (room: RecallExerciseState) => {
    const isSelected = selectedRoom === room.roomId;
    const isRevealed = room.revealed;

    return (
      <div
        key={room.roomId}
        className={`recall-exercise-room ${isSelected ? 'selected' : ''} ${room.correctRecall ? 'correct' : ''} ${room.incorrectRecall ? 'incorrect' : ''}`}
        onClick={() => handleSelectRoom(room.roomId)}
      >
        <div className="room-header">
          <h4>{room.roomName}</h4>
          {isRevealed && (
            <span className={`room-status ${room.correctRecall ? 'correct' : 'incorrect'}`}>
              {room.correctRecall ? '✓ Correct' : '✗ Incorrect'}
            </span>
          )}
        </div>

        {isRevealed ? (
          <div className="room-items revealed">
            {room.items.map((item) => (
              <div key={item.id} className="item-item revealed">
                {item.text}
              </div>
            ))}
          </div>
        ) : (
          <div className="room-items not-revealed">
            {room.items.map((item) => (
              <div key={item.id} className="item-item">
                <span className="item-text">
                  {item.text}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Render exercise controls
  const renderExerciseControls = () => (
    <div className="exercise-controls">
      <div className="control-group">
        <div className="timer-display">
          <span>Time Left:</span>
          <span className="timer-value">{exerciseState.timer}s</span>
        </div>
        <div className="score-display">
          <span>Score:</span>
          <span className="score-value">{exerciseState.score}</span>
        </div>
      </div>

      <div className="control-buttons">
        <button
          className="btn btn-secondary"
          onClick={handlePauseExercise}
          disabled={exerciseState.isPaused || exerciseState.isCompleted}
        >
          {exerciseState.isPaused ? 'Resume' : 'Pause'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={handleResumeExercise}
          disabled={!exerciseState.isPaused}
        >
          Resume
        </button>
      </div>
    </div>
  );

  // Render review mode
  const renderReviewMode = () => (
    <div className="review-mode">
      <div className="review-controls">
        <div className="difficulty-selector">
          <label htmlFor="difficulty">Difficulty:</label>
          <select
            id="difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value as ExerciseDifficulty)}
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>

        <div className="review-actions">
          <button
            className="btn btn-primary"
            onClick={handleStartExercise}
          >
            Start Exercise
          </button>
        </div>
      </div>

      <div className="rooms-container">
        {rooms.map(renderRoomCard)}
      </div>
    </div>
  );

  // Render exercise mode
  const renderExerciseMode = () => (
    <div className="exercise-mode">
      {renderExerciseControls()}

      <div className="exercise-content">
        <div className="rooms-container">
          {rooms.map(renderRoomCard)}
        </div>

        {selectedRoom && (
          <div className="exercise-input-section">
            <div className="input-header">
              <h4>Recall items for: {rooms.find(r => r.roomId === selectedRoom)?.roomName}</h4>
              {rooms.find(r => r.roomId === selectedRoom)?.revealed && (
                <span className="item-count">
                  {rooms.find(r => r.roomId === selectedRoom)?.items.length} items
                </span>
              )}
            </div>

            <textarea
              className="recall-input"
              placeholder="Type each item on a new line..."
              value={userInput}
              onChange={handleInputChange}
              disabled={exerciseState.isPaused || exerciseState.isCompleted}
              rows={5}
            />

            <div className="input-actions">
              <button
                className="btn btn-secondary"
                onClick={handleReveal}
                disabled={rooms.find(r => r.roomId === selectedRoom)?.revealed || exerciseState.isPaused || exerciseState.isCompleted}
              >
                Reveal Items
              </button>
              <button
                className="btn btn-primary"
                onClick={handleRecall}
                disabled={!userInput.trim() || exerciseState.isPaused || exerciseState.isCompleted}
              >
                Submit Recall
              </button>
            </div>

            {exerciseState.feedback && (
              <div className={`feedback-message ${exerciseState.feedback.type}`}>
                {exerciseState.feedback.message}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  // Render completion screen
  const renderCompletionScreen = () => (
    <div className="exercise-completion">
      <h2>Exercise Complete!</h2>
      <div className="completion-summary">
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Score</span>
            <span className="stat-value">{exerciseState.score}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Correct Recalls</span>
            <span className="stat-value">{exerciseState.correctRecalls}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Incorrect Recalls</span>
            <span className="stat-value">{exerciseState.incorrectRecalls}</span>
          </div>
        </div>

        <div className="completion-actions">
          <button
            className="btn btn-primary"
            onClick={handleRestart}
          >
            Try Again
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleBackToPractice}
          >
            Back to Practice
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="recall-exercise">
      {exerciseState.isCompleted ? (
        renderCompletionScreen()
      ) : exerciseState.currentMode === 'review' ? (
        renderReviewMode()
      ) : (
        renderExerciseMode()
      )}
    </div>
  );
};

export default RecallExercise;
