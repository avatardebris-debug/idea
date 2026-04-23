import { describe, it, expect, vi } from 'vitest';
import * as cardGenerator from '../src/utils/cardGenerator';

describe('Card Generator Utilities', () => {
  describe('generateDeck', () => {
    it('generates a standard 52-card deck', () => {
      const deck = cardGenerator.generateDeck();

      expect(deck).toHaveLength(52);
    });

    it('includes all suits', () => {
      const deck = cardGenerator.generateDeck();
      const suits = deck.map(card => card.suit);

      expect(suits).toContain('hearts');
      expect(suits).toContain('diamonds');
      expect(suits).toContain('clubs');
      expect(suits).toContain('spades');
    });

    it('includes all ranks', () => {
      const deck = cardGenerator.generateDeck();
      const ranks = deck.map(card => card.rank);

      expect(ranks).toContain('ace');
      expect(ranks).toContain('2');
      expect(ranks).toContain('10');
      expect(ranks).toContain('jack');
      expect(ranks).toContain('queen');
      expect(ranks).toContain('king');
    });

    it('includes all 13 ranks per suit', () => {
      const deck = cardGenerator.generateDeck();

      const hearts = deck.filter(card => card.suit === 'hearts');
      expect(hearts).toHaveLength(13);

      const heartsRanks = hearts.map(card => card.rank);
      expect(heartsRanks).toContain('ace');
      expect(heartsRanks).toContain('king');
      expect(heartsRanks).toContain('queen');
      expect(heartsRanks).toContain('jack');
      expect(heartsRanks).toContain('10');
      expect(heartsRanks).toContain('2');
    });

    it('has unique card combinations', () => {
      const deck = cardGenerator.generateDeck();
      const cardStrings = deck.map(card => `${card.rank}-${card.suit}`);
      const uniqueCardStrings = new Set(cardStrings);

      expect(cardStrings.length).toBe(uniqueCardStrings.size);
    });

    it('includes card objects with all properties', () => {
      const deck = cardGenerator.generateDeck();
      const card = deck[0];

      expect(card.id).toBeDefined();
      expect(card.rank).toBeDefined();
      expect(card.suit).toBeDefined();
      expect(card.value).toBeDefined();
      expect(card.color).toBeDefined();
    });

    it('assigns correct values to ranks', () => {
      const deck = cardGenerator.generateDeck();

      const ace = deck.find(card => card.rank === 'ace');
      expect(ace?.value).toBe(1);

      const king = deck.find(card => card.rank === 'king');
      expect(king?.value).toBe(13);

      const queen = deck.find(card => card.rank === 'queen');
      expect(queen?.value).toBe(12);

      const jack = deck.find(card => card.rank === 'jack');
      expect(jack?.value).toBe(11);

      const ten = deck.find(card => card.rank === '10');
      expect(ten?.value).toBe(10);
    });

    it('assigns correct colors to suits', () => {
      const deck = cardGenerator.generateDeck();

      const hearts = deck.find(card => card.suit === 'hearts');
      expect(hearts?.color).toBe('red');

      const diamonds = deck.find(card => card.suit === 'diamonds');
      expect(diamonds?.color).toBe('red');

      const clubs = deck.find(card => card.suit === 'clubs');
      expect(clubs?.color).toBe('black');

      const spades = deck.find(card => card.suit === 'spades');
      expect(spades?.color).toBe('black');
    });

    it('generates unique IDs for each card', () => {
      const deck = cardGenerator.generateDeck();
      const cardIds = deck.map(card => card.id);
      const uniqueIds = new Set(cardIds);

      expect(cardIds.length).toBe(uniqueIds.size);
    });
  });

  describe('getDeckColorCount', () => {
    it('returns red and black counts', () => {
      const counts = cardGenerator.getDeckColorCount();

      expect(counts.red).toBe(26);
      expect(counts.black).toBe(26);
    });

    it('returns correct total', () => {
      const counts = cardGenerator.getDeckColorCount();

      expect(counts.red + counts.black).toBe(52);
    });
  });

  describe('getDeckSuitCount', () => {
    it('returns count for each suit', () => {
      const counts = cardGenerator.getDeckSuitCount();

      expect(counts.hearts).toBe(13);
      expect(counts.diamonds).toBe(13);
      expect(counts.clubs).toBe(13);
      expect(counts.spades).toBe(13);
    });

    it('returns correct total', () => {
      const counts = cardGenerator.getDeckSuitCount();

      expect(counts.hearts + counts.diamonds + counts.clubs + counts.spades).toBe(52);
    });
  });

  describe('getDeckRankCount', () => {
    it('returns count for each rank', () => {
      const counts = cardGenerator.getDeckRankCount();

      expect(counts.ace).toBe(4);
      expect(counts.king).toBe(4);
      expect(counts.queen).toBe(4);
      expect(counts.jack).toBe(4);
      expect(counts.ten).toBe(4);
      expect(counts.two).toBe(4);
    });

    it('returns correct total', () => {
      const counts = cardGenerator.getDeckRankCount();

      const total = Object.values(counts).reduce((sum, count) => sum + count, 0);
      expect(total).toBe(52);
    });
  });

  describe('getRankValue', () => {
    it('returns value for ace', () => {
      const value = cardGenerator.getRankValue('ace');
      expect(value).toBe(1);
    });

    it('returns value for king', () => {
      const value = cardGenerator.getRankValue('king');
      expect(value).toBe(13);
    });

    it('returns value for queen', () => {
      const value = cardGenerator.getRankValue('queen');
      expect(value).toBe(12);
    });

    it('returns value for jack', () => {
      const value = cardGenerator.getRankValue('jack');
      expect(value).toBe(11);
    });

    it('returns value for numeric ranks', () => {
      expect(cardGenerator.getRankValue('10')).toBe(10);
      expect(cardGenerator.getRankValue('9')).toBe(9);
      expect(cardGenerator.getRankValue('2')).toBe(2);
    });

    it('returns undefined for invalid rank', () => {
      const value = cardGenerator.getRankValue('invalid');
      expect(value).toBeUndefined();
    });
  });

  describe('getRankValueForCard', () => {
    it('returns value for card with ace', () => {
      const value = cardGenerator.getRankValueForCard({ id: 'c1', rank: 'ace', suit: 'hearts', value: 1, color: 'red' });
      expect(value).toBe(1);
    });

    it('returns value for card with king', () => {
      const value = cardGenerator.getRankValueForCard({ id: 'c2', rank: 'king', suit: 'spades', value: 13, color: 'black' });
      expect(value).toBe(13);
    });

    it('returns value for card with numeric rank', () => {
      const value = cardGenerator.getRankValueForCard({ id: 'c3', rank: '7', suit: 'diamonds', value: 7, color: 'red' });
      expect(value).toBe(7);
    });
  });

  describe('getDeckRanks', () => {
    it('returns all unique ranks', () => {
      const ranks = cardGenerator.getDeckRanks();

      expect(ranks).toContain('ace');
      expect(ranks).toContain('king');
      expect(ranks).toContain('queen');
      expect(ranks).toContain('jack');
      expect(ranks).toContain('10');
      expect(ranks).toContain('2');
    });

    it('returns 13 unique ranks', () => {
      const ranks = cardGenerator.getDeckRanks();

      expect(ranks).toHaveLength(13);
    });

    it('returns ranks in correct order', () => {
      const ranks = cardGenerator.getDeckRanks();

      expect(ranks[0]).toBe('ace');
      expect(ranks[ranks.length - 1]).toBe('2');
    });
  });

  describe('getDeckSuits', () => {
    it('returns all suits', () => {
      const suits = cardGenerator.getDeckSuits();

      expect(suits).toContain('hearts');
      expect(suits).toContain('diamonds');
      expect(suits).toContain('clubs');
      expect(suits).toContain('spades');
    });

    it('returns 4 suits', () => {
      const suits = cardGenerator.getDeckSuits();

      expect(suits).toHaveLength(4);
    });

    it('returns suits in correct order', () => {
      const suits = cardGenerator.getDeckSuits();

      expect(suits[0]).toBe('hearts');
      expect(suits[3]).toBe('spades');
    });
  });

  describe('getDeckColors', () => {
    it('returns both colors', () => {
      const colors = cardGenerator.getDeckColors();

      expect(colors).toContain('red');
      expect(colors).toContain('black');
    });

    it('returns 2 colors', () => {
      const colors = cardGenerator.getDeckColors();

      expect(colors).toHaveLength(2);
    });
  });

  describe('getSuitColor', () => {
    it('returns red for hearts', () => {
      const color = cardGenerator.getSuitColor('hearts');
      expect(color).toBe('red');
    });

    it('returns red for diamonds', () => {
      const color = cardGenerator.getSuitColor('diamonds');
      expect(color).toBe('red');
    });

    it('returns black for clubs', () => {
      const color = cardGenerator.getSuitColor('clubs');
      expect(color).toBe('black');
    });

    it('returns black for spades', () => {
      const color = cardGenerator.getSuitColor('spades');
      expect(color).toBe('black');
    });

    it('returns undefined for invalid suit', () => {
      const color = cardGenerator.getSuitColor('invalid');
      expect(color).toBeUndefined();
    });
  });

  describe('getSuitSymbol', () => {
    it('returns hearts symbol', () => {
      const symbol = cardGenerator.getSuitSymbol('hearts');
      expect(symbol).toBe('♥');
    });

    it('returns diamonds symbol', () => {
      const symbol = cardGenerator.getSuitSymbol('diamonds');
      expect(symbol).toBe('♦');
    });

    it('returns clubs symbol', () => {
      const symbol = cardGenerator.getSuitSymbol('clubs');
      expect(symbol).toBe('♣');
    });

    it('returns spades symbol', () => {
      const symbol = cardGenerator.getSuitSymbol('spades');
      expect(symbol).toBe('♠');
    });

    it('returns empty string for invalid suit', () => {
      const symbol = cardGenerator.getSuitSymbol('invalid');
      expect(symbol).toBe('');
    });
  });

  describe('getCardSymbol', () => {
    it('returns card symbol with suit', () => {
      const symbol = cardGenerator.getCardSymbol('ace', 'hearts');
      expect(symbol).toBe('A♥');
    });

    it('returns card symbol with numeric rank', () => {
      const symbol = cardGenerator.getCardSymbol('10', 'spades');
      expect(symbol).toBe('10♠');
    });

    it('returns card symbol with queen', () => {
      const symbol = cardGenerator.getCardSymbol('queen', 'diamonds');
      expect(symbol).toBe('Q♦');
    });

    it('returns empty string for invalid suit', () => {
      const symbol = cardGenerator.getCardSymbol('ace', 'invalid');
      expect(symbol).toBe('');
    });
  });

  describe('getCardDisplay', () => {
    it('returns formatted card display', () => {
      const display = cardGenerator.getCardDisplay('ace', 'hearts');
      expect(display).toBe('A♥');
    });

    it('returns formatted card display for numeric rank', () => {
      const display = cardGenerator.getCardDisplay('10', 'spades');
      expect(display).toBe('10♠');
    });

    it('returns formatted card display for queen', () => {
      const display = cardGenerator.getCardDisplay('queen', 'clubs');
      expect(display).toBe('Q♣');
    });

    it('returns empty string for invalid suit', () => {
      const display = cardGenerator.getCardDisplay('ace', 'invalid');
      expect(display).toBe('');
    });
  });

  describe('getCardDisplayWithColor', () => {
    it('returns formatted card display with color', () => {
      const display = cardGenerator.getCardDisplayWithColor('ace', 'hearts');
      expect(display).toBe('A♥');
    });

    it('returns black card display', () => {
      const display = cardGenerator.getCardDisplayWithColor('king', 'spades');
      expect(display).toBe('K♠');
    });

    it('returns red card display', () => {
      const display = cardGenerator.getCardDisplayWithColor('queen', 'hearts');
      expect(display).toBe('Q♥');
    });
  });
});
