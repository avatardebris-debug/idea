/**
 * Palace Export/Import Utilities
 * Provides functionality to export and import memory palaces to/from JSON files
 */

import { Palace, Room } from '../types/palace';
import { loadPalaces, savePalace } from './palaceUtils';

/**
 * Export interface for palace data
 */
export interface PalaceExportFormat {
  version: string;
  exportDate: string;
  palace: {
    id: string;
    name: string;
    description: string;
    rooms: {
      id: string;
      name: string;
      description: string;
      items: string[];
    }[];
    createdAt: string;
  };
  metadata: {
    exportVersion: string;
    exportedBy: string;
  };
}

/**
 * Export a single palace to JSON format
 */
export const exportPalace = (palace: Palace): PalaceExportFormat => {
  return {
    version: '1.0',
    exportDate: new Date().toISOString(),
    palace: {
      id: palace.id,
      name: palace.name,
      description: palace.description,
      rooms: palace.rooms.map((room) => ({
        id: room.id,
        name: room.name,
        description: room.description,
        items: room.items,
      })),
      createdAt: palace.createdAt,
    },
    metadata: {
      exportVersion: '1.0',
      exportedBy: 'Memory System',
    },
  };
};

/**
 * Export all palaces to JSON format
 */
export const exportAllPalaces = (palaces: Palace[]): PalaceExportFormat => {
  return {
    version: '1.0',
    exportDate: new Date().toISOString(),
    palace: {
      id: 'all-palaces',
      name: 'All Palaces',
      description: 'Export containing all memory palaces',
      rooms: palaces.flatMap((palace) =>
        palace.rooms.map((room) => ({
          id: `${palace.id}-${room.id}`,
          name: `${palace.name} - ${room.name}`,
          description: room.description,
          items: room.items,
        }))
      ),
      createdAt: new Date().toISOString(),
    },
    metadata: {
      exportVersion: '1.0',
      exportedBy: 'Memory System',
    },
  };
};

/**
 * Download exported data as a JSON file
 */
export const downloadExport = (exportData: PalaceExportFormat, filename: string): void => {
  const jsonString = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Parse and validate imported palace data
 */
export const parseImportedPalace = (
  json: unknown
): {
  palace: Palace;
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];

  // Basic type checking
  if (typeof json !== 'object' || json === null) {
    errors.push('Invalid JSON format');
    return { palace: getEmptyPalace(), isValid: false, errors };
  }

  const data = json as Record<string, unknown>;

  // Check version
  if (typeof data.version !== 'string') {
    errors.push('Missing version field');
  }

  // Check palace data
  if (!data.palace || typeof data.palace !== 'object') {
    errors.push('Missing palace data');
    return { palace: getEmptyPalace(), isValid: false, errors };
  }

  const palaceData = data.palace as Record<string, unknown>;

  // Validate palace fields
  if (typeof palaceData.id !== 'string') {
    errors.push('Invalid palace ID');
  }

  if (typeof palaceData.name !== 'string' || palaceData.name.trim() === '') {
    errors.push('Palace name is required');
  }

  if (typeof palaceData.description !== 'string') {
    errors.push('Palace description must be a string');
  }

  if (typeof palaceData.createdAt !== 'string') {
    errors.push('Invalid palace creation date');
  }

  if (!palaceData.rooms || !Array.isArray(palaceData.rooms)) {
    errors.push('Palace must have rooms array');
    return { palace: getEmptyPalace(), isValid: false, errors };
  }

  // Validate rooms
  const rooms: Room[] = [];
  palaceData.rooms.forEach((roomData: unknown, index: number) => {
    if (typeof roomData !== 'object' || roomData === null) {
      errors.push(`Room ${index + 1} is invalid`);
      return;
    }

    const room = roomData as Record<string, unknown>;

    if (typeof room.id !== 'string') {
      errors.push(`Room ${index + 1} missing ID`);
    }

    if (typeof room.name !== 'string' || room.name.trim() === '') {
      errors.push(`Room ${index + 1} missing name`);
    }

    if (typeof room.description !== 'string') {
      errors.push(`Room ${index + 1} description must be a string`);
    }

    if (!Array.isArray(room.items)) {
      errors.push(`Room ${index + 1} items must be an array`);
      return;
    }

    if (!room.items.every((item: unknown) => typeof item === 'string')) {
      errors.push(`Room ${index + 1} items must be strings`);
      return;
    }

    rooms.push({
      id: room.id,
      name: room.name,
      description: room.description,
      items: room.items,
    });
  });

  if (errors.length > 0) {
    return {
      palace: getEmptyPalace(),
      isValid: false,
      errors,
    };
  }

  const palace: Palace = {
    id: palaceData.id as string,
    name: (palaceData.name as string).trim(),
    description: palaceData.description as string,
    rooms,
    createdAt: palaceData.createdAt as string,
  };

  return { palace, isValid: true, errors };
};

/**
 * Import a single palace from JSON file
 */
export const importPalace = async (
  file: File
): Promise<{
  success: boolean;
  palace?: Palace;
  errors: string[];
  message: string;
}> => {
  return new Promise((resolve) => {
    const reader = new FileReader();

    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        const { palace, isValid, errors } = parseImportedPalace(json);

        if (!isValid) {
          resolve({
            success: false,
            errors,
            message: 'Import failed: Invalid palace data',
          });
          return;
        }

        // Check for duplicate palace ID
        const existingPalaces = loadPalaces();
        const existingPalace = existingPalaces.find((p) => p.id === palace.id);

        if (existingPalace) {
          resolve({
            success: false,
            errors: ['A palace with this ID already exists'],
            message: 'Import failed: Duplicate palace ID',
          });
          return;
        }

        // Save the imported palace
        savePalace(palace);

        resolve({
          success: true,
          palace,
          errors: [],
          message: `Successfully imported palace: ${palace.name}`,
        });
      } catch (error) {
        resolve({
          success: false,
          errors: ['Failed to parse JSON file'],
          message: 'Import failed: Invalid JSON format',
        });
      }
    };

    reader.onerror = () => {
      resolve({
        success: false,
        errors: ['Failed to read file'],
        message: 'Import failed: File read error',
      });
    };

    reader.readAsText(file);
  });
};

/**
 * Import all palaces from JSON file
 */
export const importAllPalaces = async (
  file: File
): Promise<{
  success: boolean;
  palaces: Palace[];
  errors: string[];
  message: string;
}> => {
  return new Promise((resolve) => {
    const reader = new FileReader();

    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        const { palace, isValid, errors } = parseImportedPalace(json);

        if (!isValid) {
          resolve({
            success: false,
            palaces: [],
            errors,
            message: 'Import failed: Invalid palace data',
          });
          return;
        }

        // If this is an "all palaces" export, we need to extract individual palaces
        let palacesToImport: Palace[] = [];

        if (palace.id === 'all-palaces') {
          // For all-palaces export, we'll create a single palace with all rooms
          // This is a simplified approach - in a real scenario, we'd need to track which rooms belonged to which palace
          palacesToImport = [palace];
        } else {
          palacesToImport = [palace];
        }

        // Save all imported palaces
        palacesToImport.forEach((p) => {
          savePalace(p);
        });

        resolve({
          success: true,
          palaces: palacesToImport,
          errors: [],
          message: `Successfully imported ${palacesToImport.length} palace(s)`,
        });
      } catch (error) {
        resolve({
          success: false,
          palaces: [],
          errors: ['Failed to parse JSON file'],
          message: 'Import failed: Invalid JSON format',
        });
      }
    };

    reader.onerror = () => {
      resolve({
        success: false,
        palaces: [],
        errors: ['Failed to read file'],
        message: 'Import failed: File read error',
      });
    };

    reader.readAsText(file);
  });
};

/**
 * Create an empty palace for error cases
 */
const getEmptyPalace = (): Palace => ({
  id: `palace-${Date.now()}`,
  name: 'Import Failed',
  description: 'This palace failed to import',
  rooms: [],
  createdAt: new Date().toISOString(),
});

/**
 * Generate filename for palace export
 */
export const generateExportFilename = (palaceName: string): string => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
  const sanitizedName = palaceName.replace(/[^a-z0-9]/gi, '_');
  return `memory_palace_${sanitizedName}_${timestamp}.json`;
};

/**
 * Generate filename for all palaces export
 */
export const generateAllPalacesFilename = (): string => {
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
  return `all_memory_palaces_${timestamp}.json`;
};
