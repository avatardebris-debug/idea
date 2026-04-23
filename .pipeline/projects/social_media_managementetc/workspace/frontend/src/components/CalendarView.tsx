import React, { useState } from 'react'
import { useRecords } from '../hooks/useRecords'
import { ScheduleModal } from './ScheduleModal'

interface CalendarViewProps {
  tableId: number
  loading: boolean
  error: string | null
}

export function CalendarView({ tableId, loading, error }: CalendarViewProps) {
  const [filterStatus, setFilterStatus] = useState<string | null>(null)
  const [filterTags, setFilterTags] = useState<string | null>(null)
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [showSchedule, setShowSchedule] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<any>(null)

  const {
    records,
    totalPages,
    createRecord,
    updateRecord,
    deleteRecord,
    refetch
  } = useRecords(tableId, filterStatus, filterTags, sortBy, sortOrder)

  const handleCreate = async () => {
    const newRecord = await createRecord({
      title: 'New Post',
      content: '',
      status: 'draft',
      tags: [],
      scheduled_date: null
    })
    refetch()
  }

  const handleSchedule = (record: any) => {
    setSelectedRecord(record)
    setShowSchedule(true)
  }

  const handleScheduleConfirm = () => {
    setShowSchedule(false)
    setSelectedRecord(null)
    refetch()
  }

  const handleScheduleCancel = () => {
    setShowSchedule(false)
    setSelectedRecord(null)
  }

  if (loading) return <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>
  if (error) return <div style={{ padding: '20px', color: '#dc3545' }}>{error}</div>

  return (
    <div style={{ padding: '20px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Content Calendar</h2>
        <button onClick={handleCreate} style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Create Post
        </button>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <select
          value={filterStatus || ''}
          onChange={e => setFilterStatus(e.target.value || null)}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="scheduled">Scheduled</option>
          <option value="published">Published</option>
        </select>
        <select
          value={sortBy}
          onChange={e => setSortBy(e.target.value)}
          style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
        >
          <option value="created_at">Created At</option>
          <option value="scheduled_date">Scheduled Date</option>
          <option value="title">Title</option>
        </select>
        <button onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}>
          {sortOrder === 'asc' ? '↑' : '↓'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        {records.map(record => (
          <div key={record.id} style={{ padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px', border: '1px solid #dee2e6' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <h3 style={{ margin: 0 }}>{record.title}</h3>
              <span style={{
                padding: '4px 8px',
                borderRadius: '12px',
                fontSize: '12px',
                backgroundColor: record.status === 'published' ? '#28a745' : record.status === 'scheduled' ? '#ffc107' : '#6c757d',
                color: record.status === 'scheduled' ? '#000' : 'white'
              }}>
                {record.status}
              </span>
            </div>
            <p style={{ color: '#6c757d', fontSize: '14px' }}>{record.content}</p>
            <div style={{ display: 'flex', gap: '5px', marginBottom: '10px' }}>
              {record.tags?.map((tag: string) => (
                <span key={tag} style={{ padding: '2px 6px', backgroundColor: '#e9ecef', borderRadius: '4px', fontSize: '12px' }}>
                  {tag}
                </span>
              ))}
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button onClick={() => handleSchedule(record)} style={{ padding: '6px 12px', backgroundColor: '#17a2b8', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Schedule
              </button>
              <button onClick={() => updateRecord(record.id, { ...record, status: 'published' })} style={{ padding: '6px 12px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Publish
              </button>
              <button onClick={() => deleteRecord(record.id)} style={{ padding: '6px 12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', marginTop: '20px' }}>
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ padding: '8px 16px', borderRadius: '4px', border: '1px solid #ced4da', cursor: page === 1 ? 'not-allowed' : 'pointer', opacity: page === 1 ? 0.5 : 1 }}>
            Previous
          </button>
          <span style={{ padding: '8px' }}>Page {page} of {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} style={{ padding: '8px 16px', borderRadius: '4px', border: '1px solid #ced4da', cursor: page === totalPages ? 'not-allowed' : 'pointer', opacity: page === totalPages ? 0.5 : 1 }}>
            Next
          </button>
        </div>
      )}

      {showSchedule && selectedRecord && (
        <ScheduleModal
          recordId={selectedRecord.id}
          scheduledDate={selectedRecord.scheduled_date || ''}
          onSchedule={handleScheduleConfirm}
          onCancel={handleScheduleCancel}
        />
      )}
    </div>
  )
}