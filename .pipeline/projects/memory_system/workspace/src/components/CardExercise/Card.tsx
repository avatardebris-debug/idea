import React from 'react';
import { Card } from '../types/cards';
import './Card.css';

interface CardProps {
  card: Card;
  onClick: (card: Card) => void;
}

const CardComponent: React.FC<CardProps> = ({ card, onClick }) => {
  const handleClick = () => {
    if (!card.isFlipped && !card.isMatched) {
      onClick(card);
    }
  };

  return (
    <div
      className={`card ${card.isFlipped ? 'flipped' : ''} ${card.isMatched ? 'matched' : ''}`}
      onClick={handleClick}
    >
      <div className="card-face card-front">
        <span className="card-number">{card.value}</span>
      </div>
      <div className="card-face card-back">
        <div className="card-back-pattern"></div>
      </div>
    </div>
  );
};

export default CardComponent;
