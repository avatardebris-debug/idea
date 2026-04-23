import React, { useState } from 'react'

interface WorkspaceManagerProps {
  workspaces: any[]
  loading: boolean
  onCreateWorkspace: (name: string, description?: string) => Promise<any>
  onSelectWorkspace: (id: number) => void
}

export function WorkspaceManager({ workspaces, loading, onCreateWorkspace, onSelectWorkspace }: WorkspaceManagerProps) {
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleCreate = async () => {
    if (!name.trim()) {
      setError('Workspace name is required')
      return
    }
    try {
      setError(null)
      const newWorkspace = await onCreateWorkspace(name, description)
      setShowCreate(false)
      setName('')
      setDescription('')
      onSelectWorkspace(newWorkspace.id)
    } catch (err: any) {
      setError(err.message || 'Failed to create workspace')
    }
  }

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Workspaces</h2>
        <button onClick={() => setShowCreate(true)} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Create Workspace
        </button>
      </div>

      {error && <div style={{ padding: '10px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '10px' }}>{error}</div>}

      {showCreate && (
        <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
          <h3>Create New Workspace</h3>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Name:</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
              placeholder="My Workspace"
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Description:</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
              placeholder="Optional description"
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button onClick={handleCreate} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
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
      ) : workspaces.length === 0 ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#6c757d' }}>No workspaces yet. Create one to get started.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {workspaces.map(workspace => (
            <div
              key={workspace.id}
              onClick={() => onSelectWorkspace(workspace.id)}
              style={{
                padding: '15px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px',
                cursor: 'pointer',
                border: '1px solid #dee2e6',
                transition: 'background-color 0.2s'
              }}
              onMouseEnter={e => (e.currentTarget.style.backgroundColor = '#e9ecef')}
              onMouseLeave={e => (e.currentTarget.style.backgroundColor = '#f8f9fa')}
            >
              <h3 style={{ margin: '0 0 5px 0' }}>{workspace.name}</h3>
              {workspace.description && <p style={{ margin: 0, color: '#6c757d' }}>{workspace.description}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}