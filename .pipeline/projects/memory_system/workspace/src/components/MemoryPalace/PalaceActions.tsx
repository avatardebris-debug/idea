import React, { useRef, useState } from 'react';
import { Palace } from '../types/palace';
import {
  exportPalace,
  exportAllPalaces,
  downloadExport,
  importPalace,
  importAllPalaces,
  generateExportFilename,
  generateAllPalacesFilename,
} from '../utils/palaceExportImport';
import { loadPalaces } from '../utils/palaceUtils';
import './PalaceActions.css';

interface PalaceActionsProps {
  palace: Palace | null;
  onImportSuccess?: (palace: Palace) => void;
}

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (palace: Palace) => void;
  palaceData: {
    name: string;
    roomCount: number;
    description: string;
    creationDate: string;
  };
}

const ImportModal: React.FC<ImportModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  palaceData,
}) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm(palaceData as unknown as Palace);
    onClose();
  };

  const handleCancel = () => {
    onClose();
  };

  return (
    <div className="import-modal-overlay" onClick={onClose}>
      <div className="import-modal" onClick={(e) => e.stopPropagation()}>
        <div className="import-modal-header">
          <h3>Import Palace</h3>
          <button className="btn-modal-close" onClick={onClose} aria-label="Close modal">
            ×
          </button>
        </div>

        <div className="import-modal-content">
          <div className="palace-preview">
            <h4>Palace Details</h4>
            <div className="preview-details">
              <div className="preview-item">
                <span className="preview-label">Name:</span>
                <span className="preview-value">{palaceData.name}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Rooms:</span>
                <span className="preview-value">{palaceData.roomCount} rooms</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Description:</span>
                <span className="preview-value">{palaceData.description}</span>
              </div>
              <div className="preview-item">
                <span className="preview-label">Created:</span>
                <span className="preview-value">
                  {new Date(palaceData.creationDate).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          <div className="import-actions">
            <button className="btn btn-secondary" onClick={handleCancel}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={handleConfirm}>
              Import Palace
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const PalaceActions: React.FC<PalaceActionsProps> = ({
  palace,
  onImportSuccess,
}) => {
  const [importModalOpen, setImportModalOpen] = useState<boolean>(false);
  const [importPalaceData, setImportPalaceData] = useState<{
    name: string;
    roomCount: number;
    description: string;
    creationDate: string;
  } | null>(null);
  const [importError, setImportError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExportPalace = () => {
    if (!palace) return;

    const exportData = exportPalace(palace);
    const filename = generateExportFilename(palace.name);
    downloadExport(exportData, filename);
  };

  const handleExportAllPalaces = () => {
    const palaces = loadPalaces();
    const exportData = exportAllPalaces(palaces);
    const filename = generateAllPalacesFilename();
    downloadExport(exportData, filename);
  };

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
      setImportError('Please select a valid JSON file');
      return;
    }

    try {
      const result = await importPalace(file);

      if (result.success && result.palace) {
        setImportPalaceData({
          name: result.palace.name,
          roomCount: result.palace.rooms.length,
          description: result.palace.description,
          creationDate: result.palace.createdAt,
        });
        setImportModalOpen(true);
        setImportError(null);
      } else {
        setImportError(result.errors.join(', '));
      }
    } catch (error) {
      setImportError('Failed to import palace');
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleConfirmImport = (palace: Palace) => {
    onImportSuccess?.(palace);
    setImportModalOpen(false);
    setImportPalaceData(null);
  };

  const handleCancelImport = () => {
    setImportModalOpen(false);
    setImportPalaceData(null);
    setImportError(null);
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="palace-actions">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleImportFile}
        accept=".json,application/json"
        style={{ display: 'none' }}
      />

      <div className="action-buttons">
        <button
          className="btn btn-primary btn-action"
          onClick={handleExportPalace}
          disabled={!palace}
          aria-label="Export current palace"
        >
          📥 Export Palace
        </button>

        <button
          className="btn btn-secondary btn-action"
          onClick={handleExportAllPalaces}
          aria-label="Export all palaces"
        >
          📥 Export All
        </button>

        <button
          className="btn btn-success btn-action"
          onClick={triggerFileInput}
          disabled={!palace}
          aria-label="Import palace"
        >
          📤 Import Palace
        </button>

        <button
          className="btn btn-success btn-action"
          onClick={triggerFileInput}
          aria-label="Import all palaces"
        >
          📤 Import All
        </button>
      </div>

      {importError && (
        <div className="import-error">
          <p className="error-message">{importError}</p>
          <button className="btn btn-small" onClick={() => setImportError(null)}>
            Dismiss
          </button>
        </div>
      )}

      <ImportModal
        isOpen={importModalOpen}
        onClose={handleCancelImport}
        onConfirm={handleConfirmImport}
        palaceData={importPalaceData || { name: '', roomCount: 0, description: '', creationDate: '' }}
      />
    </div>
  );
};

export default PalaceActions;
