"""Shared test fixtures for the test suite"""
import pytest
from unittest.mock import Mock
from vector_store import SearchResults
from search_tools import CourseSearchTool


@pytest.fixture
def mock_vector_store():
    """
    Returns a Mock object mimicking VectorStore.
    Pre-configured with search(), get_lesson_link(), get_course_link() methods.
    """
    mock_store = Mock()

    # Default return values (can be overridden in tests)
    mock_store.search.return_value = SearchResults(
        documents=[],
        metadata=[],
        distances=[]
    )
    mock_store.get_lesson_link.return_value = None
    mock_store.get_course_link.return_value = None

    return mock_store


@pytest.fixture
def sample_search_results():
    """
    Factory function for creating SearchResults instances.

    Usage:
        results = sample_search_results(num_docs=3, course_title="Python Basics")
    """
    def _create_results(
        num_docs=1,
        course_title="Test Course",
        lesson_number=1,
        include_error=False
    ):
        if include_error:
            return SearchResults(
                documents=[],
                metadata=[],
                distances=[],
                error="Database connection failed"
            )

        documents = [f"Content for document {i+1}" for i in range(num_docs)]
        metadata = [
            {
                "course_title": course_title,
                "lesson_number": lesson_number + i
            }
            for i in range(num_docs)
        ]
        distances = [0.1 * (i + 1) for i in range(num_docs)]

        return SearchResults(
            documents=documents,
            metadata=metadata,
            distances=distances
        )

    return _create_results


@pytest.fixture
def course_search_tool(mock_vector_store):
    """
    Returns CourseSearchTool instance with injected mock VectorStore.
    Ready for testing without ChromaDB dependency.
    """
    return CourseSearchTool(mock_vector_store)
