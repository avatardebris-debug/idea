import React, { useState } from 'react'
import { CellEditor } from './CellEditor'

interface ContentGridProps {
  records: any[]
  loading: boolean
  error: string | null
  totalPages: number
  onCreateRecord: (data: Record<string, any>) => void
  onUpdateRecord: (id: number, data: Partial<Record<string, any>>) => void
  onDeleteRecord: (id: number) => void
}

export function ContentGrid({ records, loading, error, totalPages, onCreateRecord, onUpdateRecord, onDeleteRecord }: ContentGridProps) {
  const [editingCell, setEditingCell] = useState<{ recordId: number; field: string } | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  if (loading) return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>

  const columns = records.length > 0 ? Object.keys(records[0].data || {}) : []

  return (
    <div>
      <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between' }}>
        <button onClick={() => onCreateRecord({})} style={{ padding: '8px 16px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          + New Post
        </button>
        <div>
          <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} style={{ padding: '4px 8px', marginRight: '5px' }}>
            Prev
          </button>
          <span>Page {currentPage} of {totalPages}</span>
          <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} style={{ padding: '4px 8px', marginLeft: '5px' }}>
            Next
          </button>
        </div>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6', textAlign: 'left' }}>Status</th>
              {columns.map(col => (
                <th key={col} style={{ padding: '12px', borderBottom: '2px solid #dee2e6', textAlign: 'left' }}>{col}</th>
              ))}
              <th style={{ padding: '12px', borderBottom: '2px solid #dee2e6', textAlign: 'left' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {records.map(record => (
              <tr key={record.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                <td style={{ padding: '12px' }}>
                  <span style={{
                    padding: '4px 8px',
                    borderRadius: '12px',
                    backgroundColor: record.status === 'published' ? '#d4edda' : record.status === 'scheduled' ? '#cce5ff' : '#fff3cd',
                    color: record.status === 'published' ? '#155724' : record.status === 'scheduled' ? '#004085' : '#856404',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}>
                    {record.status}
                  </span>
                </td>
                {columns.map(col => (
                  <td key={col} style={{ padding: '12px' }}>
                    {editingCell?.recordId === record.id && editingCell?.field === col ? (
                      <CellEditor
                        value={record.data[col] || ''}
                        onSave={(val) => {
                          onUpdateRecord(record.id, { [col]: val })
                          setEditingCell(null)
                        }}
                        onCancel={() => setEditingCell(null)}
                      />
                    ) : (
                      <span onClick={() => setEditingCell({ recordId: record.id, field: col })} style={{ cursor: 'pointer', padding: '4px', borderRadius: '4px', display: 'block' }}>
                        {record.data[col] || <span style={{ color: '#adb5bd', fontStyle: 'italic' }}>Empty</span>}
                      </span>
                    )}
                  </td>
                ))}
                <td style={{ padding: '12px' }}>
                  <button onClick={() => onDeleteRecord(record.id)} style={{ padding: '4px 8px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
