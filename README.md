# DeepSearchResearcher - 深度搜索研究智能体系统

---

## 中文版技术方案设计文档

### 一、项目概述

DeepSearchResearcher是一个基于多智能体协作架构的智能研究助手系统，通过集成LangChain/LangGraph框架实现复杂任务的自动化处理。系统能够自动协调网络搜索、数据库查询、知识库检索等多个专业智能体，完成信息收集、分析、报告生成等全流程任务，并通过WebSocket实现实时进度反馈。

**核心特性：**
- 多智能体协作架构，支持复杂任务分解与编排
- 三大专业子智能体：网络搜索、数据库查询、RAGFlow知识库
- 实时通信机制，任务执行过程可视化
- 多格式文档生成（Markdown/PDF）
- 多用户并发支持，会话数据隔离

---

### 二、系统架构设计

#### 2.1 整体架构

系统采用分层架构设计，分为前端交互层、API服务层、智能体编排层、工具执行层四个层次：

```
┌─────────────────────────────────────────────────────────┐
│                    前端交互层 (Vue3)                      │
│              WebSocket实时通信 / 文件管理                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  API服务层 (FastAPI)                     │
│        REST API / WebSocket / 文件上传下载                │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              智能体编排层 (LangGraph)                     │
│         主智能体协调 / 子智能体调度 / 状态管理              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  工具执行层 (Tools)                       │
│   网络搜索 / 数据库查询 / 知识库检索 / 文档生成            │
└─────────────────────────────────────────────────────────┘
```

#### 2.2 核心模块设计

**1. 主智能体 (Main Agent)**
- 职责：任务分解、子智能体协调、结果整合
- 技术：基于`deepagents.create_deep_agent`工厂方法构建
- 特性：支持流式处理、工具调用、子智能体委托

**2. 子智能体 (Sub Agents)**

| 智能体名称 | 功能描述 | 核心工具 |
|-----------|---------|---------|
| 网络搜索助手 | 互联网公开信息检索 | Tavily Search API |
| 数据库查询助手 | 企业内部数据库查询 | MySQL Connector |
| RAGFlow助手 | 企业知识库检索 | RAGFlow SDK |

**3. API服务模块**
- REST API：任务提交、文件上传下载
- WebSocket：实时消息推送、进度反馈
- 会话管理：多用户并发、会话隔离

**4. 上下文管理模块**
- 技术：Python ContextVar实现协程级数据隔离
- 功能：会话目录管理、Thread ID绑定

---

### 三、核心技术栈

#### 3.1 后端技术栈

| 技术组件 | 版本 | 用途 |
|---------|------|------|
| Python | 3.13+ | 核心开发语言 |
| LangChain | 0.2.0+ | LLM应用框架 |
| LangGraph | 0.1.0+ | 智能体工作流编排 |
| FastAPI | 0.100.0+ | 异步Web框架 |
| Uvicorn | 0.20.0+ | ASGI服务器 |
| MySQL Connector | 8.0+ | 数据库驱动 |
| Tavily Python | 0.3.0+ | 网络搜索API |
| RAGFlow SDK | 0.1.0+ | 知识库SDK |

#### 3.2 前端技术栈

| 技术组件 | 版本 | 用途 |
|---------|------|------|
| Vue.js | 3.x | 前端框架 |
| TypeScript | 5.x | 类型安全 |
| Vite | 5.x | 构建工具 |
| Axios | 1.x | HTTP客户端 |
| Marked | 4.x | Markdown解析 |

#### 3.3 大模型服务

- 支持OpenAI API兼容接口
- 配置灵活，支持自定义Base URL
- 当前默认模型：GPT-4o-mini

---

### 四、数据流程设计

#### 4.1 任务执行流程

```
用户请求 → API接收 → 创建会话目录 → 设置上下文 
    → 主智能体启动 → 任务分解 → 子智能体调度 
    → 工具执行 → 结果汇总 → 文档生成 → WebSocket推送 
    → 清理上下文 → 返回结果
```

#### 4.2 WebSocket消息类型

| 事件类型 | 说明 | 数据结构 |
|---------|------|---------|
| session_created | 会话目录创建 | `{path: "/output/session_xxx"}` |
| tool_start | 工具调用开始 | `{tool_name, args}` |
| assistant_call | 子智能体调用 | `{assistant_name, args}` |
| task_result | 任务最终结果 | `{result: "..."}` |
| error | 错误信息 | `{message: "..."}` |

#### 4.3 会话数据隔离机制

**核心技术：Python ContextVar**

```python
# 存储当前会话目录
_session_dir_ctx: ContextVar[Optional[str]] = ContextVar("session_dir")

# 存储当前会话Thread ID
_thread_id_ctx: ContextVar[Optional[str]] = ContextVar("thread_id")
```

**隔离原理：**
- 每个异步任务(Task)拥有独立的上下文环境
- ContextVar自动隔离不同协程的数据
- 避免多用户并发时的数据串混

---

### 五、核心模块详解

#### 5.1 主智能体配置

```python
main_agent = create_deep_agent(
    model=model,                    # LLM模型实例
    system_prompt=system_prompt,    # 系统提示词
    tools=[generate_markdown, convert_md_to_pdf, read_file_content],
    checkpointer=InMemorySaver(),   # 状态持久化
    subagents=[                     # 子智能体列表
        database_query_agent,
        network_search_agent,
        knowledge_base_agent
    ]
)
```

#### 5.2 工具模块设计

**网络搜索工具 (tavily_tool.py)**
- 集成Tavily搜索API
- 支持普通/新闻/金融等多种主题
- 返回结构化搜索结果

**数据库查询工具 (db_tool.py)**
- `list_sql_tables`: 列出数据库表
- `get_table_data`: 预览表数据
- `execute_sql_query`: 执行自定义SQL

**知识库检索工具 (ragflow_tools.py)**
- `get_assistant_list`: 获取可用助手列表
- `create_ask_delete`: 创建会话提问并销毁

**文档生成工具 (markdown_tools.py / pdf_tools.py)**
- Markdown文档生成
- PDF格式转换

#### 5.3 监控模块 (monitor.py)

**设计模式：单例模式**

```python
class ToolMonitor:
    _instance = None
    
    def report_tool(self, tool_name, args):
        # 上报工具调用
        
    def report_assistant(self, assistant_name, args):
        # 上报子智能体调用
        
    def report_task_result(self, result):
        # 上报最终结果
```

**推送机制：**
- 通过WebSocket向特定Thread ID推送消息
- 使用`asyncio.run_coroutine_threadsafe`实现跨线程调度

---

### 六、部署与运行

#### 6.1 环境准备

```bash
# 克隆项目
git clone [项目地址]

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (.env文件)
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
TAVILY_API_KEY=your_tavily_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
```

#### 6.2 启动服务

```bash
# 启动后端服务
cd api
python server.py

# 启动前端服务
cd ui
npm install
npm run dev
```

#### 6.3 访问地址

- 后端API: http://localhost:8000
- 前端界面: http://localhost:5173
- API文档: http://localhost:8000/docs

---

### 七、项目结构

```
DeepSearchResearcher/
├── agent/                 # 智能体模块
│   ├── main_agent.py     # 主智能体
│   ├── llm.py            # LLM配置
│   ├── load_prompts.py   # 提示词加载
│   └── sub_agent/        # 子智能体
│       ├── network_search_agent.py
│       ├── database_query_agent.py
│       └── knowledge_base_agent.py
├── api/                   # API服务模块
│   ├── server.py         # FastAPI服务
│   ├── monitor.py        # 监控模块
│   ├── context.py        # 上下文管理
│   └── logger.py         # 日志模块
├── tools/                 # 工具模块
│   ├── tavily_tool.py    # 网络搜索
│   ├── db_tool.py        # 数据库查询
│   ├── ragflow_tools.py  # 知识库检索
│   ├── markdown_tools.py # Markdown生成
│   └── pdf_tools.py      # PDF转换
├── utils/                 # 工具函数
├── prompt/                # 提示词配置
│   └── prompts.yaml
├── ui/                    # 前端项目
│   └── src/
│       └── App.vue       # 主应用组件
├── output/                # 输出目录
├── updated/               # 上传文件目录
├── requirements.txt       # 依赖清单
└── README.md             # 项目文档
```

---

### 八、核心优势

1. **智能编排**：主智能体自动分解复杂任务，协调多个专业子智能体协作完成
2. **实时反馈**：通过WebSocket实时推送任务执行进度，用户体验友好
3. **数据隔离**：基于ContextVar实现协程级数据隔离，支持多用户并发
4. **扩展性强**：模块化设计，易于添加新的子智能体和工具
5. **配置灵活**：YAML配置提示词，环境变量管理敏感信息

---

### 九、应用场景

- 企业市场调研报告自动生成
- 竞品分析与行业研究
- 内部数据查询与分析报告
- 知识库问答与文档生成
- 多源信息整合与报告撰写

