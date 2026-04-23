# Phase 3: Content Scheduling System

## Tasks

### Week 1: Scheduler Backend
- [ ] Design video status state machine: Draft → Scheduled → Publishing → Published/Failed
- [ ] Implement scheduler service with async task runner (Celery/ARQ)
- [ ] Build API for scheduling videos (set date/time)
- [ ] Implement publish queue with priority handling
- [ ] Add timezone support for all scheduling operations
- [ ] Build retry logic (3 attempts on failure)

### Week 2: Calendar UI & Templates
- [ ] Build calendar view component for scheduling
- [ ] Implement drag-and-drop scheduling on calendar
- [ ] Add color coding for video status
- [ ] Build recurring schedule templates (daily/weekly/monthly)
- [ ] Add publish queue management UI
- [ ] Implement conflict detection (double-scheduling)

### Week 3: Notifications & Polish
- [ ] Add email notifications for publish success/failure
- [ ] Build publish history log
- [ ] Add manual publish trigger
- [ ] Implement schedule preview (see upcoming week)
- [ ] Write integration tests for scheduler

### Acceptance Criteria
- [ ] Can schedule a video for a future date/time via calendar UI
- [ ] Scheduled videos are automatically published to YouTube at the correct time
- [ ] Scheduler handles timezone differences correctly
- [ ] Can create recurring schedules (daily/weekly/monthly)
- [ ] Publish failures are retried (3 attempts) and user is notified
- [ ] Calendar view shows all scheduled videos with color coding
