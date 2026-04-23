import { describe, it, expect, vi } from 'vitest';
import * as palaceUtils from '../src/utils/palaceUtils';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('Palace Utils', () => {
  const mockPalace = {
    id: 'palace-1',
    name: 'Test Palace',
    description: 'A test palace',
    rooms: [
      { id: 'room-1', name: 'Room 1', description: 'Room 1 desc', items: ['item1', 'item2'] },
    ],
    createdAt: '2024-01-01T00:00:00.000Z',
  };

  describe('generateId', () => {
    it('generates unique IDs', () => {
      const id1 = palaceUtils.generateId();
      const id2 = palaceUtils.generateId();

      expect(id1).not.toBe(id2);
      expect(id1).toMatch(/^palace-\d+$/);
      expect(id2).toMatch(/^palace-\d+$/);
    });

    it('generates IDs with different timestamps', () => {
      const id1 = palaceUtils.generateId();
      const id2 = palaceUtils.generateId();

      const timestamp1 = parseInt(id1.split('-')[1]);
      const timestamp2 = parseInt(id2.split('-')[1]);

      expect(timestamp1).toBeLessThanOrEqual(timestamp2);
    });
  });

  describe('savePalace', () => {
    it('saves a palace to localStorage', () => {
      const result = palaceUtils.savePalace(mockPalace);

      expect(localStorage.setItem).toHaveBeenCalledWith('memoryPalaces', expect.any(String));
      expect(result).toBe(true);
    });

    it('handles save errors gracefully', () => {
      localStorageMock.setItem = vi.fn(() => {
        throw new Error('Storage error');
      });

      const result = palaceUtils.savePalace(mockPalace);

      expect(result).toBe(false);
    });

    it('overwrites existing palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const updatedPalace = { ...mockPalace, name: 'Updated Palace' };
      palaceUtils.savePalace(updatedPalace);

      expect(localStorage.setItem).toHaveBeenCalled();
    });
  });

  describe('loadPalaces', () => {
    it('loads palaces from localStorage', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.loadPalaces();

      expect(result).toHaveLength(1);
      expect(result[0].id).toBe('palace-1');
    });

    it('returns empty array when no palaces stored', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(null);

      const result = palaceUtils.loadPalaces();

      expect(result).toEqual([]);
    });

    it('handles invalid JSON gracefully', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue('invalid json');

      const result = palaceUtils.loadPalaces();

      expect(result).toEqual([]);
    });

    it('handles null storage gracefully', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(undefined);

      const result = palaceUtils.loadPalaces();

      expect(result).toEqual([]);
    });
  });

  describe('getPalaceById', () => {
    it('finds palace by ID', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.getPalaceById('palace-1');

      expect(result).toEqual(mockPalace);
    });

    it('returns undefined for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.getPalaceById('non-existent');

      expect(result).toBeUndefined();
    });

    it('handles empty storage', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = palaceUtils.getPalaceById('palace-1');

      expect(result).toBeUndefined();
    });
  });

  describe('deletePalace', () => {
    it('deletes a palace by ID', () => {
      const palaces = [mockPalace, { ...mockPalace, id: 'palace-2', name: 'Palace 2' }];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(palaces));

      const result = palaceUtils.deletePalace('palace-1');

      expect(result).toBe(true);
      expect(localStorage.removeItem).toHaveBeenCalledWith('memoryPalaces');
      expect(localStorage.setItem).toHaveBeenCalledWith('memoryPalaces', expect.any(String));
    });

    it('returns false for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.deletePalace('non-existent');

      expect(result).toBe(false);
    });

    it('handles deletion errors gracefully', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));
      localStorageMock.setItem = vi.fn(() => {
        throw new Error('Storage error');
      });

      const result = palaceUtils.deletePalace('palace-1');

      expect(result).toBe(false);
    });
  });

  describe('getPalaceStats', () => {
    it('returns stats for a palace', () => {
      const palaces = [mockPalace];
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify(palaces));

      const result = palaceUtils.getPalaceStats('palace-1');

      expect(result.palaceId).toBe('palace-1');
      expect(result.palaceName).toBe('Test Palace');
      expect(result.totalRooms).toBe(1);
    });

    it('returns default stats for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = palaceUtils.getPalaceStats('non-existent');

      expect(result.palaceId).toBe('non-existent');
      expect(result.palaceName).toBe('Unknown Palace');
      expect(result.totalSessions).toBe(0);
      expect(result.totalRooms).toBe(0);
    });
  });

  describe('getRoomById', () => {
    it('finds room by ID', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.getRoomById('palace-1', 'room-1');

      expect(result).toEqual(mockPalace.rooms[0]);
    });

    it('returns undefined for non-existent room', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.getRoomById('palace-1', 'non-existent');

      expect(result).toBeUndefined();
    });

    it('returns undefined for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = palaceUtils.getRoomById('non-existent', 'room-1');

      expect(result).toBeUndefined();
    });
  });

  describe('getRoomsForPalace', () => {
    it('returns all rooms for a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.getRoomsForPalace('palace-1');

      expect(result).toEqual(mockPalace.rooms);
    });

    it('returns empty array for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = palaceUtils.getRoomsForPalace('non-existent');

      expect(result).toEqual([]);
    });
  });

  describe('addRoomToPalace', () => {
    it('adds a room to a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const newRoom = { id: 'room-2', name: 'Room 2', description: 'Room 2 desc', items: [] };
      const result = palaceUtils.addRoomToPalace('palace-1', newRoom);

      expect(result).toBe(true);
      expect(localStorage.setItem).toHaveBeenCalled();
    });

    it('returns false for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const newRoom = { id: 'room-2', name: 'Room 2', description: 'Room 2 desc', items: [] };
      const result = palaceUtils.addRoomToPalace('non-existent', newRoom);

      expect(result).toBe(false);
    });
  });

  describe('updateRoom', () => {
    it('updates a room in a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const updatedRoom = { ...mockPalace.rooms[0], name: 'Updated Room 1' };
      const result = palaceUtils.updateRoom('palace-1', updatedRoom);

      expect(result).toBe(true);
      expect(localStorage.setItem).toHaveBeenCalled();
    });

    it('returns false for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const updatedRoom = { id: 'room-1', name: 'Updated Room 1', description: 'Desc', items: [] };
      const result = palaceUtils.updateRoom('non-existent', updatedRoom);

      expect(result).toBe(false);
    });

    it('returns false for non-existent room', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const updatedRoom = { id: 'non-existent', name: 'Updated Room 1', description: 'Desc', items: [] };
      const result = palaceUtils.updateRoom('palace-1', updatedRoom);

      expect(result).toBe(false);
    });
  });

  describe('removeRoomFromPalace', () => {
    it('removes a room from a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.removeRoomFromPalace('palace-1', 'room-1');

      expect(result).toBe(true);
      expect(localStorage.setItem).toHaveBeenCalled();
    });

    it('returns false for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const result = palaceUtils.removeRoomFromPalace('non-existent', 'room-1');

      expect(result).toBe(false);
    });

    it('returns false for non-existent room', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const result = palaceUtils.removeRoomFromPalace('palace-1', 'non-existent');

      expect(result).toBe(false);
    });
  });

  describe('updatePalace', () => {
    it('updates a palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([mockPalace]));

      const updatedPalace = { ...mockPalace, name: 'Updated Palace' };
      const result = palaceUtils.updatePalace(updatedPalace);

      expect(result).toBe(true);
      expect(localStorage.setItem).toHaveBeenCalled();
    });

    it('returns false for non-existent palace', () => {
      localStorageMock.getItem = vi.fn().mockReturnValue(JSON.stringify([]));

      const updatedPalace = { ...mockPalace, id: 'non-existent', name: 'Updated Palace' };
      const result = palaceUtils.updatePalace(updatedPalace);

      expect(result).toBe(false);
    });
  });
});
