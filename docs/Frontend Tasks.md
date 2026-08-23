# WebMorph Frontend Tasks

## Phase 1: Setup & Scaffolding
- [ ] Initialize Shadcn/UI (configure `components.json`, Tailwind config for dark mode).
- [ ] Install essential Shadcn components (Button, Card, Badge, Progress, Tabs, Separator, Table, ScrollArea).
- [ ] Install `lucide-react` and `date-fns`.
- [ ] Create `lib/api.ts` for strictly typed fetch wrappers communicating with `http://localhost:8000`.

## Phase 2: Core Layout & Navigation
- [ ] Create top navigation bar with WebMorph logo/branding.
- [ ] Create global layout wrapper forcing dark mode.

## Phase 3: Overview Dashboard (`/app/page.tsx`)
- [ ] Fetch and display active collectors from `/api/collectors`.
- [ ] Fetch and display recent incidents from `/api/incidents`.
- [ ] Build `CollectorSummaryCard` (showing URL, health score, state).
- [ ] Build `IncidentList` (showing severity, status, created_at).

## Phase 4: Collector Detail (`/app/collectors/[id]/page.tsx`)
- [ ] Fetch collector and snapshots from `/api/collectors/{id}` and `/api/collectors/{id}/snapshots`.
- [ ] Build Header with status badge and overall health.
- [ ] Build Schema Contract viewer (read-only JSON/code block).
- [ ] Build Snapshot history table.

## Phase 5: Incident Detail & Healing Flow (`/app/incidents/[id]/page.tsx`) - *MAIN DEMO*
- [ ] Fetch incident from `/api/incidents/{id}` (includes `healing_events` and `audit_events`).
- [ ] Build Incident Header (Severity, Status, Target).
- [ ] Build `IncidentTimeline` component iterating over `audit_events`.
- [ ] Build `HealingProposalCard`:
  - Show AI Diagnosis and Root Cause.
  - Show Confidence Score (visual gauge or progress bar).
  - Show Code Diff utilizing a custom `CodeDiffViewer` component.
- [ ] Implement Approve/Reject action buttons triggering `/api/incidents/{id}/approve`.
- [ ] Implement auto-polling logic to refresh incident state every 2 seconds when status is `HEALING`, `VERIFYING`, or `AWAITING_APPROVAL`.

## Phase 6: Polish
- [ ] Add loading skeletons for data fetching.
- [ ] Add empty states.
- [ ] Ensure micro-animations (hover states, pulsing active states) feel premium.
