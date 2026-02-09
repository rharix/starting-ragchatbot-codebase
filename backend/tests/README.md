# Test Suite for CourseSearchTool

This directory contains comprehensive tests for the `CourseSearchTool.execute()` method in `backend/search_tools.py`.

## Test Overview

The test suite includes **29 test cases** organized into 5 logical groups:

1. **TestCourseSearchToolExecute** (9 tests) - Main flow tests covering:
   - Successful searches with different filter combinations
   - Empty result handling with proper messages
   - Error propagation from VectorStore

2. **TestCourseSearchToolFormatResults** (5 tests) - Formatting logic tests:
   - Single and multiple document formatting
   - Header generation with/without lesson numbers
   - Graceful handling of missing metadata

3. **TestCourseSearchToolSourceTracking** (6 tests) - Source metadata tests:
   - Source structure validation
   - URL generation (lesson links vs course links)
   - Source reset behavior between calls
   - Count matching

4. **TestCourseSearchToolEdgeCases** (5 tests) - Edge cases:
   - Empty queries
   - Special characters (quotes, newlines, unicode)
   - Lesson number zero
   - Multiple documents from same lesson
   - Mixed courses in results

5. **Parametrized Tests** (4 tests) - Filter combination messages

## Installation

Install test dependencies:

```bash
uv sync --extra dev
```

This installs:
- pytest>=8.0.0
- pytest-cov>=4.1.0

## Running Tests

### Run all tests
```bash
pytest tests/test_search_tools.py -v
```

### Run with coverage
```bash
pytest tests/test_search_tools.py --cov=search_tools --cov-report=term-missing
```

### Run with HTML coverage report
```bash
pytest tests/test_search_tools.py --cov=search_tools --cov-report=html
# Open htmlcov/index.html in browser
```

### Run specific test class
```bash
pytest tests/test_search_tools.py::TestCourseSearchToolExecute -v
```

### Run single test
```bash
pytest tests/test_search_tools.py::TestCourseSearchToolExecute::test_successful_search_no_filters -v
```

## Test Coverage

**CourseSearchTool class coverage: 100%**

The test suite achieves complete coverage of:
- `CourseSearchTool.execute()` method
- `CourseSearchTool._format_results()` helper method
- All code paths including error handling and edge cases

Overall file coverage is 73% because ToolManager and abstract base classes are not in scope.

## Test Strategy

### Mock Isolation
- Tests use `unittest.mock.Mock` to mock VectorStore
- No actual ChromaDB instances are created
- No external dependencies required during testing
- Fast execution (all 29 tests run in < 0.1 seconds)

### Fixtures (conftest.py)
- `mock_vector_store`: Pre-configured Mock for VectorStore
- `sample_search_results`: Factory for creating SearchResults
- `course_search_tool`: CourseSearchTool with injected mock

### Assertion Patterns
Tests verify:
1. **Return values**: Correct formatting, proper messages
2. **Mock calls**: VectorStore methods called with right parameters
3. **State changes**: `last_sources` tracked correctly
4. **Edge cases**: Special characters preserved, no crashes

## Key Test Cases

**Filter combinations:**
- No filters → searches all content
- Course filter only → filters by course
- Lesson filter only → filters by lesson
- Both filters → applies both constraints

**Empty result messages:**
- "No relevant content found."
- "No relevant content found in course 'X'."
- "No relevant content found in lesson N."
- "No relevant content found in course 'X' in lesson N."

**Source tracking:**
- Each result generates a source dict with: display_text, url, course_title, lesson_number
- Lesson links preferred over course links
- Sources reset between calls
- Count always matches document count

**Error handling:**
- Errors from VectorStore are propagated as-is
- Missing metadata uses fallback values ('unknown')
- Empty queries don't crash

## Maintenance

When modifying `CourseSearchTool.execute()`:
1. Run tests to ensure no regressions
2. Add new test cases for new functionality
3. Update parametrized tests if message formats change
4. Maintain 100% coverage of the execute method

## Future Improvements

Potential additions:
- Integration tests with real ChromaDB
- Performance benchmarks
- Tests for get_tool_definition()
- Tests for ToolManager class
- Mutation testing to verify test quality
