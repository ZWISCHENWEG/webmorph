# WebMorph Frontend Design System

## Core Aesthetic
- **Inspiration:** Vercel, Datadog, Linear.
- **Theme:** Dark mode default. Sleek, professional, high-contrast developer tools.
- **Vibe:** "Premium Developer Infrastructure".
- **Visuals:** Glassmorphism panels, subtle borders (`border-zinc-800`), muted backgrounds (`bg-zinc-950`), and vibrant accent colors for statuses.

## Typography
- **Primary Font:** Inter (or similar clean sans-serif like Geist/Roboto).
- **Monospace Font:** JetBrains Mono or similar for code snippets, JSON payloads, and diffs.
- **Hierarchy:** Clear distinction between data labels (muted, uppercase, small) and values (high contrast, standard size).

## Color Palette & Status Mapping
Status colors are critical for a monitoring dashboard. We will use a strict, semantic palette:
- **Backgrounds:** `bg-black`, `bg-zinc-950`, `bg-zinc-900`.
- **Borders:** `border-zinc-800`.
- **Text:** `text-zinc-50` (Primary), `text-zinc-400` (Secondary).

**Semantic Status Colors:**
- **Healthy / Active / Recovered:** Vibrant Green (`text-emerald-400`, `bg-emerald-400/10`, `border-emerald-500/20`).
- **Warning / Awaiting Approval / Diagnosing:** Amber/Yellow (`text-amber-400`, `bg-amber-400/10`, `border-amber-500/20`).
- **Critical / Failed / Manual Intervention:** Red (`text-rose-400`, `bg-rose-400/10`, `border-rose-500/20`).
- **Processing / Healing / Verifying:** Blue (`text-blue-400`, `bg-blue-400/10`, `border-blue-500/20`).

## Key UI Components
1. **Code Diff Viewer:**
   - Red background/text for removed lines (`-`).
   - Green background/text for added lines (`+`).
   - Monospace font with clear line separation.

2. **Incident Timeline:**
   - Vertical timeline with connecting dashed lines.
   - Nodes color-coded by event type.
   - Pulsing animations for active states (e.g. while `VERIFYING` or `HEALING`).

3. **Metrics / KPIs:**
   - Large, legible numbers (e.g., `98%`).
   - Trend indicators (e.g., small green arrow pointing up).

4. **Approval Action Bar:**
   - A sticky or prominent section in the Incident Detail view.
   - "Approve Fix" (Primary button, green accent or bright white).
   - "Reject" (Secondary button, outlined or subtle red).
