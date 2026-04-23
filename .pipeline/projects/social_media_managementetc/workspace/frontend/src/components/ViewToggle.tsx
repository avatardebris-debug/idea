import React from 'react'

interface ViewToggleProps {
  currentView: 'grid' | 'calendar'
  onViewChange: (view: 'grid' | 'calendar') => void
}

export function ViewToggle({ currentView, onViewChange }: ViewToggleProps) {
  return (
    <div style={{ display: 'flex', gap: '5px' }}>
      <button
        onClick={() => onViewChange('grid')}
        style={{
          padding: '8px 16px',
          backgroundColor: currentView === 'grid' ? '#007bff' : '#e9ecef',
          color: currentView === 'grid' ? 'white' : '#495057',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Grid View
      </button>
      <button
        onClick={() => onViewChange('calendar')}
        style={{
          padding: '8px 16px',
          backgroundColor: currentView === 'calendar' ? '#007bff' : '#e9ecef',
          color: currentView === 'calendar' ? 'white' : '#495057',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Calendar View
      </button>
    </div>
  )
}
