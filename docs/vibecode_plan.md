# Project Aether: Real-time Collaborative AI Analytics Dashboard - Implementation Plan

**Contract Level:** Full Contract (Level A) - Required for new features and architecture changes.

## 1. Project Overview

"Project Aether" is envisioned as a high-performance, real-time collaborative AI analytics dashboard, specifically tailored for global fintech operations. It will deliver dynamic sales data, AI-driven insights, and interactive collaborative features, ensuring a robust and insightful user experience.

## 2. Tech Stack Specification

*   **Frontend:** Next.js 16 (App Router), React Server Components (RSC), Tailwind CSS, Framer Motion for micro-animations, Recharts with custom themes.
*   **Backend:** Node.js (h3/Nitro) for API routes, Socket.io for real-time WebSocket data streaming.
*   **Database:** PostgreSQL, managed via Prisma ORM.
*   **AI Layer:** Gemini 3 Flash SDK for natural language querying.
*   **Authentication:** Clerk (logic-only; will use a mock provider if API keys are absent to guarantee build completion).

## 3. Core Features & Acceptance Criteria

### A. Real-time "Global Sales" Feed
*   **Description:** A dynamic dashboard component that displays simulated global sales data in real-time.
*   **Acceptance Criteria:**
    *   Data streamed continuously via a dedicated WebSocket (Socket.io) channel.
    *   Sales figures and related metrics update every 1-3 seconds.
    *   Each data point includes `timestamp`, `region`, `product_category`, `amount`, `currency`.
    *   Data is visually represented using Recharts, adhering to custom themes.

### B. AI Insight Sidebar
*   **Description:** An interactive chat interface that enables users to query dashboard data using natural language prompts.
*   **Acceptance Criteria:**
    *   A dedicated sidebar UI featuring an input field for queries and a scrollable chat history.
    *   Seamless integration with the Gemini 3 Flash SDK for natural language processing.
    *   Natural language queries are translated into precise database queries (via Prisma) to retrieve relevant data.
    *   Responses provide clear, data-driven insights (e.g., "Sales dipped in Q3 due to a regional slowdown in EMEA, primarily impacting the 'Wealth Management' product category.").

### C. Collaborative Cursors
*   **Description:** Visual indicators on the dashboard displaying the real-time positions of other active users' cursors.
*   **Acceptance Criteria:**
    *   Real-time cursor position updates broadcast and received via WebSocket.
    *   Each active user's cursor is represented by a distinct, identifiable visual element (e.g., unique color, small user avatar/initials).
    *   Cursor movements are smooth, leveraging Framer Motion for micro-animations.
    *   Positions are accurately rendered relative to the dashboard viewport.

### D. Automatic Reporting
*   **Description:** A scheduled backend task responsible for generating and distributing weekly PDF summaries of dashboard data and key AI insights.
*   **Acceptance Criteria:**
    *   A robust backend scheduling mechanism (e.g., `node-cron`) configured to run weekly.
    *   Generates a professional PDF document summarizing critical sales metrics, performance trends, and AI-generated insights.
    *   (Future Enhancement v1.1): Integration for automated email delivery of the generated PDF reports.

## 4. Detailed Implementation Plan

### Phase 1: Environment Setup & Core Infrastructure
*   **Task 1.1: Project Initialization**
    *   Initialize a new Next.js 16 project using the App Router, configuring TypeScript and Tailwind CSS.
    *   Establish `tsconfig.json` for essential path aliases (e.g., `@/`).
*   **Task 1.2: Database Setup (PostgreSQL & Prisma)**
    *   Install Prisma CLI and Prisma Client.
    *   Define the initial `schema.prisma` for `User`, `Workspace`, `DataStream`, and `Insight` models.
    *   Execute `npx prisma migrate dev --name init` to apply the schema.
    *   Develop `prisma/seed.ts` to populate the database with realistic, high-volume seed data for a Global Fintech company.
    *   Run `npx prisma db seed` to apply the seed data.
*   **Task 1.3: Backend (h3/Nitro & Socket.io)**
    *   Create a `server/` directory to host the h3/Nitro backend logic.
    *   Configure `socket.io` for robust WebSocket communication.
    *   Integrate the h3/Nitro backend either via Next.js API routes or as a separate, dedicated server process.
*   **Task 1.4: Authentication (Clerk Mock Provider)**
    *   Implement a mock Clerk provider/context to handle authentication logic, ensuring the application can run even without live Clerk API keys.

### Phase 2: Backend API & Real-time Data Services
*   **Task 2.1: REST API Routes**
    *   Develop core API routes (`/api/sales`, `/api/insights`, `/api/users`, `/api/workspaces`) for initial dashboard data fetching.
    *   Implement efficient Prisma queries to retrieve and filter data based on request parameters.
*   **Task 2.2: WebSocket Data Stream (Global Sales)**
    *   Implement a Socket.io server endpoint (`/ws/sales`) dedicated to streaming real-time simulated sales data.
    *   Ensure data generation and streaming are highly performant and consistent.
*   **Task 2.3: AI Integration (Gemini 3 Flash SDK)**
    *   Create a backend API endpoint (`/api/ai-query`) to receive and process natural language queries from the frontend.
    *   Integrate the Gemini 3 Flash SDK to interpret queries, dynamically construct Prisma queries, and return insightful responses.
*   **Task 2.4: Automatic Reporting Logic**
    *   Implement a scheduled task (e.g., using `node-cron`) within the backend to trigger weekly PDF report generation.
    *   Utilize a suitable PDF generation library (e.g., `pdfkit`, `html-pdf`, or `puppeteer` for advanced rendering) to create comprehensive reports.

### Phase 3: Frontend Component Library & Dashboard UI
*   **Task 3.1: Base UI Components**
    *   Develop a foundational library of reusable Tailwind CSS components (e.g., `Button`, `Card`, `Input`, `Modal`).
    *   Define and apply a custom, HSL-tailored branded color palette featuring "Deep Indigo" and "Neon Teal."
*   **Task 3.2: Chart Components (Recharts)**
    *   Create a `SalesChart` component utilizing Recharts to visualize the real-time sales feed.
    *   Ensure custom branded themes are consistently applied to all chart elements.
*   **Task 3.3: Navigation & Layout**
    *   Design and implement a responsive dashboard layout, including a persistent `Sidebar`, `Header`, and the primary `Main Content Area`.
    *   Implement intuitive navigation elements.
*   **Task 3.4: Real-time Sales Feed Integration**
    *   Connect the `SalesChart` and other relevant UI elements to the `/ws/sales` WebSocket stream.
    *   Ensure smooth and efficient rendering of streaming data on the dashboard.
*   **Task 3.5: AI Insight Sidebar UI**
    *   Implement the complete user interface for the AI insight sidebar, including message display and input handling.
    *   Integrate with the backend `/api/ai-query` endpoint for sending and receiving chat messages.
*   **Task 3.6: Collaborative Cursors Frontend**
    *   Implement the client-side WebSocket connection for receiving and broadcasting cursor position data.
    *   Develop dynamic cursor components, using Framer Motion for fluid and visually appealing animations.

## 5. Design Philosophy Adherence

*   **Visual Excellence:** Strict adherence to custom HSL-tailored palettes (Deep Indigo & Neon Teal), meticulous spacing, and sophisticated micro-animations powered by Framer Motion.
*   **High-Performance:** Strategic use of Next.js App Router and React Server Components, optimized data fetching, robust caching strategies, and efficient client-side rendering.
*   **Zero Placeholders:** All content, including mock data, will be realistic and representative of a Global Fintech company, avoiding "Lorem Ipsum" or generic placeholders.

## 6. Testing Strategy

*   **Unit Tests (Jest/Vitest):** Comprehensive testing for individual functions, utility helpers, and isolated business logic (e.g., data processing, API handler logic).
*   **Integration Tests:** Validate the interaction between different layers, including API routes, WebSocket connections, and Prisma database operations.
*   **End-to-End Tests (Playwright):**
    *   Verify successful rendering and display of all dashboard data.
    *   Confirm real-time updates via WebSocket simulation are functional and accurate.
    *   Test the full interaction flow of the AI chat sidebar.
    *   Validate the visibility and smooth movement of collaborative cursors.
    *   Ensure UI responsiveness and accessibility across various breakpoints.

## 7. Rollback Plan

*   **Database:** Prisma's migration system provides robust capabilities to roll back to previous database schema states if issues arise.
*   **Codebase:** All changes will be managed under Git version control, allowing for immediate and reliable rollback to any prior commit.

## 8. Completion Criteria

The project build will be considered complete upon the following:
*   The application is successfully running and accessible in the Antigravity preview environment.
*   All Playwright end-to-end tests pass with a "Green" status.
*   A final `walkthrough.md` artifact is generated, demonstrating all working features.
