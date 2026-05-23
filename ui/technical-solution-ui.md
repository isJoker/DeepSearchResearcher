# DeepSearchResearcher UI Technical Solution

## Overview
The `ui` directory hosts a Vue 3 + TypeScript SPA powered by Vite (ui/package.json:5-23). `main.ts` simply mounts `App.vue` (`ui/src/main.ts:0-4`), so the bulk of behavior resides in the single-file component at `ui/src/App.vue`.

## Key Components
### App.vue
- **State management** keeps the chat state (`messages`, `status`, `fileList`, etc.) in Vue `ref`s plus a computed flag for welcome mode (`ui/src/App.vue:27-38`). A persistent thread ID is seeded via `crypto.randomUUID()` so uploads/resumptions stay tied to a session (`ui/src/App.vue:38-40`).
- **WebSocket orchestration** (`connectWebSocket`, `handleSocketMessage`) opens `ws://localhost:8000/ws/` with the current thread ID. Incoming events (session creation, tool_start, assistant_call, task_result, error) mutate `messages`, `fileList`, and helper metadata (logs/files, timestamps) while keeping the sidebar in sync (`ui/src/App.vue:69-177`).
- **Message sending pipeline** handles text input, file uploads, and API calls. `sendMessage` guards against empty inputs, updates the UI with user/AI placeholders, uploads files via FormData to `/api/upload`, and posts prompts to `/api/task` (`ui/src/App.vue:180-297`). Upload progress and error handling are surfaced through structured logs attached to the latest AI message. File selection/removal logic lives next to the uploader helpers (`ui/src/App.vue:299-320`). Markdown rendering relies on `marked` with a fallback “Thinking…” indicator (`ui/src/App.vue:321-327`).
- **File list refresh** occurs on session creation, tool invocations, and task completions through `fetchFiles`, which calls `http://localhost:8000/api/files` and enriches each entry with a download URL (`ui/src/App.vue:50-66`). The sidebar shows these files when open (`ui/src/App.vue:472-494`).

## Data Flow and UX
1. The user composes text (or attaches files) and triggers `sendMessage` via the textarea or the send button (`ui/src/App.vue:432-465`).
2. The app pushes a user message followed by an empty AI message to keep the chat visually active, then uploads files (if any) before calling the backend task endpoint (`ui/src/App.vue:187-279`).
3. The backend responds with a new `thread_id` if necessary. The WebSocket handler updates the AI message content, appends thinking logs/files, and refreshes generated files whenever a tool runs or completes (`ui/src/App.vue:76-177`).
4. The file sidebar exposes newly generated artifacts via `currentSessionUrl` derived from the backend session path (`ui/src/App.vue:101-108`).

## Styling and Layout
The component defines a dark mode theme with CSS variables, responsive layout (chat area plus optional sidebar), and polished controls (file chips, buttons, logs, scrollbars) within the `<style>` block of `App.vue` (`ui/src/App.vue:498-1072`). Animations support file chip entrance and spinner activity indicators.

## Dependencies and Tooling
- Vue 3 + `<script setup>` syntax
- Axios for REST calls and uploads
- `marked` to render AI responses as Markdown
- Vite+rolldown for dev/build (`ui/package.json:5-27`, `ui/vite.config.ts`)
- TypeScript type coverage via `vue-tsc`

## Running and Iterating
1. `npm install` inside `ui` installs dependencies (including the custom `rolldown-vite` override).  
2. `npm run dev` launches the Vite dev server; the SPA communicates with `http://localhost:8000` for backend REST and WebSocket endpoints.  
3. `npm run build` runs `vue-tsc -b && vite build` if bundling is needed.

## Integration Notes
- The frontend assumes the backend exposes `/api/files`, `/api/download`, `/api/upload`, `/api/task`, and `ws://localhost:8000/ws/{thread}` with predictable payload shapes.  
- Session persistence relies on the backend returning absolute paths under `output` directories so the UI can point to `http://localhost:8000/outputs/...`.  
- File uploads include the thread ID in both FormData and the WebSocket route so that the server can correlate user input with existing sessions.

This document should serve as a technical reference when evolving the UI or explaining the chat pipeline to collaborators.