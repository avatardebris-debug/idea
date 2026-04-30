# Integration Prompts for 80/20 Learning Extraction Pipeline

This document contains the prompts used for integrating Phase 1 summaries with Phase 2 extraction.

## Overview

The integration layer connects Phase 1 (Topic Analysis and Source Gathering) with Phase 2 (80/20 Extraction). It provides the context and structure needed for the extraction components to work effectively.

## Prompt Templates

### Content Summary Integration

When integrating Phase 1 summaries, the following structure is used:

```
Topic: {topic_name}
Content Summary: {summary_text}
Key Points: {key_points}
Source Summaries: {source_summaries}
```

### Vital Concepts Extraction Context

The vital concepts extractor receives:
- Topic name for context
- Content summary with main ideas
- Key points from the content
- Optional source summaries for cross-referencing

### Learning Patterns Extraction Context

The pattern generator receives:
- Topic name for domain context
- Content summary for pattern identification
- Vital concepts to analyze for compression opportunities
- Source summaries for additional pattern detection

### Learning Outline Generation Context

The outline generator receives:
- Topic name for structure context
- Content summary for module identification
- Vital concepts for sequencing
- Pattern extraction results for optimization opportunities

## Integration Flow

1. **Input**: Phase 1 outputs (TopicSummary, SourceSummary objects)
2. **Processing**: Extractors receive structured content summaries
3. **Output**: ExtractionResult with vital concepts, patterns, and outline

## Configuration

The integration layer uses the following configuration:
- API key for LLM access
- Model selection (default: gpt-4o)
- Temperature for response variability (default: 0.5)

## Error Handling

The integration layer includes validation to ensure:
- Vital concepts are extracted (minimum 3 recommended)
- Compression opportunities are identified
- Learning modules are structured properly (minimum 2 recommended)
