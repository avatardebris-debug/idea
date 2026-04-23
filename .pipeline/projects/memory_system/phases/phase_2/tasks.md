# Memory System - Phase 2: Memory Palace System - Task List

## Project Status: Phase 2 Planning

**Dependencies Met:**
- ✅ Phase 1 visualization interface complete (musical wheel, basic palace creator)
- ✅ Local storage persistence working
- ✅ Basic palace/room creation working

---

## Task 1: Spatial Memory Exercise Component
**What to Build:**
Create a spatial memory exercise component that allows users to place items into loci (rooms) and test their memory through recall.

**Files to Create:**
1. `src/components/MemoryPalace/SpatialExercise.tsx` - Main spatial memory exercise component
2. `src/components/MemoryPalace/SpatialExercise.css` - Styling for the exercise
3. `src/types/exercises.ts` - Exercise interfaces and types

**Acceptance Criteria:**
- [ ] Users can view all rooms/loci in a selected palace in grid layout
- [ ] Users can place items (text labels) into specific rooms
- [ ] Visual indicators show which rooms have items placed
- [ ] Exercise can transition to "recall mode" where items are hidden
- [ ] Users can click rooms to reveal items and test their memory
- [ ] Score tracking for correct/incorrect recalls
- [ ] Timer functionality for timed recall challenges
- [ ] Success/failure feedback with visual cues

---

## Task 2: Palace Template System
**What to Build:**
Create a template system that provides pre-built palace structures for users to start with.

**Files to Create:**
1. `src/utils/palaceTemplates.ts` - Template definitions and loading functions
2. `src/components/MemoryPalace/TemplateSelector.tsx` - UI component for selecting templates
3. `src/components/MemoryPalace/TemplateSelector.css` - Styling for template selection
4. Update `src/types/palace.ts` - Add Template interface

**Acceptance Criteria:**
- [ ] At least 3 different palace templates available:
  - Template 1: "Home Palace" - 5 rooms (living room, kitchen, bedroom, bathroom, garden)
  - Template 2: "Office Palace" - 6 rooms (reception, workspace, conference room, pantry, restroom, parking)
  - Template 3: "School Palace" - 8 rooms (entrance, hallway, classroom A, classroom B, library, cafeteria, gym, playground)
- [ ] Templates load with predefined room names and descriptions
- [ ] Users can select a template when creating a new palace
- [ ] Template selector displays template preview and room count
- [ ] Users can customize template rooms after selection
- [ ] Templates stored as JSON constants in template utils

---

## Task 3: Palace Export/Import System
**What to Build:**
Implement functionality to export palaces to JSON files and import them back.

**Files to Create:**
1. `src/utils/palaceExportImport.ts` - Export/import functions
2. `src/components/MemoryPalace/PalaceActions.tsx` - Export/Import action buttons
3. `src/components/MemoryPalace/PalaceActions.css` - Styling for action buttons
4. Update `src/utils/palaceUtils.ts` - Add export/import utilities

**Acceptance Criteria:**
- [ ] Users can export a single palace to JSON file
- [ ] Users can export all palaces as a single JSON file
- [ ] Exported JSON includes palace metadata (name, description, rooms, timestamps)
- [ ] Users can import palaces from JSON file
- [ ] Import validates JSON structure before importing
- [ ] Import handles conflicts (duplicate palace names, IDs)
- [ ] Import provides feedback on successful/failed imports
- [ ] Exported files use proper MIME type and filename conventions
- [ ] Import modal displays file contents before confirming import

---

## Task 4: Progress Tracking System
**What to Build:**
Create a comprehensive progress tracking system for palace-based exercises.

**Files to Create:**
1. `src/utils/progressTracking.ts` - Progress tracking utilities
2. `src/components/MemoryPalace/ProgressTracker.tsx` - Progress display component
3. `src/components/MemoryPalace/ProgressTracker.css` - Progress visualization styling
4. Update `src/types/palace.ts` - Add PalaceExerciseSession interface

**Acceptance Criteria:**
- [ ] Track exercise sessions (palace ID, exercise type, timestamp, duration)
- [ ] Track accuracy metrics (correct recalls, total attempts)
- [ ] Track improvement over time (accuracy trend line)
- [ ] Display progress dashboard with:
  - Total exercise sessions completed
  - Average accuracy percentage
  - Best performance streak
  - Most practiced palace
- [ ] Progress data stored in localStorage
- [ ] Progress charts (simple line/bar visualization using CSS)
- [ ] Progress can be reset for individual palaces
- [ ] Progress exports along with palace data

---

## Task 5: Enhanced Palace Navigation
**What to Build:**
Improve palace navigation with better UI/UX for browsing and managing palaces.

**Files to Create:**
1. `src/components/MemoryPalace/PalaceNavigator.tsx` - Enhanced navigation component
2. `src/components/MemoryPalace/PalaceNavigator.css` - Navigation styling
3. Update `src/components/MemoryPalace/PalaceCreator.tsx` - Integrate new navigation

**Acceptance Criteria:**
- [ ] Palace list shows additional metadata (room count, last used, progress summary)
- [ ] Search/filter functionality for palaces by name
- [ ] Sort options (created date, last used, room count, name)
- [ ] Quick navigation to recently used palaces
- [ ] Palace detail view shows rooms with item counts
- [ ] Keyboard shortcuts for navigation (arrow keys, enter to select)
- [ ] Responsive navigation that works on mobile
- [ ] Loading states for palace operations

---

## Task 6: Palace Exercise Runner
**What to Build:**
Create a unified exercise runner that can launch different palace-based exercises.

**Files to Create:**
1. `src/components/MemoryPalace/ExerciseRunner.tsx` - Exercise launcher and controller
2. `src/components/MemoryPalace/ExerciseRunner.css` - Runner styling
3. `src/types/exercises.ts` - Exercise configuration interfaces

**Acceptance Criteria:**
- [ ] Exercise runner can launch spatial memory exercises
- [ ] Exercise runner can launch recall mode exercises
- [ ] Exercise runner displays exercise type and instructions
- [ ] Exercise runner tracks exercise session start/end
- [ ] Exercise runner provides summary after completion
- [ ] Exercise runner shows progress after each session
- [ ] Users can select difficulty level (easy, medium, hard)
- [ ] Exercise runner integrates with progress tracking system

---

## Task 7: Integration Tests
**What to Create:**
Comprehensive tests for Phase 2 functionality.

**Files to Create:**
1. `tests/palaceSpatialExercise.test.tsx` - Spatial exercise tests
2. `tests/palaceTemplates.test.ts` - Template system tests
3. `tests/palaceExportImport.test.ts` - Export/import tests
4. `tests/progressTracking.test.ts` - Progress tracking tests
5. `tests/palaceIntegration.test.tsx` - Integration tests

**Acceptance Criteria:**
- [ ] 30+ test cases total
- [ ] Test spatial exercise item placement and recall
- [ ] Test all 3 palace templates load correctly
- [ ] Test export generates valid JSON
- [ ] Test import validates and handles errors
- [ ] Test progress tracking updates correctly
- [ ] Test navigation search and filter functionality
- [ ] Test exercise runner lifecycle
- [ ] Achieve 75%+ code coverage for Phase 2 components

---

## Success Metrics Summary

### Must Have (All Required):
- [x] Users can create, edit, and delete memory palaces (Phase 1 + Task 5)
- [x] Spatial memory exercises with loci placement work smoothly (Task 1, Task 6)
- [x] Palace navigation is intuitive and responsive (Task 5)
- [x] Users can track their progress on palace-based tasks (Task 4)
- [x] Export/import palaces to JSON format works (Task 3)
- [x] At least 3 different palace templates available (Task 2)

### Quality Standards:
- All components use TypeScript with proper type definitions
- Responsive design works on desktop and mobile
- Performance optimized for smooth interactions
- Comprehensive error handling
- Clear inline documentation via JSDoc comments
- Clean separation of concerns (components, utils, types)

---

## Implementation Order

1. **Task 1** - Spatial Memory Exercise (core functionality)
2. **Task 2** - Palace Templates (content foundation)
3. **Task 3** - Export/Import (data portability)
4. **Task 4** - Progress Tracking (analytics)
5. **Task 5** - Enhanced Navigation (UX improvements)
6. **Task 6** - Exercise Runner (unified interface)
7. **Task 7** - Integration Tests (quality assurance)

---

## Notes

- All components should follow React best practices and TypeScript conventions
- Use existing CSS variables from global styles for consistency
- Reuse existing utilities where possible (palaceUtils)
- Ensure backward compatibility with Phase 1 data structures
- Test on both desktop and mobile devices
- Consider accessibility (ARIA labels, keyboard navigation)

**Status:** Ready for Phase 2 implementation
