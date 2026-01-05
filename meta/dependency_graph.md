# Project Aether - Dependency Graph

```mermaid
graph TD
    User[Web Browser]
    
    subgraph Frontend [Next.js App Router]
        Page[src/app/page.tsx]
        Chart[SalesChart.tsx]
        Sidebar[InsightSidebar.tsx]
        Cursors[CollaborativeCursors.tsx]
        SocketClient[utils/socket.ts]
    end

    subgraph Backend [Node.js / Nitro]
        Server[server.ts]
        SocketServer[socket.ts]
        APIRoutes[/api/insights]
        Prisma[Prisma Client]
    end

    subgraph Database
        SQLite[(dev.db)]
    end

    User --> Page
    Page --> Chart
    Page --> Sidebar
    Page --> Cursors

    %% Real-time Data Flow
    SocketClient <-->|WebSocket Connection| SocketServer
    Chart <-->|Subscribe: sales-update| SocketClient
    Cursors <-->|Emit: cursor-move| SocketClient
    
    %% API Flow
    Sidebar -->|POST /api/insights| APIRoutes
    APIRoutes -->|Mock Query| AI_Logic[AI Service Mock]

    %% Data Persistence
    Server --> Prisma
    Prisma --> SQLite
```

## Data Flow Description
1.  **Real-time**: The `socket.ts` on the backend emits random simulated sales data every 1.5s. `SalesChart.tsx` listens to this event via `utils/socket.ts`.
2.  **Collaboration**: Mouse coordinates are emitted from `CollaborativeCursors.tsx` -> Backend -> Broadcast to all other clients.
3.  **AI Insights**: User prompts are sent via HTTP POST to `/api/insights`. The backend processes (mocks) the response and returns JSON.
