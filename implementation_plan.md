# Project Aether: Full-Stack Autonomous Build Plan

## 1. Overview

This document outlines the comprehensive implementation plan for "Project Aether," a production-ready, real-time collaborative AI analytics dashboard. The build will prioritize visual excellence, high performance, and robust functionality, following a strict autonomous workflow with zero intervention.

**Tech Stack:**
*   **Frontend:** Next.js 16 (App Router), Tailwind CSS, Framer Motion, Recharts
*   **Backend:** Node.js (h3/Nitro), WebSocket (Socket.io)
*   **Database:** Prisma ORM, PostgreSQL
*   **AI Layer:** Gemini 3 Flash SDK
*   **Auth:** Clerk (logic-only, mock provider if API keys missing)

**Core Features:**
*   Real-time "Global Sales" feed (WebSocket)
*   AI Insight Sidebar (chat interface, DB querying)
*   Collaborative Cursors (visual indicators)
*   Automatic Reporting (scheduled PDF summary)

**Design Philosophy:**
*   Visual Excellence: HSL-tailored palettes (Deep Indigo & Neon Teal), micro-animations.
*   High-Performance: React Server Components (RSC), optimized caching.
*   Zero Placeholders: Realistic data for a Global Fintech company.

## 2. Environment Setup

### 2.1. Repository Initialization
*   Initialize a new Next.js project with TypeScript, ESLint, Tailwind CSS.
*   Configure `jsconfig.json` or `tsconfig.json` for path aliases.
*   Initialize Git repository.

### 2.2. Core Dependencies Installation
*   **Frontend:**
    *   `next@16`
    *   `react`, `react-dom`
    *   `tailwindcss`, `postcss`, `autoprefixer`
    *   `framer-motion`
    *   `recharts`
    *   `socket.io-client`
    *   `@clerk/nextjs` (for Auth, with mock fallback)
    *   `@google/generative-ai` (Gemini SDK)
*   **Backend (Shared/Root level for h3/Nitro):**
    *   `h3`
    *   `nitro`
    *   `socket.io`
    *   `prisma`, `@prisma/client`
    *   `pg` (PostgreSQL client, may be implicitly handled by Prisma)
    *   `dotenv`
    *   `pdfkit` (for PDF generation)
    *   `node-schedule` (for automatic reporting)
*   **Development & Testing:**
    *   `typescript`, `eslint`, `prettier`
    *   `jest` / `vitest` (for unit tests, if not already configured by Next.js init)
    *   `@playwright/test` (for E2E tests)

### 2.3. Project Structure
