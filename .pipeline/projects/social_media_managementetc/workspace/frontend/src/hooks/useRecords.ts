import React, { useState, useEffect, useCallback } from 'react'
import { getRecords, createRecord, updateRecord, deleteRecord } from '../api'

interface UseRecordsReturn {
  records: any[]
  loading: boolean
  error: string | null
  totalPages: number
  page: number
  setPage: (page: number) => void
  createRecord: (data: any) => Promise<any>
  updateRecord: (id: number, data: any) => Promise<any>
  deleteRecord: (id: number) => Promise<void>
  refetch: () => void
}

export function useRecords(
  tableId: number,
  filterStatus: string | null = null,
  filterTags: string | null = null,
  sortBy: string = 'created_at',
  sortOrder: string = 'asc'
): UseRecordsReturn {
  const [records, setRecords] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(1)
  const [page, setPage] = useState(1)

  const fetchRecords = useCallback(async () => {
    if (!tableId) {
      setRecords([])
      setTotalPages(1)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        per_page: '20',
        sort_by: sortBy,
        sort_order: sortOrder
      })
      if (filterStatus) params.append('filter_status', filterStatus)
      if (filterTags) params.append('filter_tags', filterTags)
      
      const data = await getRecords(tableId, params.toString())
      setRecords(data.items || data)
      setTotalPages(data.total_pages || 1)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch records')
    } finally {
      setLoading(false)
    }
  }, [tableId, page, filterStatus, filterTags, sortBy, sortOrder])

  useEffect(() => {
    fetchRecords()
  }, [fetchRecords])

  const createNewRecord = async (data: any) => {
    setLoading(true)
    setError(null)
    try {
      const newRecord = await createRecord(tableId, data)
      setRecords(prev => [newRecord, ...prev])
      return newRecord
    } catch (err: any) {
      setError(err.message || 'Failed to create record')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const updateRecordData = async (id: number, data: any) => {
    setLoading(true)
    setError(null)
    try {
      const updatedRecord = await updateRecord(tableId, id, data)
      setRecords(prev => prev.map(record => record.id === id ? updatedRecord : record))
      return updatedRecord
    } catch (err: any) {
      setError(err.message || 'Failed to update record')
      throw err
    } finally {
      setLoading(false)
    }
  }

  const deleteRecordData = async (id: number) => {
    setLoading(true)
    setError(null)
    try {
      await deleteRecord(tableId, id)
      setRecords(prev => prev.filter(record => record.id !== id))
    } catch (err: any) {
      setError(err.message || 'Failed to delete record')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return {
    records,
    loading,
    error,
    totalPages,
    page,
    setPage,
    createRecord: createNewRecord,
    updateRecord: updateRecordData,
    deleteRecord: deleteRecordData,
    refetch: fetchRecords
  }
}