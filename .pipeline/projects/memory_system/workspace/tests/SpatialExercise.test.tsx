import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SpatialExercise, { SpatialExerciseProps } from '../src/components/MemoryPalace/SpatialExercise';
import { Palace } from '../src/types/palace';

// Mock the progress tracking functions
vi.mock('../src/utils/progressTracking', () => ({
  saveExerciseSession: vi.fn(),
  getPalaceExerciseStats: vi.fn().mockReturnValue({
    totalSessions: 0,
    totalItems: 0,
    totalCorrect: 0,
    averageAccuracy: 0,
    lastSession: null,
    bestAccuracy: 0,
  }),
}));

describe('SpatialExercise', () => {
  const mockPalace: Palace = {
    id: 'palace-1',
    name: 'Test Palace',
    description: 'A test palace for exercises',
    rooms: [
      {
        id: 'room-1',
        name: 'Living Room',
        description: 'The main living area',
        items: ['Red apple', 'Blue book', 'Green plant'],
      },
      {
        id: 'room-2',
        name: 'Kitchen',
        description: 'The kitchen area',
        items: ['Yellow banana', 'Orange juice', 'Purple grapes'],
      },
    ],
    createdAt: '2024-01-01T00:00:00.000Z',
  };

  const renderComponent = (palace: Palace = mockPalace, props = {}) => {
    return render(
      <SpatialExercise palace={palace} {...props} />
    );
  };

  it('renders the exercise header', () => {
    renderComponent();
    expect(screen.getByText('Test Palace - Spatial Memory Exercise')).toBeInTheDocument();
  });

  it('displays difficulty options', () => {
    renderComponent();
    expect(screen.getByText('Easy (120s)')).toBeInTheDocument();
    expect(screen.getByText('Medium (90s)')).toBeInTheDocument();
    expect(screen.getByText('Hard (60s)')).toBeInTheDocument();
  });

  it('displays Start Exercise button initially', () => {
    renderComponent();
    expect(screen.getByText('Start Exercise')).toBeInTheDocument();
  });

  it('shows timer when exercise starts', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Time Left:/)).toBeInTheDocument();
    });
  });

  it('displays rooms grid when exercise starts', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Living Room')).toBeInTheDocument();
      expect(screen.getByText('Kitchen')).toBeInTheDocument();
    });
  });

  it('allows user to add items to rooms', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Enter item to add');
      fireEvent.change(input, { target: { value: 'Test item' } });
      fireEvent.keyDown(input, { key: 'Enter' });
    });

    await waitFor(() => {
      expect(screen.getByText('Test item')).toBeInTheDocument();
    });
  });

  it('allows user to switch to recall mode', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const recallButton = screen.getByText('Switch to Recall');
      fireEvent.click(recallButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Recall mode active')).toBeInTheDocument();
    });
  });

  it('shows rooms in recall mode', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const recallButton = screen.getByText('Switch to Recall');
      fireEvent.click(recallButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Click to reveal items')).toBeInTheDocument();
    });
  });

  it('shows completion screen when timer expires', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    // Fast forward time using fake timers
    vi.useFakeTimers();
    vi.advanceTimersByTime(90000); // 90 seconds

    await waitFor(() => {
      expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('calls onExerciseComplete when exercise finishes', async () => {
    const onComplete = vi.fn();
    renderComponent(mockPalace, { onExerciseComplete: onComplete });

    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    vi.useFakeTimers();
    vi.advanceTimersByTime(90000);

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled();
    });

    vi.useRealTimers();
  });

  it('displays score during exercise', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Score:/)).toBeInTheDocument();
    });
  });

  it('allows user to end exercise manually', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const recallButton = screen.getByText('Switch to Recall');
      fireEvent.click(recallButton);
    });

    await waitFor(() => {
      const endButton = screen.getByText('Complete');
      fireEvent.click(endButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
    });
  });

  it('displays results summary after completion', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    vi.useFakeTimers();
    vi.advanceTimersByTime(90000);

    await waitFor(() => {
      expect(screen.getByText('Score')).toBeInTheDocument();
      expect(screen.getByText('Correct Recalls')).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('allows user to try again after completion', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    vi.useFakeTimers();
    vi.advanceTimersByTime(90000);

    await waitFor(() => {
      const tryAgainButton = screen.getByText('Try Again');
      fireEvent.click(tryAgainButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Start Exercise')).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('handles empty palace gracefully', () => {
    const emptyPalace: Palace = {
      ...mockPalace,
      rooms: [],
    };
    const { container } = renderComponent(emptyPalace);
    expect(container).toBeInTheDocument();
  });

  it('displays room item count when items are revealed', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Living Room')).toBeInTheDocument();
    });

    // Click to select room and reveal items
    const livingRoomCard = screen.getByText('Living Room').closest('div');
    if (livingRoomCard) {
      fireEvent.click(livingRoomCard);
    }

    await waitFor(() => {
      const revealButton = screen.getByText('Reveal Items');
      fireEvent.click(revealButton);
    });

    await waitFor(() => {
      expect(screen.getByText('3 items')).toBeInTheDocument();
    });
  });
});
