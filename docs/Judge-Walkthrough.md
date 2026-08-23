# Judge Walkthrough Guide

This document is designed to guide hackathon judges through evaluating the technical depth and product execution of WebMorph.

## 1. Product Positioning
**What is WebMorph?**
It is not merely a "web scraper." It is an **AI-powered infrastructure layer** that manages web scrapers. It introduces self-healing capabilities to brittle data pipelines. 

**The Value:**
Companies lose millions dealing with broken ETL pipelines because target DOM structures change. WebMorph automates the role of a production support engineer.

## 2. Key Features to Highlight

### The Data Contract Engine
- **Where to look:** Explain the concept of Data Contracts. WebMorph enforces a strict JSON schema for every scrape. 
- **Why it matters:** This ensures bad data never reaches the database. It converts silent failures into actionable incidents.

### The Autonomous Healing Loop
- **Where to look:** The **Incident Detail Screen**.
- **Why it matters:** WebMorph detects a failure, captures the raw DOM snapshot, feeds it to an LLM alongside the failed schema, and requests a diagnostic patch. It writes its own code to fix itself.

### Enterprise-Grade Safety
- **Where to look:** The **Approval Action Bar**.
- **Why it matters:** AI can hallucinate. WebMorph mitigates risk by requiring human approval before deploying patches to production, acting as a powerful co-pilot rather than an unchecked script.

## 3. Technical Architecture (If Asked)
- **Backend:** Python (FastAPI), SQLAlchemy (Async), PostgreSQL (Neon)
- **Frontend:** Next.js (App Router), TypeScript, Tailwind v4, shadcn/ui
- **Workers:** Custom async Python polling architecture built for robustness and easy deployment on Render without needing Redis.
- **AI Integration:** Multi-modal LLM integration (OpenAI/Gemini) structured to return specific patch schemas.

## 4. Judging Criteria Mapping
- **Innovation:** Moving beyond "AI that writes code" to "AI that maintains infrastructure."
- **Execution:** Premium Linear/Vercel design aesthetic. Fully type-safe and deployment-ready.
- **Real-World Impact:** Directly addresses one of the most painful, expensive, and ubiquitous problems in data engineering today.
