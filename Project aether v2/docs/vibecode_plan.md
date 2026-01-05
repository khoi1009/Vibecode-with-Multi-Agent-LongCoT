**Agent 01 (Architect) Activated**

What would you like to build? I will start the Intake process.

Please describe:
1. The feature or problem you're solving.
2. Who will use it (end-users, admins, developers).
3. Any constraints (timeline, tech stack, performance).

I will ask follow-up questions as needed, then automatically generate the Blueprint and Contract.

---

**INTAKE STARTED**

Based on your prompt, we are building "Project Aether v2: A real-time collaborative AI analytics dashboard."

To ensure we capture all necessary requirements for a production-ready system, I need some clarifications.

**A. Universal Questions:**
1.  **Problem Solved:** Your description clearly states the need for real-time, collaborative AI analytics. This addresses the pain point of needing up-to-date business insights and shared understanding of dynamic data.
2.  **Who are the users?** (End-users, admins, API consumers?)
    *   It's implied end-users (analysts, business users) will interact with the dashboard. Are there any specific admin users with different permissions or API consumers for the AI insights?
3.  **MVP Scope:** The prompt outlines specific key features ("Deep Thought" Sidebar, Live Sales Feed, Cursor Presence). Are all of these strictly mandatory for the initial MVP, or can any be de-prioritized if time/resources become a constraint?
4.  **Success Criteria:** How do we objectively measure the success of "real-time" and "collaborative"? For example:
    *   What is the maximum acceptable latency for 'Live User Cursors' updates?
    *   What is the target update frequency/latency for the 'Live Sales Feed' beyond "every 3 seconds"?
    *   What is the target concurrent user count for the collaboration features?

**B. Domain-Specific Questions:**

**If Web App (Next.js 14+, Tailwind CSS v4, Recharts, Socket.io-client, Framer Motion, Lucide-React):**
*   **Authentication Strategy:** A collaborative dashboard will require user authentication. What is the preferred strategy (e.g., JWT, OAuth 2.0, Session-based, or a third-party service like Auth0/Clerk)?
*   **Mobile Responsiveness:** Should the dashboard be fully responsive across mobile, tablet, and desktop breakpoints, or is it primarily designed for desktop use?
*   **Accessibility Requirements:** Are there specific accessibility standards (e.g., WCAG 2.1 AA) that need to be met for the UI?

**If API/Backend (Node.js, TypeScript, Socket.io server, Prisma with SQLite, REST):**
*   **Backend Framework Choice:** You mentioned "Express or H3". Which one is the preferred choice for the backend? I will default to Express.js if not specified, due to its maturity and extensive ecosystem.
*   **Rate Limiting:** What are the requirements for rate limiting on the REST API endpoints to prevent abuse?
*   **API Versioning:** What is the preferred API versioning approach (e.g., `/api/v1/`, header-based)?
*   **Error Response Format:** What is the desired standard for API error responses (e.g., RFC 7807, or a custom JSON format with `code`, `message`, `details`)?

**If Data Processing (AI Insights, Live Sales Feed):**
*   **Data Volume/Velocity:** For the "Live Sales Feed" and "Deep Thought" Sidebar, what is the expected maximum data volume (e.g., records per second/minute) or data complexity in a production environment? This helps in scaling considerations, even if mock data is used initially.

Please provide answers to these questions. If some details are not yet decided, I can propose sensible defaults based on modern best practices for a "production-ready" application.