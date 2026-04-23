## Phase 1: Core Video Database (Smallest Useful Thing)

**Goal**: A working Airtable-like grid interface for organizing video metadata.

**Description**: Build the foundational data model and UI for managing video content as structured records. Each "video" is a row with fields like title, description, status, tags, publish date, thumbnail URL, etc. Users can create custom fields (like Airtable), filter, sort, and search their video library. This is the core data layer that everything else builds on.

**Deliverable**:
- Database schema for `videos` table with extensible custom fields
- CRUD API endpoints for video records (REST)
- Grid UI component with inline editing, filtering, and sorting
- Field type system (text, date, select, checkbox, number, URL, tags)
- Sample data seeding for demo

**Dependencies**: None (foundation phase)

**Success Criteria**:
- [ ] Can create, read, update, and delete video records via API
- [ ] Can add custom fields to the video table and see them in the grid
- [ ] Can filter records by any field and sort by any column
- [ ] Grid UI renders 100+ rows with inline editing without lag
- [ ] All API endpoints have input validation and error handling

---