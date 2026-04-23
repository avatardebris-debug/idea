import { describe, it, expect, vi } from 'vitest';
import * as musicalWheel from '../src/utils/musicalWheel';

describe('Musical Wheel Utilities', () => {
  describe('getWheelColors', () => {
    it('returns all wheel colors', () => {
      const colors = musicalWheel.getWheelColors();

      expect(colors).toContain('red');
      expect(colors).toContain('blue');
      expect(colors).toContain('green');
      expect(colors).toContain('orange');
      expect(colors).toContain('purple');
      expect(colors).toContain('teal');
      expect(colors).toContain('pink');
      expect(colors).toContain('brown');
      expect(colors).toContain('gray');
      expect(colors).toContain('gold');
    });

    it('returns 10 colors', () => {
      const colors = musicalWheel.getWheelColors();

      expect(colors).toHaveLength(10);
    });

    it('returns colors in correct order', () => {
      const colors = musicalWheel.getWheelColors();

      expect(colors[0]).toBe('red');
      expect(colors[1]).toBe('blue');
      expect(colors[2]).toBe('green');
      expect(colors[3]).toBe('orange');
      expect(colors[4]).toBe('purple');
      expect(colors[5]).toBe('teal');
      expect(colors[6]).toBe('pink');
      expect(colors[7]).toBe('brown');
      expect(colors[8]).toBe('gray');
      expect(colors[9]).toBe('gold');
    });
  });

  describe('getWheelColorsWithValues', () => {
    it('returns colors with their values', () => {
      const colorValues = musicalWheel.getWheelColorsWithValues();

      expect(colorValues[0].color).toBe('red');
      expect(colorValues[0].value).toBe(0);
      expect(colorValues[1].color).toBe('blue');
      expect(colorValues[1].value).toBe(1);
    });

    it('returns 10 color values', () => {
      const colorValues = musicalWheel.getWheelColorsWithValues();

      expect(colorValues).toHaveLength(10);
    });

    it('includes all colors', () => {
      const colorValues = musicalWheel.getWheelColorsWithValues();
      const colors = colorValues.map(cv => cv.color);

      expect(colors).toContain('red');
      expect(colors).toContain('gold');
    });

    it('values are in correct order', () => {
      const colorValues = musicalWheel.getWheelColorsWithValues();

      const redValue = colorValues.find(cv => cv.color === 'red');
      expect(redValue?.value).toBe(0);

      const goldValue = colorValues.find(cv => cv.color === 'gold');
      expect(goldValue?.value).toBe(9);
    });
  });

  describe('getColorValue', () => {
    it('returns value for red', () => {
      const value = musicalWheel.getColorValue('red');
      expect(value).toBe(0);
    });

    it('returns value for blue', () => {
      const value = musicalWheel.getColorValue('blue');
      expect(value).toBe(1);
    });

    it('returns value for green', () => {
      const value = musicalWheel.getColorValue('green');
      expect(value).toBe(2);
    });

    it('returns value for gold', () => {
      const value = musicalWheel.getColorValue('gold');
      expect(value).toBe(9);
    });

    it('returns undefined for invalid color', () => {
      const value = musicalWheel.getColorValue('invalid');
      expect(value).toBeUndefined();
    });
  });

  describe('getCardColor', () => {
    it('returns red color for card with value 0', () => {
      const color = musicalWheel.getCardColor(0);
      expect(color).toBe('red');
    });

    it('returns blue color for card with value 1', () => {
      const color = musicalWheel.getCardColor(1);
      expect(color).toBe('blue');
    });

    it('returns gold color for card with value 9', () => {
      const color = musicalWheel.getCardColor(9);
      expect(color).toBe('gold');
    });

    it('returns undefined for invalid value', () => {
      const color = musicalWheel.getCardColor(10);
      expect(color).toBeUndefined();
    });

    it('returns undefined for negative value', () => {
      const color = musicalWheel.getCardColor(-1);
      expect(color).toBeUndefined();
    });
  });

  describe('getCardValue', () => {
    it('returns 0 for red card', () => {
      const value = musicalWheel.getCardValue('red');
      expect(value).toBe(0);
    });

    it('returns 1 for blue card', () => {
      const value = musicalWheel.getCardValue('blue');
      expect(value).toBe(1);
    });

    it('returns 9 for gold card', () => {
      const value = musicalWheel.getCardValue('gold');
      expect(value).toBe(9);
    });

    it('returns undefined for invalid color', () => {
      const value = musicalWheel.getCardValue('invalid');
      expect(value).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValuePair', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValuePair(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValuePair(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValuePair(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValuePair(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });

  describe('getCardColorValue', () => {
    it('returns color and value for card with value 0', () => {
      const result = musicalWheel.getCardColorValue(0);
      expect(result.color).toBe('red');
      expect(result.value).toBe(0);
    });

    it('returns color and value for card with value 5', () => {
      const result = musicalWheel.getCardColorValue(5);
      expect(result.color).toBe('teal');
      expect(result.value).toBe(5);
    });

    it('returns color and value for card with value 9', () => {
      const result = musicalWheel.getCardColorValue(9);
      expect(result.color).toBe('gold');
      expect(result.value).toBe(9);
    });

    it('returns undefined for invalid value', () => {
      const result = musicalWheel.getCardColorValue(10);
      expect(result).toBeUndefined();
    });
  });
});
