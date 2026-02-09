"""Comprehensive test suite for CourseSearchTool.execute() method"""
import pytest
from unittest.mock import Mock
from vector_store import SearchResults
from search_tools import CourseSearchTool


class TestCourseSearchToolExecute:
    """Tests for main flow of CourseSearchTool.execute()"""

    def test_successful_search_no_filters(self, course_search_tool, mock_vector_store):
        """Test 1: Successful search without filters"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Machine learning basics", "Neural networks intro", "Deep learning overview"],
            metadata=[
                {"course_title": "AI Fundamentals", "lesson_number": 1},
                {"course_title": "AI Fundamentals", "lesson_number": 2},
                {"course_title": "Advanced AI", "lesson_number": 1}
            ],
            distances=[0.1, 0.15, 0.2]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson"

        # Execute
        result = course_search_tool.execute(query="machine learning")

        # Verify
        mock_vector_store.search.assert_called_once_with(
            query="machine learning",
            course_name=None,
            lesson_number=None
        )
        assert isinstance(result, str)
        assert "[AI Fundamentals - Lesson 1]" in result
        assert "[AI Fundamentals - Lesson 2]" in result
        assert "[Advanced AI - Lesson 1]" in result
        assert "Machine learning basics" in result
        assert len(course_search_tool.last_sources) == 3

    def test_successful_search_with_course_filter(self, course_search_tool, mock_vector_store):
        """Test 2: Successful search with course filter"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Async programming in Python"],
            metadata=[{"course_title": "Advanced Python", "lesson_number": 5}],
            distances=[0.12]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson5"

        # Execute
        result = course_search_tool.execute(query="async", course_name="Advanced Python")

        # Verify
        mock_vector_store.search.assert_called_once_with(
            query="async",
            course_name="Advanced Python",
            lesson_number=None
        )
        assert "[Advanced Python - Lesson 5]" in result
        assert "Async programming in Python" in result

    def test_successful_search_with_lesson_filter(self, course_search_tool, mock_vector_store):
        """Test 3: Successful search with lesson filter"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Python basics content"],
            metadata=[{"course_title": "Python 101", "lesson_number": 5}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson5"

        # Execute
        result = course_search_tool.execute(query="basics", lesson_number=5)

        # Verify
        mock_vector_store.search.assert_called_once_with(
            query="basics",
            course_name=None,
            lesson_number=5
        )
        assert "[Python 101 - Lesson 5]" in result

    def test_successful_search_with_both_filters(self, course_search_tool, mock_vector_store):
        """Test 4: Successful search with both filters"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Test content"],
            metadata=[{"course_title": "Python Basics", "lesson_number": 3}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson3"

        # Execute
        result = course_search_tool.execute(
            query="test",
            course_name="Python Basics",
            lesson_number=3
        )

        # Verify
        mock_vector_store.search.assert_called_once_with(
            query="test",
            course_name="Python Basics",
            lesson_number=3
        )
        assert "[Python Basics - Lesson 3]" in result

    def test_empty_results_without_filters(self, course_search_tool, mock_vector_store):
        """Test 5: Empty results without filters"""
        # Setup
        mock_vector_store.search.return_value = SearchResults([], [], [])

        # Execute
        result = course_search_tool.execute(query="nonexistent")

        # Verify
        assert result == "No relevant content found."
        assert len(course_search_tool.last_sources) == 0

    def test_empty_results_with_course_filter(self, course_search_tool, mock_vector_store):
        """Test 6: Empty results with course filter"""
        # Setup
        mock_vector_store.search.return_value = SearchResults([], [], [])

        # Execute
        result = course_search_tool.execute(query="test", course_name="Python Basics")

        # Verify
        assert result == "No relevant content found in course 'Python Basics'."

    def test_empty_results_with_lesson_filter(self, course_search_tool, mock_vector_store):
        """Test 7: Empty results with lesson filter"""
        # Setup
        mock_vector_store.search.return_value = SearchResults([], [], [])

        # Execute
        result = course_search_tool.execute(query="test", lesson_number=5)

        # Verify
        assert result == "No relevant content found in lesson 5."

    def test_empty_results_with_both_filters(self, course_search_tool, mock_vector_store):
        """Test 8: Empty results with both filters"""
        # Setup
        mock_vector_store.search.return_value = SearchResults([], [], [])

        # Execute
        result = course_search_tool.execute(
            query="test",
            course_name="Python Basics",
            lesson_number=3
        )

        # Verify
        assert result == "No relevant content found in course 'Python Basics' in lesson 3."

    def test_error_from_vector_store(self, course_search_tool, mock_vector_store):
        """Test 9: Error from VectorStore"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=[],
            metadata=[],
            distances=[],
            error="Database connection failed"
        )

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify
        assert result == "Database connection failed"
        assert len(course_search_tool.last_sources) == 0


class TestCourseSearchToolFormatResults:
    """Tests for formatting logic in _format_results()"""

    def test_single_document_formatting(self, course_search_tool, mock_vector_store):
        """Test 10: Single document formatting"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Introduction to AI concepts"],
            metadata=[{"course_title": "Intro to AI", "lesson_number": 2}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson2"

        # Execute
        result = course_search_tool.execute(query="AI")

        # Verify
        assert result == "[Intro to AI - Lesson 2]\nIntroduction to AI concepts"

    def test_multiple_documents_formatting(self, course_search_tool, mock_vector_store):
        """Test 11: Multiple documents formatting"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content 1", "Content 2", "Content 3"],
            metadata=[
                {"course_title": "Course A", "lesson_number": 1},
                {"course_title": "Course A", "lesson_number": 2},
                {"course_title": "Course B", "lesson_number": 1}
            ],
            distances=[0.1, 0.15, 0.2]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson"

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify
        assert "[Course A - Lesson 1]" in result
        assert "[Course A - Lesson 2]" in result
        assert "[Course B - Lesson 1]" in result
        assert "Content 1" in result
        assert "Content 2" in result
        assert "Content 3" in result
        # Verify blocks are separated by double newline
        blocks = result.split("\n\n")
        assert len(blocks) == 3

    def test_document_without_lesson_number(self, course_search_tool, mock_vector_store):
        """Test 12: Document without lesson number"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Course overview content"],
            metadata=[{"course_title": "Python Fundamentals"}],
            distances=[0.1]
        )
        mock_vector_store.get_course_link.return_value = "https://example.com/course"

        # Execute
        result = course_search_tool.execute(query="overview")

        # Verify
        assert result == "[Python Fundamentals]\nCourse overview content"
        mock_vector_store.get_course_link.assert_called_once_with("Python Fundamentals")
        mock_vector_store.get_lesson_link.assert_not_called()

    def test_document_with_lesson_number(self, course_search_tool, mock_vector_store):
        """Test 13: Document with lesson number"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Lesson content"],
            metadata=[{"course_title": "Data Science", "lesson_number": 5}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson5"

        # Execute
        result = course_search_tool.execute(query="data")

        # Verify
        mock_vector_store.get_lesson_link.assert_called_once_with("Data Science", 5)
        mock_vector_store.get_course_link.assert_not_called()

    def test_metadata_with_missing_course_title(self, course_search_tool, mock_vector_store):
        """Test 14: Metadata with missing course_title"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Some content"],
            metadata=[{"lesson_number": 1}],  # Missing course_title
            distances=[0.1]
        )

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify - should use 'unknown' as fallback
        assert "[unknown - Lesson 1]" in result
        assert "Some content" in result


class TestCourseSearchToolSourceTracking:
    """Tests for source metadata tracking"""

    def test_source_structure_validation(self, course_search_tool, mock_vector_store):
        """Test 15: Source structure validation"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Test content"],
            metadata=[{"course_title": "Python 101", "lesson_number": 3}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson3"

        # Execute
        course_search_tool.execute(query="test")

        # Verify
        assert len(course_search_tool.last_sources) == 1
        source = course_search_tool.last_sources[0]
        assert "display_text" in source
        assert "url" in source
        assert "course_title" in source
        assert "lesson_number" in source
        assert source["display_text"] == "Python 101 - Lesson 3"

    def test_source_url_with_lesson_link(self, course_search_tool, mock_vector_store):
        """Test 16: Source URL with lesson link"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content"],
            metadata=[{"course_title": "Web Dev", "lesson_number": 5}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://course.com/lesson5"

        # Execute
        course_search_tool.execute(query="test")

        # Verify
        source = course_search_tool.last_sources[0]
        assert source["url"] == "https://course.com/lesson5"

    def test_source_url_with_course_link_fallback(self, course_search_tool, mock_vector_store):
        """Test 17: Source URL with course link fallback"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content"],
            metadata=[{"course_title": "Database Systems"}],  # No lesson_number
            distances=[0.1]
        )
        mock_vector_store.get_course_link.return_value = "https://course.com"

        # Execute
        course_search_tool.execute(query="test")

        # Verify
        source = course_search_tool.last_sources[0]
        assert source["url"] == "https://course.com"
        mock_vector_store.get_course_link.assert_called_once_with("Database Systems")

    def test_source_url_when_link_not_found(self, course_search_tool, mock_vector_store):
        """Test 18: Source URL when link not found"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content"],
            metadata=[{"course_title": "Math 101", "lesson_number": 2}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = None

        # Execute
        course_search_tool.execute(query="test")

        # Verify
        source = course_search_tool.last_sources[0]
        assert source["url"] is None
        assert source["course_title"] == "Math 101"
        assert source["lesson_number"] == 2

    def test_sources_reset_between_calls(self, course_search_tool, mock_vector_store):
        """Test 19: Sources reset between calls"""
        # First call
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content 1", "Content 2"],
            metadata=[
                {"course_title": "Course A", "lesson_number": 1},
                {"course_title": "Course A", "lesson_number": 2}
            ],
            distances=[0.1, 0.15]
        )
        course_search_tool.execute(query="first")
        assert len(course_search_tool.last_sources) == 2

        # Second call
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content 3"],
            metadata=[{"course_title": "Course B", "lesson_number": 1}],
            distances=[0.1]
        )
        course_search_tool.execute(query="second")

        # Verify only second call's sources are present
        assert len(course_search_tool.last_sources) == 1
        assert course_search_tool.last_sources[0]["course_title"] == "Course B"

    def test_source_count_matches_document_count(self, course_search_tool, mock_vector_store):
        """Test 20: Source count matches document count"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Doc 1", "Doc 2", "Doc 3", "Doc 4", "Doc 5"],
            metadata=[
                {"course_title": "Course", "lesson_number": i + 1}
                for i in range(5)
            ],
            distances=[0.1 * (i + 1) for i in range(5)]
        )

        # Execute
        course_search_tool.execute(query="test")

        # Verify
        assert len(course_search_tool.last_sources) == 5


class TestCourseSearchToolEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_empty_query_string(self, course_search_tool, mock_vector_store):
        """Test 21: Empty query string"""
        # Setup
        mock_vector_store.search.return_value = SearchResults([], [], [])

        # Execute
        result = course_search_tool.execute(query="")

        # Verify - should not crash
        mock_vector_store.search.assert_called_once_with(
            query="",
            course_name=None,
            lesson_number=None
        )
        assert result == "No relevant content found."

    def test_special_characters_in_content(self, course_search_tool, mock_vector_store):
        """Test 22: Special characters in content"""
        # Setup
        special_content = 'Content with "quotes"\nand newlines\nand unicode: café ñ 中文'
        mock_vector_store.search.return_value = SearchResults(
            documents=[special_content],
            metadata=[{"course_title": "Special Course", "lesson_number": 1}],
            distances=[0.1]
        )

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify - content should be preserved
        assert special_content in result
        assert '"quotes"' in result
        assert 'café' in result
        assert '中文' in result

    def test_lesson_number_zero(self, course_search_tool, mock_vector_store):
        """Test 23: Lesson number zero"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Intro content"],
            metadata=[{"course_title": "Python Basics", "lesson_number": 0}],
            distances=[0.1]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson0"

        # Execute
        result = course_search_tool.execute(query="intro")

        # Verify - zero should be treated as valid lesson number
        assert "[Python Basics - Lesson 0]" in result
        assert "Intro content" in result
        mock_vector_store.get_lesson_link.assert_called_once_with("Python Basics", 0)

    def test_multiple_documents_from_same_lesson(self, course_search_tool, mock_vector_store):
        """Test 24: Multiple documents from same lesson"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Chunk 1", "Chunk 2", "Chunk 3"],
            metadata=[
                {"course_title": "AI Course", "lesson_number": 5},
                {"course_title": "AI Course", "lesson_number": 5},
                {"course_title": "AI Course", "lesson_number": 5}
            ],
            distances=[0.1, 0.12, 0.14]
        )
        mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson5"

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify - get_lesson_link should be called for each document
        assert mock_vector_store.get_lesson_link.call_count == 3
        assert result.count("[AI Course - Lesson 5]") == 3

    def test_mixed_courses_in_results(self, course_search_tool, mock_vector_store):
        """Test 25: Mixed courses in results"""
        # Setup
        mock_vector_store.search.return_value = SearchResults(
            documents=["Content A", "Content B"],
            metadata=[
                {"course_title": "Course A", "lesson_number": 1},
                {"course_title": "Course B", "lesson_number": 2}
            ],
            distances=[0.1, 0.15]
        )

        def mock_get_lesson_link(course_title, lesson_num):
            if course_title == "Course A":
                return "https://example.com/courseA/lesson1"
            return "https://example.com/courseB/lesson2"

        mock_vector_store.get_lesson_link.side_effect = mock_get_lesson_link

        # Execute
        result = course_search_tool.execute(query="test")

        # Verify both courses appear
        assert "[Course A - Lesson 1]" in result
        assert "[Course B - Lesson 2]" in result
        assert "Content A" in result
        assert "Content B" in result
        assert len(course_search_tool.last_sources) == 2


# Parametrized test for empty result messages
@pytest.mark.parametrize("course_name,lesson_number,expected_msg", [
    (None, None, "No relevant content found."),
    ("Python Basics", None, "No relevant content found in course 'Python Basics'."),
    (None, 5, "No relevant content found in lesson 5."),
    ("Python Basics", 5, "No relevant content found in course 'Python Basics' in lesson 5."),
])
def test_empty_results_messages(course_name, lesson_number, expected_msg, course_search_tool, mock_vector_store):
    """Parametrized test for empty result messages with different filter combinations"""
    mock_vector_store.search.return_value = SearchResults([], [], [])
    result = course_search_tool.execute("query", course_name, lesson_number)
    assert result == expected_msg
