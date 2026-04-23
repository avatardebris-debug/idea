# Phase 1 Tasks

- [ ] Task 1: Project scaffolding and package structure
  - What: Create the Python package skeleton with pyproject.toml, package directory, and entry point configuration
  - Files: pyproject.toml, udemy_training_tool/__init__.py, udemy_training_tool/cli.py
  - Done when: pyproject.toml declares the package with a CLI entry point (udemy), __init__.py exports public symbols, cli.py has a working argparse/click setup with --version and --help, `pip install -e .` succeeds

- [ ] Task 2: Course and learning path data models
  - What: Build core data models for Udemy courses and learning paths — Course (title, instructor, rating, num_students, price, level, category, tags, duration, num_lectures, description), Module (title, order, num_lectures), Lesson (title, duration, type), LearningPath (title, courses, target_skill, estimated_hours, difficulty)
  - Files: udemy_training_tool/models.py
  - Done when: Course, Module, Lesson, LearningPath classes have typed fields with defaults, from_dict() classmethods, to_dict() instance methods; Course.validate() raises ValueError on missing required fields (title, instructor, rating); LearningPath has a compute_estimated_hours() method that sums course durations

- [ ] Task 3: Course search and filtering engine
  - What: Build a search/filter engine that takes a list of courses and filters them by criteria — skill/topic match, price range, rating threshold, level, category, language
  - Files: udemy_training_tool/search.py
  - Done when: search_courses(courses, query, min_rating=0, max_price=None, level=None, category=None) returns a list of matching Course objects; query matching is case-insensitive and supports partial word matching against title, description, tags, and instructor; filters are combined with AND logic; returns empty list if no courses match; handles None/empty inputs gracefully

- [ ] Task 4: Course comparison and recommendation engine
  - What: Build a comparison engine that scores and ranks courses for a given skill/topic — computes a composite score based on rating (weighted 30%), student count (weighted 25%), price value (weighted 20%), course depth/lectures (weighted 15%), and instructor quality (weighted 10%); generates a recommendation list sorted by score
  - Files: udemy_training_tool/recommender.py
  - Done when: recommend_courses(courses, target_skill, top_n=5) returns a list of dicts with course, score (0-100), and breakdown; score normalization handles varying scales (e.g., student counts in thousands); ties broken by rating then price (lower is better); handles courses with missing fields by using median imputation

- [ ] Task 5: CLI interface for search, compare, and recommend
  - What: Build the CLI that accepts commands to search courses, compare courses, and get recommendations — supports input via JSON file, JSONL file, or stdin; supports output in JSON or text format
  - Files: udemy_training_tool/cli.py (extend from Task 1)
  - Done when: CLI supports subcommands: `search` (query courses from a JSON/JSONL file with --min-rating, --max-price, --level, --category filters), `compare` (compare two or more courses from a file, prints side-by-side score breakdown), `recommend` (get top-N course recommendations for a skill, prints ranked list with scores); --output flag supports json or text format; returns exit code 0 on success, 1 on error

- [ ] Task 6: Unit tests for Phase 1
  - What: Write comprehensive unit tests for all modules — models, search, recommender, and CLI
  - Files: tests/test_models.py, tests/test_search.py, tests/test_recommender.py, tests/test_cli.py, tests/fixtures/sample_courses.json
  - Done when: All tests pass with pytest; models tests cover from_dict, to_dict, validate (valid and invalid), compute_estimated_hours; search tests cover exact match, partial match, all filters, empty results, case insensitivity; recommender tests cover full overlap, partial overlap, missing fields, score normalization, top_n selection; CLI tests verify search, compare, and recommend subcommands with sample fixtures
