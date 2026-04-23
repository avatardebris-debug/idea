# Scott Adams Bot / LLM Fine-Tuning — Master Plan

## Idea Summary
Build a bot that generates content (blog posts, tweets, LinkedIn-style posts) in Scott Adams' distinctive writing style — blending business philosophy, contrarian thinking, humor, and the "Stack of Luck" framework. The bot will be powered by either prompt-engineering with style few-shot examples or fine-tuning an open-weight LLM on a curated corpus of his writing.

## Architecture Notes
- **Corpus collection**: Scrape/crawl Scott Adams' blog (scottadamsslog.com), books, tweets, and interviews
- **Style analysis**: Extract stylistic features (sentence length, rhetorical devices, humor patterns, recurring themes, contrarian framing)
- **Two parallel tracks**:
  1. **Prompt-engineering track**: Curate few-shot examples + style prompt templates → test with GPT-4/Claude
  2. **Fine-tuning track**: Curate training corpus → LoRA fine-tune an open-weight model (e.g., Llama 3, Mistral)
- **Content generator**: Unified interface that produces text in the target style
- **Evaluation**: Style similarity metrics, human evaluation, engagement prediction

## Risks
- **Copyright**: Scott Adams' writing is copyrighted. Training corpus must be used only for personal/educational purposes (fair use). Cannot redistribute the corpus or the fine-tuned model commercially without permission.
- **Style vs. substance**: The bot may replicate surface style but miss the underlying reasoning quality. Need to evaluate both.
- **Fine-tuning quality**: A single-author fine-tune may overfit to idiosyncrasies. Need a balanced corpus and regularization.
- **Evaluation subjectivity**: Style matching is hard to quantify. Will need both automated metrics and human judges.

---

## Phase 1: Corpus Collection & Style Analysis (Smallest Useful Thing)

**Description**: Collect a representative corpus of Scott Adams' writing and perform initial style analysis. This produces a curated dataset and a style profile that informs all downstream work.

**Deliverable**:
- Curated corpus of 500-1000 writing samples (blog posts, tweets, book excerpts) in a structured format (JSONL with text, metadata, source)
- Style analysis report documenting: average sentence length, paragraph structure, humor patterns, recurring themes, rhetorical devices, tone distribution
- A "style prompt" template that captures the key stylistic features

**Dependencies**: None — this is the foundational phase

**Success Criteria**:
- Corpus contains at least 500 samples spanning multiple years and content types
- Style analysis identifies at least 10 distinct stylistic features with quantitative measurements
- A prompt template using 5 few-shot examples can generate text that a blind human rater identifies as "possibly Scott Adams" ≥ 40% of the time

**Tasks**:
- [ ] Task 1: Set up project — directory structure, requirements, data schema
- [ ] Task 2: Build corpus scraper — scrape scottadamsslog.com, Twitter/X archives, book excerpts (fair use)
- [ ] Task 3: Clean and deduplicate corpus — remove boilerplate, ads, comments
- [ ] Task 4: Annotate corpus — tag samples by type (blog, tweet, book, interview), date, theme
- [ ] Task 5: Quantitative style analysis — sentence length, word frequency, rhetorical devices, humor markers
- [ ] Task 6: Qualitative style analysis — recurring themes, contrarian patterns, "Stack of Luck" framing
- [ ] Task 7: Draft style prompt template with few-shot examples
- [ ] Task 8: Write style analysis report

---

## Phase 2: Prompt-Engineered Content Generator (Quick Validation)

**Description**: Build a content generator using prompt engineering with the style analysis from Phase 1. This validates the approach quickly before investing in fine-tuning.

**Deliverable**:
- A Python package `sacbot` with a `generate()` function that takes a topic and produces Scott Adams-style content
- Support for multiple content types: blog post, tweet thread, LinkedIn post
- CLI tool `sacbot generate --topic "..." --type blog`
- Evaluation harness that compares generated text to ground-truth samples using style metrics

**Dependencies**: Phase 1 (corpus + style analysis)

**Success Criteria**:
- Generated blog posts (300-500 words) achieve ≥ 50% "possibly Scott Adams" in blind human evaluation (10+ raters)
- Generated tweets capture his contrarian humor style (≥ 60% accuracy in blind evaluation)
- Evaluation metrics (perplexity, n-gram overlap, sentiment) correlate with human judgment (r ≥ 0.5)
- CLI tool runs end-to-end in < 30 seconds per generation

**Tasks**:
- [ ] Task 9: Package scaffolding — pyproject.toml, sacbot package structure
- [ ] Task 10: Implement content generator — prompt templates, few-shot selection, generation logic
- [ ] Task 11: Content type support — blog, tweet, LinkedIn templates
- [ ] Task 12: CLI tool — `sacbot generate` command with topic/type/format args
- [ ] Task 13: Evaluation harness — automated metrics + human eval interface
- [ ] Task 14: Iterative prompt refinement — test with real raters, refine few-shot examples
- [ ] Task 15: Write documentation — usage, style guide, limitations

---

## Phase 3: Fine-Tuning Pipeline (Parallel Track)

**Description**: Build a fine-tuning pipeline to create a model that natively generates Scott Adams-style content. This is the higher-quality but higher-effort path.

**Deliverable**:
- Fine-tuning dataset: 1000+ instruction-tuning pairs (topic → Scott Adams-style text)
- LoRA fine-tuned model checkpoint (based on Llama 3 8B or Mistral 7B)
- Training pipeline scripts (data prep, training, evaluation)
- Model serving interface compatible with the `sacbot` package

**Dependencies**: Phase 1 (corpus), Phase 2 (evaluation framework)

**Success Criteria**:
- Fine-tuned model achieves ≥ 60% "possibly Scott Adams" in blind human evaluation (improvement over prompt-engineered baseline)
- Training completes on a single GPU (≤ 48 hours for LoRA on 8B model)
- Model generates coherent, on-topic content (≥ 90% coherence rating from 5+ raters)
- Fine-tuned model outperforms prompt-engineered version on automated style metrics

**Tasks**:
- [ ] Task 16: Instruction dataset creation — convert corpus to instruction-tuning pairs
- [ ] Task 17: Data augmentation — paraphrase, style transfer, synthetic examples
- [ ] Task 18: Model selection — evaluate Llama 3 8B vs Mistral 7B as base models
- [ ] Task 19: LoRA fine-tuning — configure and run training
- [ ] Task 20: Model evaluation — automated + human evaluation against baseline
- [ ] Task 21: Model serving — integrate fine-tuned model into `sacbot` package
- [ ] Task 22: Compare prompt vs fine-tuned — A/B evaluation report

---

## Phase 4: Content Pipeline & Scheduling

**Description**: Build a production-ready content pipeline that can generate, review, and schedule content for publishing. This makes the bot practically useful.

**Deliverable**:
- Content pipeline: topic research → generation → review → scheduling
- Topic generator that suggests topics based on current events and Adams' typical subjects
- Review system: automated style checks + optional human review
- Scheduler: integrates with Twitter/X API, LinkedIn API, or RSS feed
- Dashboard for monitoring content output and engagement

**Dependencies**: Phase 2 (content generation) or Phase 3 (fine-tuned model)

**Success Criteria**:
- Pipeline can generate and schedule a week's worth of content autonomously
- Content passes automated style checks (≥ 80% style match score)
- Scheduler successfully posts to at least one platform (Twitter/X or RSS)
- Dashboard shows real-time content pipeline status

**Tasks**:
- [ ] Task 23: Topic research module — current events aggregation, topic suggestion algorithm
- [ ] Task 24: Content review system — automated style checks, quality filters
- [ ] Task 25: Platform integrations — Twitter/X API, LinkedIn API, RSS
- [ ] Task 26: Scheduler — cron-based or event-driven content scheduling
- [ ] Task 27: Dashboard — web-based or CLI dashboard for pipeline monitoring
- [ ] Task 28: End-to-end pipeline test — generate and publish a week of content
- [ ] Task 29: Documentation — deployment guide, API reference

---

## Phase 5: Engagement Optimization & Iteration

**Description**: Optimize the bot for engagement by analyzing what types of content perform best and iterating on the style/model accordingly.

**Deliverable**:
- Engagement analytics: track likes, retweets, comments, shares per content type
- A/B testing framework for comparing different style variants
- Style refinement loop: use engagement data to improve prompts/fine-tuning
- Final evaluation report comparing bot-generated vs. human-generated engagement

**Dependencies**: Phase 4 (content pipeline with published content)

**Success Criteria**:
- Bot-generated content achieves ≥ 50% of the engagement of comparable human-written Scott Adams posts (normalized by reach)
- A/B tests identify at least 3 statistically significant style features that improve engagement
- Style refinement loop produces measurable improvement over 4+ weeks
- Final report documents engagement results and lessons learned

**Tasks**:
- [ ] Task 30: Engagement tracking — API integrations for metrics collection
- [ ] Task 31: A/B testing framework — experimental design, statistical analysis
- [ ] Task 32: Style refinement — iterate on prompts/fine-tuning based on engagement data
- [ ] Task 33: Long-term monitoring — 4-week engagement study
- [ ] Task 34: Final evaluation report — engagement comparison, style analysis, recommendations
- [ ] Task 35: Lessons learned document — what worked, what didn't, future directions

---

## Overall Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Copyright issues with corpus | Legal | Use only fair use for personal/educational purposes; do not redistribute corpus or model |
| Fine-tuning doesn't improve over prompting | Time waste | Phase 2 validates prompt approach first; only proceed to Phase 3 if Phase 2 shows promise |
| Content sounds "off" or inauthentic | Quality | Heavy human evaluation at each phase; stop if quality is unacceptable |
| Platform API rate limits | Delivery | Implement retry logic, rate limiting, and fallback to manual posting |
| Overfitting to Adams' idiosyncrasies | Generalization | Include diverse corpus; evaluate on out-of-domain topics |
