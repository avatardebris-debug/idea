import React, { useState, useEffect } from 'react'
import { getTables, createTable } from '../api'

export function useTables(workspaceId: number | null) {
  const [tables, setTables] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTables = async () => {
    if (!workspaceId) {
      setTables([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await getTables(workspaceId)
      setTables(data.items || data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tables')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTables()
  }, [workspaceId])

  const createNewTable = async (name: string, columnDefinitions: any[]) => {
    if (!workspaceId) return null
    setLoading(true)
    setError(null)
    try {
      const newTable = await createTable({ workspace_id: workspaceId, name, column_definitions: columnDefinitions })
      setTables(prev => [...prev, newTable])
      return newTable
    } catch (err: any) {
      setError(err.message || 'Failed to create table')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { tables, loading, error, createTable: createNewTable }
}