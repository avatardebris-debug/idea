## Phase 2: 80/20 Vital Extraction & Outline Generation

**Status**: PENDING

### Description
Implement the critical 80/20 extraction engine that identifies the vital 20% of content that delivers 80% of the learning value, and generate structured outlines for efficient learning.

### Deliverable
- `extraction/eighty_twenty/vital_extractor.py` - Extracts most important concepts
- `extraction/outline/outline_generator.py` - Creates learning outlines
- `extraction/patterns/learning_patterns.py` - Identifies common learning patterns
- Integration with Phase 1 summaries

### Dependencies
- Phase 1 (source summaries)

### Success Criteria
- [x] Can identify and extract core concepts from summaries
- [x] Can rank concepts by importance/impact
- [x] Can generate hierarchical learning outlines
- [x] Can identify prerequisite relationships between concepts
- [x] Can flag "must-know" vs "nice-to-know" content
- [x] Can handle different topic types (technical, conceptual, skill-based)

### Technical Notes
- Use frequency analysis + semantic importance scoring
- Track concept co-occurrence to identify relationships
- Generate both linear and concept-map style outlines
- Allow user feedback to improve extraction accuracy

---

