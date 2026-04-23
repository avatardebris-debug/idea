import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ExerciseRunner } from '../src/components/MemoryPalace/ExerciseRunner';

// Mock the child components
vi.mock('../src/components/MemoryPalace/SpatialExercise', () => ({
  default: ({ onExerciseComplete }: { onExerciseComplete: any }) => (
    <div data-testid="spatial-exercise">
      <button onClick={() => onExerciseComplete(true)}>Complete</button>
    </div>
  ),
}));

vi.mock('../src/components/MemoryPalace/RecallExercise', () => ({
  default: ({ onExerciseComplete }: { onExerciseComplete: any }) => (
    <div data-testid="recall-exercise">
      <button onClick={() => onExerciseComplete(true)}>Complete</button>
    </div>
  ),
}));

const mockPalace = {
  id: 'palace-1',
  name: 'Test Palace',
  description: 'A test palace',
  createdAt: '2024-01-01T00:00:00.000Z',
  rooms: [
    {
      id: 'room-1',
      name: 'Room 1',
      items: ['Item 1', 'Item 2', 'Item 3'],
    },
  ],
};

describe('ExerciseRunner', () => {
  const mockOnExerciseComplete = vi.fn();

  beforeEach(() => {
    mockOnExerciseComplete.mockClear();
  });

  describe('initial state', () => {
    it('renders start screen when exercise has not started', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('Start Spatial Exercise')).toBeInTheDocument();
      expect(screen.getByText('Test Palace')).toBeInTheDocument();
      expect(screen.getByText('Start Exercise')).toBeInTheDocument();
      expect(screen.getByText('Back to Practice')).toBeInTheDocument();
    });

    it('displays palace information correctly', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="recall"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('Test Palace')).toBeInTheDocument();
      expect(screen.getByText('A test palace')).toBeInTheDocument();
      expect(screen.getByText('Total Rooms: 1')).toBeInTheDocument();
      expect(screen.getByText('Exercise Type: Recall')).toBeInTheDocument();
    });

    it('shows error when no palace is selected', () => {
      render(
        <ExerciseRunner
          palace={null}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('No palace selected')).toBeInTheDocument();
    });
  });

  describe('exercise flow', () => {
    it('starts exercise when user clicks Start Exercise', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));

      expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
    });

    it('completes exercise when child component signals completion', async () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));
      await waitFor(() => {
        expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Complete'));

      await waitFor(() => {
        expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
      });

      expect(mockOnExerciseComplete).toHaveBeenCalledWith(true);
    });

    it('handles recall exercise type', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="recall"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));

      expect(screen.getByTestId('recall-exercise')).toBeInTheDocument();
    });

    it('handles unknown exercise type gracefully', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="unknown" as any
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));

      expect(screen.getByText('Unknown exercise type')).toBeInTheDocument();
    });

    it('can go back to practice from start screen', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Back to Practice'));

      expect(screen.getByText('Start Spatial Exercise')).toBeInTheDocument();
    });

    it('can try again after completion', async () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));
      await waitFor(() => {
        expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Complete'));
      await waitFor(() => {
        expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Try Again'));

      expect(screen.getByText('Start Spatial Exercise')).toBeInTheDocument();
    });
  });

  describe('exercise completion screen', () => {
    it('displays completion message after exercise', async () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));
      await waitFor(() => {
        expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Complete'));

      await waitFor(() => {
        expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
      });

      expect(screen.getByText('Great job completing your spatial exercise!')).toBeInTheDocument();
    });

    it('calls onExerciseComplete with success status', async () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));
      await waitFor(() => {
        expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Complete'));

      await waitFor(() => {
        expect(mockOnExerciseComplete).toHaveBeenCalledWith(true);
      });
    });

    it('can navigate back to practice from completion screen', async () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));
      await waitFor(() => {
        expect(screen.getByTestId('spatial-exercise')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Complete'));

      await waitFor(() => {
        expect(screen.getByText('Exercise Complete!')).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText('Back to Practice'));

      expect(screen.getByText('Start Spatial Exercise')).toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('renders error message for unknown exercise type', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="unknown" as any
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      fireEvent.click(screen.getByText('Start Exercise'));

      expect(screen.getByText('Unknown exercise type')).toBeInTheDocument();
    });

    it('handles null palace gracefully', () => {
      render(
        <ExerciseRunner
          palace={null}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('No palace selected')).toBeInTheDocument();
    });
  });

  describe('button states', () => {
    it('displays correct exercise type in title', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="spatial"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('Start Spatial Exercise')).toBeInTheDocument();
    });

    it('displays correct exercise type in description', () => {
      render(
        <ExerciseRunner
          palace={mockPalace}
          exerciseType="recall"
          onExerciseComplete={mockOnExerciseComplete}
        />
      );

      expect(screen.getByText('Great job completing your recall exercise!')).toBeInTheDocument();
    });
  });
});
