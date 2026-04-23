import React, { useState, useEffect } from 'react'
import { getWorkspaces, createWorkspace } from '../api'

export function useWorkspaces() {
  const [workspaces, setWorkspaces] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWorkspaces = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getWorkspaces()
      setWorkspaces(data.items || data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch workspaces')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkspaces()
  }, [])

  const createNewWorkspace = async (name: string, description?: string) => {
    setLoading(true)
    setError(null)
    try {
      const newWorkspace = await createWorkspace({ name, description })
      setWorkspaces(prev => [...prev, newWorkspace])
      return newWorkspace
    } catch (err: any) {
      setError(err.message || 'Failed to create workspace')
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { workspaces, loading, error, createWorkspace: createNewWorkspace }
}