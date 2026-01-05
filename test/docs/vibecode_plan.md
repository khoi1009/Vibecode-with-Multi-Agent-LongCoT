**Agent 01 (Architect) Activated**

What would you like to build? I will start the Intake process.

Please describe:
1. The feature or problem you're solving.
2. Who will use it (end-users, admins, developers).
3. Any constraints (timeline, tech stack, performance).

I will ask follow-up questions as needed, then automatically generate the Blueprint and Contract.

---

✅ **INTAKE COMPLETE**
Requirements captured:
  - Feature: Real-time collaborative AI analytics dashboard ('Project Aether').
  - Users: End-users (business users, analysts, decision-makers) who need collaborative, real-time insights.
  - Constraints: Next.js 14+ (App Router), Tailwind CSS v4 (Glassmorphism dark theme), Recharts, Socket.io (client/server), Node.js (Express), TypeScript, Prisma (SQLite), Framer Motion, Lucide React. Must be a monorepo (frontend/backend). Real-time sales updates (3s), live user cursors.

**Sensible Defaults / Clarifications Applied:**
*   **Authentication Strategy:** For MVP, user identification for collaboration (cursor presence) will rely on a unique, anonymous `userId` generated client-side and managed in `UserSession` model for presence tracking. Full user authentication (login/signup) is deferred to v2.
*   **Backend Framework:** Express.js is chosen for its maturity and robust Socket.io integration.
*   **AI Insights Streaming:** Mock predictive analytics will be streamed over the existing Socket.io connection to consolidate real-time communication.

Next: Generating Blueprint...

---

✅ **BLUEPRINT DRAFT COMPLETE**
Architecture: Monorepo with Next.js (Frontend) and Node.js/Express (Backend). Real-time communication via Socket.io. Data persistence with Prisma/SQLite.
Key Components: DashboardLayout, LiveSalesFeed, SalesChart, AiInsightsSidebar, CursorOverlay (Frontend); SocketService, SalesService, AiService (Backend).
Dependencies: next, react, react-dom, tailwindcss, postcss, autoprefixer, socket.io-client, recharts, framer-motion, lucide-react, next-themes (Frontend); express, socket.io, prisma, @prisma/client, typescript, ts-node, nodemon, zod (Backend); turbo (Monorepo).

Next: Finalizing Contract...

---

✅ **CONTRACT FINALIZED**
Location: `docs/vibecode_plan.md`
Status: APPROVED FOR CONSTRUCTION

Next: Hand off to Agent 02 (Builder).
Gate: Agent 04 will review before merge.

---

# Blueprint: Project Aether v2
**Status:** FINAL CONTRACT
**Architect:** Agent 01
**Date:** 2024-07-30
**Estimated Complexity:** High

---

## 1. Executive Summary
This blueprint details the architecture and implementation plan for 'Project Aether v2', a real-time collaborative AI analytics dashboard. It will feature a Next.js frontend with a custom Glassmorphism dark theme, real-time data visualizations using Recharts, live user cursor tracking, and a Node.js/Express backend handling real-time sales data, mock AI insights, and historical analytics via Prisma and SQLite. The project will be structured as a Turborepo monorepo.

---

## 2. The Contract (Type Definitions)

**CRITICAL:** Agent 02 must use these EXACT interfaces. No deviations.

```typescript
// packages/types/src/index.ts
// Shared types for frontend and backend

export interface ISalesData {
  id: string;
  amount: number;
  productName: string;
  timestamp: string; // ISO 8601 string
}

export interface ICursorPosition {
  id: string; // Unique ID for the specific cursor instance (e.g., socket.id)
  userId: string; // Anonymous user ID for the session
  x: number;
  y: number;
  pageId: string; // Identifier for the current page/view
}

export interface IAiInsight {
  id: string;
  timestamp: string; // ISO 8601 string
  insight: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  confidence: number; // 0-1 for mock purposes
}

// Socket.io event definitions
export interface ServerToClientEvents {
  'sales-update': (data: ISalesData) => void;
  'cursor-move': (data: ICursorPosition) => void;
  'ai-insight-stream': (data: IAiInsight) => void;
  'user-disconnected': (userId: string) => void;
}

export interface ClientToServerEvents {
  'cursor-move': (data: Omit<ICursorPosition, 'id'>) => void; // Client sends userId, x, y, pageId
  'register-user': (userId: string) => void; // Client registers its anonymous userId
}

// Backend Prisma Schema (will be in apps/backend/prisma/schema.prisma)
// Note: Cursor positions are ephemeral and not persisted in DB.
// UserSession is for tracking active users, not cursor coords.
interface SalesDB { // Represents Prisma model
  id: string;
  amount: number;
  productName: string;
  timestamp: Date;
}

interface UserSessionDB { // Represents Prisma model
  id: string; // Prisma's own ID for the session
  userId: string; // Unique anonymous ID provided by client
  lastSeen: Date;
  createdAt: Date;
}
```

**Validation Rules:**
- All API inputs (REST and Socket.io) must be validated with Zod before processing.
- All API responses must conform to expected data structures.

---

## 3. Component Architecture

### Monorepo Root (`./`)
*   **File Path:** `package.json`, `turbo.json`, `pnpm-workspace.yaml` (or `package.json` for npm/yarn workspaces).
*   **Responsibility:** Define workspace, global scripts, and Turborepo pipeline.

### Frontend Application (`apps/frontend`)

#### Module A: Root Layout & Theme
*   **File Path:** `apps/frontend/app/layout.tsx`
*   **Responsibility:** Global layout, `ThemeProvider` for dark mode, `SocketProvider` wrapper.
*   **Props (Input):** `children: React.ReactNode`
*   **State Management:** `next-themes` for theme state, `SocketContext` for Socket.io instance.
*   **Dependencies:** `next-themes`, `@repo/types`, `socket.io-client` (via `useSocket`).

#### Module B: Dashboard Page
*   **File Path:** `apps/frontend/app/page.tsx`
*   **Responsibility:** Orchestrates main dashboard components.
*   **Props (Input):** None (uses Server Component capabilities).
*   **Dependencies:** `DashboardLayout`, `Suspense`.

#### Module C: Dashboard Layout
*   **File Path:** `apps/frontend/components/dashboard/DashboardLayout.tsx`
*   **Responsibility:** Provides the overall two-column layout (main content + AI sidebar) and wraps other dashboard components.
*   **Props (Input):** `children: React.ReactNode`
*   **Styling:** Uses Tailwind CSS for responsive grid layout and Glassmorphism effects.
*   **Dependencies:** `AiInsightsSidebar`, `LiveSalesFeed`, `SalesChart`, `CursorOverlay`.

#### Module D: Live Sales Feed
*   **File Path:** `apps/frontend/components/dashboard/LiveSalesFeed.tsx`
*   **Responsibility:** Displays a ticker of real-time sales data received via Socket.io. Updates every 3 seconds.
*   **Props (Input):** None (fetches data via hook).
*   **State Management:** Local state to hold incoming sales data.
*   **Dependencies:** `useSocket`, `@repo/types`.
*   **Error Handling:** Displays a message if socket connection fails.

#### Module E: Sales Chart
*   **File Path:** `apps/frontend/components/dashboard/SalesChart.tsx`
*   **Responsibility:** Visualizes sales data (historical and real-time) using Recharts.
*   **Props (Input):** None (fetches data via hook).
*   **State Management:** Local state for chart data, updated by historical REST calls and real-time Socket.io events.
*   **Dependencies:** `recharts`, `useSocket`, `apiClient.ts`, `@repo/types`.
*   **Error Handling:** Displays a fallback UI if data fetching fails.

#### Module F: AI Insights Sidebar
*   **File Path:** `apps/frontend/components/dashboard/AiInsightsSidebar.tsx`
*   **Responsibility:** Streams mock predictive analytics insights from the backend.
*   **Props (Input):** None (subscribes via hook).
*   **State Management:** Local state to accumulate streamed insights.
*   **Dependencies:** `useSocket`, `@repo/types`.

#### Module G: Cursor Overlay
*   **File Path:** `apps/frontend/components/dashboard/CursorOverlay.tsx`
*   **Responsibility:** Renders the cursors of other active users on the screen.
*   **Props (Input):** None (subscribes via hook).
*   **State Management:** Local state to store and update positions of other users' cursors.
*   **Dependencies:** `useSocket`, `useCursorTracking`, `framer-motion`, `@repo/types`.

#### Module H: Socket Context & Hook
*   **File Path:** `apps/frontend/hooks/useSocket.ts`, `apps/frontend/lib/socket.ts`, `apps/frontend/context/SocketContext.tsx`
*   **Responsibility:** Provides a global Socket.io client instance and hooks for components to subscribe to real-time events. Manages connection/disconnection.
*   **Functions:**
    1. `useSocket(): { socket: Socket | null, isConnected: boolean }`
    2. `SocketProvider`: React Context Provider.
*   **Dependencies:** `socket.io-client`, `react`.

#### Module I: Cursor Tracking Hook
*   **File Path:** `apps/frontend/hooks/useCursorTracking.ts`
*   **Responsibility:** Tracks the local user's cursor position and emits `cursor-move` events via Socket.io. Subscribes to other users' `cursor-move` events.
*   **Functions:**
    1. `useCursorTracking(pageId: string): Map<string, ICursorPosition>`: Returns a map of other users' cursor positions.
*   **Dependencies:** `useSocket`, `@repo/types`.

#### Module J: Glassmorphism Theme
*   **File Path:** `apps/frontend/tailwind.config.ts`, `apps/frontend/app/globals.css`
*   **Responsibility:** Configure Tailwind CSS with custom colors, blur utilities, and a dark theme that implements the Glassmorphism aesthetic.
*   **Dependencies:** `tailwindcss`, `postcss`, `autoprefixer`.

### Backend Application (`apps/backend`)

#### Module K: Entry Point & Server Setup
*   **File Path:** `apps/backend/src/index.ts`
*   **Responsibility:** Initializes Express app, HTTP server, Socket.io server, connects to Prisma, and sets up routes.
*   **Dependencies:** `express`, `socket.io`, `@prisma/client`, `salesService`, `socketService`.

#### Module L: REST API Routes
*   **File Path:** `apps/backend/src/routes/api.ts`
*   **Responsibility:** Defines REST endpoints for historical analytics data (e.g., `/api/sales/history`).
*   **Functions:**
    1. `GET /api/sales/history`: Fetches historical sales data from the database.
        - Query params: `startDate`, `endDate`, `limit`.
        - Returns `ISalesData[]`.
*   **Dependencies:** `express`, `salesService`, `zod` (for query param validation).

#### Module M: Socket Service
*   **File Path:** `apps/backend/src/services/socketService.ts`
*   **Responsibility:** Manages Socket.io connections and event handling for `sales-update`, `cursor-move`, `ai-insight-stream`, and `register-user`. Emits real-time data.
*   **Functions:**
    1. `initSocket(io: Server)`: Sets up all Socket.io listeners and emitters.
    2. `emitSalesUpdate(data: ISalesData)`: Emits a new sales data point to all clients.
    3. `emitAiInsight(data: IAiInsight)`: Emits a new AI insight to all clients.
    4. `handleCursorMove(socket: Socket, data: Omit<ICursorPosition, 'id'>)`: Broadcasts cursor movement to other clients.
    5. `handleRegisterUser(socket: Socket, userId: string)`: Registers a user session.
*   **State Management:** In-memory map to track active user sessions and their latest cursor positions.
*   **Dependencies:** `socket.io`, `userService`, `aiService`, `@repo/types`.

#### Module N: Sales Service
*   **File Path:** `apps/backend/src/services/salesService.ts`
*   **Responsibility:** Handles all sales data logic, including database interactions (Prisma).
*   **Functions:**
    1. `getHistoricalSales(startDate?: Date, endDate?: Date, limit?: number): Promise<ISalesData[]>`: Queries historical sales data.
    2. `generateMockSales(): Promise<ISalesData>`: Creates and persists a new mock sales record, then returns it.
*   **Dependencies:** `@prisma/client`, `@repo/types`.

#### Module O: AI Service
*   **File Path:** `apps/backend/src/services/aiService.ts`
*   **Responsibility:** Generates mock AI insights and streams them via Socket.io.
*   **Functions:**
    1. `startMockInsightStream(io: Server)`: Initiates a recurring task to generate and emit mock AI insights.
    2. `generateMockInsight(): IAiInsight`: Creates a new mock AI insight.
*   **Dependencies:** `socket.io`, `@repo/types`.

#### Module P: User Service
*   **File Path:** `apps/backend/src/services/userService.ts`
*   **Responsibility:** Manages user sessions in the database (Prisma).
*   **Functions:**
    1. `upsertUserSession(userId: string): Promise<UserSessionDB>`: Creates or updates a user session record.
    2. `removeUserSession(userId: string): Promise<void>`: Removes a user session.
*   **Dependencies:** `@prisma/client`, `@repo/types`.

#### Module Q: Prisma Schema & Seed
*   **File Path:** `apps/backend/prisma/schema.prisma`, `apps/backend/prisma/seed.ts`
*   **Responsibility:** Defines the database schema for `Sales` and `UserSession` models and provides initial seed data.
*   **Dependencies:** `prisma`.

### Shared Types Package (`packages/types`)
*   **File Path:** `packages/types/src/index.ts`, `packages/types/package.json`
*   **Responsibility:** Centralized definition of shared TypeScript interfaces and types, consumed by both frontend and backend.
*   **Dependencies:** `typescript`.

---

## 4. Implementation Checklist (Sequential Steps)

**Agent 02 must complete in this order:**

1.  [ ] **Monorepo Setup:**
    *   [ ] Initialize Turborepo monorepo: `npx create-turbo@latest project-aether-v2 --pnpm` (or preferred package manager).
    *   [ ] Create `apps/frontend` (Next.js 14+) and `apps/backend` (Node.js/Express) directories.
    *   [ ] Create `packages/types` directory.
    *   [ ] Update root `package.json` and `turbo.json` with initial scripts and pipeline for `build`, `dev`, `lint` tasks for `frontend`, `backend`, and `types`.
2.  [ ] **Shared Types:**
    *   [ ] Create `packages/types/package.json` and `packages/types/tsconfig.json`.
    *   [ ] Define `ISalesData`, `ICursorPosition`, `IAiInsight`, `ServerToClientEvents`, `ClientToServerEvents` interfaces in `packages/types/src/index.ts`.
3.  [ ] **Backend Initialization (`apps/backend`):**
    *   [ ] Initialize Node.js/Express project with TypeScript.
    *   [ ] Install `express`, `socket.io`, `prisma`, `@prisma/client`, `zod`, `typescript`, `ts-node`, `nodemon`.
    *   [ ] Configure `tsconfig.json` for backend.
    *   [ ] Set up Prisma: `npx prisma init --datasource-provider sqlite`.
    *   [ ] Define `Sales` and `UserSession` models in `apps/backend/prisma/schema.prisma`.
    *   [ ] Create `apps/backend/prisma/seed.ts` for mock sales data generation.
    *   [ ] Run `npx prisma migrate dev --name init` to apply schema.
4.  [ ] **Backend Services:**
    *   [ ] Implement `salesService.ts` with `getHistoricalSales` and `generateMockSales`.
    *   [ ] Implement `userService.ts` with `upsertUserSession` and `removeUserSession`.
    *   [ ] Implement `aiService.ts` with `startMockInsightStream` and `generateMockInsight`.
    *   [ ] Implement `socketService.ts` to manage all Socket.io events (`sales-update`, `cursor-move`, `ai-insight-stream`, `register-user`, `user-disconnected`).
5.  [ ] **Backend Server:**
    *   [ ] Set up `apps/backend/src/index.ts` to initialize Express, Socket.io, Prisma, and connect services.
    *   [ ] Define REST endpoint `GET /api/sales/history` in `apps/backend/src/routes/api.ts` using `salesService`.
    *   [ ] Ensure `npm run dev` in `apps/backend` starts the server and Socket.io.
6.  [ ] **Frontend Initialization (`apps/frontend`):**
    *   [ ] Initialize Next.js 14+ project with App Router, TypeScript, and ESLint.
    *   [ ] Install `tailwindcss`, `postcss`, `autoprefixer`, `next-themes`, `socket.io-client`, `recharts`, `framer-motion`, `lucide-react`.
    *   [ ] Configure `tailwind.config.ts` and `app/globals.css` for base Tailwind and Glassmorphism dark theme (using `backdrop-filter: blur()`).
7.  [ ] **Frontend Real-time Core:**
    *   [ ] Create `apps/frontend/context/SocketContext.tsx` and `apps/frontend/hooks/useSocket.ts` to provide and consume the Socket.io client instance.
    *   [ ] Wrap root `apps/frontend/app/layout.tsx` with `ThemeProvider` and `SocketProvider`.
    *   [ ] Implement `apps/frontend/hooks/useCursorTracking.ts` to send local cursor data and receive/manage other cursors.
8.  [