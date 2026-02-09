# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Retrieval-Augmented Generation (RAG) chatbot system** for course materials. It uses ChromaDB for vector storage, Anthropic's Claude API for AI generation with tool use, and provides a web interface for querying educational content.

**Tech Stack:**
- Backend: FastAPI, Python 3.13+
- Frontend: Vanilla JavaScript with HTML/CSS
- Vector DB: ChromaDB with sentence-transformers embeddings
- AI: Anthropic Claude with tool calling
- Package Manager: uv

## Running the Application

**Start server:**
```bash
./run.sh
```
or manually:
```bash
cd backend && uv run uvicorn app:app --reload --port 8000
```

**Install dependencies:**
```bash
uv sync
```

**Environment setup:**
Create `.env` file in root with:
```
ANTHROPIC_API_KEY=your_api_key_here
```

The app runs at http://localhost:8000 with API docs at http://localhost:8000/docs.

## Architecture

### RAG Query Flow

The system uses **Claude's tool calling** to intelligently decide when to search the knowledge base:

```
User Query → FastAPI → RAGSystem → AIGenerator (Claude) → Tool Decision
                                                               ↓
                                                    [Search Tool or Direct Answer]
                                                               ↓
                                                    VectorStore (ChromaDB)
                                                               ↓
                                                    Format Results → Claude → Response
```

### Core Components

**RAGSystem (rag_system.py)** - Main orchestrator
- Coordinates all subsystems
- Manages query lifecycle: prompt building → AI generation → tool execution → session updates
- Entry point: `query(query, session_id)` returns `(answer, sources)`

**AIGenerator (ai_generator.py)** - Claude API wrapper
- Handles Anthropic API calls with tool use
- Manages agentic loop: tool request → execute → send results → final answer
- System prompt is pre-built and static for performance
- `generate_response()` handles both direct answers and tool-based searches

**VectorStore (vector_store.py)** - ChromaDB interface
- **Two collections:**
  - `course_catalog`: Course metadata for semantic course name resolution
  - `course_content`: Chunked course content with embeddings
- `search()` method performs unified search with course/lesson filtering
- Uses semantic search to resolve partial course names (e.g., "MCP" → full title)

**ToolManager & CourseSearchTool (search_tools.py)** - Tool system
- Abstract `Tool` class for extensibility
- `CourseSearchTool` provides semantic search to Claude
- Tracks sources from search results for UI display
- Tool definition includes course name matching and lesson filtering parameters

**DocumentProcessor (document_processor.py)** - Document ingestion
- Parses structured course documents with expected format (see below)
- Sentence-based chunking with configurable overlap
- Extracts: course title, instructor, lessons, content
- Chunks include context prefix for better retrieval (e.g., "Course X Lesson Y content: ...")

**SessionManager (session_manager.py)** - Conversation context
- In-memory session storage (not persistent)
- Maintains rolling conversation history (configurable via `MAX_HISTORY`)
- Formats history for Claude's context

### Configuration (config.py)

Key settings:
- `ANTHROPIC_MODEL`: "claude-sonnet-4-20250514"
- `EMBEDDING_MODEL`: "all-MiniLM-L6-v2" (sentence-transformers)
- `CHUNK_SIZE`: 800 chars with 100 char overlap
- `MAX_RESULTS`: 5 search results
- `MAX_HISTORY`: 2 conversation exchanges

### Data Models (models.py)

- `Course`: title (unique ID), course_link, instructor, lessons[]
- `Lesson`: lesson_number, title, lesson_link
- `CourseChunk`: content, course_title, lesson_number, chunk_index

## Document Format

Course documents in `docs/` folder must follow this structure:

```
Course Title: [Title]
Course Link: [URL]
Course Instructor: [Name]

Lesson 0: [Lesson Title]
Lesson Link: [URL]
[Lesson content...]

Lesson 1: [Lesson Title]
Lesson Link: [URL]
[Lesson content...]
```

**Important:**
- First 3 lines are course metadata (required)
- Lessons must start with `Lesson N:` pattern
- Lesson links are optional and come immediately after lesson header
- Course title serves as unique identifier (no duplicates)
- Documents are loaded automatically on server startup

## Key Design Decisions

**Tool-Based Search:** Claude decides autonomously whether to search based on query. System prompt restricts to one search per query for cost/latency optimization.

**Dual Collection Strategy:** Course metadata is separate from content to enable fast course name resolution via semantic search. This allows users to use partial course names.

**Chunking with Context:** Each chunk includes course title and lesson number prefix to improve retrieval accuracy when chunks are shown to Claude.

**Session Management:** In-memory only (not database-backed), suitable for development/demo. Sessions are lost on server restart.

**Source Tracking:** Sources are captured during tool execution and returned separately from the answer for UI display.

## Frontend Architecture (frontend/)

**Single-page application:**
- `index.html`: Layout with chat interface, course stats sidebar, suggested questions
- `script.js`: Handles API calls, Markdown rendering (via marked.js), loading states
- `style.css`: Styling (not documented here)

**API calls:**
- `POST /api/query`: Send user query, receive answer + sources
- `GET /api/courses`: Fetch course statistics for sidebar

**Session handling:** Frontend tracks `currentSessionId` and includes it in subsequent queries for conversation context.

## Extending the System

**Adding new tools:**
1. Create class extending `Tool` in `search_tools.py`
2. Implement `get_tool_definition()` and `execute()`
3. Register with `ToolManager` in `RAGSystem.__init__()`

**Modifying search behavior:**
- Adjust system prompt in `AIGenerator.SYSTEM_PROMPT`
- Change search parameters in `VectorStore` constructor
- Modify chunking strategy in `DocumentProcessor`

**Supporting new document formats:**
- Extend `DocumentProcessor.process_course_document()` to handle PDF/DOCX parsing
- Currently only supports plain text with structured format

## Troubleshooting

**Documents not loading:** Check `docs/` folder structure and file format. Server logs show loading progress on startup.

**Empty search results:** Course name resolution may fail if query doesn't semantically match any course title. Check `course_catalog` collection.

**ChromaDB persistence:** Database is stored in `./chroma_db` (relative to backend directory). Delete to reset all data.

**API key errors:** Ensure `.env` file exists in root directory (not backend/) with valid `ANTHROPIC_API_KEY`.
