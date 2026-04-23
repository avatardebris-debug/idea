# Phase 2: YouTube Suite Integration

## Tasks

### Week 1: OAuth & Channel Connection
- [ ] Set up OAuth 2.0 flow for YouTube API access
- [ ] Build channel connection UI (connect/disconnect button)
- [ ] Store and refresh OAuth tokens securely
- [ ] Fetch and display channel info (name, avatar, subscriber count)

### Week 2: Video Sync Engine
- [ ] Implement video sync (pull all existing channel videos)
- [ ] Map YouTube video metadata to platform's video schema
- [ ] Handle sync conflicts (local edits vs YouTube changes)
- [ ] Implement incremental sync (only changed videos)
- [ ] Handle deleted/removed YouTube videos gracefully
- [ ] Add sync status indicator in UI

### Week 3: YouTube Upload & Stats
- [ ] Build YouTube upload endpoint (create video with metadata)
- [ ] Implement thumbnail upload/sync
- [ ] Set up periodic stats fetch (views, likes, comments)
- [ ] Build channel stats dashboard
- [ ] Add manual sync trigger button

### Acceptance Criteria
- [ ] User can connect their YouTube channel via OAuth
- [ ] All existing channel videos are synced into the platform within 5 minutes
- [ ] New videos created in the platform can be published to YouTube
- [ ] Channel stats update automatically (every 15 min or on demand)
- [ ] Sync handles deleted/removed YouTube videos gracefully
