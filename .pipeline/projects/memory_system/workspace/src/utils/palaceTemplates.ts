/**
 * Palace template definitions and utilities
 * Provides pre-built palace structures for users to start with
 */

import { Room } from '../types/palace';

/**
 * Template definition interface
 */
export interface PalaceTemplate {
  id: string;
  name: string;
  description: string;
  roomCount: number;
  rooms: { name: string; description: string }[];
  category: 'home' | 'office' | 'school' | 'custom';
}

/**
 * Home Palace Template - 5 rooms
 */
export const HOME_PALACE_TEMPLATE: PalaceTemplate = {
  id: 'template-home',
  name: 'Home Palace',
  description: 'A cozy home with familiar rooms for memory training',
  roomCount: 5,
  rooms: [
    { name: 'Living Room', description: 'Main gathering area with comfortable seating' },
    { name: 'Kitchen', description: 'Space for cooking and dining' },
    { name: 'Bedroom', description: 'Private sleeping quarters' },
    { name: 'Bathroom', description: 'Personal hygiene space' },
    { name: 'Garden', description: 'Outdoor green space with plants' },
  ],
  category: 'home',
};

/**
 * Office Palace Template - 6 rooms
 */
export const OFFICE_PALACE_TEMPLATE: PalaceTemplate = {
  id: 'template-office',
  name: 'Office Palace',
  description: 'Professional workspace with distinct areas',
  roomCount: 6,
  rooms: [
    { name: 'Reception', description: 'Front desk and waiting area' },
    { name: 'Workspace', description: 'Individual desk area' },
    { name: 'Conference Room', description: 'Meeting and presentation space' },
    { name: 'Pantry', description: 'Kitchenette and break area' },
    { name: 'Restroom', description: 'Employee facilities' },
    { name: 'Parking', description: 'Vehicle storage area' },
  ],
  category: 'office',
};

/**
 * School Palace Template - 8 rooms
 */
export const SCHOOL_PALACE_TEMPLATE: PalaceTemplate = {
  id: 'template-school',
  name: 'School Palace',
  description: 'Educational environment with learning spaces',
  roomCount: 8,
  rooms: [
    { name: 'Entrance', description: 'Main entry point to the building' },
    { name: 'Hallway', description: 'Corridor connecting all rooms' },
    { name: 'Classroom A', description: 'Primary learning space' },
    { name: 'Classroom B', description: 'Secondary learning space' },
    { name: 'Library', description: 'Reading and research area' },
    { name: 'Cafeteria', description: 'Dining and social area' },
    { name: 'Gym', description: 'Physical education and sports' },
    { name: 'Playground', description: 'Outdoor recreation area' },
  ],
  category: 'school',
};

/**
 * All available templates
 */
export const AVAILABLE_TEMPLATES: PalaceTemplate[] = [
  HOME_PALACE_TEMPLATE,
  OFFICE_PALACE_TEMPLATE,
  SCHOOL_PALACE_TEMPLATE,
];

/**
 * Get a template by ID
 */
export const getTemplateById = (templateId: string): PalaceTemplate | null => {
  return AVAILABLE_TEMPLATES.find((t) => t.id === templateId) || null;
};

/**
 * Get templates by category
 */
export const getTemplatesByCategory = (category: string): PalaceTemplate[] => {
  return AVAILABLE_TEMPLATES.filter((t) => t.category === category);
};

/**
 * Create a palace from a template
 */
export const createPalaceFromTemplate = (
  template: PalaceTemplate,
  palaceName: string
): {
  name: string;
  description: string;
  rooms: { name: string; description: string; items: string[] }[];
} => {
  return {
    name: palaceName,
    description: `Created from ${template.name} template`,
    rooms: template.rooms.map((room, index) => ({
      name: room.name,
      description: room.description,
      items: [],
    })),
  };
};

/**
 * Get all template categories
 */
export const getTemplateCategories = (): string[] => {
  const categories = new Set(AVAILABLE_TEMPLATES.map((t) => t.category));
  return Array.from(categories);
};

/**
 * Get template preview data (for display in selectors)
 */
export const getTemplatePreview = (template: PalaceTemplate): {
  id: string;
  name: string;
  description: string;
  roomCount: number;
  roomNames: string[];
  category: string;
} => {
  return {
    id: template.id,
    name: template.name,
    description: template.description,
    roomCount: template.roomCount,
    roomNames: template.rooms.map((r) => r.name),
    category: template.category,
  };
};
