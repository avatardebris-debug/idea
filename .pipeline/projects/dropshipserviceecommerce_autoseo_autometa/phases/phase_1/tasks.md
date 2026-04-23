# Phase 1 Tasks

- [ ] Task 1: Project scaffolding — pyproject.toml, package structure, config
  - What: Create the project skeleton with pyproject.toml, package layout, config module, and CLI entry point registration
  - Files: pyproject.toml, dropship_seo/__init__.py, dropship_seo/config.py, dropship_seo/cli.py, tests/__init__.py
  - Done when: pyproject.toml has project metadata + click dependency + entry point; package imports cleanly; `dropship-seo --help` works; config module loads defaults and reads from a YAML/JSON file

- [ ] Task 2: Data models — Product, SEOReport, MetaTag definitions
  - What: Implement core data models: Product (name, description, category, price, target_keywords, images), SEOReport (title, meta_description, meta_keywords, canonical_url, open_graph, twitter_card, issues), MetaTag (name, content, tag_type: meta/og/twitter)
  - Files: dropship_seo/models.py, tests/test_models.py
  - Done when: All dataclasses have proper type hints, serialization (to_dict/from_dict), and validation; Product validates required fields; SEOReport has helper methods for generating meta tag lists; tests cover valid construction, serialization round-trip, and validation errors

- [ ] Task 3: SEO analyzer — extract and evaluate product SEO readiness
  - What: Build an Analyzer that takes a Product and evaluates its SEO readiness: checks title length, meta description length, keyword presence, image alt text coverage, category richness, and generates a scored report with actionable issues
  - Files: dropship_seo/analyzer.py, tests/test_analyzer.py
  - Done when: Analyzer.analyze(product) returns an SEOReport with total_score (0-100), category_scores (title, meta_description, keywords, images, content), and a list of issues; scoring rules: title 0-20 pts (length 50-70 chars = full score), meta_description 0-20 pts (length 120-160 chars), keywords 0-20 pts (presence and density), images 0-20 pts (alt text coverage), content 0-20 pts (description length and richness); issues list includes specific fix suggestions; handles edge cases (empty product, very long/short fields)

- [ ] Task 4: Meta tag generator — auto-generate SEO metadata from product data
  - What: Build a MetaGenerator that takes a Product and generates optimized SEO metadata: auto-generated title (with keyword placement), meta description (compelling, keyword-rich, within 120-160 chars), meta keywords, Open Graph tags (og:title, og:description, og:image, og:type), Twitter Card tags (twitter:card, twitter:title, twitter:description), and canonical URL suggestions
  - Files: dropship_seo/meta_generator.py, tests/test_meta_generator.py
  - Done when: MetaGenerator.generate(product) returns a dict with title (str), meta_description (str), meta_keywords (list[str]), open_graph (dict[str, str]), twitter_card (dict[str, str]); title is 50-70 chars with primary keyword near the front; meta_description is 120-160 chars and compelling; meta_keywords has 5-15 deduplicated keywords; OG and Twitter tags are complete and properly formatted; supports custom overrides via optional parameters; generates at least 3 title variants when requested

- [ ] Task 5: CLI entry point — click commands for analysis and generation
  - What: Build the CLI with click subcommands: `analyze` (analyze a product's SEO readiness), `generate` (generate SEO metadata from product data), `list-templates` (list available title/description templates)
  - Files: dropship_seo/cli.py (updated), tests/test_cli.py
  - Done when: `dropship-seo analyze --json '{"name":"...","description":"..."}'` outputs a scored SEO report; `dropship-seo generate --json '{"name":"...","description":"..."}'` outputs generated metadata; `dropship-seo list-templates` lists available templates; all commands support --output-file flag; CLI errors are handled gracefully with helpful messages; exit code 0 on success, non-zero on error

- [ ] Task 6: Unit tests for Phase 1 (50+ tests, all passing)
  - What: Write comprehensive unit tests covering all Phase 1 modules — models, analyzer, meta_generator, CLI
  - Files: tests/test_models.py, tests/test_analyzer.py, tests/test_meta_generator.py, tests/test_cli.py, tests/fixtures/sample_products.json
  - Done when: 50+ tests across all test files; all tests pass with `pytest`; test coverage > 85% for all Phase 1 modules; fixtures directory with sample product data; tests cover edge cases (empty product, unicode characters, very long descriptions, missing fields, boundary score values)
