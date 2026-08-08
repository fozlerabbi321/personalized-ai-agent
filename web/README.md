# personalized_ai_agent — Web Client (Next.js)

> Next.js App Router · TypeScript · Tailwind CSS · Feature-First Architecture · Server-Driven UI (SDUI)

---

## 🚀 Quick Start

### 1. Prerequisites
Make sure the backend container is running:
```bash
# From root directory
make backend
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env.local
```

### 3. Run Development Server
```bash
npm run dev
# OR from root directory:
make frontend
```

The web application will be available at: **`http://localhost:3000`**

---

## 🏗️ Feature-First Folder Architecture

```
web/src/
├── app/                           # Next.js App Router Pages
│   ├── layout.tsx                # Root layout with AuthProvider & Theme
│   ├── page.tsx                  # Home page (login or chat)
│   ├── (chat)/chat/
│   │   ├── page.tsx              # New Chat
│   │   └── [sessionId]/page.tsx  # Load existing session
│   └── api/chat/stream/route.ts  # Next.js SSE proxy handler
│
├── features/                      # Feature Modules (Clean Architecture)
│   ├── auth/                     # Authentication feature
│   │   ├── components/LoginForm.tsx
│   │   ├── context/AuthContext.tsx
│   │   ├── services/authService.ts
│   │   └── types/
│   │
│   ├── sessions/                 # Chat History & Sessions feature
│   │   ├── components/
│   │   │   ├── SessionSidebar.tsx
│   │   │   └── SessionItem.tsx
│   │   ├── hooks/useSessions.ts
│   │   ├── services/sessionService.ts
│   │   └── types/
│   │
│   ├── chat/                     # Main Chat & SSE Streaming feature
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── InputBar.tsx
│   │   ├── hooks/useChat.ts
│   │   ├── services/chatService.ts
│   │   └── types/
│   │
│   └── widgets/                  # Server-Driven UI (SDUI) Engine
│       ├── WidgetRenderer.tsx    # Maps widget_type -> Component
│       ├── registry.ts           # Component lookup registry
│       ├── components/
│       │   ├── CandlestickChart.tsx  # Dynamic OHLC SVG chart
│       │   ├── MetricCard.tsx        # Financial metrics & sentiment
│       │   └── DataTable.tsx         # Structured tabular data
│       └── types/
│
└── shared/                        # Shared Utilities & UI Primitives
    ├── components/ui/            # Button, Input, Spinner, Avatar
    └── lib/cn.ts                 # Class merger utility
```

---

## 💡 How Server-Driven UI (SDUI) Works

1. **FastAPI Backend** emits a `widget` SSE event containing `widget_json` (e.g. `{ "widget_type": "candlestick_chart", ... }`).
2. **`useChat` Hook** receives the SSE event and attaches `widget_json` to the assistant's message.
3. **`MessageBubble`** renders `<WidgetRenderer widget={message.widget_json} />`.
4. **`WidgetRenderer`** inspects `widget_type` and resolves it dynamically via **`registry.ts`**, rendering custom interactive UI widgets without hardcoded layout logic in the chat system.
