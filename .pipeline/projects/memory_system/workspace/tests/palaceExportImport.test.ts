import { describe, it, expect, vi } from 'vitest';
import * as exportUtils from '../src/utils/palaceExportImport';

// Mock the palace utils
vi.mock('../src/utils/palaceUtils', () => ({
  loadPalaces: vi.fn(),
  savePalace: vi.fn(),
}));

describe('Palace Export/Import Utilities', () => {
  const mockPalace = {
    id: 'palace-1',
    name: 'Test Palace',
    description: 'A test palace',
    rooms: [
      { id: 'room-1', name: 'Room 1', description: 'Room 1 desc', items: ['item1', 'item2'] },
      { id: 'room-2', name: 'Room 2', description: 'Room 2 desc', items: ['item3'] },
    ],
    createdAt: '2024-01-01T00:00:00.000Z',
  };

  describe('exportPalace', () => {
    it('exports a single palace with correct format', () => {
      const result = exportUtils.exportPalace(mockPalace);

      expect(result.version).toBe('1.0');
      expect(result.exportDate).toBeDefined();
      expect(result.palace.id).toBe('palace-1');
      expect(result.palace.name).toBe('Test Palace');
      expect(result.palace.description).toBe('A test palace');
      expect(result.palace.rooms).toHaveLength(2);
      expect(result.palace.createdAt).toBe('2024-01-01T00:00:00.000Z');
      expect(result.metadata.exportVersion).toBe('1.0');
    });

    it('preserves all room information', () => {
      const result = exportUtils.exportPalace(mockPalace);

      expect(result.palace.rooms[0].id).toBe('room-1');
      expect(result.palace.rooms[0].name).toBe('Room 1');
      expect(result.palace.rooms[0].description).toBe('Room 1 desc');
      expect(result.palace.rooms[0].items).toEqual(['item1', 'item2']);
    });

    it('includes metadata with exporter info', () => {
      const result = exportUtils.exportPalace(mockPalace);

      expect(result.metadata.exportedBy).toBe('Memory System');
    });
  });

  describe('exportAllPalaces', () => {
    it('exports all palaces as a single export', () => {
      const palaces = [mockPalace, { ...mockPalace, id: 'palace-2', name: 'Palace 2' }];
      const result = exportUtils.exportAllPalaces(palaces);

      expect(result.version).toBe('1.0');
      expect(result.palace.id).toBe('all-palaces');
      expect(result.palace.name).toBe('All Palaces');
      expect(result.palace.rooms).toHaveLength(4); // 2 rooms per palace
    });

    it('combines rooms from all palaces', () => {
      const palaces = [mockPalace, { ...mockPalace, id: 'palace-2', name: 'Palace 2' }];
      const result = exportUtils.exportAllPalaces(palaces);

      expect(result.metadata.exportedPalaces).toHaveLength(2);
      expect(result.metadata.exportedPalaces[0]).toBe('Test Palace');
      expect(result.metadata.exportedPalaces[1]).toBe('Palace 2');
    });

    it('includes metadata about all palaces', () => {
      const palaces = [mockPalace, { ...mockPalace, id: 'palace-2', name: 'Palace 2' }];
      const result = exportUtils.exportAllPalaces(palaces);

      expect(result.metadata.exportedPalaces).toHaveLength(2);
      expect(result.metadata.exportDate).toBeDefined();
    });
  });

  describe('downloadExport', () => {
    it('creates a Blob and triggers download', () => {
      const mockData = { version: '1.0', palace: mockPalace };
      const mockUrl = 'mock-url';
      const mockDownloadLink = {
        href: '',
        download: '',
        click: vi.fn(),
        parentNode: { removeChild: vi.fn() },
      };

      const createObjectURL = vi.fn(() => mockUrl);
      const createElement = vi.fn(() => mockDownloadLink as any);
      vi.spyOn(window, 'createObjectURL').mockImplementation(createObjectURL);
      vi.spyOn(document, 'createElement').mockImplementation(createElement);

      exportUtils.downloadExport(mockData, 'test.json');

      expect(createObjectURL).toHaveBeenCalledWith(JSON.stringify(mockData));
      expect(mockDownloadLink.href).toBe(mockUrl);
      expect(mockDownloadLink.download).toBe('test.json');
      expect(mockDownloadLink.click).toHaveBeenCalled();
    });

    it('handles download errors gracefully', () => {
      const mockData = { version: '1.0', palace: mockPalace };
      const consoleError = vi.spyOn(console, 'error').mockImplementation();

      vi.spyOn(document, 'createElement').mockReturnValue({
        href: '',
        download: '',
        click: vi.fn(),
        parentNode: null,
      } as any);

      exportUtils.downloadExport(mockData, 'test.json');

      expect(consoleError).toHaveBeenCalled();
      consoleError.mockRestore();
    });

    it('uses default filename when none provided', () => {
      const mockData = { version: '1.0', palace: mockPalace };
      const createElement = vi.fn(() => ({
        href: '',
        download: '',
        click: vi.fn(),
        parentNode: { removeChild: vi.fn() },
      }));

      vi.spyOn(document, 'createElement').mockImplementation(createElement);

      exportUtils.downloadExport(mockData);

      expect(createElement).toHaveBeenCalledWith('a');
    });
  });

  describe('generateExportFilename', () => {
    it('generates filename with palace name and timestamp', () => {
      const result = exportUtils.generateExportFilename(mockPalace);

      expect(result).toContain('test-palace');
      expect(result).toContain('.json');
      expect(result).toMatch(/\d{8}/);
    });

    it('handles spaces in palace name', () => {
      const palaceWithSpaces = { ...mockPalace, name: 'My Test Palace' };
      const result = exportUtils.generateExportFilename(palaceWithSpaces);

      expect(result).toContain('my-test-palace');
    });

    it('handles special characters in palace name', () => {
      const palaceWithSpecial = { ...mockPalace, name: 'Test Palace @ 2024' };
      const result = exportUtils.generateExportFilename(palaceWithSpecial);

      expect(result).toContain('test-palace-2024');
    });
  });

  describe('generateAllPalacesFilename', () => {
    it('generates all palaces filename', () => {
      const result = exportUtils.generateAllPalacesFilename();

      expect(result).toBe('all-palaces.json');
    });
  });

  describe('importPalace', () => {
    it('imports valid palace JSON', async () => {
      const importData = JSON.stringify({
        version: '1.0',
        palace: mockPalace,
        metadata: { exportVersion: '1.0' },
      });

      const result = await exportUtils.importPalace(importData);

      expect(result.success).toBe(true);
      expect(result.palace.id).toBe('palace-1');
      expect(result.palace.name).toBe('Test Palace');
    });

    it('handles invalid JSON format', async () => {
      const invalidData = 'not valid json';

      const result = await exportUtils.importPalace(invalidData);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid');
    });

    it('handles missing required fields', async () => {
      const invalidData = JSON.stringify({ version: '1.0' });

      const result = await exportUtils.importPalace(invalidData);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Invalid');
    });

    it('handles unsupported export versions', async () => {
      const invalidData = JSON.stringify({
        version: '99.0',
        palace: mockPalace,
      });

      const result = await exportUtils.importPalace(invalidData);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Unsupported');
    });

    it('validates palace structure', async () => {
      const invalidData = JSON.stringify({
        version: '1.0',
        palace: {
          id: 'palace-1',
          name: 'Test Palace',
          rooms: [],
          createdAt: '2024-01-01T00:00:00.000Z',
        },
      });

      const result = await exportUtils.importPalace(invalidData);

      expect(result.success).toBe(true);
    });
  });

  describe('importAllPalaces', () => {
    it('imports all palaces from combined export', async () => {
      const importData = JSON.stringify({
        version: '1.0',
        palace: {
          id: 'all-palaces',
          name: 'All Palaces',
          rooms: [
            { id: 'room-1', name: 'Room 1', description: 'Desc', items: [] },
          ],
          createdAt: '2024-01-01T00:00:00.000Z',
        },
        metadata: {
          exportedPalaces: ['Palace 1', 'Palace 2'],
          exportVersion: '1.0',
          exportDate: '2024-01-01T00:00:00.000Z',
        },
      });

      const result = await exportUtils.importAllPalaces(importData);

      expect(result.success).toBe(true);
      expect(result.palaces).toHaveLength(2);
    });

    it('handles invalid all-palaces format', async () => {
      const invalidData = JSON.stringify({ version: '1.0', palace: mockPalace });

      const result = await exportUtils.importAllPalaces(invalidData);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Expected');
    });

    it('handles missing metadata', async () => {
      const invalidData = JSON.stringify({
        version: '1.0',
        palace: {
          id: 'all-palaces',
          name: 'All Palaces',
          rooms: [],
          createdAt: '2024-01-01T00:00:00.000Z',
        },
      });

      const result = await exportUtils.importAllPalaces(invalidData);

      expect(result.success).toBe(false);
      expect(result.error).toContain('Expected');
    });
  });
});
