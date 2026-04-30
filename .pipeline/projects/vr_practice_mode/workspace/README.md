# Thronglets VR Practice Mode - Test Suite

Comprehensive test suite for the Thronglets VR Practice Mode application using Vitest.

## Test Coverage

The test suite covers the following areas:

### 1. Thronglet Class Tests
- Creating thronglets with default values
- Health color retrieval for different health states
- Health badge generation
- Timestamp updates
- JSON serialization

### 2. Connection Class Tests
- Creating connections with default values
- JSON serialization

### 3. VRState Tests
- Default state initialization
- Settings configuration

### 4. VRPracticeMode Class Tests
- Initialization
- Configuration loading
- Thronglet creation
- Connection creation
- Thronglet selection/deselection
- Teleportation
- Visibility toggles (nameplates, connections, health halos)
- Debug mode toggle
- Keyboard event handling
- Simulation updates
- Proximity alerts

### 5. Global Functions Tests
- Initialization
- Panel management
- Visibility toggles
- Teleportation
- Deselection
- Resize handling

### 6. Edge Cases
- Empty configuration handling
- Missing thronglet selection
- Invalid teleport indices
- Missing configuration files

### 7. Integration Tests
- Full workflow testing

## Running Tests

### Prerequisites
- Node.js >= 14.0.0
- npm or yarn

### Install Dependencies
```bash
npm install
```

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests with Verbose Output
```bash
npm run test:verbose
```

### Run Tests with Coverage Report
```bash
npm run test:coverage
```

## Test Structure

```
workspace/
├── vr_practice_mode.js          # Main application code
├── vr_practice_mode.test.js     # Comprehensive test suite
├── test/
│   └── setup.js                 # Test setup and mocks
├── vitest.config.js             # Vitest configuration
├── package.json                 # Project dependencies and scripts
└── README.md                    # This file
```

## Test Framework

This project uses **Vitest**, a fast and lightweight testing framework that provides:
- Fast HMR (Hot Module Replacement)
- Native ESM support
- Built-in coverage support
- Jest-compatible API

## Writing New Tests

When writing new tests, follow these guidelines:

1. **Use descriptive test names**: Each test should clearly describe what it's testing
2. **Follow Arrange-Act-Assert pattern**:
   - Arrange: Set up test data and state
   - Act: Execute the code being tested
   - Assert: Verify the expected results
3. **Keep tests independent**: Each test should be able to run in isolation
4. **Clean up after tests**: Use `afterEach` to reset state
5. **Test edge cases**: Include tests for error conditions and edge cases

## Mocking

The test suite uses mocks for:
- DOM elements (document, window)
- Browser APIs (performance, console)
- External dependencies

Mock setup is defined in `test/setup.js` and can be overridden in individual tests as needed.

## Coverage Goals

The test suite aims for:
- **100% line coverage** for core functionality
- **100% branch coverage** for critical paths
- **100% function coverage** for public APIs

## CI/CD Integration

To integrate with CI/CD, add the following to your CI configuration:

```yaml
- name: Run Tests
  run: npm run test:coverage

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/coverage-final.json
```

## Troubleshooting

### Tests fail to run
- Ensure all dependencies are installed: `npm install`
- Check Node.js version: `node --version` (should be >= 14.0.0)

### Coverage report is empty
- Ensure the coverage reporter is configured correctly in `vitest.config.js`
- Check that test files are being discovered (check `include` pattern)

### Tests are slow
- Use `npm run test:verbose` to identify slow tests
- Consider splitting large test suites into smaller files
- Use `--reporter=verbose` to see test execution times

## Contributing

When contributing tests:
1. Create a new test file or add to existing test files
2. Follow the existing test patterns and conventions
3. Include tests for both happy paths and edge cases
4. Update this README if adding new test categories

## License

MIT License - see LICENSE file for details
