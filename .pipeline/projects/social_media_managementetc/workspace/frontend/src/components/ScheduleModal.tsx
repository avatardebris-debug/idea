import React, { useState, useEffect } from 'react'
import { scheduleContent, cancelSchedule } from '../api'

interface ScheduleProps {
  recordId: number
  scheduledDate: string
  onSchedule: () => void
  onCancel: () => void
}

export function ScheduleModal({ recordId, scheduledDate, onSchedule, onCancel }: ScheduleProps) {
  const [date, setDate] = useState(scheduledDate)
  const [time, setTime] = useState('12:00')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleSchedule = async () => {
    if (!date || !time) {
      setError('Date and time are required')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const scheduledDateTime = `${date}T${time}:00`
      await scheduleContent({ record_id: recordId, scheduled_date: scheduledDateTime })
      setSuccess(true)
      setTimeout(() => {
        onSchedule()
      }, 1000)
    } catch (err: any) {
      setError(err.message || 'Failed to schedule content')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    setLoading(true)
    setError(null)
    try {
      await cancelSchedule(recordId)
      onCancel()
    } catch (err: any) {
      setError(err.message || 'Failed to cancel schedule')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div style={{ color: '#28a745', fontSize: '24px', marginBottom: '10px' }}>✓</div>
        <h3>Scheduled Successfully!</h3>
        <p>Content will be posted at {date} at {time}</p>
      </div>
    )
  }

  return (
    <div style={{ padding: '20px' }}>
      <h3>Schedule Content</h3>
      {error && <div style={{ padding: '10px', backgroundColor: '#f8d7da', color: '#721c24', borderRadius: '4px', marginBottom: '10px' }}>{error}</div>}
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>Date:</label>
        <input
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          min={new Date().toISOString().split('T')[0]}
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
        />
      </div>
      
      <div style={{ marginBottom: '15px' }}>
        <label style={{ display: 'block', marginBottom: '5px' }}>Time:</label>
        <input
          type="time"
          value={time}
          onChange={e => setTime(e.target.value)}
          style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ced4da' }}
        />
      </div>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={handleSchedule}
          disabled={loading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1
          }}
        >
          {loading ? 'Scheduling...' : 'Schedule'}
        </button>
        <button
          onClick={handleCancel}
          disabled={loading}
          style={{
            padding: '8px 16px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer'
          }}
        >
          Cancel
        </button>
      </div>
    </div>
  )
}