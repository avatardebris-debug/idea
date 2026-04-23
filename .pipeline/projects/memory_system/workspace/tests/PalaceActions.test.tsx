import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PalaceActions } from '../src/components/MemoryPalace/PalaceActions';
import * as exportUtils from '../src/utils/palaceExportImport';
import * as palaceUtils from '../src/utils/palaceUtils';

// Mock the export/import utilities
vi.mock('../src/utils/palaceExportImport', () => ({
  exportPalace: vi.fn(),
  exportAllPalaces: vi.fn(),
  downloadExport: vi.fn(),
  importPalace: vi.fn(),
  importAllPalaces: vi.fn(),
  generateExportFilename: vi.fn(),
  generateAllPalacesFilename: vi.fn(),
}));

// Mock the palace utils
vi.mock('../src/utils/palaceUtils', () => ({
  loadPalaces: vi.fn(),
  savePalace: vi.fn(),
}));

describe('PalaceActions', () => {
  const mockPalace = {
    id: 'palace-1',
    name: 'Test Palace',
    description: 'A test palace',
    rooms: [
      { id: 'room-1', name: 'Room 1', description: 'Room 1 description', items: [] },
    ],
    createdAt: '2024-01-01T00:00:00.000Z',
  };

  const mockOnImportSuccess = vi.fn();

  const renderComponent = (props = {}) => {
    return render(
      <PalaceActions palace={mockPalace} onImportSuccess={mockOnImportSuccess} {...props} />
    );
  };

  it('renders export and import buttons', () => {
    renderComponent();

    expect(screen.getByText('📥 Export Palace')).toBeInTheDocument();
    expect(screen.getByText('📥 Export All')).toBeInTheDocument();
    expect(screen.getByText('📤 Import Palace')).toBeInTheDocument();
    expect(screen.getByText('📤 Import All')).toBeInTheDocument();
  });

  it('disables export buttons when palace is null', () => {
    const { rerender } = render(<PalaceActions palace={null} onImportSuccess={mockOnImportSuccess} />);

    const exportPalaceBtn = screen.getByText('📥 Export Palace');
    expect(exportPalaceBtn).toBeDisabled();

    rerender(<PalaceActions palace={mockPalace} onImportSuccess={mockOnImportSuccess} />);

    const enabledBtn = screen.getByText('📥 Export Palace');
    expect(enabledBtn).not.toBeDisabled();
  });

  it('calls exportPalace when Export Palace button is clicked', async () => {
    const mockExportData = { version: '1.0', palace: mockPalace };
    vi.spyOn(exportUtils, 'exportPalace').mockReturnValue(mockExportData);
    vi.spyOn(exportUtils, 'generateExportFilename').mockReturnValue('palace.json');

    renderComponent();

    const exportButton = screen.getByText('📥 Export Palace');
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(exportUtils.exportPalace).toHaveBeenCalledWith(mockPalace);
    });
  });

  it('calls exportAllPalaces when Export All button is clicked', async () => {
    const mockPalaces = [mockPalace];
    vi.spyOn(palaceUtils, 'loadPalaces').mockReturnValue(mockPalaces);
    vi.spyOn(exportUtils, 'exportAllPalaces').mockReturnValue({
      version: '1.0',
      exportDate: new Date().toISOString(),
      palace: { id: 'all', name: 'All', description: '', rooms: [], createdAt: '' },
      metadata: { exportVersion: '1.0', exportedBy: 'Test' },
    });
    vi.spyOn(exportUtils, 'generateAllPalacesFilename').mockReturnValue('all.json');

    renderComponent();

    const exportAllButton = screen.getByText('📥 Export All');
    fireEvent.click(exportAllButton);

    await waitFor(() => {
      expect(exportUtils.exportAllPalaces).toHaveBeenCalled();
    });
  });

  it('shows import modal when Import Palace button is clicked', async () => {
    const mockFile = new File(['test data'], 'palace.json', { type: 'application/json' });
    const mockReader = {
      onload: vi.fn(),
      onerror: vi.fn(),
      readAsText: vi.fn(),
    };
    vi.spyOn(window, 'FileReader').mockImplementation(() => mockReader as unknown as FileReader);

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    // Trigger file input change
    const fileInput = screen.getByRole('textbox');
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('Import Palace')).toBeInTheDocument();
    });
  });

  it('calls onImportSuccess when import is successful', async () => {
    const mockImportData = { success: true, palace: mockPalace };
    vi.spyOn(exportUtils, 'importPalace').mockResolvedValue(mockImportData);

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(mockOnImportSuccess).toHaveBeenCalled();
    });
  });

  it('shows error message when import fails', async () => {
    vi.spyOn(exportUtils, 'importPalace').mockRejectedValue(new Error('Invalid file format'));

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(screen.getByText('Error:')).toBeInTheDocument();
    });
  });

  it('handles import all functionality', async () => {
    const mockImportData = { success: true, palaces: [mockPalace] };
    vi.spyOn(exportUtils, 'importAllPalaces').mockResolvedValue(mockImportData);

    renderComponent();

    const importAllButton = screen.getByText('📤 Import All');
    fireEvent.click(importAllButton);

    await waitFor(() => {
      expect(exportUtils.importAllPalaces).toHaveBeenCalled();
    });
  });

  it('displays palace preview in import modal', async () => {
    const mockImportData = { success: true, palace: mockPalace };
    vi.spyOn(exportUtils, 'importPalace').mockResolvedValue(mockImportData);

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(screen.getByText('Palace Preview')).toBeInTheDocument();
      expect(screen.getByText('Test Palace')).toBeInTheDocument();
    });
  });

  it('closes import modal when cancel button is clicked', async () => {
    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      const cancelButton = screen.getByText('Cancel');
      fireEvent.click(cancelButton);
    });

    expect(screen.queryByText('Import Palace')).not.toBeInTheDocument();
  });

  it('confirms import action with user', () => {
    const mockConfirm = vi.fn(() => true);
    vi.spyOn(window, 'confirm').mockImplementation(mockConfirm);

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    expect(window.confirm).toHaveBeenCalled();
  });

  it('handles keyboard navigation in import modal', async () => {
    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      const cancelButton = screen.getByText('Cancel');
      fireEvent.keyDown(cancelButton, { key: 'Escape' });
    });

    expect(screen.queryByText('Import Palace')).not.toBeInTheDocument();
  });

  it('displays loading state during import', async () => {
    vi.useFakeTimers();
    const mockImportData = { success: true, palace: mockPalace };
    vi.spyOn(exportUtils, 'importPalace').mockImplementation(() =>
      new Promise((resolve) => setTimeout(() => resolve(mockImportData), 100))
    );

    renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(screen.getByText('Importing...')).toBeInTheDocument();
    });

    vi.useRealTimers();
  });

  it('handles file read errors gracefully', async () => {
    const mockFile = new File(['invalid json'], 'palace.json', { type: 'application/json' });
    const mockReader = {
      onload: vi.fn(),
      onerror: vi.fn(),
      readAsText: vi.fn((cb) => cb({ target: { error: new Error('File read error') } })),
    };
    vi.spyOn(window, 'FileReader').mockImplementation(() => mockReader as unknown as FileReader);

    const { container } = renderComponent();

    const importButton = screen.getByText('📤 Import Palace');
    fireEvent.click(importButton);

    await waitFor(() => {
      expect(container.querySelector('[data-testid="error-message"]')).toBeInTheDocument();
    });
  });

  it('supports aria attributes for accessibility', () => {
    renderComponent();

    const exportButton = screen.getByRole('button', { name: /export/i });
    expect(exportButton).toHaveAttribute('aria-label', 'Export Palace');
  });
});
