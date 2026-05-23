# DeepSearchResearcher

---

## English Technical Design Document

### I. Project Overview

DeepSearchResearcher is an intelligent research assistant system based on a multi-agent collaborative architecture, implementing automated processing of complex tasks through integration with the LangChain/LangGraph framework. The system automatically coordinates multiple specialized agents including web search, database query, and knowledge base retrieval to complete full-process tasks such as information collection, analysis, and report generation, with real-time progress feedback via WebSocket.

**Core Features:**
- Multi-agent collaborative architecture supporting complex task decomposition and orchestration
- Three specialized sub-agents: Web Search, Database Query, RAGFlow Knowledge Base
- Real-time communication mechanism with visible task execution process
- Multi-format document generation (Markdown/PDF)
- Multi-user concurrency support with session data isolation

---

### II. System Architecture Design

#### 2.1 Overall Architecture

The system adopts a layered architecture design, divided into four layers: Frontend Interaction Layer, API Service Layer, Agent Orchestration Layer, and Tool Execution Layer:

```
┌─────────────────────────────────────────────────────────┐
│              Frontend Interaction Layer (Vue3)           │
│          WebSocket Real-time Communication / File Mgmt   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                API Service Layer (FastAPI)               │
│          REST API / WebSocket / File Upload & Download   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│           Agent Orchestration Layer (LangGraph)          │
│    Main Agent Coordination / Sub-agent Scheduling / State│
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                Tool Execution Layer (Tools)              │
│  Web Search / Database Query / Knowledge Retrieval / Doc│
└─────────────────────────────────────────────────────────┘
```

#### 2.2 Core Module Design

**1. Main Agent**
- Responsibility: Task decomposition, sub-agent coordination, result integration
- Technology: Built using `deepagents.create_deep_agent` factory method
- Features: Streaming processing, tool invocation, sub-agent delegation

**2. Sub Agents**

| Agent Name | Description | Core Tools |
|-----------|-------------|-----------|
| Web Search Agent | Internet public information retrieval | Tavily Search API |
| Database Query Agent | Enterprise internal database queries | MySQL Connector |
| RAGFlow Agent | Enterprise knowledge base retrieval | RAGFlow SDK |

**3. API Service Module**
- REST API: Task submission, file upload/download
- WebSocket: Real-time messaging, progress feedback
- Session Management: Multi-user concurrency, session isolation

**4. Context Management Module**
- Technology: Python ContextVar for coroutine-level data isolation
- Features: Session directory management, Thread ID binding

---

### III. Core Technology Stack

#### 3.1 Backend Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13+ | Core development language |
| LangChain | 0.2.0+ | LLM application framework |
| LangGraph | 0.1.0+ | Agent workflow orchestration |
| FastAPI | 0.100.0+ | Async web framework |
| Uvicorn | 0.20.0+ | ASGI server |
| MySQL Connector | 8.0+ | Database driver |
| Tavily Python | 0.3.0+ | Web search API |
| RAGFlow SDK | 0.1.0+ | Knowledge base SDK |

#### 3.2 Frontend Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Vue.js | 3.x | Frontend framework |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build tool |
| Axios | 1.x | HTTP client |
| Marked | 4.x | Markdown parser |

#### 3.3 LLM Service

- Supports OpenAI API compatible interfaces
- Flexible configuration with custom Base URL
- Current default model: GPT-4o-mini

---

### IV. Data Flow Design

#### 4.1 Task Execution Flow

```
User Request → API Reception → Create Session Directory → Set Context
    → Main Agent Start → Task Decomposition → Sub-agent Scheduling
    → Tool Execution → Result Aggregation → Document Generation → WebSocket Push
    → Context Cleanup → Return Result
```

#### 4.2 WebSocket Message Types

| Event Type | Description | Data Structure |
|-----------|-------------|----------------|
| session_created | Session directory created | `{path: "/output/session_xxx"}` |
| tool_start | Tool invocation started | `{tool_name, args}` |
| assistant_call | Sub-agent invocation | `{assistant_name, args}` |
| task_result | Final task result | `{result: "..."}` |
| error | Error message | `{message: "..."}` |

#### 4.3 Session Data Isolation Mechanism

**Core Technology: Python ContextVar**

```python
# Store current session directory
_session_dir_ctx: ContextVar[Optional[str]] = ContextVar("session_dir")

# Store current session Thread ID
_thread_id_ctx: ContextVar[Optional[str]] = ContextVar("thread_id")
```

**Isolation Principle:**
- Each async task has an independent context environment
- ContextVar automatically isolates data from different coroutines
- Prevents data mixing during multi-user concurrency

---

### V. Core Module Details

#### 5.1 Main Agent Configuration

```python
main_agent = create_deep_agent(
    model=model,                    # LLM model instance
    system_prompt=system_prompt,    # System prompt
    tools=[generate_markdown, convert_md_to_pdf, read_file_content],
    checkpointer=InMemorySaver(),   # State persistence
    subagents=[                     # Sub-agent list
        database_query_agent,
        network_search_agent,
        knowledge_base_agent
    ]
)
```

#### 5.2 Tool Module Design

**Web Search Tool (tavily_tool.py)**
- Integrates Tavily Search API
- Supports general/news/finance topics
- Returns structured search results

**Database Query Tool (db_tool.py)**
- `list_sql_tables`: List database tables
- `get_table_data`: Preview table data
- `execute_sql_query`: Execute custom SQL

**Knowledge Base Tool (ragflow_tools.py)**
- `get_assistant_list`: Get available assistant list
- `create_ask_delete`: Create session, query, and destroy

**Document Generation Tool (markdown_tools.py / pdf_tools.py)**
- Markdown document generation
- PDF format conversion

#### 5.3 Monitor Module (monitor.py)

**Design Pattern: Singleton Pattern**

```python
class ToolMonitor:
    _instance = None
    
    def report_tool(self, tool_name, args):
        # Report tool invocation
        
    def report_assistant(self, assistant_name, args):
        # Report sub-agent invocation
        
    def report_task_result(self, result):
        # Report final result
```

**Push Mechanism:**
- Push messages to specific Thread ID via WebSocket
- Use `asyncio.run_coroutine_threadsafe` for cross-thread scheduling

---

### VI. Deployment & Running

#### 6.1 Environment Setup

```bash
# Clone project
git clone [project_url]

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env file)
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
TAVILY_API_KEY=your_tavily_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

#### 6.2 Start Services

```bash
# Start backend service
cd api
python server.py

# Start frontend service
cd ui
npm install
npm run dev
```

#### 6.3 Access URLs

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173
- API Docs: http://localhost:8000/docs

---

### VII. Project Structure

```
DeepSearchResearcher/
├── agent/                 # Agent module
│   ├── main_agent.py     # Main agent
│   ├── llm.py            # LLM configuration
│   ├── load_prompts.py   # Prompt loading
│   └── sub_agent/        # Sub-agents
│       ├── network_search_agent.py
│       ├── database_query_agent.py
│       └── knowledge_base_agent.py
├── api/                   # API service module
│   ├── server.py         # FastAPI service
│   ├── monitor.py        # Monitor module
│   ├── context.py        # Context management
│   └── logger.py         # Logger module
├── tools/                 # Tool module
│   ├── tavily_tool.py    # Web search
│   ├── db_tool.py        # Database query
│   ├── ragflow_tools.py  # Knowledge retrieval
│   ├── markdown_tools.py # Markdown generation
│   └── pdf_tools.py      # PDF conversion
├── utils/                 # Utility functions
├── prompt/                # Prompt configuration
│   └── prompts.yaml
├── ui/                    # Frontend project
│   └── src/
│       └── App.vue       # Main app component
├── output/                # Output directory
├── updated/               # Upload directory
├── requirements.txt       # Dependencies
└── README.md             # Project documentation
```

---

### VIII. Core Advantages

1. **Intelligent Orchestration**: Main agent automatically decomposes complex tasks and coordinates multiple specialized sub-agents
2. **Real-time Feedback**: Real-time task progress push via WebSocket for excellent user experience
3. **Data Isolation**: Coroutine-level data isolation based on ContextVar supporting multi-user concurrency
4. **High Extensibility**: Modular design, easy to add new sub-agents and tools
5. **Flexible Configuration**: YAML-based prompt configuration, environment variable management for sensitive information

---

### IX. Application Scenarios

- Enterprise market research report auto-generation
- Competitor analysis and industry research
- Internal data query and analysis reports
- Knowledge base Q&A and document generation
- Multi-source information integration and report writing

---

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For questions or support, please open an issue in the repository.
