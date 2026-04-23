import { describe, it, expect, vi } from 'vitest';
import * as cardExercise from '../src/utils/cardExercise';

describe('Card Exercise Utilities', () => {
  describe('getCardColor', () => {
    it('returns red color for card with value 0', () => {
      const color = cardExercise.getCardColor(0);
      expect(color).toBe('red');
    });

    it('returns blue color for card with value 1', () => {
      const color = cardExercise.getCardColor(1);
      expect(color).toBe('blue');
    });

    it('returns green color for card with value 2', () => {
      const color = cardExercise.getCardColor(2);
      expect(color).toBe('green');
    });

    it('returns orange color for card with value 3', () => {
      const color = cardExercise.getCardColor(3);
      expect(color).toBe('orange');
    });

    it('returns purple color for card with value 4', () => {
      const color = cardExercise.getCardColor(4);
      expect(color).toBe('purple');
    });

    it('returns teal color for card with value 5', () => {
      const color = cardExercise.getCardColor(5);
      expect(color).toBe('teal');
    });

    it('returns pink color for card with value 6', () => {
      const color = cardExercise.getCardColor(6);
      expect(color).toBe('pink');
    });

    it('returns brown color for card with value 7', () => {
      const color = cardExercise.getCardColor(7);
      expect(color).toBe('brown');
    });

    it('returns gray color for card with value 8', () => {
      const color = cardExercise.getCardColor(8);
      expect(color).toBe('gray');
    });

    it('returns gold color for card with value 9', () => {
      const color = cardExercise.getCardColor(9);
      expect(color).toBe('gold');
    });

    it('returns undefined for invalid value', () => {
      const color = cardExercise.getCardColor(10);
      expect(color).toBeUndefined();
    });

    it('returns undefined for negative value', () => {
      const color = cardExercise.getCardColor(-1);
      expect(color).toBeUndefined();
    });
  });

  describe('getCardValue', () => {
    it('returns 0 for red card', () => {
      const value = cardExercise.getCardValue('red');
      expect(value).toBe(0);
    });

    it('returns 1 for blue card', () => {
      const value = cardExercise.getCardValue('blue');
      expect(value).toBe(1);
    });

    it('returns 2 for green card', () => {
      const value = cardExercise.getCardValue('green');
      expect(value).toBe(2);
    });

    it('returns 3 for orange card', () => {
      const value = cardExercise.getCardValue('orange');
      expect(value).toBe(3);
    });

    it('returns 4 for purple card', () => {
      const value = cardExercise.getCardValue('purple');
      expect(value).toBe(4);
    });

    it('returns 5 for teal card', () => {
      const value = cardExercise.getCardValue('teal');
      expect(value).toBe(5);
    });

    it('returns 6 for pink card', () => {
      const value = cardExercise.getCardValue('pink');
      expect(value).toBe(6);
    });

    it('returns 7 for brown card', () => {
      const value = cardExercise.getCardValue('brown');
      expect(value).toBe(7);
    });

    it('returns 8 for gray card', () => {
      const value = cardExercise.getCardValue('gray');
      expect(value).toBe(8);
    });

    it('returns 9 for gold card', () => {
      const value = cardExercise.getCardValue('gold');
      expect(value).toBe(9);
    });

    it('returns undefined for invalid color', () => {
      const value = cardExercise.getCardValue('invalid');
      expect(value).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValue(10);
      expect(result).toBeUndefined();
    });

    it('returns undefined for negative value', () => {
      const result = cardExercise.getCardColorValue(-1);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValuePair', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValuePair(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValuePair(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValuePair(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValuePair(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColor', () => {
    it('returns red color for card with value 0', () => {
      const color = cardExercise.getCardColor(0);
      expect(color).toBe('red');
    });

    it('returns blue color for card with value 1', () => {
      const color = cardExercise.getCardColor(1);
      expect(color).toBe('blue');
    });

    it('returns gold color for card with value 9', () => {
      const color = cardExercise.getCardColor(9);
      expect(color).toBe('gold');
    });

    it('returns undefined for invalid value', () => {
      const color = cardExercise.getCardColor(10);
      expect(color).toBeUndefined();
    });
  });

  describe('getCardValue', () => {
    it('returns 0 for red card', () => {
      const value = cardExercise.getCardValue('red');
      expect(value).toBe(0);
    });

    it('returns 1 for blue card', () => {
      const value = cardExercise.getCardValue('blue');
      expect(value).toBe(1);
    });

    it('returns 9 for gold card', () => {
      const value = cardExercise.getCardValue('gold');
      expect(value).toBe(9);
    });

    it('returns undefined for invalid color', () => {
      const value = cardExercise.getCardValue('invalid');
      expect(value).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = cardExercise.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = cardExercise.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = cardExercise.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = cardExercise.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });
});
