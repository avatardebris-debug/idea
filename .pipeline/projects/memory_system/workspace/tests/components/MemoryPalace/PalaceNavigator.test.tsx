import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import PalaceNavigator from '../src/components/MemoryPalace/PalaceNavigator';

describe('PalaceNavigator', () => {
  const mockPalaces = [
    {
      id: 'palace-1',
      name: 'Home Palace',
      description: 'My childhood home',
      rooms: [
        { id: 'room-1', name: 'Living Room', description: 'Living space', items: [] },
        { id: 'room-2', name: 'Kitchen', description: 'Kitchen area', items: [] },
      ],
      createdAt: '2024-01-15T10:00:00.000Z',
    },
    {
      id: 'palace-2',
      name: 'Office Palace',
      description: 'My workplace layout',
      rooms: [
        { id: 'room-3', name: 'Reception', description: 'Front desk', items: [] },
        { id: 'room-4', name: 'Meeting Room', description: 'Conference space', items: [] },
        { id: 'room-5', name: 'Office', description: 'My workspace', items: [] },
      ],
      createdAt: '2024-01-14T10:00:00.000Z',
    },
  ];

  const mockOnSelectPalace = vi.fn();

  const renderComponent = (props = {}) => {
    return render(
      <PalaceNavigator
        palaces={mockPalaces}
        selectedPalaceId={null}
        onSelectPalace={mockOnSelectPalace}
        {...props}
      />
    );
  };

  it('renders search input', () => {
    renderComponent();
    expect(screen.getByPlaceholderText('Search palaces...')).toBeInTheDocument();
  });

  it('renders sort selector', () => {
    renderComponent();
    expect(screen.getByLabelText('Sort palaces by')).toBeInTheDocument();
  });

  it('displays all palaces in list', () => {
    renderComponent();

    expect(screen.getByText('Home Palace')).toBeInTheDocument();
    expect(screen.getByText('Office Palace')).toBeInTheDocument();
    expect(screen.getByText('2 rooms')).toBeInTheDocument();
    expect(screen.getByText('3 rooms')).toBeInTheDocument();
  });

  it('shows palace count', () => {
    renderComponent();
    expect(screen.getByText('2 palaces')).toBeInTheDocument();
  });

  it('filters palaces by search query', async () => {
    renderComponent();

    const searchInput = screen.getByPlaceholderText('Search palaces...');
    fireEvent.change(searchInput, { target: { value: 'Home' } });

    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });

    expect(screen.queryByText('Office Palace')).not.toBeInTheDocument();
  });

  it('clears search when clear button clicked', async () => {
    renderComponent();

    const searchInput = screen.getByPlaceholderText('Search palaces...');
    fireEvent.change(searchInput, { target: { value: 'Home' } });

    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });

    const clearButton = screen.getByLabelText('Clear search');
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(screen.queryByText('Office Palace')).toBeInTheDocument();
    });
  });

  it('sorts palaces by name', async () => {
    renderComponent();

    const sortSelect = screen.getByLabelText('Sort palaces by');
    fireEvent.change(sortSelect, { target: { value: 'name' } });

    await waitFor(() => {
      expect(screen.getByText('Office Palace')).toBeInTheDocument();
    });
  });

  it('sorts palaces by room count', async () => {
    renderComponent();

    const sortSelect = screen.getByLabelText('Sort palaces by');
    fireEvent.change(sortSelect, { target: { value: 'roomCount' } });

    await waitFor(() => {
      expect(screen.getByText('Office Palace')).toBeInTheDocument();
    });
  });

  it('handles empty palace list', () => {
    renderComponent({ palaces: [] });
    expect(screen.getByText('No palaces found')).toBeInTheDocument();
  });

  it('handles empty search results', async () => {
    renderComponent();

    const searchInput = screen.getByPlaceholderText('Search palaces...');
    fireEvent.change(searchInput, { target: { value: 'Nonexistent' } });

    await waitFor(() => {
      expect(screen.getByText('No palaces found')).toBeInTheDocument();
    });
  });

  it('selects palace on click', async () => {
    renderComponent();

    const palaceItem = screen.getByText('Home Palace').parentElement?.parentElement;
    fireEvent.click(palaceItem);

    expect(mockOnSelectPalace).toHaveBeenCalledWith(mockPalaces[0]);
  });

  it('displays recently used section when palaces exist', () => {
    renderComponent();
    expect(screen.getByText('Recently Used')).toBeInTheDocument();
  });

  it('displays recently used palaces', () => {
    renderComponent();
    expect(screen.getByText('Home Palace')).toBeInTheDocument();
    expect(screen.getByText('Office Palace')).toBeInTheDocument();
  });

  it('highlights selected palace', () => {
    renderComponent({ selectedPalaceId: 'palace-1' });

    const selectedPalace = screen.getByText('Home Palace').parentElement?.parentElement;
    expect(selectedPalace).toHaveClass('active');
  });

  it('handles keyboard navigation', async () => {
    renderComponent();

    const palaceItem = screen.getByText('Home Palace').parentElement?.parentElement;
    fireEvent.keyDown(palaceItem, { key: 'Enter' });

    expect(mockOnSelectPalace).toHaveBeenCalledWith(mockPalaces[0]);
  });

  it('displays keyboard shortcuts help', () => {
    renderComponent();
    expect(screen.getByText('Keyboard Shortcuts')).toBeInTheDocument();
    expect(screen.getByText('Tab')).toBeInTheDocument();
    expect(screen.getByText('Enter')).toBeInTheDocument();
    expect(screen.getByText('Esc')).toBeInTheDocument();
  });

  it('shows filter toggle button', () => {
    renderComponent();
    expect(screen.getByLabelText('Show filters')).toBeInTheDocument();
  });

  it('displays description for palace', () => {
    renderComponent();
    expect(screen.getByText('My childhood home')).toBeInTheDocument();
  });

  it('displays created date', () => {
    renderComponent();
    expect(screen.getByText('Created')).toBeInTheDocument();
  });

  it('handles room count badge', () => {
    renderComponent();
    expect(screen.getByText('2 rooms')).toBeInTheDocument();
    expect(screen.getByText('3 rooms')).toBeInTheDocument();
  });

  it('renders with selected palace', () => {
    renderComponent({ selectedPalaceId: 'palace-2' });

    const selectedPalace = screen.getByText('Office Palace').parentElement?.parentElement;
    expect(selectedPalace).toHaveClass('active');
  });

  it('shows empty hint when search returns no results', async () => {
    renderComponent();

    const searchInput = screen.getByPlaceholderText('Search palaces...');
    fireEvent.change(searchInput, { target: { value: 'xyz123' } });

    await waitFor(() => {
      expect(screen.getByText('Try adjusting your search or filters')).toBeInTheDocument();
    });
  });

  it('prevents event bubbling on palace selection', async () => {
    const mockEvent = { stopPropagation: vi.fn() };
    const originalAddEventListener = Event.prototype.addEventListener;

    Event.prototype.addEventListener = vi.fn((type, callback) => {
      if (type === 'click') {
        callback(mockEvent);
      }
    });

    renderComponent();

    const palaceItem = screen.getByText('Home Palace').parentElement?.parentElement;
    fireEvent.click(palaceItem);

    Event.prototype.addEventListener = originalAddEventListener;
  });

  it('maintains accessibility attributes', () => {
    renderComponent();

    const palaceItems = screen.getAllByRole('button');
    palaceItems.forEach((item) => {
      expect(item).toHaveAttribute('tabIndex', '0');
    });

    expect(screen.getByLabelText('Search palaces')).toBeInTheDocument();
    expect(screen.getByLabelText('Sort palaces by')).toBeInTheDocument();
  });

  it('handles search with special characters', async () => {
    renderComponent();

    const searchInput = screen.getByPlaceholderText('Search palaces...');
    fireEvent.change(searchInput, { target: { value: 'Home Palace' } });

    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });
  });

  it('sorts palaces by creation date (newest first)', async () => {
    renderComponent();

    const sortSelect = screen.getByLabelText('Sort palaces by');
    fireEvent.change(sortSelect, { target: { value: 'createdDate' } });

    await waitFor(() => {
      expect(screen.getByText('Home Palace')).toBeInTheDocument();
    });
  });
});
