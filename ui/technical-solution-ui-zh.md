# DeepSearchResearcher UI 技术方案（中文版）

## 概览
`ui` 目录包含一个基于 Vue 3 + TypeScript 的单页应用（ui/package.json:5-27），由 Vite（rolldown-vite 7.2.5）驱动。`ui/src/main.ts:0-4` 仅负责挂载 `App.vue`，所以所有交互逻辑都集中在单个 `App.vue` 文件中（ui/src/App.vue:0-327）。

## 核心模块
### App.vue 的职责
- **状态管理** 使用 Vue `ref` 保存聊天内容、文件列表、当前状态、WebSocket 实例等（ui/src/App.vue:27-40）。会话线程 ID 通过 `crypto.randomUUID()` 生成，页面不刷新时保持不变，确保上传和后台任务可以继续沿用同一个上下文（ui/src/App.vue:38-40）。
- **WebSocket 连接** 由 `connectWebSocket` 负责，连接 `ws://localhost:8000/ws/{threadId}`。`handleSocketMessage` 处理 `session_created`、`tool_start`、`assistant_call`、`task_result` 和 `error` 事件，动态更新 `messages`、`fileList` 以及 AI 消息里的思维日志和文件列表，保证右侧文件栏实时展示新生成的产物（ui/src/App.vue:69-177）。
- **请求与上传流程**：`sendMessage` 会先验证输入，然后推入用户与 AI 占位消息，再处理文件上传（FormData 到 `/api/upload`）并调用 `/api/task`，同时把 `thread_id`/文件信息附到请求/日志里，错误时在系统消息里提示（ui/src/App.vue:180-297）。选中文件的添加/删除逻辑紧邻上传函数（ui/src/App.vue:299-320）。
- **文件刷新**：`fetchFiles` 通过 `/api/files` 获取当前 session 的文件列表并包装下载 URL（ui/src/App.vue:50-66），在 session 创建、工具启动、任务完成等节点刷新文件栏（ui/src/App.vue:101-167）。
- **Markdown 渲染与提示**：`renderMarkdown` 使用 `marked` 渲染 AI 内容，空文本显示 “Thinking...” 提示（ui/src/App.vue:321-327）。

## 数据流与用户体验
1. 用户在底部输入框或上传文件后点击发送，触发 `sendMessage`（ui/src/App.vue:432-465）。
2. 界面立即创建用户消息和占位 AI 消息；如果有文件，先上传再调用后端任务接口；后端如果返回新 `thread_id` 会更新前端（ui/src/App.vue:187-282）。
3. WebSocket 持续接收事件，更新 AI 消息内容、附上“思维”日志/文件链接，并在文件侧边栏中展示新生成文件（ui/src/App.vue:76-177、472-494）。
4. 文件下载地址依赖后端提供的 `output` 路径（ui/src/App.vue:101-107），确保点击时通过 `http://localhost:8000/outputs/...` 能访问。

## 样式与布局
`App.vue` 内嵌样式定义了深色主题变量、侧边栏+主体的 flex 布局、进度日志折叠面板、文件卡片、上传文件标签等视觉行为，并包括 spinner/动画、滚动条样式等（ui/src/App.vue:498-1072）。

## 依赖与构建
- Vue 3 + `<script setup>` 语法 + TypeScript
- Axios 用于 HTTP/文件上传
- `marked` 渲染 Markdown 响应
- Vite（基于 `rolldown-vite`）负责开发/打包（ui/package.json:5-27, ui/vite.config.ts）
- `vue-tsc` 做类型检查

## 运行说明
1. 在 `ui` 目录下运行 `npm install` 安装依赖。  
2. `npm run dev` 启动 Vite 开发服务器，前端通过 `http://localhost:8000` 的 REST/WebSocket 与后端通信。  
3. `npm run build` 会依次执行 `vue-tsc -b` 与 `vite build`，生成生产包。

## 后端集成约定
- 前端假设后端提供 `/api/files`、`/api/download`、`/api/upload`、`/api/task` 以及 `ws://localhost:8000/ws/{threadId}`。  
- 会话路径必须包含 `output` 目录，前端才能拼出 `http://localhost:8000/outputs/...` 链接。  
- 文件上传时会携带字段 `thread_id` 以便服务器将请求和现有会话关联起来。

以上内容可作为 UI 模块方案的中文参考文档，方便与团队同事或后续开发者沟通产品架构。