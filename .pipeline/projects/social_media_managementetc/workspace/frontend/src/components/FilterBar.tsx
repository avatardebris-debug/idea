import React, { useState } from 'react'

interface FilterBarProps {
  onFilterChange: (status: string | null, tags: string | null) => void
  onSortChange: (field: string, order: string) => void
}

export function FilterBar({ onFilterChange, onSortChange }: FilterBarProps) {
  const [status, setStatus] = useState<string | null>(null)
  const [tags, setTags] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<string>('created_at')
  const [sortOrder, setSortOrder] = useState<string>('asc')

  const handleApply = () => {
    onFilterChange(status, tags)
    onSortChange(sortBy, sortOrder)
  }

  const handleClear = () => {
    setStatus(null)
    setTags(null)
    setSortBy('created_at')
    setSortOrder('asc')
    onFilterChange(null, null)
    onSortChange('created_at', 'asc')
  }

  return (
    <div style={{
      padding: '15px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      display: 'flex',
      gap: '10px',
      alignItems: 'center',
      flexWrap: 'wrap'
    }}>
      <select value={status || ''} onChange={e => setStatus(e.target.value || null)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}>
        <option value="">All Statuses</option>
        <option value="draft">Draft</option>
        <option value="scheduled">Scheduled</option>
        <option value="published">Published</option>
      </select>

      <input
        type="text"
        placeholder="Filter by tags"
        value={tags || ''}
        onChange={e => setTags(e.target.value || null)}
        style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da', flex: '1', minWidth: '150px' }}
      />

      <select value={sortBy} onChange={e => setSortBy(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}>
        <option value="created_at">Created</option>
        <option value="scheduled_date">Scheduled</option>
      </select>

      <select value={sortOrder} onChange={e => setSortOrder(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>

      <button onClick={handleApply} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        Apply
      </button>

      <button onClick={handleClear} style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
        Clear
      </button>
    </div>
  )
}
