import React, { useState, useEffect } from 'react';
import { Palace, Room, PalaceStats } from '../types/palace';
import { savePalace, loadPalaces, deletePalace, getPalaceStats as getStats } from '../utils/palaceUtils';
import { AVAILABLE_TEMPLATES, createPalaceFromTemplate, PalaceTemplate } from '../utils/palaceTemplates';
import TemplateSelector from './TemplateSelector';
import PalaceActions from './PalaceActions';
import './PalaceCreator.css';

interface PalaceCreatorProps {
  onPalaceCreated?: (palace: Palace) => void;
}

const PalaceCreator: React.FC<PalaceCreatorProps> = ({ onPalaceCreated }) => {
  const [palaceName, setPalaceName] = useState<string>('');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [palaceList, setPalaceList] = useState<Palace[]>([]);
  const [currentPalace, setCurrentPalace] = useState<Palace | null>(null);
  const [newRoomName, setNewRoomName] = useState<string>('');
  const [useTemplate, setUseTemplate] = useState<boolean>(false);
  const [selectedTemplate, setSelectedTemplate] = useState<PalaceTemplate | null>(null);

  // Load saved palaces on mount
  useEffect(() => {
    const saved = loadPalaces();
    setPalaceList(saved);
  }, []);

  // Update current palace when list changes
  useEffect(() => {
    if (palaceList.length > 0 && !currentPalace) {
      setCurrentPalace(palaceList[0]);
    }
  }, [palaceList, currentPalace]);

  // Update rooms when current palace changes
  useEffect(() => {
    if (currentPalace) {
      setRooms(currentPalace.rooms);
    }
  }, [currentPalace]);

  // Handle template selection
  const handleTemplateSelected = (template: PalaceTemplate) => {
    setSelectedTemplate(template);
  };

  // Apply template to current palace
  const handleApplyTemplate = () => {
    if (!selectedTemplate || !currentPalace) return;

    const palaceData = createPalaceFromTemplate(selectedTemplate, currentPalace.name);
    const newRooms: Room[] = palaceData.rooms.map((room, index) => ({
      id: `room-${Date.now()}-${index}`,
      name: room.name,
      description: room.description,
      items: room.items,
    }));

    const updatedPalace = {
      ...currentPalace,
      description: palaceData.description,
      rooms: newRooms,
    };

    setCurrentPalace(updatedPalace);
    setRooms(newRooms);
    setSelectedTemplate(null);
  };

  const handleCreatePalace = () => {
    if (!palaceName.trim()) return;

    const newPalace: Palace = {
      id: `palace-${Date.now()}`,
      name: palaceName.trim(),
      description: '',
      rooms: [],
      createdAt: new Date().toISOString(),
    };

    const updatedPalaces = [...palaceList, newPalace];
    savePalace(newPalace);
    setPalaceList(updatedPalaces);
    setCurrentPalace(newPalace);
    setPalaceName('');
    
    if (onPalaceCreated) {
      onPalaceCreated(newPalace);
    }
  };

  const handleSelectPalace = (palace: Palace) => {
    setCurrentPalace(palace);
    setRooms(palace.rooms);
  };

  const handleDeletePalace = (palaceId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updatedPalaces = palaceList.filter(p => p.id !== palaceId);
    savePalace(updatedPalaces);
    setPalaceList(updatedPalaces);
    
    if (currentPalace?.id === palaceId) {
      setCurrentPalace(updatedPalaces[0] || null);
      setRooms([]);
    }
  };

  const handleAddRoom = () => {
    if (!newRoomName.trim() || !currentPalace) return;

    const newRoom: Room = {
      id: `room-${Date.now()}`,
      name: newRoomName.trim(),
      description: '',
      items: [],
    };

    const updatedRooms = [...rooms, newRoom];
    setRooms(updatedRooms);

    // Update the palace
    if (currentPalace) {
      const updatedPalace = {
        ...currentPalace,
        rooms: updatedRooms,
      };
      setCurrentPalace(updatedPalace);
      savePalace(updatedPalace);
    }

    setNewRoomName('');
  };

  const handleSelectRoom = (room: Room) => {
    setSelectedRoom(room);
  };

  const handleDeleteRoom = (roomId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updatedRooms = rooms.filter(r => r.id !== roomId);
    setRooms(updatedRooms);

    if (currentPalace) {
      const updatedPalace = {
        ...currentPalace,
        rooms: updatedRooms,
      };
      setCurrentPalace(updatedPalace);
      savePalace(updatedPalace);
    }

    if (selectedRoom?.id === roomId) {
      setSelectedRoom(null);
    }
  };

  const handleUpdateRoomDescription = (roomId: string, description: string) => {
    const updatedRooms = rooms.map(r => 
      r.id === roomId ? { ...r, description } : r
    );
    setRooms(updatedRooms);

    if (currentPalace) {
      const updatedPalace = {
        ...currentPalace,
        rooms: updatedRooms,
      };
      setCurrentPalace(updatedPalace);
      savePalace(updatedPalace);
    }
  };

  const handleImportSuccess = (importedPalace: Palace) => {
    // Check if palace already exists
    const exists = palaceList.some(p => p.id === importedPalace.id);
    
    if (exists) {
      // Update existing palace
      const updatedPalaces = palaceList.map(p => 
        p.id === importedPalace.id ? importedPalace : p
      );
      setPalaceList(updatedPalaces);
      setCurrentPalace(importedPalace);
      setRooms(importedPalace.rooms);
    } else {
      // Add new palace
      const updatedPalaces = [...palaceList, importedPalace];
      savePalace(updatedPalaces);
      setPalaceList(updatedPalaces);
      setCurrentPalace(importedPalace);
      setRooms(importedPalace.rooms);
    }
  };

  const getRoomStats = (): PalaceStats => {
    const totalRooms = rooms.length;
    const totalItems = rooms.reduce((sum, r) => sum + r.items.length, 0);
    const lastUsed = currentPalace?.createdAt || new Date().toISOString();

    return {
      totalPalaces: palaceList.length,
      totalRooms,
      lastUsed,
    };
  };

  const roomStats = getRoomStats();

  return (
    <div className="palace-creator">
      <h2>Memory Palace Creator</h2>

      <div className="creator-layout">
        {/* Left Panel: Palace List */}
        <div className="palace-list-panel">
          <h3>Your Palaces</h3>
          <div className="palace-list">
            {palaceList.length === 0 ? (
              <p className="empty-palace-list">No palaces yet. Create one to get started!</p>
            ) : (
              palaceList.map((palace) => (
                <div
                  key={palace.id}
                  className={`palace-item ${currentPalace?.id === palace.id ? 'active' : ''}`}
                  onClick={() => handleSelectPalace(palace)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      handleSelectPalace(palace);
                    }
                  }}
                >
                  <div className="palace-item-content">
                    <h4 className="palace-name">{palace.name}</h4>
                    <p className="palace-description">
                      {palace.description || 'No description'}
                    </p>
                    <div className="palace-meta">
                      <span className="room-count">{palace.rooms.length} rooms</span>
                      <span className="created-date">
                        Created {new Date(palace.createdAt).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <button
                    className="btn btn-small btn-danger delete-btn"
                    onClick={(e) => handleDeletePalace(palace.id, e)}
                    aria-label={`Delete ${palace.name}`}
                  >
                    ×
                  </button>
                </div>
              ))
            )}
          </div>

          <div className="create-palace-form">
            <h3>Create New Palace</h3>
            <div className="form-group">
              <label htmlFor="palaceName">Palace Name</label>
              <input
                type="text"
                id="palaceName"
                value={palaceName}
                onChange={(e) => setPalaceName(e.target.value)}
                placeholder="Enter palace name"
                className="input-field"
              />
            </div>
            <button
              className="btn btn-primary"
              onClick={handleCreatePalace}
              disabled={!palaceName.trim()}
            >
              Create Palace
            </button>
          </div>
        </div>

        {/* Right Panel: Palace Editor */}
        <div className="palace-editor-panel">
          {currentPalace ? (
            <>
              <div className="editor-header">
                <h3>{currentPalace.name}</h3>
                <p className="editor-description">{currentPalace.description}</p>
              </div>

              <div className="rooms-section">
                <div className="rooms-header">
                  <h4>Rooms</h4>
                  <div className="room-add-section">
                    <input
                      type="text"
                      value={newRoomName}
                      onChange={(e) => setNewRoomName(e.target.value)}
                      placeholder="New room name"
                      className="input-field"
                      onKeyPress={(e) => e.key === 'Enter' && handleAddRoom()}
                    />
                    <button
                      className="btn btn-primary"
                      onClick={handleAddRoom}
                      disabled={!newRoomName.trim()}
                    >
                      Add Room
                    </button>
                  </div>
                </div>

                <div className="rooms-grid">
                  {rooms.map((room) => (
                    <div
                      key={room.id}
                      className={`room-card ${selectedRoom?.id === room.id ? 'selected' : ''}`}
                      onClick={() => handleSelectRoom(room)}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          handleSelectRoom(room);
                        }
                      }}
                    >
                      <div className="room-header">
                        <h5>{room.name}</h5>
                        <button
                          className="btn btn-small btn-danger room-delete"
                          onClick={(e) => handleDeleteRoom(room.id, e)}
                          aria-label={`Delete ${room.name}`}
                        >
                          ×
                        </button>
                      </div>
                      <textarea
                        className="room-description"
                        placeholder="Room description (optional)"
                        value={room.description}
                        onChange={(e) => handleUpdateRoomDescription(room.id, e.target.value)}
                        rows={2}
                      />
                    </div>
                  ))}
                </div>
              </div>

              {/* Template Section */}
              <div className="template-section">
                <div className="template-toggle">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={useTemplate}
                      onChange={(e) => setUseTemplate(e.target.checked)}
                    />
                    <span className="toggle-slider"></span>
                    Use Template
                  </label>
                </div>

                {useTemplate && (
                  <div className="template-container">
                    <TemplateSelector
                      onTemplateSelected={handleTemplateSelected}
                      selectedTemplateId={selectedTemplate?.id || null}
                    />
                    {selectedTemplate && (
                      <button
                        className="btn btn-primary btn-full-width"
                        onClick={handleApplyTemplate}
                      >
                        Apply Template to This Palace
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Export/Import Actions */}
              <PalaceActions
                palace={currentPalace}
                onImportSuccess={handleImportSuccess}
              />
            </>
          ) : (
            <div className="no-palace-selected">
              <p>Select a palace from the list or create a new one to get started.</p>
            </div>
          )}
        </div>
      </div>

      {/* Stats Summary */}
      <div className="stats-summary">
        <div className="stat-item">
          <span className="stat-label">Total Palaces:</span>
          <span className="stat-value">{roomStats.totalPalaces}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Rooms in Current Palace:</span>
          <span className="stat-value">{roomStats.totalRooms}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Last Used:</span>
          <span className="stat-value">
            {new Date(roomStats.lastUsed).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PalaceCreator;
