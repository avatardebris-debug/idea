import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import RecallExercise from '../src/components/MemoryPalace/RecallExercise';
import { Palace } from '../src/types/palace';

// Mock the progress tracking functions
vi.mock('../src/utils/progressTracking', () => ({
  saveExerciseSession: vi.fn(),
}));

describe('RecallExercise', () => {
  const mockPalace: Palace = {
    id: 'palace-1',
    name: 'Test Palace',
    description: 'A test palace for recall exercises',
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
      <RecallExercise palace={palace} {...props} />
    );
  };

  it('renders the recall exercise header', () => {
    renderComponent();
    expect(screen.getByText('Test Palace')).toBeInTheDocument();
  });

  it('displays difficulty selector', () => {
    renderComponent();
    expect(screen.getByText('Difficulty:')).toBeInTheDocument();
    expect(screen.getByText('Easy')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
    expect(screen.getByText('Hard')).toBeInTheDocument();
  });

  it('displays Start Exercise button', () => {
    renderComponent();
    expect(screen.getByText('Start Exercise')).toBeInTheDocument();
  });

  it('shows rooms before exercise starts', () => {
    renderComponent();
    expect(screen.getByText('Living Room')).toBeInTheDocument();
    expect(screen.getByText('Kitchen')).toBeInTheDocument();
  });

  it('starts exercise when button is clicked', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText('Time Left:')).toBeInTheDocument();
    });
  });

  it('displays timer during exercise', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Time Left: \d+s/)).toBeInTheDocument();
    });
  });

  it('displays score during exercise', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(screen.getByText(/Score: \d+/)).toBeInTheDocument();
    });
  });

  it('allows user to select a room', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const livingRoomCard = screen.getByText('Living Room').closest('div');
      if (livingRoomCard) {
        fireEvent.click(livingRoomCard);
      }
    });

    await waitFor(() => {
      expect(screen.getByPlaceholderText('Type each item on a new line...')).toBeInTheDocument();
    });
  });

  it('allows user to reveal items', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const livingRoomCard = screen.getByText('Living Room').closest('div');
      if (livingRoomCard) {
        fireEvent.click(livingRoomCard);
      }
    });

    await waitFor(() => {
      const revealButton = screen.getByText('Reveal Items');
      fireEvent.click(revealButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Red apple')).toBeInTheDocument();
    });
  });

  it('allows user to submit recall', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const livingRoomCard = screen.getByText('Living Room').closest('div');
      if (livingRoomCard) {
        fireEvent.click(livingRoomCard);
      }
    });

    await waitFor(() => {
      const revealButton = screen.getByText('Reveal Items');
      fireEvent.click(revealButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type each item on a new line...');
      fireEvent.change(input, { target: { value: 'Red apple\nBlue book\nGreen plant' } });
    });

    await waitFor(() => {
      const submitButton = screen.getByText('Submit Recall');
      fireEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Correct!')).toBeInTheDocument();
    });
  });

  it('shows correct/incorrect feedback for items', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const livingRoomCard = screen.getByText('Living Room').closest('div');
      if (livingRoomCard) {
        fireEvent.click(livingRoomCard);
      }
    });

    await waitFor(() => {
      const revealButton = screen.getByText('Reveal Items');
      fireEvent.click(revealButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type each item on a new line...');
      fireEvent.change(input, { target: { value: 'Wrong item' } });
    });

    await waitFor(() => {
      const submitButton = screen.getByText('Submit Recall');
      fireEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Incorrect')).toBeInTheDocument();
    });
  });

  it('pauses and resumes exercise', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const pauseButton = screen.getByText('Pause');
      fireEvent.click(pauseButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Resume')).toBeInTheDocument();
    });

    await waitFor(() => {
      const resumeButton = screen.getByText('Resume');
      fireEvent.click(resumeButton);
    });

    await waitFor(() => {
      expect(screen.getByText('Pause')).toBeInTheDocument();
    });
  });

  it('shows completion screen when timer expires', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

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

  it('shows completion stats', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    vi.useFakeTimers();
    vi.advanceTimersByTime(90000);

    await waitFor(() => {
      expect(screen.getByText('Score')).toBeInTheDocument();
      expect(screen.getByText('Correct Recalls')).toBeInTheDocument();
      expect(screen.getByText('Incorrect Recalls')).toBeInTheDocument();
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

  it('allows user to change difficulty during review', () => {
    renderComponent();
    const mediumSelect = screen.getByRole('combobox');
    fireEvent.change(mediumSelect, { target: { value: 'hard' } });
    expect(mediumSelect).toHaveValue('hard');
  });

  it('handles empty palace gracefully', () => {
    const emptyPalace: Palace = {
      ...mockPalace,
      rooms: [],
    };
    const { container } = renderComponent(emptyPalace);
    expect(container).toBeInTheDocument();
  });

  it('displays feedback message on correct recall', async () => {
    renderComponent();
    const startButton = screen.getByText('Start Exercise');
    fireEvent.click(startButton);

    await waitFor(() => {
      const livingRoomCard = screen.getByText('Living Room').closest('div');
      if (livingRoomCard) {
        fireEvent.click(livingRoomCard);
      }
    });

    await waitFor(() => {
      const revealButton = screen.getByText('Reveal Items');
      fireEvent.click(revealButton);
    });

    await waitFor(() => {
      const input = screen.getByPlaceholderText('Type each item on a new line...');
      fireEvent.change(input, { target: { value: 'Red apple' } });
    });

    await waitFor(() => {
      const submitButton = screen.getByText('Submit Recall');
      fireEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/Correct!/)).toBeInTheDocument();
    });
  });
});
