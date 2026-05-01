## Phase 2: Real Course Discovery & Ranking
**Goal**: Implement real Udemy course search (via Udemy API or scraper), full ranking engine, and course detail enrichment.
**Deliverable**: `udemy_client.py` that fetches real courses, ranker that scores them, CLI output showing top N ranked results with details.
**Tasks**:
- Implement Udemy REST API client (free API: api.udemy.com/api-2.0/courses/)
- Handle auth (client_id + client_secret config)
- Fetch courses by keyword, parse response into Course models
- Build multi-factor ranker: weighted score of rating, num_reviews, price, duration
- Add category/subcategory filtering
- Cache API results to SQLite to avoid re-fetching
- Update CLI: `search <topic> --top N --min-rating X --max-price Y`
- Integration tests with recorded API fixtures

