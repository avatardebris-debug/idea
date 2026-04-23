import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Palace, Room } from '../types/palace';
import {
  RoomExerciseState,
  ExerciseState,
  ExerciseSession,
  DIFFICULTY_CONFIG,
  ExerciseItem,
  ExerciseDifficulty,
} from '../types/exercises';
import { saveExerciseSession } from '../utils/progressTracking';
import './SpatialExercise.css';

export interface SpatialExerciseProps {
  palace: Palace;
  onExerciseComplete?: (session: ExerciseSession) => void;
}

const SpatialExercise: React.FC<SpatialExerciseProps> = ({
  palace,
  onExerciseComplete,
}) => {
  // Initialize rooms with exercise state
  const [rooms, setRooms] = useState<RoomExerciseState[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  const [newItemText, setNewItemText] = useState<string>('');
  
  // Exercise state
  const [exerciseState, setExerciseState] = useState<ExerciseState>({
    isPlaying: false,
    isPaused: false,
    isCompleted: false,
    currentMode: 'placement',
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
  const initializeExerciseRooms = useCallback((palace: Palace): RoomExerciseState[] => {
    return palace.rooms.map((room) => ({
      roomId: room.id,
      roomName: room.name,
      items: room.items.map((item, index) => ({
        id: `item-${index}`,
        text: item,
      })),
      revealed: false,
      correctRecall: false,
    }));
  }, []);

  // Set up initial rooms
  useEffect(() => {
    const initialRooms = initializeExerciseRooms(palace);
    setRooms(initialRooms);
  }, [palace, initializeExerciseRooms]);

  // Timer effect
  useEffect(() => {
    if (exerciseState.isPlaying && !exerciseState.isPaused && !exerciseState.isCompleted) {
      timerRef.current = setInterval(() => {
        setExerciseState((prev) => {
          const newTime = prev.timer - 1;
          if (newTime <= 0) {
            // Time's up
            return {
              ...prev,
              timer: 0,
              isCompleted: true,
              feedback: {
                message: 'Time\'s up! Review your answers.',
                type: 'info',
              },
            };
          }
          return { ...prev, timer: newTime };
        });
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [exerciseState.isPlaying, exerciseState.isPaused, exerciseState.isCompleted]);

  // Handle difficulty change
  const handleDifficultyChange = (newDifficulty: ExerciseDifficulty) => {
    setDifficulty(newDifficulty);
    const config = DIFFICULTY_CONFIG[newDifficulty];
    setExerciseState((prev) => ({
      ...prev,
      timer: config.timerDuration,
      score: 0,
      correctRecalls: 0,
      incorrectRecalls: 0,
    }));
  };

  // Start exercise
  const startExercise = () => {
    const config = DIFFICULTY_CONFIG[difficulty];
    setExerciseState({
      isPlaying: true,
      isPaused: false,
      isCompleted: false,
      currentMode: 'placement',
      timer: config.timerDuration,
      score: 0,
      correctRecalls: 0,
      incorrectRecalls: 0,
      feedback: {
        message: 'Start placing items in rooms. You can switch to recall mode anytime!',
        type: 'info',
      },
    });
  };

  // Switch to recall mode
  const switchToRecall = () => {
    // Hide all items
    setRooms((prev) =>
      prev.map((room) => ({
        ...room,
        revealed: false,
      }))
    );

    setExerciseState((prev) => ({
      ...prev,
      currentMode: 'recall',
      feedback: {
        message: 'Recall mode active. Place items back in the correct rooms!',
        type: 'info',
      },
    }));
  };

  // Reveal items in a room
  const revealItems = (roomId: string) => {
    setRooms((prev) =>
      prev.map((room) =>
        room.roomId === roomId ? { ...room, revealed: true } : room
      )
    );

    setExerciseState((prev) => ({
      ...prev,
      feedback: {
        message: 'Items revealed for review',
        type: 'info',
      },
    }));
  };

  // Hide items in a room
  const hideItems = (roomId: string) => {
    setRooms((prev) =>
      prev.map((room) =>
        room.roomId === roomId ? { ...room, revealed: false } : room
      )
    );
  };

  // Select a room
  const selectRoom = (roomId: string) => {
    if (exerciseState.isCompleted) return;
    setSelectedRoom(roomId);
  };

  // Add a new item to the selected room
  const addItem = () => {
    if (!newItemText.trim() || !selectedRoom) return;

    setRooms((prev) =>
      prev.map((room) =>
        room.roomId === selectedRoom
          ? {
              ...room,
              items: [
                ...room.items,
                {
                  id: `new-item-${Date.now()}`,
                  text: newItemText.trim(),
                },
              ],
            }
          : room
      )
    );

    setNewItemText('');
  };

  // Remove an item from a room
  const removeItem = (roomId: string, itemId: string) => {
    setRooms((prev) =>
      prev.map((room) =>
        room.roomId === roomId
          ? {
              ...room,
              items: room.items.filter((item) => item.id !== itemId),
            }
          : room
      )
    );
  };

  // Handle item placement (recall mode)
  const placeItem = (roomId: string, itemId: string) => {
    if (exerciseState.isCompleted) return;

    setRooms((prev) =>
      prev.map((room) => {
        if (room.roomId === roomId) {
          const item = room.items.find((i) => i.id === itemId);
          if (item) {
            // Mark as correctly placed
            return {
              ...room,
              correctRecall: true,
              correctRecalls: true,
            };
          }
        }
        return room;
      })
    );

    setExerciseState((prev) => ({
      ...prev,
      correctRecalls: prev.correctRecalls + 1,
      feedback: {
        message: 'Item placed correctly!',
        type: 'success',
      },
    }));
  };

  // Handle incorrect item placement
  const handleIncorrectPlacement = (roomId: string, itemId: string) => {
    setExerciseState((prev) => ({
      ...prev,
      incorrectRecalls: prev.incorrectRecalls + 1,
      feedback: {
        message: 'That room is incorrect. Try again!',
        type: 'error',
      },
    }));
  };

  // Pause/Resume exercise
  const togglePause = () => {
    setExerciseState((prev) => ({
      ...prev,
      isPaused: !prev.isPaused,
    }));
  };

  // Complete exercise
  const completeExercise = () => {
    if (exerciseState.isPlaying) {
      // Calculate total items and correct recalls
      const totalItems = palace.rooms.reduce((sum, room) => sum + room.items.length, 0);
      const correctItems = exerciseState.correctRecalls;

      // Create session record
      const session: ExerciseSession = {
        id: `spatial-${Date.now()}`,
        palaceId: palace.id,
        palaceName: palace.name,
        exerciseType: 'spatial',
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        duration: getDifficultySettings().timerDuration - exerciseState.timer,
        score: exerciseState.score,
        totalItems,
        correctItems,
        accuracy: totalItems > 0
          ? Math.round((correctItems / totalItems) * 100)
          : 0,
        difficulty,
      };

      // Save session
      saveExerciseSession(session);
      onExerciseComplete?.(session);

      setExerciseState((prev) => ({
        ...prev,
        isCompleted: true,
        isPlaying: false,
      }));
    }
  };

  // Get difficulty settings
  const getDifficultySettings = useCallback(() => {
    const settings = DIFFICULTY_CONFIG[difficulty];
    const totalItems = palace.rooms.reduce((sum, room) => sum + room.items.length, 0);
    return {
      itemsPerRoom: Math.floor(totalItems / settings.roomsPerExercise),
      timeLimit: settings.timerDuration,
      revealDelay: settings.revealDelay,
    };
  }, [difficulty, palace.rooms]);

  // Render room card
  const renderRoomCard = (room: RoomExerciseState) => {
    const isSelected = selectedRoom === room.roomId;
    const isRevealed = room.revealed;

    return (
      <div
        key={room.roomId}
        className={`spatial-room ${isSelected ? 'selected' : ''} ${room.correctRecall ? 'correct' : ''}`}
        onClick={() => selectRoom(room.roomId)}
      >
        <div className="room-header">
          <h4>{room.roomName}</h4>
          {isRevealed && (
            <span className="item-count">
              {room.items.length} items
            </span>
          )}
        </div>

        <div className="room-items">
          {isRevealed ? (
            room.items.map((item) => (
              <div key={item.id} className="item revealed">
                <span className="item-text">{item.text}</span>
              </div>
            ))
          ) : (
            <div className="items-placeholder">
              {exerciseState.currentMode === 'recall' ? 'Click to reveal items' : 'No items placed'}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render controls
  const renderControls = () => (
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
          onClick={togglePause}
          disabled={exerciseState.isPaused || exerciseState.isCompleted}
        >
          {exerciseState.isPaused ? 'Resume' : 'Pause'}
        </button>
        <button
          className="btn btn-secondary"
          onClick={() => switchToRecall()}
          disabled={exerciseState.isCompleted}
        >
          Switch to Recall
        </button>
        <button
          className="btn btn-secondary"
          onClick={completeExercise}
          disabled={exerciseState.isCompleted}
        >
          Complete
        </button>
      </div>
    </div>
  );

  // Render placement mode
  const renderPlacementMode = () => (
    <div className="exercise-content">
      <div className="rooms-container">
        {rooms.map(renderRoomCard)}
      </div>

      {selectedRoom && (
        <div className="item-input-section">
          <div className="input-header">
            <h4>Add items to: {rooms.find((r) => r.roomId === selectedRoom)?.roomName}</h4>
          </div>

          <div className="input-group">
            <input
              type="text"
              className="item-input"
              placeholder="Enter item to add"
              value={newItemText}
              onChange={(e) => setNewItemText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  addItem();
                }
              }}
              disabled={exerciseState.isPaused || exerciseState.isCompleted}
            />
            <button
              className="btn btn-primary"
              onClick={addItem}
              disabled={!newItemText.trim() || exerciseState.isPaused || exerciseState.isCompleted}
            >
              Add Item
            </button>
          </div>

          <div className="room-actions">
            <button
              className="btn btn-secondary"
              onClick={() => revealItems(selectedRoom)}
              disabled={rooms.find((r) => r.roomId === selectedRoom)?.revealed || exerciseState.isPaused || exerciseState.isCompleted}
            >
              Reveal Items
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => hideItems(selectedRoom)}
              disabled={!rooms.find((r) => r.roomId === selectedRoom)?.revealed || exerciseState.isPaused || exerciseState.isCompleted}
            >
              Hide Items
            </button>
          </div>
        </div>
      )}
    </div>
  );

  // Render recall mode
  const renderRecallMode = () => (
    <div className="exercise-content">
      <div className="rooms-container">
        {rooms.map(renderRoomCard)}
      </div>

      {selectedRoom && (
        <div className="item-input-section">
          <div className="input-header">
            <h4>
              Recall items for: {rooms.find((r) => r.roomId === selectedRoom)?.roomName}
            </h4>
          </div>

          <div className="input-group">
            <input
              type="text"
              className="item-input"
              placeholder="Enter item to place"
              value={newItemText}
              onChange={(e) => setNewItemText(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  placeItem(selectedRoom, `new-item-${Date.now()}`);
                  setNewItemText('');
                }
              }}
              disabled={exerciseState.isPaused || exerciseState.isCompleted}
            />
            <button
              className="btn btn-primary"
              onClick={() => placeItem(selectedRoom, `new-item-${Date.now()}`)}
              disabled={!newItemText.trim() || exerciseState.isPaused || exerciseState.isCompleted}
            >
              Place Item
            </button>
          </div>
        </div>
      )}
    </div>
  );

  // Render review mode
  const renderReviewMode = () => (
    <div className="exercise-content">
      <div className="rooms-container">
        {rooms.map(renderRoomCard)}
      </div>

      <div className="item-input-section">
        <div className="input-header">
          <h4>Add items to: {selectedRoom ? rooms.find((r) => r.roomId === selectedRoom)?.roomName : 'Select a room'}</h4>
        </div>

        <div className="input-group">
          <input
            type="text"
            className="item-input"
            placeholder="Enter item to add"
            value={newItemText}
            onChange={(e) => setNewItemText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                addItem();
              }
            }}
            disabled={exerciseState.isPaused || exerciseState.isCompleted}
          />
          <button
            className="btn btn-primary"
            onClick={addItem}
            disabled={!newItemText.trim() || exerciseState.isPaused || exerciseState.isCompleted}
          >
            Add Item
          </button>
        </div>
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
            onClick={completeExercise}
          >
            Try Again
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => {
              setRooms(initializeExerciseRooms(palace));
              setExerciseState({
                isPlaying: false,
                isPaused: false,
                isCompleted: false,
                currentMode: 'placement',
                timer: getDifficultySettings().timerDuration,
                score: 0,
                correctRecalls: 0,
                incorrectRecalls: 0,
                feedback: null,
              });
            }}
          >
            Back to Practice
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="spatial-exercise">
      {exerciseState.isCompleted ? (
        renderCompletionScreen()
      ) : (
        <>
          {exerciseState.currentMode === 'recall' ? renderRecallMode() : renderPlacementMode()}
          {renderControls()}
        </>
      )}
    </div>
  );
};

export default SpatialExercise;
