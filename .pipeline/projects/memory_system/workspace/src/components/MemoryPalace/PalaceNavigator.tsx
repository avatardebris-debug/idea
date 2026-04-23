import React, { useState, useMemo } from 'react';
import { Palace } from '../types/palace';
import './PalaceNavigator.css';

interface PalaceNavigatorProps {
  palaces: Palace[];
  selectedPalaceId: string | null;
  onSelectPalace: (palace: Palace) => void;
  onSearch?: (query: string) => void;
}

type SortOption = 'name' | 'createdDate' | 'lastUsed' | 'roomCount';

interface PalaceNavProps {
  palaces: Palace[];
  selectedPalaceId: string | null;
  onSelectPalace: (palace: Palace) => void;
}

const PalaceNavigator: React.FC<PalaceNavProps> = ({
  palaces,
  selectedPalaceId,
  onSelectPalace,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortOption, setSortOption] = useState<SortOption>('createdDate');
  const [showFilters, setShowFilters] = useState<boolean>(false);

  // Filter palaces by search query
  const filteredPalaces = useMemo(() => {
    if (!searchQuery.trim()) return palaces;

    const query = searchQuery.toLowerCase();
    return palaces.filter(
      (palace) =>
        palace.name.toLowerCase().includes(query) ||
        palace.description.toLowerCase().includes(query)
    );
  }, [palaces, searchQuery]);

  // Sort palaces by selected criteria
  const sortedPalaces = useMemo(() => {
    const sorted = [...filteredPalaces];

    switch (sortOption) {
      case 'name':
        sorted.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'createdDate':
        sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
        break;
      case 'lastUsed':
        // For demo, we'll use createdAt as lastUsed since we don't track it
        sorted.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
        break;
      case 'roomCount':
        sorted.sort((a, b) => b.rooms.length - a.rooms.length);
        break;
    }

    return sorted;
  }, [filteredPalaces, sortOption]);

  // Get recently used palaces (last 3)
  const recentlyUsed = useMemo(() => {
    return sortedPalaces.slice(0, 3);
  }, [sortedPalaces]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSortOption(e.target.value as SortOption);
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };

  const clearSearch = () => {
    setSearchQuery('');
  };

  const handleSelectPalace = (palace: Palace, e: React.MouseEvent) => {
    e.stopPropagation();
    onSelectPalace(palace);
  };

  return (
    <div className="palace-navigator">
      {/* Search and Filter Controls */}
      <div className="navigator-controls">
        <div className="search-container">
          <div className="search-icon">🔍</div>
          <input
            type="text"
            className="search-input"
            placeholder="Search palaces..."
            value={searchQuery}
            onChange={handleSearchChange}
            aria-label="Search palaces"
          />
          {searchQuery && (
            <button className="search-clear" onClick={clearSearch} aria-label="Clear search">
              ×
            </button>
          )}
        </div>

        <div className="filter-controls">
          <select
            className="sort-select"
            value={sortOption}
            onChange={handleSortChange}
            aria-label="Sort palaces by"
          >
            <option value="createdDate">Newest First</option>
            <option value="lastUsed">Recently Used</option>
            <option value="name">Name (A-Z)</option>
            <option value="roomCount">Room Count</option>
          </select>

          <button
            className="btn btn-small btn-icon filter-toggle"
            onClick={toggleFilters}
            aria-label={showFilters ? 'Hide filters' : 'Show filters'}
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* Recently Used Section */}
      {recentlyUsed.length > 0 && (
        <div className="recently-used-section">
          <h4>Recently Used</h4>
          <div className="recent-palaces-list">
            {recentlyUsed.map((palace) => (
              <div
                key={palace.id}
                className={`recent-palace-item ${selectedPalaceId === palace.id ? 'active' : ''}`}
                onClick={(e) => handleSelectPalace(palace, e)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleSelectPalace(palace, e);
                  }
                }}
              >
                <div className="recent-palace-info">
                  <h5 className="recent-palace-name">{palace.name}</h5>
                  <span className="recent-palace-meta">
                    {palace.rooms.length} rooms
                  </span>
                </div>
                {selectedPalaceId === palace.id && (
                  <span className="active-indicator">●</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Palaces List */}
      <div className="all-palaces-section">
        <div className="section-header">
          <h4>All Palaces</h4>
          <span className="palace-count">{sortedPalaces.length} palaces</span>
        </div>

        {sortedPalaces.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <p>No palaces found</p>
            {searchQuery && (
              <p className="empty-hint">Try adjusting your search or filters</p>
            )}
          </div>
        ) : (
          <div className="palaces-list">
            {sortedPalaces.map((palace) => (
              <div
                key={palace.id}
                className={`palace-list-item ${selectedPalaceId === palace.id ? 'selected' : ''}`}
                onClick={(e) => handleSelectPalace(palace, e)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    handleSelectPalace(palace, e);
                  }
                }}
              >
                <div className="palace-item-header">
                  <h5 className="palace-item-name">{palace.name}</h5>
                  <span className="room-count-badge">{palace.rooms.length} rooms</span>
                </div>
                <p className="palace-item-description">
                  {palace.description || 'No description'}
                </p>
                <div className="palace-item-meta">
                  <span className="created-date">
                    Created {new Date(palace.createdAt).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Keyboard Shortcuts Help */}
      <div className="keyboard-shortcuts">
        <h5>Keyboard Shortcuts</h5>
        <div className="shortcut-row">
          <kbd className="kbd">Tab</kbd>
          <span>Navigate between items</span>
        </div>
        <div className="shortcut-row">
          <kbd className="kbd">Enter</kbd>
          <span>Select palace</span>
        </div>
        <div className="shortcut-row">
          <kbd className="kbd">Esc</kbd>
          <span>Close navigator</span>
        </div>
      </div>
    </div>
  );
};

export default PalaceNavigator;
