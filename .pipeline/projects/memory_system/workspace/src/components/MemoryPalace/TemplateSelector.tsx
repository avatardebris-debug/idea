import React, { useState } from 'react';
import {
  AVAILABLE_TEMPLATES,
  getTemplateById,
  getTemplatePreview,
  PalaceTemplate,
} from '../utils/palaceTemplates';
import './TemplateSelector.css';

interface TemplateSelectorProps {
  onTemplateSelected: (template: PalaceTemplate) => void;
  selectedTemplateId?: string | null;
}

const TemplateSelector: React.FC<TemplateSelectorProps> = ({
  onTemplateSelected,
  selectedTemplateId = null,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isExpanded, setIsExpanded] = useState<boolean>(false);

  const handleTemplateClick = (template: PalaceTemplate) => {
    onTemplateSelected(template);
    setIsExpanded(false);
  };

  const filterTemplates = (templates: PalaceTemplate[], category: string): PalaceTemplate[] => {
    if (category === 'all') return templates;
    return templates.filter((t) => t.category === category);
  };

  const filteredTemplates = filterTemplates(AVAILABLE_TEMPLATES, selectedCategory);

  const categories = ['all', 'home', 'office', 'school'];

  return (
    <div className="template-selector">
      <div className="template-selector-header">
        <h3>Choose a Palace Template</h3>
        <button
          className="btn btn-small btn-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
        >
          {isExpanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      <div className={`template-selector-content ${isExpanded ? 'expanded' : ''}`}>
        {/* Category Filter */}
        <div className="template-categories">
          {categories.map((category) => (
            <button
              key={category}
              className={`btn btn-category ${
                selectedCategory === category ? 'active' : ''
              }`}
              onClick={() => setSelectedCategory(category)}
              aria-pressed={selectedCategory === category}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>

        {/* Template Grid */}
        <div className="templates-grid">
          {filteredTemplates.length === 0 ? (
            <div className="no-templates">
              <p>No templates available in this category</p>
            </div>
          ) : (
            filteredTemplates.map((template) => {
              const preview = getTemplatePreview(template);
              const isSelected = selectedTemplateId === template.id;

              return (
                <div
                  key={template.id}
                  className={`template-card ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleTemplateClick(template)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      handleTemplateClick(template);
                    }
                  }}
                  aria-selected={isSelected}
                >
                  <div className="template-card-header">
                    <h4 className="template-name">{preview.name}</h4>
                    <span className={`template-category category-${preview.category}`}>
                      {preview.category}
                    </span>
                  </div>

                  <p className="template-description">{preview.description}</p>

                  <div className="template-stats">
                    <span className="stat-item">
                      <span className="stat-icon">🏠</span>
                      <span className="stat-value">{preview.roomCount} rooms</span>
                    </span>
                  </div>

                  <div className="template-rooms-preview">
                    <h5>Rooms:</h5>
                    <ul className="room-list">
                      {preview.roomNames.map((roomName, index) => (
                        <li key={index} className="room-item">
                          {roomName}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {isSelected && (
                    <div className="template-selected-indicator">
                      ✓ Selected
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Selected Template Summary */}
      {selectedTemplateId && (
        <div className="template-selection-summary">
          <p className="summary-label">Selected Template:</p>
          <div className="summary-content">
            {(() => {
              const template = getTemplateById(selectedTemplateId);
              if (!template) return null;
              const preview = getTemplatePreview(template);
              return (
                <>
                  <span className="summary-name">{preview.name}</span>
                  <span className="summary-room-count">
                    {preview.roomCount} rooms
                  </span>
                </>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateSelector;
