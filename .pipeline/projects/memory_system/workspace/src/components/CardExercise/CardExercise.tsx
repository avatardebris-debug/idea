import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../types/cards';
import { generateCards, shuffleArray } from '../utils/cardGenerator';
import { MIN_CARD_PAIRS, MAX_CARD_PAIRS } from '../config/constants';
import CardComponent from './Card';
import './Card.css';

interface CardExerciseProps {
  cardCount?: number;
  onExerciseComplete?: (stats: any) => void;
}

interface CardGameStats {
  moves: number;
  timeElapsed: number;
  pairsFound: number;
  totalPairs: number;
}

const CardExercise: React.FC<CardExerciseProps> = ({ 
  cardCount = 6,
  onExerciseComplete 
}) => {
  const [cards, setCards] = useState<Card[]>([]);
  const [flippedCards, setFlippedCards] = useState<Card[]>([]);
  const [matchedPairs, setMatchedPairs] = useState<number>(0);
  const [moves, setMoves] = useState<number>(0);
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [gameComplete, setGameComplete] = useState<boolean>(false);

  const totalPairs = cardCount;

  // Initialize game
  const initializeGame = useCallback(() => {
    const newCards = generateCards(cardCount);
    setCards(newCards);
    setFlippedCards([]);
    setMatchedPairs(0);
    setMoves(0);
    setTimeElapsed(0);
    setIsPlaying(true);
    setGameComplete(false);
  }, [cardCount]);

  useEffect(() => {
    initializeGame();
  }, [initializeGame]);

  // Timer
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && !gameComplete) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, gameComplete]);

  // Check for match
  const checkForMatch = useCallback(() => {
    if (flippedCards.length === 2) {
      const [firstCard, secondCard] = flippedCards;
      
      if (firstCard.value === secondCard.value) {
        // Match found
        setCards(prevCards => 
          prevCards.map(card => 
            (card.id === firstCard.id || card.id === secondCard.id)
              ? { ...card, isMatched: true, isFlipped: true }
              : card
          )
        );
        setMatchedPairs(prev => prev + 1);
        setFlippedCards([]);
      } else {
        // No match - flip back after delay
        setTimeout(() => {
          setCards(prevCards => 
            prevCards.map(card => 
              (card.id === firstCard.id || card.id === secondCard.id)
                ? { ...card, isFlipped: false }
                : card
            )
          );
          setFlippedCards([]);
        }, 1000);
      }
      setMoves(prev => prev + 1);
    }
  }, [flippedCards]);

  useEffect(() => {
    checkForMatch();
  }, [flippedCards, checkForMatch]);

  // Check for game completion
  useEffect(() => {
    if (matchedPairs === totalPairs && totalPairs > 0) {
      setGameComplete(true);
      setIsPlaying(false);
      if (onExerciseComplete) {
        onExerciseComplete({
          moves,
          timeElapsed,
          pairsFound: matchedPairs,
          totalPairs
        });
      }
    }
  }, [matchedPairs, totalPairs, moves, timeElapsed, onExerciseComplete]);

  const handleCardClick = (card: Card) => {
    if (flippedCards.length >= 2 || card.isFlipped || card.isMatched) {
      return;
    }

    const newFlipped = [...flippedCards, card];
    setFlippedCards(newFlipped);

    setCards(prevCards => 
      prevCards.map(c => 
        c.id === card.id ? { ...c, isFlipped: true } : c
      )
    );
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleReset = () => {
    initializeGame();
  };

  return (
    <div className="card-exercise">
      <h2>Card Matching Exercise</h2>
      
      <div className="exercise-stats">
        <div className="stat">
          <span className="stat-label">Moves:</span>
          <span className="stat-value">{moves}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Time:</span>
          <span className="stat-value">{formatTime(timeElapsed)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Pairs:</span>
          <span className="stat-value">{matchedPairs}/{totalPairs}</span>
        </div>
      </div>

      <div className="card-grid">
        {cards.map(card => (
          <CardComponent
            key={card.id}
            card={card}
            onClick={handleCardClick}
          />
        ))}
      </div>

      {gameComplete && (
        <div className="game-complete-overlay">
          <div className="game-complete-message">
            <h3>🎉 Exercise Complete!</h3>
            <p>You matched all {totalPairs} pairs in {moves} moves and {formatTime(timeElapsed)}!</p>
            <button className="btn btn-primary" onClick={handleReset}>
              Play Again
            </button>
          </div>
        </div>
      )}

      <div className="exercise-controls">
        <button className="btn btn-secondary" onClick={handleReset}>
          Reset Game
        </button>
      </div>
    </div>
  );
};

export default CardExercise;
