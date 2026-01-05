**Agent 01 (Architect) Activated**

What would you like to build? I will start the Intake process.

Please describe:
1. The feature or problem you're solving.
2. Who will use it (end-users, admins, developers).
3. Any constraints (timeline, tech stack, performance).

I will ask follow-up questions as needed, then automatically generate the Blueprint and Contract.
✅ **INTAKE COMPLETE**
Requirements captured:
  - Feature: Real-time collaborative AI analytics dashboard ('Project Aether v2')
  - Users: End-users needing real-time sales analytics and AI insights.
  - Constraints: Next.js 14+ (App Router), Tailwind CSS v4 (Glassmorphism dark theme), Recharts, Socket.io (client/server), Node.js (Express), Prisma (SQLite), Framer Motion, Lucide React. Must be a monorepo. Real-time sales feed (3s update), live user cursors.
  
Next: Generating Blueprint...
✅ **BLUEPRINT DRAFT COMPLETE**
Architecture: Monorepo (Turborepo) with Next.js 14+ frontend (App Router, RSC/Client Components), Node.js (Express) backend, Prisma/SQLite for data, Socket.io for real-time.
Key Components: Frontend: DashboardLayout, LiveSalesFeed, AiInsightsSidebar, SalesChart, LiveCursors. Backend: Express API, SocketManager, AnalyticsService.
Dependencies: next, react, tailwindcss, socket.io-client, recharts, framer-motion, lucide-react, next-themes (frontend); express, socket.io, prisma, @prisma/client (backend); turbo (monorepo).

Next: Finalizing Contract...
# Blueprint: Project Aether v2 - Real-time Collaborative AI Analytics Dashboard
**Status:** FINAL CONTRACT
**Architect:** Agent 01
**Date:** 2024-07-30
**Estimated Complexity:** High

---

## 1. Executive Summary
Develop 'Project Aether v2', a production-ready real-time collaborative AI analytics dashboard. It features a Next.js 14+ frontend with Glassmorphism styling, Recharts visualizations, and live user cursors via Socket.io. The Node.js (Express) backend serves historical data and real-time sales/cursor events using Socket.io and Prisma with SQLite. The entire project will be structured as a Turborepo monorepo.

---

## 2. The Contract (Type Definitions)

**CRITICAL:** Agent 02 must use these EXACT interfaces. No deviations.

```typescript
// packages/types/src/index.ts

/**
 * Interface for real-time or historical sales data.
 */
interface ISalesData {
  id: string;
  amount: number;
  product: string;
  region: string;
  timestamp: string; // ISO 8601 string
}

/**
 * Interface for live user cursor positions.
 */
interface IUserCursor {
  clientId: string; // Unique ID for each browser tab/client instance
  username?: string; // Optional display name for the cursor
  x: number;
  y: number;
}

/**
 * Interface for mock AI predictive insights.
 */
interface IAiInsight {
  id: string;
  timestamp: string; // ISO 8601 string
  insight: string;
  prediction: string;
  confidence: number; // 0-1 range
}

/**
 * Standard API response wrapper.
 * @template T The type of the data returned by the API.
 */
type ApiResponse<T> = {
  data: T;
  error: string | null;
  status: number;
}
```

**Prisma Schema (apps/backend/prisma/schema.prisma):**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = env("DATABASE_URL")
}

model Sales {
  id        String    @id @default(uuid())
  amount    Float
  product   String
  region    String
  timestamp DateTime  @default(now())
}

model UserSession {
  id           String    @id @default(uuid())
  clientId     String    @unique // Unique ID for each browser tab/client instance (stored in localStorage)
  socketId     String?   @unique // Current active socket connection for this client
  lastActive   DateTime  @default(now())
  cursorX      Float     @default(0)
  cursorY      Float     @default(0)
  username     String?   // Optional display name for the cursor
}
```

**Validation Rules:**
- All user inputs must be validated with Zod before processing (especially for API routes).
- All API responses must conform to `ApiResponse<T>`.

---

## 3. Component Architecture

### Monorepo Root Structure (`project-aether-v2/`)
*   **File Path:** `./turbo.json`
*   **Responsibility:** Turborepo pipeline configuration for `build`, `dev`, `lint`, `test` tasks across `frontend` and `backend` apps.
*   **Design Decision:** Turborepo is chosen for efficient monorepo management, task orchestration, and caching, as per `web-frameworks` skill.

*   **File Path:** `./package.json`
*   **Responsibility:** Root workspace setup, shared dev dependencies (e.g., `turbo`, `typescript`), and common scripts to run tasks across packages.

*   **File Path:** `./apps/frontend/`
*   **Responsibility:** Next.js 14+ application with App Router.

*   **File Path:** `./apps/backend/`
*   **Responsibility:** Node.js (Express) application with Socket.io server.

*   **File Path:** `./packages/types/`
*   **Responsibility:** Contains shared TypeScript interfaces (`ISalesData`, `IUserCursor`, `IAiInsight`, `ApiResponse<T>`) used by both frontend and backend.
*   **Design Decision:** Centralizing types prevents duplication and