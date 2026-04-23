import { Card } from '../types/cards';
import { MIN_CARD_PAIRS, MAX_CARD_PAIRS } from '../config/constants';

export const generateCards = (pairCount: number): Card[] => {
  if (pairCount < MIN_CARD_PAIRS) {
    pairCount = MIN_CARD_PAIRS;
  }
  if (pairCount > MAX_CARD_PAIRS) {
    pairCount = MAX_CARD_PAIRS;
  }

  const cardValues: (string | number)[] = [];
  for (let i = 0; i < pairCount; i++) {
    cardValues.push(i + 1);
  }

  const shuffledValues = [...cardValues, ...cardValues].sort(() => Math.random() - 0.5);

  return shuffledValues.map((value, index) => ({
    id: `card-${index}`,
    value,
    isFlipped: false,
    isMatched: false,
  }));
};

export const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
