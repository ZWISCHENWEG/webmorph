# Bright Data Setup & Integration

## Canonical Integration: Bright Data CLI
For the hackathon MVP, the official Bright Data CLI (`bdata scraper`) is the ONLY primary mechanism for interacting with Scraper Studio. The WEBMORPH Backend orchestrates the CLI asynchronously via a secure subprocess runner.

## Core Commands & Behavior
1. **Trigger Run:** `bdata scraper run <collector_id> <url>`
   - The CLI performs necessary API triggering and polling internally.
   - WEBMORPH waits for the command to exit, capturing the JSON output.
2. **Request Heal:** `bdata scraper heal <collector_id> "<what broke>"`
   - `scraper heal` is human-in-the-loop by default. It returns a proposal.
3. **Approve Heal:** `bdata scraper approve <collector_id>`
   - WEBMORPH executes this ONLY after explicit human approval in the UI. **NEVER use `--auto-approve`.**

*Do not rely on undocumented internal REST endpoints unless the CLI fails to support the required machine-readable JSON output natively.*

## ID Disambiguation
- **Collector ID (`c_xxxxx`):** The persistent identifier for the scraper template in Bright Data. This ID remains unchanged before, during, and after healing.
- **Snapshot ID / Collection ID (`j_xxxxx`):** The identifier for a specific, single run of a collector. Each execution produces a new snapshot.

## Target Website Requirements
The target website selection is a manual, human decision.
- Must be publicly accessible.
- No login required.
- No paywall.
- No personal or private data.
- No government websites.
- Not currently covered by a pre-built Bright Data scraper template.
- Has enough structural complexity to demonstrate meaningful data validation.
- Unstable enough (or conceptually understandable enough) to demonstrate DOM degradation.

## Workflow Overview
1. Create a Bright Data Account.
2. Access Scraper Studio.
3. Build a new Collector for the target website.
4. Retrieve the Collector ID (`c_xxxxx`).
5. Register the Collector ID and Data Contract in WEBMORPH.
6. WEBMORPH handles triggering, secure CLI orchestration, and healing approval.
