const API_BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || 'Request failed')
  }

  if (response.status === 204) return null as T
  return response.json()
}

export async function getWorkspaces() {
  return request('/workspaces/')
}

export async function createWorkspace(data: { name: string; description?: string }) {
  return request('/workspaces/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getTables(workspaceId: number) {
  return request(`/tables/?workspace_id=${workspaceId}`)
}

export async function createTable(data: { workspace_id: number; name: string; column_definitions: any[] }) {
  return request('/tables/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getRecords(tableId: number, params: URLSearchParams) {
  return request(`/tables/${tableId}/records/?${params.toString()}`)
}

export async function createRecord(data: Record<string, any>) {
  return request('/tables/0/records/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateRecord(id: number, data: Partial<Record<string, any>>) {
  return request(`/records/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteRecord(id: number) {
  return request(`/records/${id}`, { method: 'DELETE' })
}

export async function connectAccount(data: { workspace_id: number; platform: string; access_token: string; refresh_token: string; expires_in: number }) {
  return request('/accounts/connect/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function disconnectAccount(data: { workspace_id: number; platform: string }) {
  return request('/accounts/disconnect/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getAnalytics(workspaceId: number, period: string) {
  return request(`/analytics/?workspace_id=${workspaceId}&period=${period}`)
}

export async function scheduleContent(data: { record_id: number; scheduled_date: string }) {
  return request('/schedule/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function cancelSchedule(data: { record_id: number }) {
  return request('/schedule/cancel/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}