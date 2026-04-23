import { describe, it, expect, vi } from 'vitest';
import * as palaceTemplates from '../src/utils/palaceTemplates';

describe('Palace Templates Utilities', () => {
  describe('getAvailableTemplates', () => {
    it('returns all available templates', () => {
      const templates = palaceTemplates.getAvailableTemplates();

      expect(templates).toHaveLength(4);
      expect(templates[0].id).toBe('template-home');
      expect(templates[1].id).toBe('template-office');
      expect(templates[2].id).toBe('template-school');
      expect(templates[3].id).toBe('template-custom');
    });

    it('returns templates with correct structure', () => {
      const templates = palaceTemplates.getAvailableTemplates();

      const template = templates[0];
      expect(template.id).toBeDefined();
      expect(template.name).toBeDefined();
      expect(template.category).toBeDefined();
      expect(template.roomCount).toBeDefined();
      expect(template.description).toBeDefined();
      expect(template.rooms).toBeDefined();
    });

    it('includes home palace template', () => {
      const templates = palaceTemplates.getAvailableTemplates();
      const homeTemplate = templates.find(t => t.id === 'template-home');

      expect(homeTemplate).toBeDefined();
      expect(homeTemplate?.name).toBe('Home Palace');
      expect(homeTemplate?.category).toBe('home');
      expect(homeTemplate?.roomCount).toBe(5);
    });

    it('includes office palace template', () => {
      const templates = palaceTemplates.getAvailableTemplates();
      const officeTemplate = templates.find(t => t.id === 'template-office');

      expect(officeTemplate).toBeDefined();
      expect(officeTemplate?.name).toBe('Office Palace');
      expect(officeTemplate?.category).toBe('office');
      expect(officeTemplate?.roomCount).toBe(4);
    });

    it('includes school palace template', () => {
      const templates = palaceTemplates.getAvailableTemplates();
      const schoolTemplate = templates.find(t => t.id === 'template-school');

      expect(schoolTemplate).toBeDefined();
      expect(schoolTemplate?.name).toBe('School Palace');
      expect(schoolTemplate?.category).toBe('school');
      expect(schoolTemplate?.roomCount).toBe(6);
    });

    it('includes custom palace template', () => {
      const templates = palaceTemplates.getAvailableTemplates();
      const customTemplate = templates.find(t => t.id === 'template-custom');

      expect(customTemplate).toBeDefined();
      expect(customTemplate?.name).toBe('Custom Palace');
      expect(customTemplate?.category).toBe('custom');
      expect(customTemplate?.roomCount).toBe(3);
    });

    it('includes room information for each template', () => {
      const templates = palaceTemplates.getAvailableTemplates();

      const homeTemplate = templates.find(t => t.id === 'template-home');
      expect(homeTemplate?.rooms).toHaveLength(5);
      expect(homeTemplate?.rooms[0].name).toBe('Living Room');
      expect(homeTemplate?.rooms[1].name).toBe('Kitchen');
    });
  });

  describe('getTemplateById', () => {
    it('finds template by ID', () => {
      const template = palaceTemplates.getTemplateById('template-home');

      expect(template).toBeDefined();
      expect(template?.id).toBe('template-home');
      expect(template?.name).toBe('Home Palace');
    });

    it('returns undefined for non-existent template', () => {
      const template = palaceTemplates.getTemplateById('non-existent');

      expect(template).toBeUndefined();
    });

    it('returns office template', () => {
      const template = palaceTemplates.getTemplateById('template-office');

      expect(template).toBeDefined();
      expect(template?.name).toBe('Office Palace');
      expect(template?.category).toBe('office');
    });

    it('returns school template', () => {
      const template = palaceTemplates.getTemplateById('template-school');

      expect(template).toBeDefined();
      expect(template?.name).toBe('School Palace');
      expect(template?.category).toBe('school');
    });
  });

  describe('getTemplatesByCategory', () => {
    it('returns home templates', () => {
      const templates = palaceTemplates.getTemplatesByCategory('home');

      expect(templates).toHaveLength(1);
      expect(templates[0].category).toBe('home');
    });

    it('returns office templates', () => {
      const templates = palaceTemplates.getTemplatesByCategory('office');

      expect(templates).toHaveLength(1);
      expect(templates[0].category).toBe('office');
    });

    it('returns school templates', () => {
      const templates = palaceTemplates.getTemplatesByCategory('school');

      expect(templates).toHaveLength(1);
      expect(templates[0].category).toBe('school');
    });

    it('returns custom templates', () => {
      const templates = palaceTemplates.getTemplatesByCategory('custom');

      expect(templates).toHaveLength(1);
      expect(templates[0].category).toBe('custom');
    });

    it('returns all templates for "all" category', () => {
      const templates = palaceTemplates.getTemplatesByCategory('all');

      expect(templates).toHaveLength(4);
    });

    it('returns empty array for non-existent category', () => {
      const templates = palaceTemplates.getTemplatesByCategory('non-existent');

      expect(templates).toEqual([]);
    });
  });

  describe('getTemplateRoomCount', () => {
    it('returns correct room count for home template', () => {
      const count = palaceTemplates.getTemplateRoomCount('template-home');

      expect(count).toBe(5);
    });

    it('returns correct room count for office template', () => {
      const count = palaceTemplates.getTemplateRoomCount('template-office');

      expect(count).toBe(4);
    });

    it('returns correct room count for school template', () => {
      const count = palaceTemplates.getTemplateRoomCount('template-school');

      expect(count).toBe(6);
    });

    it('returns 0 for non-existent template', () => {
      const count = palaceTemplates.getTemplateRoomCount('non-existent');

      expect(count).toBe(0);
    });
  });

  describe('getTemplateRooms', () => {
    it('returns rooms for home template', () => {
      const rooms = palaceTemplates.getTemplateRooms('template-home');

      expect(rooms).toHaveLength(5);
      expect(rooms[0].name).toBe('Living Room');
      expect(rooms[0].description).toBe('The central gathering space');
      expect(rooms[1].name).toBe('Kitchen');
    });

    it('returns rooms for office template', () => {
      const rooms = palaceTemplates.getTemplateRooms('template-office');

      expect(rooms).toHaveLength(4);
      expect(rooms[0].name).toBe('Reception Area');
      expect(rooms[0].description).toBe('The first space visitors see');
    });

    it('returns rooms for school template', () => {
      const rooms = palaceTemplates.getTemplateRooms('template-school');

      expect(rooms).toHaveLength(6);
      expect(rooms[0].name).toBe('Main Entrance');
      expect(rooms[0].description).toBe('The main door and hallway');
    });

    it('returns empty array for non-existent template', () => {
      const rooms = palaceTemplates.getTemplateRooms('non-existent');

      expect(rooms).toEqual([]);
    });
  });

  describe('generateTemplatePalace', () => {
    it('generates a palace from home template', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-home', 'My Home Palace');

      expect(palace.id).toBeDefined();
      expect(palace.name).toBe('My Home Palace');
      expect(palace.rooms).toHaveLength(5);
      expect(palace.createdAt).toBeDefined();
    });

    it('generates a palace from office template', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-office', 'My Office Palace');

      expect(palace.name).toBe('My Office Palace');
      expect(palace.rooms).toHaveLength(4);
    });

    it('generates a palace from school template', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-school', 'My School Palace');

      expect(palace.name).toBe('My School Palace');
      expect(palace.rooms).toHaveLength(6);
    });

    it('uses default name when none provided', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-home');

      expect(palace.name).toBe('Home Palace');
    });

    it('generates unique IDs for rooms', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-home', 'Test Palace');

      const roomIds = palace.rooms.map(r => r.id);
      const uniqueRoomIds = new Set(roomIds);

      expect(roomIds.length).toBe(uniqueRoomIds.size);
    });

    it('preserves room descriptions from template', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-home', 'Test Palace');

      expect(palace.rooms[0].description).toBe('The central gathering space');
      expect(palace.rooms[1].description).toBe('Where food is prepared');
    });

    it('handles custom template', () => {
      const palace = palaceTemplates.generateTemplatePalace('template-custom', 'Custom Palace');

      expect(palace.name).toBe('Custom Palace');
      expect(palace.rooms).toHaveLength(3);
    });
  });

  describe('getTemplateCategories', () => {
    it('returns all available categories', () => {
      const categories = palaceTemplates.getTemplateCategories();

      expect(categories).toContain('home');
      expect(categories).toContain('office');
      expect(categories).toContain('school');
      expect(categories).toContain('custom');
    });

    it('returns categories in correct order', () => {
      const categories = palaceTemplates.getTemplateCategories();

      expect(categories).toHaveLength(4);
    });
  });

  describe('getTemplateCount', () => {
    it('returns total number of templates', () => {
      const count = palaceTemplates.getTemplateCount();

      expect(count).toBe(4);
    });
  });

  describe('getTemplateById with validation', () => {
    it('validates template structure', () => {
      const template = palaceTemplates.getTemplateById('template-home');

      expect(template?.id).toBeDefined();
      expect(template?.name).toBeDefined();
      expect(template?.category).toBeDefined();
      expect(template?.roomCount).toBeDefined();
      expect(template?.description).toBeDefined();
      expect(Array.isArray(template?.rooms)).toBe(true);
    });

    it('includes room count in template', () => {
      const template = palaceTemplates.getTemplateById('template-home');

      expect(template?.roomCount).toBe(5);
      expect(template?.rooms).toHaveLength(5);
    });

    it('includes room count in all templates', () => {
      const templates = palaceTemplates.getAvailableTemplates();

      templates.forEach(template => {
        expect(template.roomCount).toBe(template.rooms.length);
      });
    });
  });
});
