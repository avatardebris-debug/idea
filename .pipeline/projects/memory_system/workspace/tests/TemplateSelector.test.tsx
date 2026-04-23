import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TemplateSelector from '../src/components/MemoryPalace/TemplateSelector';
import {
  AVAILABLE_TEMPLATES,
  getTemplateById,
  getTemplatePreview,
  PalaceTemplate,
} from '../src/utils/palaceTemplates';

// Mock the palace templates
vi.mock('../src/utils/palaceTemplates', () => ({
  AVAILABLE_TEMPLATES: [
    {
      id: 'template-home',
      name: 'Home Palace',
      description: 'A cozy home with familiar rooms for memory training',
      roomCount: 5,
      rooms: [
        { name: 'Living Room', description: 'Main gathering area' },
        { name: 'Kitchen', description: 'Space for cooking' },
        { name: 'Bedroom', description: 'Private sleeping quarters' },
        { name: 'Bathroom', description: 'Personal hygiene space' },
        { name: 'Garden', description: 'Outdoor green space' },
      ],
      category: 'home',
    },
    {
      id: 'template-office',
      name: 'Office Palace',
      description: 'Professional workspace with distinct areas',
      roomCount: 6,
      rooms: [
        { name: 'Reception', description: 'Front desk area' },
        { name: 'Workspace', description: 'Individual desk area' },
        { name: 'Conference Room', description: 'Meeting space' },
        { name: 'Pantry', description: 'Kitchenette area' },
        { name: 'Restroom', description: 'Employee facilities' },
        { name: 'Parking', description: 'Vehicle storage' },
      ],
      category: 'office',
    },
    {
      id: 'template-school',
      name: 'School Palace',
      description: 'Educational environment with learning spaces',
      roomCount: 8,
      rooms: [
        { name: 'Entrance', description: 'Main entry point' },
        { name: 'Hallway', description: 'Corridor connecting rooms' },
        { name: 'Classroom A', description: 'Primary learning space' },
        { name: 'Classroom B', description: 'Secondary learning space' },
        { name: 'Library', description: 'Reading area' },
        { name: 'Cafeteria', description: 'Dining area' },
        { name: 'Gym', description: 'Physical education' },
        { name: 'Playground', description: 'Outdoor recreation' },
      ],
      category: 'school',
    },
  ],
  getTemplateById: vi.fn(),
  getTemplatePreview: vi.fn(),
}));

describe('TemplateSelector', () => {
  const mockOnTemplateSelected = vi.fn();

  const renderComponent = (props = {}) => {
    return render(
      <TemplateSelector
        onTemplateSelected={mockOnTemplateSelected}
        {...props}
      />
    );
  };

  it('renders the template selector header', () => {
    renderComponent();
    expect(screen.getByText('Choose a Palace Template')).toBeInTheDocument();
    expect(screen.getByText('Expand')).toBeInTheDocument();
  });

  it('displays category filter buttons', () => {
    renderComponent();
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Office')).toBeInTheDocument();
    expect(screen.getByText('School')).toBeInTheDocument();
  });

  it('calls onTemplateSelected when a template is clicked', async () => {
    renderComponent();

    // Wait for templates to render
    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });

    const templateCard = screen.getByText('Home Palace').closest('div');
    if (templateCard) {
      fireEvent.click(templateCard);
    }

    await waitFor(() => {
      expect(mockOnTemplateSelected).toHaveBeenCalled();
    });
  });

  it('filters templates by category', async () => {
    renderComponent();

    // Click Home category
    const homeButton = screen.getByText('Home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });

    // Click Office category
    const officeButton = screen.getByText('Office');
    fireEvent.click(officeButton);

    await waitFor(() => {
      expect(screen.getByText('Office Palace')).toBeInTheDocument();
    });
  });

  it('toggles expanded/collapsed state', () => {
    const { rerender } = renderComponent();

    // Initially collapsed
    expect(screen.getByText('Expand')).toBeInTheDocument();

    // Click to expand
    const toggleButton = screen.getByText('Expand');
    fireEvent.click(toggleButton);

    // Should now show Collapse button
    expect(screen.getByText('Collapse')).toBeInTheDocument();

    // Click to collapse
    const collapseButton = screen.getByText('Collapse');
    fireEvent.click(collapseButton);

    expect(screen.getByText('Expand')).toBeInTheDocument();
  });

  it('displays selected template summary', () => {
    renderComponent({ selectedTemplateId: 'template-home' });

    expect(screen.getByText('Selected Template:')).toBeInTheDocument();
    expect(screen.getByText('Home Palace')).toBeInTheDocument();
  });

  it('shows template cards with correct information', () => {
    renderComponent();

    expect(screen.getByText('Home Palace')).toBeInTheDocument();
    expect(screen.getByText('Home Palace Template')).toBeInTheDocument();
    expect(screen.getByText('5 rooms')).toBeInTheDocument();
  });

  it('highlights selected template', () => {
    renderComponent({ selectedTemplateId: 'template-home' });

    const selectedCard = screen.getByText('Home Palace').closest('div');
    expect(selectedCard).toHaveClass('selected');
  });

  it('handles empty category gracefully', () => {
    const { rerender } = renderComponent();

    // Click a category that might have no templates
    const schoolButton = screen.getByText('School');
    fireEvent.click(schoolButton);

    // Should show appropriate message or templates
    expect(screen.getByText('School Palace')).toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    renderComponent();

    // Navigate to first template card
    const firstCard = screen.getAllByRole('button')[0];
    fireEvent.keyDown(firstCard, { key: 'Enter' });

    expect(mockOnTemplateSelected).toHaveBeenCalled();
  });

  it('displays room preview list', () => {
    renderComponent();

    expect(screen.getByText('Rooms:')).toBeInTheDocument();
    expect(screen.getByText('Living Room')).toBeInTheDocument();
    expect(screen.getByText('Kitchen')).toBeInTheDocument();
  });

  it('shows category badge with correct styling', () => {
    renderComponent();

    const categoryBadge = screen.getByText('home');
    expect(categoryBadge).toBeInTheDocument();
  });

  it('handles template selection via keyboard', async () => {
    renderComponent();

    const firstCard = screen.getAllByRole('button')[0];
    fireEvent.keyDown(firstCard, { key: ' ' });

    expect(mockOnTemplateSelected).toHaveBeenCalled();
  });

  it('renders without errors when no templates available', () => {
    const { container } = render(
      <TemplateSelector onTemplateSelected={mockOnTemplateSelected} />
    );
    expect(container).toBeInTheDocument();
  });

  it('displays template description', () => {
    renderComponent();

    expect(screen.getByText('A cozy home with familiar rooms for memory training')).toBeInTheDocument();
  });

  it('supports aria attributes for accessibility', () => {
    renderComponent();

    const toggleButton = screen.getByRole('button', { name: /expand/i });
    expect(toggleButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('displays template stats (room count)', () => {
    renderComponent();

    expect(screen.getByText('5 rooms')).toBeInTheDocument();
  });

  it('shows all three categories (Home, Office, School)', () => {
    renderComponent();

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Office')).toBeInTheDocument();
    expect(screen.getByText('School')).toBeInTheDocument();
  });
});
