import React, { useState, useEffect } from 'react';
import { Palace, ExerciseType } from '../types/palace';
import SpatialExercise from './SpatialExercise';
import RecallExercise from './RecallExercise';
import './ExerciseRunner.css';

interface ExerciseRunnerProps {
  palace: Palace | null;
  exerciseType: ExerciseType;
  onExerciseComplete?: (success: boolean) => void;
}

/**
 * ExerciseRunner Component
 * Main component for running memory exercises
 */
const ExerciseRunner: React.FC<ExerciseRunnerProps> = ({
  palace,
  exerciseType,
  onExerciseComplete,
}) => {
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [exerciseComplete, setExerciseComplete] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleExerciseStart = () => {
    setIsRunning(true);
    setError(null);
  };

  const handleExerciseComplete = (success: boolean) => {
    setIsRunning(false);
    setExerciseComplete(true);
    onExerciseComplete?.(success);
  };

  const handleRestart = () => {
    setExerciseComplete(false);
    setIsRunning(false);
    setError(null);
  };

  const handleBackToPractice = () => {
    setExerciseComplete(false);
    setIsRunning(false);
    setError(null);
  };

  if (!palace) {
    return (
      <div className="exercise-runner">
        <div className="exercise-error">
          <p>No palace selected. Please create or select a palace to begin an exercise.</p>
        </div>
      </div>
    );
  }

  const renderExercise = () => {
    switch (exerciseType) {
      case 'spatial':
        return (
          <SpatialExercise
            palace={palace}
            onExerciseComplete={handleExerciseComplete}
          />
        );
      case 'recall':
        return (
          <RecallExercise
            palace={palace}
            onExerciseComplete={handleExerciseComplete}
          />
        );
      default:
        return (
          <div className="exercise-error">
            <p>Unknown exercise type: {exerciseType}</p>
          </div>
        );
    }
  };

  const renderStartScreen = () => (
    <div className="exercise-start-screen">
      <h2>Start {exerciseType.charAt(0).toUpperCase() + exerciseType.slice(1)} Exercise</h2>
      <p>Palace: <strong>{palace.name}</strong></p>
      <p>Description: {palace.description || 'No description'}</p>
      
      <div className="exercise-details">
        <h3>Exercise Details</h3>
        <div className="detail-item">
          <span className="label">Total Rooms:</span>
          <span className="value">{palace.rooms.length}</span>
        </div>
        <div className="detail-item">
          <span className="label">Exercise Type:</span>
          <span className="value">{exerciseType.charAt(0).toUpperCase() + exerciseType.slice(1)}</span>
        </div>
      </div>

      <div className="exercise-actions">
        <button
          className="btn btn-primary btn-large"
          onClick={handleExerciseStart}
        >
          Start Exercise
        </button>
        <button
          className="btn btn-secondary btn-large"
          onClick={handleBackToPractice}
        >
          Back to Practice
        </button>
      </div>
    </div>
  );

  const renderCompletionScreen = () => (
    <div className="exercise-completion-screen">
      <h2>Exercise Complete!</h2>
      <div className="completion-summary">
        <p>Great job completing your {exerciseType} exercise!</p>
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
    <div className="exercise-runner">
      {error && (
        <div className="exercise-error">
          <p>{error}</p>
          <button className="btn btn-small" onClick={() => setError(null)}>
            Dismiss
          </button>
        </div>
      )}

      {exerciseComplete ? (
        renderCompletionScreen()
      ) : isRunning ? (
        renderExercise()
      ) : (
        renderStartScreen()
      )}
    </div>
  );
};

export default ExerciseRunner;
