export interface Card {
  id: string;
  value: string | number;
  isFlipped: boolean;
  isMatched: boolean;
}

export interface CardGameStats {
  moves: number;
  timeElapsed: number;
  pairsFound: number;
  totalPairs: number;
}

export interface CardExerciseProps {
  cardCount?: number;
  onExerciseComplete?: (stats: CardGameStats) => void;
}
