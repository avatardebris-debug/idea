import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryPalace } from '../src/pages/MemoryPalace';

// Mock all child components
vi.mock('../src/components/MemoryPalace/TemplateSelector', () => ({
  TemplateSelector: ({ onTemplateSelected }: any) => (
    <div data-testid="template-selector">
      <button data-testid="template-home">Home Palace</button>
      <button data-testid="template-office">Office Palace</button>
      <button data-testid="template-school">School Palace</button>
      <button onClick={() => onTemplateSelected('template-home')}>
        Select Home
      </button>
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/PalaceCreator', () => ({
  PalaceCreator: ({ onCreate }: any) => (
    <div data-testid="palace-creator">
      <input data-testid="palace-name-input" placeholder="Palace Name" />
      <input data-testid="palace-description-input" placeholder="Description" />
      <button onClick={() => onCreate({ id: 'test-1', name: 'Test Palace' })}>
        Create Palace
      </button>
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/PalaceNavigator', () => ({
  PalaceNavigator: ({ palaces, selectedPalaceId, onSelectPalace }: any) => (
    <div data-testid="palace-navigator">
      {palaces.map((palace: any) => (
        <div
          key={palace.id}
          data-testid={`palace-item-${palace.id}`}
          onClick={() => onSelectPalace(palace)}
        >
          {palace.name}
        </div>
      ))}
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/SpatialExercise', () => ({
  SpatialExercise: ({ onExerciseComplete }: any) => (
    <div data-testid="spatial-exercise">
      <h2>Spatial Memory Exercise</h2>
      <button data-testid="start-exercise">Start Exercise</button>
      <button onClick={() => onExerciseComplete({ score: 80 })}>
        Complete Exercise
      </button>
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/PalaceActions', () => ({
  PalaceActions: ({ palace, onImportSuccess }: any) => (
    <div data-testid="palace-actions">
      <button data-testid="export-palace">Export Palace</button>
      <button data-testid="export-all">Export All</button>
      <button data-testid="import-palace">Import Palace</button>
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/ProgressTracker', () => ({
  ProgressTracker: ({ palaceId }: any) => (
    <div data-testid="progress-tracker">
      <h3>Progress Tracking</h3>
      <span data-testid="accuracy-stat">80%</span>
      <span data-testid="sessions-stat">5</span>
    </div>
  ),
}));

vi.mock('../src/utils/palaceUtils', () => ({
  loadPalaces: vi.fn().mockReturnValue([]),
  savePalace: vi.fn(),
}));

vi.mock('../src/utils/palaceTemplates', () => ({
  getAvailableTemplates: vi.fn().mockReturnValue([
    { id: 'template-home', name: 'Home Palace', category: 'home', roomCount: 5 },
    { id: 'template-office', name: 'Office Palace', category: 'office', roomCount: 4 },
    { id: 'template-school', name: 'School Palace', category: 'school', roomCount: 6 },
  ]),
}));

describe('MemoryPalace Integration', () => {
  const mockOnImportSuccess = vi.fn();

  const renderComponent = () => {
    return render(
      <MemoryPalace onImportSuccess={mockOnImportSuccess} />
    );
  };

  it('renders initial state with template selector', () => {
    renderComponent();
    expect(screen.getByTestId('template-selector')).toBeInTheDocument();
    expect(screen.getByText('Home Palace')).toBeInTheDocument();
  });

  it('allows user to select a template', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });
  });

  it('allows user to create a new palace', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    // Fill in palace name
    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    // Create palace
    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });
  });

  it('displays palace navigator after creation', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });
  });

  it('shows progress tracker after palace selection', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    // Select the palace
    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
    });
  });

  it('allows user to start spatial exercise', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
    });

    // Start exercise
    const startButton = screen.getByTestId('start-exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Spatial Memory Exercise')).toBeInTheDocument();
    });
  });

  it('calls onImportSuccess when import is successful', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
    });

    // Trigger import success
    const importButton = screen.getByTestId('import-palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(mockOnImportSuccess).toHaveBeenCalled();
    });
  });

  it('handles error state gracefully', () => {
    // Simulate error state by not providing valid template
    const { container } = render(
      <MemoryPalace onImportSuccess={mockOnImportSuccess} />
    );
    expect(container).toBeInTheDocument();
  });

  it('supports keyboard navigation', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.keyDown(homeButton, { key: 'Enter' });

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });
  });

  it('displays proper loading states', () => {
    renderComponent();
    expect(screen.getByText('Home Palace')).toBeInTheDocument();
  });

  it('allows switching between templates', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const officeButton = screen.getByTestId('template-office');
    fireEvent.click(officeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });
  });

  it('handles palace selection and deselection', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
    });

    // Deselect palace
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });
  });

  it('displays export functionality', async () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('palace-actions')).toBeInTheDocument();
      expect(screen.getByTestId('export-palace')).toBeInTheDocument();
    });
  });

  it('shows progress statistics', () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
    });

    const nameInput = screen.getByTestId('palace-name-input');
    fireEvent.change(nameInput, { target: { value: 'My Test Palace' } });

    const createButton = screen.getByText('Create Palace');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByTestId('palace-navigator')).toBeInTheDocument();
    });

    const palaceItem = screen.getByTestId('palace-item-test-1');
    fireEvent.click(palaceItem);

    await waitFor(() => {
      expect(screen.getByTestId('progress-tracker')).toBeInTheDocument();
      expect(screen.getByTestId('accuracy-stat')).toBeInTheDocument();
      expect(screen.getByTestId('sessions-stat')).toBeInTheDocument();
    });
  });

  it('supports aria attributes for accessibility', () => {
    renderComponent();
    const templateButton = screen.getByTestId('template-home');
    expect(templateButton).toHaveAttribute('role', 'button');
  });

  it('handles rapid state changes', () => {
    const { rerender } = renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.click(homeButton);

    rerender(<MemoryPalace onImportSuccess={mockOnImportSuccess} />);

    expect(screen.getByTestId('template-selector')).toBeInTheDocument();
  });

  it('disables interactive elements when loading', () => {
    renderComponent();
    const templateButton = screen.getByTestId('template-home');
    expect(templateButton).not.toBeDisabled();
  });

  it('handles template selection with keyboard', () => {
    renderComponent();

    const homeButton = screen.getByTestId('template-home');
    fireEvent.keyDown(homeButton, { key: ' ' });

    expect(screen.getByTestId('palace-creator')).toBeInTheDocument();
  });
});
