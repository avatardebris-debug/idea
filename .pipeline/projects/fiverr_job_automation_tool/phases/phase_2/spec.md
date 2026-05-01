## Phase 2: Fiverr Scraping & Job Discovery
**Goal**: Build the actual Fiverr scraper — login, session management, buyer request page scraping, job search, and raw data extraction.
**Deliverable**: `scraper.py` that can log in, navigate to buyer requests, extract job listings with title/description/budget/deadline, and export as structured JSON.
**Tasks**:
- Implement Playwright/Selenium login with session cookie persistence
- Scrape buyer requests page (pagination support)
- Parse job cards: title, description, budget range, posted time, buyer info
- Implement keyword-based job filtering
- Write integration tests with mock HTML fixtures
- Add rate limiting and random delays to avoid detection

