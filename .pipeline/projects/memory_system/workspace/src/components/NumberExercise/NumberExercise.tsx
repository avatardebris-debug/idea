import React, { useState, useEffect, useCallback } from 'react';
import { generateNumbers, shuffleArray } from '../utils/numberGenerator';
import { MIN_NUMBER_LENGTH, MAX_NUMBER_LENGTH } from '../config/constants';
import './NumberExercise.css';

interface NumberExerciseProps {
  initialLength?: number;
  onExerciseComplete?: (stats: any) => void;
}

interface NumberExerciseStats {
  currentLevel: number;
  correctAttempts: number;
  totalAttempts: number;
  timeElapsed: number;
}

const NumberExercise: React.FC<NumberExerciseProps> = ({
  initialLength = 3,
  onExerciseComplete
}) => {
  const [sequence, setSequence] = useState<number[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [currentLevel, setCurrentLevel] = useState<number>(initialLength);
  const [isDisplayingSequence, setIsDisplayingSequence] = useState<boolean>(false);
  const [isWaitingForInput, setIsWaitingForInput] = useState<boolean>(false);
  const [feedback, setFeedback] = useState<'correct' | 'incorrect' | null>(null);
  const [correctAttempts, setCorrectAttempts] = useState<number>(0);
  const [totalAttempts, setTotalAttempts] = useState<number>(0);
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  // Initialize sequence
  const initializeSequence = useCallback(() => {
    const newSequence = generateNumbers(currentLevel);
    setSequence(newSequence);
    setUserInput('');
    setFeedback(null);
  }, [currentLevel]);

  useEffect(() => {
    initializeSequence();
  }, [initializeSequence]);

  // Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  // Display sequence to user
  useEffect(() => {
    if (sequence.length > 0) {
      setIsDisplayingSequence(true);
      setIsWaitingForInput(false);
      
      // Show sequence with delays
      let displayIndex = 0;
      const displayInterval = setInterval(() => {
        if (displayIndex < sequence.length) {
          displayIndex++;
        } else {
          clearInterval(displayInterval);
          setIsDisplayingSequence(false);
          setIsWaitingForInput(true);
        }
      }, 1000);

      return () => clearInterval(displayInterval);
    }
  }, [sequence]);

  // Handle user input
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!isWaitingForInput) return;
    
    const value = e.target.value;
    if (/^\d*$/.test(value)) {
      setUserInput(value);
    }
  };

  const handleSubmit = () => {
    if (!isWaitingForInput) return;

    setTotalAttempts(prev => prev + 1);

    // Check if input matches sequence
    const inputArray = userInput.split('').map(Number);
    const isCorrect = JSON.stringify(inputArray) === JSON.stringify(sequence);

    if (isCorrect) {
      setFeedback('correct');
      setCorrectAttempts(prev => prev + 1);
      
      // Progress to next level
      setTimeout(() => {
        if (currentLevel < MAX_NUMBER_LENGTH) {
          setCurrentLevel(prev => prev + 1);
        } else {
          setIsPlaying(false);
          if (onExerciseComplete) {
            onExerciseComplete({
              currentLevel: currentLevel - 1,
              correctAttempts,
              totalAttempts: totalAttempts + 1,
              timeElapsed
            });
          }
        }
      }, 1500);
    } else {
      setFeedback('incorrect');
      
      setTimeout(() => {
        setFeedback(null);
        setUserInput('');
        setIsWaitingForInput(false);
        initializeSequence();
      }, 1500);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const handleReset = () => {
    setCurrentLevel(initialLength);
    setCorrectAttempts(0);
    setTotalAttempts(0);
    setTimeElapsed(0);
    setIsPlaying(true);
    setUserInput('');
    setFeedback(null);
    setIsWaitingForInput(false);
    initializeSequence();
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="number-exercise">
      <h2>Number Sequence Exercise</h2>
      
      <div className="exercise-stats">
        <div className="stat">
          <span className="stat-label">Level:</span>
          <span className="stat-value">{currentLevel}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Correct:</span>
          <span className="stat-value">{correctAttempts}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Time:</span>
          <span className="stat-value">{formatTime(timeElapsed)}</span>
        </div>
      </div>

      <div className="sequence-display">
        {isDisplayingSequence ? (
          <div className="sequence-indicators">
            {sequence.map((num, index) => (
              <div key={index} className={`sequence-dot ${index < sequence.length ? 'active' : ''}`}>
                {num}
              </div>
            ))}
          </div>
        ) : (
          <div className="input-section">
            <div className={`feedback-message ${feedback || ''}`}>
              {feedback === 'correct' && '✓ Correct!'}
              {feedback === 'incorrect' && '✗ Try again!'}
            </div>
            
            <input
              type="text"
              value={userInput}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder={isWaitingForInput ? "Enter the sequence" : "Watch the sequence"}
              disabled={!isWaitingForInput}
              maxLength={currentLevel}
              className={`input-field ${feedback || ''}`}
            />
            
            {isWaitingForInput && (
              <button 
                className="btn btn-primary" 
                onClick={handleSubmit}
                disabled={!userInput}
              >
                Submit
              </button>
            )}
          </div>
        )}
      </div>

      <div className="exercise-controls">
        <button className="btn btn-secondary" onClick={handleReset}>
          Reset Exercise
        </button>
      </div>
    </div>
  );
};

export default NumberExercise;
