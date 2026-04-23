import { Palace, Room } from '../types/palace';
import { MAX_PALACE_ROOMS, MIN_PALACE_ROOMS } from '../config/constants';

const STORAGE_KEY = 'memory_palaces';

export const loadPalaces = (): Palace[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading palaces from localStorage:', error);
  }
  return [];
};

export const savePalace = (palace: Palace | Palace[]): void => {
  try {
    const palaces = Array.isArray(palace) ? palace : [palace];
    
    // Validate palaces
    const validPalaces = palaces.filter(p => {
      if (!p.name || p.name.trim().length === 0) {
        console.warn('Invalid palace name:', p.name);
        return false;
      }
      if (p.rooms.length < MIN_PALACE_ROOMS || p.rooms.length > MAX_PALACE_ROOMS) {
        console.warn('Invalid room count:', p.rooms.length);
        return false;
      }
      return true;
    });

    localStorage.setItem(STORAGE_KEY, JSON.stringify(validPalaces));
  } catch (error) {
    console.error('Error saving palace to localStorage:', error);
  }
};

export const deletePalace = (palaceId: string): void => {
  try {
    const palaces = loadPalaces();
    const filtered = palaces.filter(p => p.id !== palaceId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Error deleting palace:', error);
  }
};

export const getPalaceById = (palaceId: string): Palace | null => {
  const palaces = loadPalaces();
  return palaces.find(p => p.id === palaceId) || null;
};

export const updatePalace = (palaceId: string, updates: Partial<Palace>): Palace | null => {
  try {
    const palaces = loadPalaces();
    const index = palaces.findIndex(p => p.id === palaceId);
    
    if (index === -1) {
      return null;
    }

    const updatedPalace = { ...palaces[index], ...updates };
    
    // Validate
    if (!updatedPalace.name || updatedPalace.name.trim().length === 0) {
      console.warn('Invalid palace name');
      return null;
    }
    if (updatedPalace.rooms.length < MIN_PALACE_ROOMS || updatedPalace.rooms.length > MAX_PALACE_ROOMS) {
      console.warn('Invalid room count');
      return null;
    }

    palaces[index] = updatedPalace;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(palaces));
    return updatedPalace;
  } catch (error) {
    console.error('Error updating palace:', error);
    return null;
  }
};

export const getPalaceStats = (): PalaceStats => {
  const palaces = loadPalaces();
  const totalRooms = palaces.reduce((sum, p) => sum + p.rooms.length, 0);
  
  return {
    totalPalaces: palaces.length,
    totalRooms,
    lastUsed: palaces.length > 0 ? palaces[0].createdAt : null,
  };
};

export const validatePalace = (palace: Palace): { valid: boolean; errors: string[] } => {
  const errors: string[] = [];

  if (!palace.name || palace.name.trim().length === 0) {
    errors.push('Palace name is required');
  }

  if (!palace.rooms || palace.rooms.length === 0) {
    errors.push('Palace must have at least one room');
  }

  if (palace.rooms.length < MIN_PALACE_ROOMS) {
    errors.push(`Palace must have at least ${MIN_PALACE_ROOMS} rooms`);
  }

  if (palace.rooms.length > MAX_PALACE_ROOMS) {
    errors.push(`Palace cannot have more than ${MAX_PALACE_ROOMS} rooms`);
  }

  palace.rooms.forEach((room, index) => {
    if (!room.name || room.name.trim().length === 0) {
      errors.push(`Room ${index + 1} name is required`);
    }
  });

  return {
    valid: errors.length === 0,
    errors,
  };
};
