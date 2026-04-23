import { MIN_NUMBER_LENGTH, MAX_NUMBER_LENGTH } from '../config/constants';

export const generateNumbers = (length: number): number[] => {
  if (length < MIN_NUMBER_LENGTH) {
    length = MIN_NUMBER_LENGTH;
  }
  if (length > MAX_NUMBER_LENGTH) {
    length = MAX_NUMBER_LENGTH;
  }

  const numbers: number[] = [];
  for (let i = 0; i < length; i++) {
    numbers.push(Math.floor(Math.random() * 10));
  }

  return numbers;
};

export const shuffleArray = <T,>(array: T[]): T[] => {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
};
