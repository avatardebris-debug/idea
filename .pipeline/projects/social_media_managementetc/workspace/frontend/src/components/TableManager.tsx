import React, { useState } from 'react'

interface TableManagerProps {
  tables: any[]
  loading: boolean
  onCreateTable: (name: string, columnDefinitions: any[]) => Promise<any>
  onSelectTable: (id: number) => void
  currentTableId: number | null
}

export function TableManager({ tables, loading, onCreateTable, onSelectTable, currentTableId }: TableManagerProps) {
  const [showCreate, setShowCreate] = useState(false)
  const [tableName, setTableName] = useState('')
  const [columns, setColumns] = useState<{ name: string; type: string }[]>([{ name: '', type: 'text' }])
  const [error, setError] = useState<string | null>(null)

  const addColumn = () => {
    setColumns([...columns, { name: '', type: 'text' }])
  }

  const removeColumn = (index: number) => {
    if (columns.length > 1) {
      setColumns(columns.filter((_, i) => i !== index))
    }
  }

  const updateColumn = (index: number, field: 'name' | 'type', value: string) => {
    const newColumns = [...columns]
    newColumns[index] = { ...newColumns[index], [field]: value }
    setColumns(newColumns)
  }

  const handleCreate = async () => {
    if (!tableName.trim()) {
      setError('Table name is required')
      return
    }
    const validColumns = columns.filter(col => col.name.trim())
    if (validColumns.length === 0) {
      setError('At least one column is required')
      return
    }
    try {
      setError(null)
      const newTable = await onCreateTable(tableName, validColumns)
      setShowCreate(false)
      setTableName('')
      setColumns([{ name: '', type: 'text' }])
      onSelectTable(newTable.id)
    } catch (err: any) {
      setError(err.message || 'Failed to create table')
    }
  }

  return (
    <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h2 style={{ margin: 0 }}>Content Tables</h2>
        <button onClick={() => setShowCreate(true)} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Create Table
        </button>
      </div>

      {error && <div style={{ padding: '10px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '10px' }}>{error}</div>}

      {showCreate && (
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3>Create New Table</h3>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Table Name:</label>
            <input
              type="text"
              value={tableName}
              onChange={e => setTableName(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
              placeholder="Content Calendar"
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Columns:</label>
            {columns.map((col, index) => (
              <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '5px' }}>
                <input
                  type="text"
                  value={col.name}
                  onChange={e => updateColumn(index, 'name', e.target.value)}
                  placeholder="Column name"
                  style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
                />
                <select
                  value={col.type}
                  onChange={e => updateColumn(index, 'type', e.target.value)}
                  style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
                >
                  <option value="text">Text</option>
                  <option value="number">Number</option>
                  <option value="date">Date</option>
                  <option value="boolean">Boolean</option>
                </select>
                <button onClick={() => removeColumn(index)} style={{ padding: '8px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                  ×
                </button>
              </div>
            ))}
            <button onClick={addColumn} style={{ padding: '5px 10px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '5px' }}>
              + Add Column
            </button>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={handleCreate} style={{ padding: '8px 16px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Create
            </button>
            <button onClick={() => setShowCreate(false)} style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>
      ) : tables.length === 0 ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>No tables yet. Create one to start managing content.</div>
      ) : (
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {tables.map(table => (
            <div
              key={table.id}
              onClick={() => onSelectTable(table.id)}
              style={{
                padding: '10px 15px',
                backgroundColor: currentTableId === table.id ? '#007bff' : '#f8f9fa',
                color: currentTableId === table.id ? 'white' : '#333',
                borderRadius: '4px',
                cursor: 'pointer',
                border: '1px solid #dee2e6',
                transition: 'all 0.2s'
              }}
            >
              {table.name}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}