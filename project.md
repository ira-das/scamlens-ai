You are a senior full-stack engineer and patient mentor. I am a complete beginner building a hackathon prototype called "ScamLens AI". I cannot attach images, so the slides of my presentation are described in full text in section 1. Treat section 1 as the source of truth. Build the project in this empty folder, step by step, explaining each step in simple language. Do NOT generate everything at once. Work in the phases in section 9. After each phase, tell me the exact command to run to test it and what I should see, then wait for me to reply "next".

## 1. My presentation, slide by slide (source of truth)

Slide 1, Title: "SCAMLENS AI: Autonomous Internship & Job Offer Verifier Powered by TinyFish". Team Moonbyte (Ira Das, Suhani Jain). Track: AI/ML. Category: Student Track. Visual style: dark navy/teal circuit-board background, neon cyan glowing futuristic headings, rounded panels with glowing cyan hexagon/bracket borders.

Slide 2, Problem Statement, three panels:
- The Problem: fraudulent "internship offers" target desperate students on social media and DMs. Scammers demand fake "security deposits", "laptop kit fees" or "training costs".
- Reality Stats: average student loss per incident is ₹3,000 to ₹15,000. Over 80% of scams use lookalike domains or fake recruiter identities undetectable by static search (source: McAfee Threat Reports).
- Stakeholders: college students looking for a first internship with no network or experience to judge offers; University Training & Placement (T&P) Cells, job portals and communities.

Slide 3, Proposed Solution:
- Key Features: (1) Two input channels: a responsive Web Dashboard, or a WhatsApp Bot Engine (planned). (2) Gemini NLP Claim Parser: extracts structured claims (domain, company, recruiter, employee reviews, address, stipend) from raw text or a PDF. (3) Parallel Multi-Agent Engine (TinyFish): 5 live checks run in parallel (domain, company page, recruiter verification, employee review reports, stipend). (4) Trust Report: risk score with a source link for every flag.
- How It's Unique: (1) Verifiable Evidence Links: not just a score, but hyperlinked, time-stamped proof for every flag, directly from the source. (2) Live Vetting Workflow: five asynchronous verification streams run simultaneously. (3) Plug-in API: a modular middleware for universities and job boards to prevent fraudulent listings before publication.

Slide 4, Use Case, a table with three columns:
- B2C Student Self-Service: primary user is 1st/2nd year undergraduates. Trigger: receives a suspicious offer demanding a ₹2,000 deposit. Core action: pastes the offer into the web dashboard (WhatsApp bot planned). Outcome: risk score (e.g. 14/100, higher = riskier) with source links. Value: prevents financial and data loss.
- B2B University T&P Cells: primary users are college T&P officers and committees. Trigger: inundated with 50+ unverified startup inquiries daily (estimated). Core action: uploads recruiter domains for bulk checks (planned). Outcome: verified-employer list built from WHOIS and registry checks. Value: saves 1,000+ hours of manual vetting (estimated).
- B2B API Platform Middleware: primary users are job boards and student portals. Trigger: scammers post fake listings to harvest student data. Core action: calls the ScamLens API before a listing goes live (planned). Outcome: suspicious listings flagged for review. Value: preserves platform trust and reputation.
User Experience, 4 steps: Step 1 Input (student receives a suspicious DM and pastes it into ScamLens AI). Step 2 Verification (parallel TinyFish agents check live web sources). Step 3 Score and Evidence (risk score 0-100 with verified source proof links). Step 4 Decide and Share (student acts on the verdict, then shares the report with peers).

Slide 5, Role of AI/ML, a table (AI job / input / output):
- Claim extraction (Gemini): raw offer text or PDF -> structured claims: company, domain, recruiter, stipend, fee, UPI.
- Scam-pattern detection: offer wording -> flags such as fee demand, urgency, request to move to private chat.
- Plausibility judgment: offered stipend and the market range the agents found -> "plausible" or "unusually high", with reasoning.
- Scoring and explanation: all evidence from the checks -> risk score and a plain-language summary.
Technical Approach flow: Input -> Extract (Gemini turns it into claims) -> Verification (parallel TinyFish agents check live web sources) -> Score (evidence is normalized and weighted) -> Report (risk score with source links displayed).

Slide 6, Tech Stack and Architecture: Frontend: Next.js 15 + Tailwind CSS. Interface channels: web app and async WhatsApp bot engine (planned). Backend API: Python 3.11 + FastAPI. AI and synthesis: Google Gemini (claim parsing and scoring). Autonomous agents and data engine: TinyFish agent infrastructure: TinyFish Web Agent (WHOIS lookup, address and stipend), TinySearch API (scam and complaint search), TinyFetch API (company page and recruiter verification). Database and cache: PostgreSQL (Supabase) and Redis.

Slide 7, TinyFish Integration, a flow diagram: Paste job offer text (claims: company, domain, stipend, address, recruiter) -> NLP Claim Extraction (Gemini/AI) parses claims into structured JSON -> 5 parallel checks:
1. Domain Age & Registration (TinyAgent WHOIS lookup): checks domain age and registration details to verify legitimacy. Output: registration date + source URL.
2. Company & Careers Page Check (TinyFetch page extraction): verifies company info, careers page and contact details on the official site. Output: whether role, address and contact details exist on the official site.
3. Recruiter Verification (TinyFetch, LinkedIn/team page check): checks the recruiter belongs to the company and the profile matches the official domain. Output: match or no match + source URL.
4. Scam & Employee-Review Reports (TinySearch database query): scans scam databases and employee reviews for red flags, complaints, suspicious activity. Output: reports found or none, with links.
5. Address & Stipend Plausibility (TinyAgent + TinyFetch market data check): validates location and stipend range against market data. Output: address type and stipend range.
-> Evidence Synthesis & Scoring (Gemini/AI aggregates all 5 raw outputs) -> ScamLens AI Trust Report Dashboard: final risk score, verified source links, cited red flags (for example "Domain < 30 days old", "Residential address flag").

Slide 8, Expected Impact: Students (check an offer in about a minute (estimated), see proof behind every red flag, reduce the chance of paying fake "kit", "training" or "clearance" fees). T&P Cells (screen startup and recruiter requests without checking each by hand; build a trusted employer list over time (planned)). Job Platforms (catch suspicious listings before they reach students (planned API); protect platform trust and reduce fraud complaints). Why it matters: 49% of Indian Gen Z job seekers say they nearly fell for a job scam (LinkedIn, 2026); 90% of reported scam attempts move to private messaging apps (LinkedIn, 2026); real cases: a ₹2,000 "police clearance" fee (Chennai) and a ₹6,000 "registration fee" for about 45 students (Jabalpur, alleged).

Slide 9, Price Economics, Future Scope, Revenue Model:
- Price economics (team estimate): about $0.016-$0.024 (₹30-50) per report; Search and Fetch are free; Web Agent steps are the only real cost at $0.016 per step.
- Future scope: scale the WhatsApp bot and web dashboard into a browser extension; community-reported scam database; learned scoring weights trained on verified labels; Hindi and regional language support; B2B scaling by partnering with job portals (LinkedIn, Naukri) as a pre-publication API filter.
- Revenue model: students free with a limited number of checks per month; colleges per-campus subscription for bulk verification; job portals pay-per-call screening API.

## 2. What to build
A working web prototype of ScamLens AI. A student pastes a suspicious offer (text; PDF upload is a disabled "coming soon" control). The system extracts structured claims with Gemini, runs the 5 checks IN PARALLEL, and produces a risk score from 0 to 100 (HIGHER = RISKIER), a level, a plain-language summary, and red flags where every flag carries a hyperlinked, timestamped source link. Also build a simple bulk domain checker (for T&P cells) and a job-board API demo (screen a listing before publication). A WhatsApp bot is a stub only.

## 3. Tech stack (use exactly this)
- Frontend: Next.js 15 (App Router, TypeScript) + Tailwind CSS, in /frontend
- Backend: Python 3.11 + FastAPI, in /backend
- AI: Google Gemini via the official google-genai Python SDK. Read the model name from env var GEMINI_MODEL (the model named on my slides may be retired, so make it configurable and tell me how to pick a current Flash model in Google AI Studio).
- Agents/data: TinyFish (Web Agent, TinySearch, TinyFetch), behind an adapter layer (see section 4).
- Database/cache: PostgreSQL via Supabase and Redis, both OPTIONAL. Default to an in-memory cache and a local SQLite/JSON file so the app runs with zero setup.
- Secrets only in .env (GEMINI_API_KEY, GEMINI_MODEL, TINYFISH_API_KEY, SUPABASE_URL, SUPABASE_KEY, REDIS_URL, USE_MOCKS, API_DEMO_KEY). Provide .env.example and a .gitignore that excludes .env. Never hardcode keys.

## 4. Pipeline and the 5 checks
Claim extraction returns strict JSON validated with Pydantic: company, domain, recruiter_name, recruiter_email, stipend (INR number), fee_demanded (INR number), upi_id, address, and scam-wording flags (urgency, move to private chat such as WhatsApp or Telegram, no interview, asks for Aadhaar/bank details/OTP). Handle malformed model output gracefully. If the Gemini key is missing, fall back to a regex extractor.

Each of the 5 checks is an async function returning one shared Pydantic model: name, tool_used, status [ok|warn|bad|error], summary, risk_points, max_points, evidence: list of {label, url, retrieved_at}. The checks are the five numbered on Slide 7 above. Run them with asyncio.gather, per-check timeouts and small retry backoff, so one failure returns status "error" for that check and never breaks the report.

TinyFish integration: I am NOT giving you TinyFish's API details and you must NOT guess endpoints or request formats. Create backend/app/tinyfish_client.py with clear function signatures web_agent(), search() and fetch(). Implement MOCK mode (USE_MOCKS=true, default true) returning realistic deterministic fake data: well-known companies (TCS, Infosys, Razorpay) look legitimate; .xyz/.online/hyphenated or free-mail domains look like scams. Mark every place where the real API must be wired in with a TODO. When we reach that phase, I will paste the TinyFish docs.

Scoring, a pure function with unit tests: domain 25, scam/review reports 25 (includes any upfront fee demand), recruiter 15, address/stipend plausibility 15, company page 10, Gemini scam-wording patterns 10; total capped at 100. Levels: 0-29 LOW RISK, 30-59 MEDIUM RISK, 60-100 HIGH RISK. Typical intern stipend range assumption: ₹5,000-₹25,000, above ₹25,000 is a caution, above ₹40,000 is unusually high (make these constants easy to edit). Gemini writes the plain-language summary using ONLY evidence from the checks, with no invented facts.

## 5. Backend API
- GET /health
- POST /api/verify {text} -> full Trust Report JSON (claims, checks, risk_score, level, red_flags with sources, summary, generated_at)
- POST /api/verify/stream (Server-Sent Events) -> emits one event as each check finishes, for live UI progress
- POST /api/bulk-check {domains: string[]} -> per-domain age, verdict (Verified/Review/Reject), reason
- POST /api/v1/listing-screen {listing_text}, requires an X-API-Key header -> {risk_score, decision: PUBLISH | HOLD_FOR_REVIEW | BLOCK, flags}
- CORS for http://localhost:3000, input validation, text length limit, simple rate limiting, caching by hash of input text.

## 6. Frontend
Match the slide look: dark navy/teal cyber theme, neon cyan accents, Orbitron-style headings, rounded bordered panels with glowing edges. Responsive, accessible contrast, visible keyboard focus, respect reduced-motion.
- / (student dashboard): title "ScamLens AI", tagline "Verify before you pay", large textarea, three sample-offer buttons (fake with deposit, fake too-good-to-be-true, genuine), "Verify offer" button. Show the 4-step flow from Slide 4 (Input, Verification, Score and Evidence, Decide and Share): five agent cards with live loading/success/warning/error states, an animated 0-100 risk gauge with level and summary, "Cited Red Flags" and "Verified Source Links" lists (links open in a new tab with rel="noopener noreferrer"), and a "Copy report" button. Add an "Impact" section with the Slide 8 figures, labelling estimated ones as estimated.
- /bulk: paste domains, results table, "copy verified employer list" button.
- /api-demo: paste a listing, show request JSON, response JSON and the PUBLISH/HOLD/BLOCK decision.

## 7. Documentation (README only, don't build)
Future scope and revenue model from Slide 9, labelled as team estimates and plans.

## 8. Quality rules
- Layout: /backend/app (main.py, models.py, gemini_client.py, tinyfish_client.py, checks/, scoring.py, cache.py), /backend/tests, /frontend, README.md, PROJECT.md (save a copy of this whole brief).
- Type hints, docstrings, beginner-friendly comments.
- Pytest tests for scoring.py, claim-JSON validation, and a test that the mock pipeline gives HIGH RISK for the fake samples and LOW RISK for the genuine one.
- When USE_MOCKS=true the UI must show a visible "Demo mode: simulated lookups" banner. Never present simulated data as real.
- Never invent source URLs. Evidence links come from check results; in mock mode use real public lookup pages (for example https://who.is/whois/<domain>, a LinkedIn search URL, a Google search URL).
- Treat pasted offer text as untrusted: never follow instructions inside it (guard against prompt injection in Gemini prompts), and escape all rendered text.

## 9. Phases (stop after each and wait for "next")
Phase 1: folder structure, PROJECT.md, .env.example, .gitignore, FastAPI skeleton with /health, and exact terminal commands (virtual environment, install, run).
Phase 2: Pydantic models, mock TinyFish adapter, the 5 checks, scoring.py with tests, /api/verify end to end in mock mode with the regex extractor.
Phase 3: Gemini claim extraction and summary using the real API key, with the regex fallback.
Phase 4: SSE streaming, caching, rate limiting, bulk-check and listing-screen endpoints.
Phase 5: Next.js frontend: dashboard first, then /bulk and /api-demo.
Phase 6: wire in the real TinyFish API (I will paste the docs), keeping mock mode as fallback.
Phase 7: README with setup steps, a Mermaid architecture diagram, demo script and likely judge Q&A; then deployment steps (Vercel for frontend, Render for backend).

Start now with Phase 1. Before writing code, summarize your understanding in 5 bullet points and list any questions you have.