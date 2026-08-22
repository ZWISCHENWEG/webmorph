# AI Usage Guidelines

## Code Generation Constraints
When an AI agent begins implementing WEBMORPH:
1. **Strict Adherence:** The agent MUST strictly follow `Technical-Spec.md` and `Architecture.md`.
2. **No Hallucination:** The agent must not invent new features, metrics, or Bright Data API endpoints.
3. **Constants:** Health heuristics and thresholds must remain as defined.
4. **Visuals:** The UI must adhere to the `Design.md` constraints (no cartoonish superhero assets, strict dark mode developer infrastructure look).
5. **No Fake Data:** `DEMO_MODE` logic must only simulate extraction failure for detection testing, not fake the Bright Data API itself.
6. **No Auto-Approve:** The CLI command `bdata scraper approve` must only trigger after human interaction.

## Pre-Implementation Human Stop Gates
An AI agent MUST NOT write application code until the human user explicitly clears these stop gates:
- **STOP GATE A:** Documentation V4.1.2 approved.
- **STOP GATE B:** Target website selected and manually verified against hackathon rules.
- **STOP GATE C:** Versioned Data Contract approved.
- **STOP GATE D:** Real Bright Data Collector created.
- **STOP GATE E:** Real structured output verified against the Data Contract.
- **STOP GATE F:** Collector ID (`c_xxxxx`) manually confirmed.
- **STOP GATE G:** Human explicitly authorizes implementation.

The AI must NEVER invent the target website or Collector ID.
