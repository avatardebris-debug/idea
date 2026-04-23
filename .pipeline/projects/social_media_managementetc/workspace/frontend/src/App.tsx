import React, { useState, useEffect } from 'react'
import { ContentGrid } from './components/ContentGrid'
import { CalendarView } from './components/CalendarView'
import { FilterBar } from './components/FilterBar'
import { ViewToggle } from './components/ViewToggle'
import { ConnectAccount } from './components/ConnectAccount'
import { WorkspaceManager } from './components/WorkspaceManager'
import { TableManager } from './components/TableManager'
import { useRecords } from './hooks/useRecords'
import { useWorkspaces } from './hooks/useWorkspaces'
import { useTables } from './hooks/useTables'

function App() {
  const [view, setView] = useState<'grid' | 'calendar'>('grid')
  const [workspaceId, setWorkspaceId] = useState<number | null>(null)
  const [tableId, setTableId] = useState<number | null>(null)
  const [filterStatus, setFilterStatus] = useState<string | null>(null)
  const [filterTags, setFilterTags] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState<string>('created_at')
  const [sortOrder, setSortOrder] = useState<string>('asc')

  const { workspaces, loading: workspacesLoading, createWorkspace } = useWorkspaces()
  const { tables, loading: tablesLoading, createTable } = useTables(workspaceId)
  const { records, loading: recordsLoading, error, totalPages, page, setPage, createRecord, updateRecord, deleteRecord, refetch } = useRecords(
    tableId || 0,
    filterStatus,
    filterTags,
    sortBy,
    sortOrder
  )

  const handleFilterChange = (status: string | null, tags: string | null) => {
    setFilterStatus(status)
    setFilterTags(tags)
  }

  const handleSortChange = (field: string, order: string) => {
    setSortBy(field)
    setSortOrder(order)
  }

  const handleWorkspaceSelect = (id: number) => {
    setWorkspaceId(id)
    setTableId(null)
  }

  const handleTableSelect = (id: number) => {
    setTableId(id)
  }

  if (!workspaceId) {
    return (
      <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        <h1>Social Media Manager</h1>
        <p>Create a workspace and content table to get started.</p>
        <WorkspaceManager
          workspaces={workspaces}
          loading={workspacesLoading}
          onCreateWorkspace={createWorkspace}
          onSelectWorkspace={handleWorkspaceSelect}
        />
      </div>
    )
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Social Media Manager</h1>
        <div style={{ display: 'flex', gap: '10px' }}>
          <ConnectAccount />
          <button onClick={() => setWorkspaceId(null)} style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Switch Workspace
          </button>
        </div>
      </div>

      <TableManager
        tables={tables}
        loading={tablesLoading}
        onCreateTable={createTable}
        onSelectTable={handleTableSelect}
        currentTableId={tableId}
      />

      {tableId && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <ViewToggle currentView={view} onViewChange={setView} />
            <FilterBar onFilterChange={handleFilterChange} onSortChange={handleSortChange} />
          </div>

          {view === 'grid' ? (
            <ContentGrid
              records={records}
              loading={recordsLoading}
              error={error}
              totalPages={totalPages}
              onCreateRecord={createRecord}
              onUpdateRecord={updateRecord}
              onDeleteRecord={deleteRecord}
            />
          ) : (
            <CalendarView records={records} loading={recordsLoading} error={error} />
          )}
        </>
      )}
    </div>
  )
}

export default App