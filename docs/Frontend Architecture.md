# WebMorph Frontend Architecture

## Stack
- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + shadcn/ui
- **Icons:** Lucide React
- **Data Fetching:** Native `fetch` with server/client components (SWR/React Query optional, but native is preferred for MVP simplicity)

## Routing Structure
- `/` - **Overview Dashboard**: High-level view of system health, active collectors, and recent incidents.
- `/collectors/[id]` - **Collector Detail**: Deep dive into a specific collector's schema, history, and snapshots.
- `/incidents/[id]` - **Incident Detail**: The main demo screen showcasing the AI-driven healing lifecycle, code diffs, and approval mechanics.

## Component Architecture
- **Layouts**: Root layout with side navigation / top navigation.
- **UI Primitives**: Button, Badge, Card, Progress, Separator, Alert, Tabs, Table (via shadcn/ui).
- **Domain Components**:
  - `CollectorCard`: Summary of a collector.
  - `StatusBadge`: Consistent color-coding for standard statuses (e.g., ACTIVE, DIAGNOSING, AWAITING_APPROVAL).
  - `HealthGauge`: Circular or linear progress indicating the health score.
  - `IncidentTimeline`: A vertical step-by-step audit log of the incident lifecycle.
  - `HealingProposalCard`: Shows the AI diagnosis, root cause, and confidence score.
  - `CodeDiffViewer`: Highlights added/removed lines of code.

## State Management
- Server Components for initial data fetching (collectors, incidents).
- Client Components for interactive elements (Approve/Reject buttons, tab switching, live polling if necessary).

## API Integration
- Centralized API utility (`lib/api.ts`) pointing to `NEXT_PUBLIC_API_URL` (defaulting to `http://localhost:8000/api`).
- Endpoint mapping:
  - `GET /api/collectors`
  - `GET /api/collectors/{id}`
  - `GET /api/incidents`
  - `GET /api/incidents/{id}`
  - `POST /api/incidents/{id}/heal`
  - `POST /api/incidents/{id}/approve`
  - `POST /api/incidents/{id}/verify`
