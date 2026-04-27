# Social Media Management Application

A React-based frontend for managing social media content across multiple workspaces, with support for scheduling, filtering, and multi-platform integration.

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── api.ts              # API client with all endpoint functions
│   ├── components/
│   │   ├── WorkspaceManager.tsx    # Workspace creation and selection
│   │   ├── TableManager.tsx        # Table creation and management
│   │   ├── ContentGrid.tsx         # Grid view of content records
│   │   ├── CalendarView.tsx        # Calendar/card view of content
│   │   ├── FilterBar.tsx           # Filtering and sorting controls
│   │   ├── ViewToggle.tsx          # Grid/Calendar view switcher
│   │   ├── CellEditor.tsx          # Inline cell editing
│   │   ├── ScheduleModal.tsx       # Content scheduling modal
│   │   └── ConnectAccount.tsx      # Social account connection
│   └── hooks/
│       ├── useWorkspaces.ts        # Workspace management hook
│       ├── useTables.ts            # Table management hook
│       └── useRecords.ts           # Record CRUD operations hook
```

## 🔌 API Reference

### Base Configuration
```typescript
const API_BASE = '/api'
```

### Workspaces

#### Get Workspaces
```typescript
async function getWorkspaces(): Promise<{ items: Workspace[] }>
```
Retrieves all workspaces for the current user.

#### Create Workspace
```typescript
async function createWorkspace(data: {
  name: string
  description?: string
}): Promise<Workspace>
```
Creates a new workspace.

### Tables

#### Get Tables
```typescript
async function getTables(workspaceId: number): Promise<{ items: Table[] }>
```
Retrieves all tables in a workspace.

#### Create Table
```typescript
async function createTable(data: {
  workspace_id: number
  name: string
  column_definitions: Array<{ name: string; type: string }>
}): Promise<Table>
```
Creates a new table with custom columns.

### Records

#### Get Records
```typescript
async function getRecords(
  tableId: number,
  params: URLSearchParams
): Promise<{ items: Record[]; total_pages: number }>
```
Retrieves records with pagination and filtering.

#### Create Record
```typescript
async function createRecord(data: {
  table_id: number
  [key: string]: any
}): Promise<Record>
```
Creates a new record in a table.

#### Update Record
```typescript
async function updateRecord(
  recordId: number,
  data: { [key: string]: any }
): Promise<Record>
```
Updates an existing record.

#### Delete Record
```typescript
async function deleteRecord(recordId: number): Promise<void>
```
Deletes a record.

### Scheduling

#### Schedule Content
```typescript
async function scheduleContent(data: {
  record_id: number
  scheduled_date: string
}): Promise<void>
```
Schedules content for future publication.

#### Cancel Schedule
```typescript
async function cancelSchedule(recordId: number): Promise<void>
```
Cancels a scheduled post.

### Account Connections

#### Get Connected Accounts
```typescript
async function getConnectedAccounts(): Promise<{ items: Account[] }>
```
Retrieves all connected social media accounts.

#### Connect Account
```typescript
async function connectAccount(platform: 'twitter' | 'instagram'): Promise<void>
```
Initiates OAuth flow for connecting a social account.

## 🎣 Custom Hooks

### useWorkspaces
```typescript
const {
  workspaces,
  loading,
  error,
  createWorkspace,
  refetch
} = useWorkspaces()
```
**Returns:**
- `workspaces`: Array of workspace objects
- `loading`: Boolean loading state
- `error`: Error message or null
- `createWorkspace`: Function to create a new workspace
- `refetch`: Function to refresh data

### useTables
```typescript
const {
  tables,
  loading,
  error,
  createTable,
  refetch
} = useTables(workspaceId)
```
**Parameters:**
- `workspaceId`: ID of the workspace

**Returns:**
- `tables`: Array of table objects
- `loading`: Boolean loading state
- `error`: Error message or null
- `createTable`: Function to create a new table
- `refetch`: Function to refresh data

### useRecords
```typescript
const {
  records,
  totalPages,
  createRecord,
  updateRecord,
  deleteRecord,
  refetch
} = useRecords(
  tableId,
  filterStatus,
  filterTags,
  sortBy,
  sortOrder
)
```
**Parameters:**
- `tableId`: ID of the table
- `filterStatus`: Status filter (draft, scheduled, published)
- `filterTags`: Tag filter string
- `sortBy`: Sort field (created_at, scheduled_date, title)
- `sortOrder`: Sort order (asc, desc)

**Returns:**
- `records`: Array of record objects
- `totalPages`: Total number of pages
- `createRecord`: Function to create a new record
- `updateRecord`: Function to update a record
- `deleteRecord`: Function to delete a record
- `refetch`: Function to refresh data

## 🧩 Components

### WorkspaceManager
Manages workspace creation and selection.

**Props:**
- `onSelectWorkspace`: Callback when workspace is selected

**Features:**
- Create new workspaces
- Select existing workspaces
- Error handling

### TableManager
Manages table creation and selection within a workspace.

**Props:**
- `workspaceId`: Current workspace ID
- `onSelectTable`: Callback when table is selected

**Features:**
- Create tables with custom columns
- Column type support (text, number, date, boolean)
- Table selection

### ContentGrid
Grid view for displaying content records.

**Props:**
- `tableId`: Current table ID
- `loading`: Loading state
- `error`: Error message
- `columns`: Table column definitions

**Features:**
- Grid layout display
- Inline cell editing
- Status badges
- Tag display

### CalendarView
Calendar/card view for content scheduling.

**Props:**
- `tableId`: Current table ID
- `loading`: Loading state
- `error`: Error message

**Features:**
- Card-based layout
- Status filtering
- Sorting controls
- Pagination

### FilterBar
Filtering and sorting controls.

**Props:**
- `onFilterChange`: Callback for filter changes
- `onSortChange`: Callback for sort changes

**Features:**
- Status filter (draft, scheduled, published)
- Tag filter
- Sort by field
- Sort order toggle

### ViewToggle
Switch between grid and calendar views.

**Props:**
- `currentView`: Current view mode ('grid' | 'calendar')
- `onViewChange`: Callback for view changes

### CellEditor
Inline cell editing component.

**Props:**
- `value`: Current cell value
- `onSave`: Callback when saved
- `onCancel`: Callback when cancelled

**Features:**
- Auto-focus on mount
- Enter to save
- Escape to cancel
- Blur to save

### ScheduleModal
Modal for scheduling content.

**Props:**
- `recordId`: Record to schedule
- `scheduledDate`: Current scheduled date
- `onSchedule`: Callback on successful schedule
- `onCancel`: Callback to cancel

**Features:**
- Date and time picker
- Schedule confirmation
- Cancel scheduled posts
- Success feedback

### ConnectAccount
Social media account connection.

**Features:**
- Twitter OAuth connection
- Instagram OAuth connection
- Modal interface

## 🎨 Styling

All components use inline styles for simplicity. Key style patterns:

```typescript
// Card container
{
  padding: '15px',
  backgroundColor: 'white',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
}

// Button variants
backgroundColor: '#007bff'  // Primary
backgroundColor: '#28a745'  // Success
backgroundColor: '#dc3545'  // Danger
backgroundColor: '#6c757d'  // Secondary

// Status badges
backgroundColor: '#28a745'  // Published
backgroundColor: '#ffc107'  // Scheduled
backgroundColor: '#6c757d'  // Draft
```

## 🚀 Usage Example

```typescript
import { WorkspaceManager } from './components/WorkspaceManager'
import { TableManager } from './components/TableManager'
import { ContentGrid } from './components/ContentGrid'
import { CalendarView } from './components/CalendarView'
import { ViewToggle } from './components/ViewToggle'

function App() {
  const [currentWorkspace, setCurrentWorkspace] = useState(null)
  const [currentTable, setCurrentTable] = useState(null)
  const [view, setView] = useState('grid')

  return (
    <div>
      <WorkspaceManager onSelectWorkspace={setCurrentWorkspace} />
      
      {currentWorkspace && (
        <TableManager
          workspaceId={currentWorkspace.id}
          onSelectTable={setCurrentTable}
        />
      )}
      
      {currentTable && (
        <>
          <ViewToggle currentView={view} onViewChange={setView} />
          {view === 'grid' ? (
            <ContentGrid tableId={currentTable.id} />
          ) : (
            <CalendarView tableId={currentTable.id} />
          )}
        </>
      )}
    </div>
  )
}
```

## 📊 Data Models

### Workspace
```typescript
interface Workspace {
  id: number
  name: string
  description?: string
  created_at: string
}
```

### Table
```typescript
interface Table {
  id: number
  name: string
  workspace_id: number
  column_definitions: Array<{
    name: string
    type: string
  }>
  created_at: string
}
```

### Record
```typescript
interface Record {
  id: number
  table_id: number
  [key: string]: any  // Dynamic columns based on table
  created_at: string
  updated_at: string
}
```

### Account
```typescript
interface Account {
  id: number
  platform: 'twitter' | 'instagram'
  username: string
  connected_at: string
}
```

## 🔐 Authentication

The application assumes authenticated users. All API calls include authentication headers automatically via the API client.

## 📱 Responsive Design

Components use flexible layouts with:
- Flexbox for alignment
- Grid for content display
- Media query considerations in inline styles
- Wrap behaviors for smaller screens

## 🧪 Testing Recommendations

1. **Unit Tests**: Test individual components with mocked props
2. **Integration Tests**: Test hook behavior with mocked API calls
3. **E2E Tests**: Test complete user flows (create workspace → create table → create content → schedule)

## 🐛 Known Limitations

1. Inline styles limit CSS optimization
2. No formal error boundaries
3. Limited accessibility features (ARIA labels)
4. No form validation beyond basic checks
5. OAuth flow is simulated (alerts instead of redirects)

## 📝 Future Enhancements

1. Add drag-and-drop for content reordering
2. Implement real-time updates with WebSockets
3. Add content preview functionality
4. Implement analytics dashboard
5. Add bulk operations (delete, publish, schedule)
6. Add content templates
7. Implement collaboration features (comments, mentions)
