# Video Management Platform — Master Plan

## Idea Summary
An Airtable-like platform for managing video content at scale. Features AI-assisted content generation, scheduling, and YouTube Suite integration. The core value proposition is a centralized workspace where creators can organize, generate, schedule, and analyze video content across YouTube.

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Web)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Video DB │  │ Schedule │  │ Analytics│          │
│  │ (Grid)   │  │ Calendar │  │ Dashboard│          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│                   Backend API                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Videos   │  │ Schedules│  │ Analytics│          │
│  │ Service  │  │ Service  │  │ Service  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────────┐
│                 External Integrations                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ YouTube  │  │ AI/LLM   │  │ Storage  │          │
│  │ API      │  │ Service  │  │ (GCS/S3) │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
```

**Tech Stack**: Python/FastAPI backend, SQLite (dev) → PostgreSQL (prod), React frontend, YouTube Data API v3, OpenAI/LLM for AI generation.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube API rate limits | Medium | Implement caching, batch operations, and quota monitoring |
| AI generation costs at scale | High | Use tiered models (cheap model for drafts, expensive for polish), caching |
| Video upload bandwidth | Medium | Support external storage (S3/GCS), chunked uploads |
| Complex state management (draft → published) | High | Finite state machine for video lifecycle, clear transitions |
| Multi-user collaboration | Medium | Row-level permissions, workspace-scoped data |

---

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

## Phase 2: YouTube Suite Integration

**Goal**: Connect the platform to real YouTube data so videos are not just local records.

**Description**: Integrate with YouTube Data API v3 to sync channel data, video metadata, and upload capabilities. Users authenticate their YouTube channel, and the platform pulls in existing videos, channel stats, and allows creating new videos directly from the platform. This bridges the gap between a local organizer and a real publishing workflow.

**Deliverable**:
- OAuth 2.0 YouTube channel connection flow
- Video sync engine (pull existing videos, thumbnails, stats)
- YouTube upload endpoint (create video with metadata via API)
- Channel stats dashboard (subscribers, views, revenue)
- Sync status indicator and conflict resolution

**Dependencies**: Phase 1 (data model for storing synced video records)

**Success Criteria**:
- [ ] User can connect their YouTube channel via OAuth
- [ ] All existing channel videos are synced into the platform within 5 minutes
- [ ] New videos created in the platform can be published to YouTube
- [ ] Channel stats update automatically (every 15 min or on demand)
- [ ] Sync handles deleted/removed YouTube videos gracefully

---

## Phase 3: Content Scheduling System

**Goal**: Plan and automate video publishing with a calendar-based scheduler.

**Description**: Build a scheduling layer on top of the video database. Users can set publish dates/times for videos, and the system handles the automated publishing workflow. Includes a calendar view, recurring schedule templates, timezone handling, and queue management. Videos go through a status pipeline: Draft → Scheduled → Ready → Published → Failed.

**Deliverable**:
- Calendar UI component for scheduling videos
- Scheduler service with cron/async task runner
- Video status state machine (Draft → Scheduled → Publishing → Published/Failed)
- Recurring schedule templates (e.g., "every Tuesday at 5 PM")
- Publish queue with priority and conflict detection
- Email/notification on publish success/failure

**Dependencies**: Phase 1 (video records), Phase 2 (YouTube upload capability)

**Success Criteria**:
- [ ] Can schedule a video for a future date/time via calendar UI
- [ ] Scheduled videos are automatically published to YouTube at the correct time
- [ ] Scheduler handles timezone differences correctly
- [ ] Can create recurring schedules (daily/weekly/monthly)
- [ ] Publish failures are retried (3 attempts) and user is notified
- [ ] Calendar view shows all scheduled videos with color coding

---

## Phase 4: AI Content Generation

**Goal**: AI-assisted content creation to scale video production.

**Description**: Integrate AI models to generate video-related content at scale. This includes video titles, descriptions, tags, hashtags, thumbnail text overlays, and even script outlines. The AI understands the channel's niche and style (learned from existing content) and generates on-brand content. Users can generate content for a single video or batch-generate for an entire week of content.

**Deliverable**:
- AI content generation API (titles, descriptions, tags, hashtags)
- "Channel style" learning from existing content history
- Batch generation workflow (generate a week of content in one click)
- Content editing interface with AI suggestions
- Thumbnail text overlay generator
- Content quality scoring (SEO score, engagement prediction)

**Dependencies**: Phase 1 (access to video metadata as context), Phase 2 (existing content as training context)

**Success Criteria**:
- [ ] AI-generated titles match channel's existing style (evaluated by creator)
- [ ] Can generate 30 video descriptions in under 2 minutes
- [ ] Generated tags include relevant SEO keywords (verified against YouTube search)
- [ ] Batch generation produces coherent weekly content calendar
- [ ] Content quality score correlates with actual video performance (r > 0.5)

---

## Phase 5: Analytics Dashboard & Insights

**Goal**: Comprehensive analytics to track video performance and guide content strategy.

**Description**: Build an analytics layer that pulls YouTube performance data (views, watch time, CTR, subscriber growth, revenue) and presents it in actionable dashboards. Includes video-level analytics, channel-level trends, content performance comparisons, and AI-powered insights (e.g., "Your tutorial videos get 3x more watch time than vlogs — consider producing more tutorials").

**Deliverable**:
- Video performance dashboard (views, CTR, watch time, engagement over time)
- Channel trend analytics (growth, revenue, audience demographics)
- Content comparison tool (side-by-side video performance)
- AI-powered content insights and recommendations
- Export analytics to CSV/PDF
- Custom report builder

**Dependencies**: Phase 2 (YouTube stats data), Phase 1 (video metadata for correlation)

**Success Criteria**:
- [ ] Dashboard loads within 2 seconds for channels with 1000+ videos
- [ ] All YouTube analytics metrics are accurate (compared to YouTube Studio)
- [ ] AI insights are actionable (creator finds at least 1 useful recommendation per session)
- [ ] Can create and export custom reports
- [ ] Trend data updates within 1 hour of YouTube data refresh

---

## Phase Summary

| Phase | Name | Duration (est.) | Key Value |
|-------|------|-----------------|-----------|
| 1 | Core Video Database | 2 weeks | Foundation — the Airtable-like grid |
| 2 | YouTube Integration | 2 weeks | Real data — connects to YouTube |
| 3 | Content Scheduling | 2 weeks | Automation — schedule & publish |
| 4 | AI Content Generation | 3 weeks | Scale — AI-assisted creation |
| 5 | Analytics Dashboard | 2 weeks | Intelligence — data-driven decisions |

**Total estimated timeline**: ~11 weeks

## Post-Phase Considerations (Future)
- Multi-channel management (manage multiple YouTube channels from one workspace)
- Team collaboration (roles, permissions, content approval workflows)
- Video editing integration (connect to editing tools like Descript, Premiere)
- Cross-platform publishing (expand to TikTok, Instagram, etc.)
- Monetization features (ad revenue tracking, sponsor management)
