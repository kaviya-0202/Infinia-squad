# AI Usage Note
## Complaint Prioritizer — Team Infinia Squad
### Infinite Computer Solutions Hackathon | June 2026
 
---
 
## 1. What AI Helped With
 
### Project Planning & Architecture
We used Claude (Anthropic) at the start to help us decide on the project structure.
We described the problem we wanted to solve and asked it to suggest a clean folder
structure and which responsibilities each file should own. The 5-layer architecture
(user_form → groq_service → helpers → db_service → dashboard) came directly from
that conversation. This saved us roughly 2 hours of back-and-forth discussion within
the team.
 
### groq_service.py — Core AI Integration
Claude helped us write the initial version of the Groq API connection and the
analyze_complaint() function. We described what inputs we had (raw complaint text)
and what outputs we needed (structured JSON with sentiment, urgency, and summary),
and Claude generated the first working draft. We then iterated on it significantly —
especially the prompt and the JSON parsing fallback logic.
 
### The Scoring Prompt
We used Claude to help refine the prompt we send to LLaMA 3.3. Our first version
was vague and produced inconsistent output. Claude helped us understand why — we
weren't telling the model to return ONLY JSON, so it was adding conversational
preamble. Claude suggested the exact phrasing "return ONLY a JSON object with no
extra text, no markdown, no explanation" which fixed the consistency issue.
 
### db_service.py — Storage Layer
Claude wrote the first version of the save_complaint() and get_sorted_complaints()
functions. It also suggested the init_db() pattern — checking if the file exists
before every read/write operation — which we adopted because it prevents
FileNotFoundError crashes on fresh installations.
 
### dashboard.py — Complaint Cards
Kaviya used Claude to help structure the complaint card layout in Streamlit.
Specifically, how to use st.columns() and st.expander() together, and how to
inject the coloured left-border using st.markdown() with inline CSS. Claude
provided working code for the card layout which we then styled to match our
dark theme.
 
### test_analyzer.py — Test Cases
Hemavarni used Claude to identify which test cases were important to write.
After describing the project, Claude suggested five test cases covering happy
path, negative detection, format validation, edge case (empty input), and
low-urgency classification. We wrote the actual test code ourselves based on
those suggestions.
 
### README.md
The README structure was drafted with Claude's help. We described all the
sections we needed and Claude generated a clean template. We then filled in
every section with our actual project details, commands, and architecture.
 
### Debugging
When our JSON parsing was breaking on certain AI responses, we pasted the
error and the raw output into Claude and asked what was going wrong. Claude
identified that LLaMA 3.3 was occasionally wrapping the JSON in markdown
code blocks (triple backticks) which json.loads() cannot parse. It suggested
the two-step fallback: try parsing directly, and if that fails, strip markdown
formatting and try again.
 
---
 
## 2. What AI Got Wrong
 
### Wrong — Initial Prompt Produced Inconsistent Output
Our first prompt to LLaMA 3.3 was:
 
````
Analyze this complaint and return sentiment, urgency, and summary.
Complaint: {text}
````
 
The model returned different formats every time. Sometimes a numbered list,
sometimes a paragraph, sometimes JSON, sometimes plain text labels. We could
not reliably parse any of it. We had to completely rewrite the prompt with
explicit format instructions before it became usable.
 
### Wrong — Suggested SQLite When We Didn't Need It
When we asked Claude for storage recommendations, it initially suggested SQLite
with a full schema — tables, primary keys, foreign keys. For a 24-hour hackathon
prototype handling under 100 complaints, this was overkill. We pushed back and
asked for the simplest possible approach. Claude then suggested JSON file storage,
which was the right call for our scope.
 
### Wrong — Over-complicated the Dashboard Layout
Claude's first suggestion for the dashboard card layout used nested columns inside
expanders inside containers. It worked but was unnecessarily complex — three levels
of nesting for what is essentially a labelled card. Kaviya simplified it
significantly by removing the outer container layer and using direct st.markdown()
with inline CSS instead.
 
### Wrong — Urgency Scores Outside Our Range
In early testing, LLaMA 3.3 occasionally returned urgency_score as 0 or 11 —
outside our 1 to 10 range. The prompt said "integer from 1 to 10" but the model
ignored the boundary in about 5% of responses. We added a clamping fix in
groq_service.py:
 
````python
urgency_score = max(1, min(10, int(result.get("urgency_score", 5))))
````
 
AI did not flag this issue — we caught it during manual testing.
 
### Wrong — Hallucinated a Non-Existent Streamlit Function
Claude once suggested using `st.live_update()` to auto-refresh the dashboard.
This function does not exist in Streamlit. When we ran the code, it threw an
AttributeError immediately. We verified by checking the official Streamlit docs
and replaced it with a manual Refresh button using `st.rerun()`, which is the
correct approach.
 
### Wrong — Generated Tests That Didn't Match Our Actual Function Signature
The first test file Claude generated imported
`from services.groq_service import analyze_complaint` and tested the JSON output.
But our test suite actually uses `analyzer.py` which returns plain text — not JSON.
The tests were written for the wrong function. Hemavarni caught this during the
first test run (all tests failed with KeyError) and rewrote the tests to match
analyzer.py's actual output format.
 
---
 
## 3. Best Prompts Used
 
---
 
### Prompt 1 — The Core Scoring Prompt (sent to LLaMA 3.3 via Groq API)
**Used in:** `services/groq_service.py`
**Purpose:** Analyze a customer complaint and return structured scores
 
````
You are a customer support AI assistant. Analyze the following customer
complaint and return ONLY a JSON object with no extra text, no markdown,
no explanation.
 
Complaint: "{complaint_text}"
 
Return exactly this JSON format:
{
    "sentiment": "Positive" or "Neutral" or "Negative",
    "sentiment_symbol": "+" or "~" or "-",
    "urgency_score": <integer from 1 to 10>,
    "urgency_label": "Low" or "Medium" or "High" or "Critical",
    "summary": "<one sentence summary of the complaint>"
}
 
Scoring guide:
- urgency_score 1-3: routine request, no time pressure
- urgency_score 4-6: issue affecting experience, no business emergency
- urgency_score 7-8: significant problem, customer frustrated, possible churn risk
- urgency_score 9-10: production down, financial loss, legal threat, or explicit
  cancellation intent
- sentiment Negative: angry, frustrated, or threatening tone
- sentiment Neutral: factual, calm, or informational tone
- sentiment Positive: happy, satisfied, or complimentary tone
````
 
**Why this worked:** The "ONLY a JSON object" instruction and the explicit
scoring guide eliminated the two biggest failure modes — conversational preamble
and inconsistent scoring boundaries. Response reliability went from ~60% to ~95%
after adding the scoring guide.
 
---
 
### Prompt 2 — Getting the Project Architecture
**Used in:** Planning phase (Claude)
**Purpose:** Design the folder structure and file responsibilities
 
````
I am building a customer complaint prioritization system for a hackathon.
I have 24 hours. The system should:
- Accept a complaint from a customer via a web form
- Send the complaint to an AI API and get back a sentiment score and urgency score
- Save the result
- Show a support team a dashboard sorted by urgency
 
I am using Python and Streamlit. What is the cleanest folder structure
and which file should be responsible for what? Keep it simple — I don't
need enterprise patterns, just clean separation that a team of 3 can divide.
````
 
**Why this worked:** Giving the constraint ("24 hours", "team of 3") forced
Claude to suggest a lightweight structure instead of over-engineering it.
The result was the 5-file architecture we actually used.
 
---
 
### Prompt 3 — Building groq_service.py
**Used in:** Writing the AI integration layer (Claude)
**Purpose:** Generate the first working version of the Groq API call
 
````
Write a Python function called analyze_complaint(complaint_text) that:
1. Takes a string of complaint text as input
2. Calls the Groq API using the groq Python SDK
3. Uses the model llama-3.3-70b-versatile
4. Sends a prompt that asks the AI to return ONLY a JSON object with these fields:
   sentiment (Positive/Neutral/Negative), urgency_score (1-10),
   urgency_label (Low/Medium/High/Critical), summary (one sentence)
5. Parses the JSON response
6. Returns a Python dictionary
7. Has a try/except that returns a safe default dictionary if anything fails
8. Reads the API key from an environment variable called GROQ_API_KEY
 
Also handle the case where the AI wraps the JSON in markdown code blocks.
````
 
**Why this worked:** Listing every requirement as numbered points gave Claude
a clear checklist. Specifically mentioning "handle markdown code blocks" at the
end made it include the fallback parsing logic without us having to add it later.
 
---
 
### Prompt 4 — Building the Dashboard Card Layout
**Used in:** Writing dashboard.py (Claude)
**Purpose:** Create a Streamlit complaint card with colour-coded left border
 
````
I am building a Streamlit dashboard. For each complaint in a list, I want
to display a card that looks like this:
 
- Dark background card
- A coloured left border (red for Critical, orange for High, yellow for Medium,
  green for Low) — the colour changes based on the urgency_label field
- Card shows: customer name, email, urgency badge, sentiment badge,
  complaint text, and timestamp
- The urgency and sentiment badges should be pill-shaped with the matching colour
 
Each complaint is a dictionary with keys: name, email, complaint, sentiment,
urgency_score, urgency_label, summary, timestamp.
 
Use st.markdown() with inline CSS for the card styling. I am using a dark
theme so card background should be #1a1d2e.
````
 
**Why this worked:** Describing the visual output first and then the data
structure made Claude generate a card that matched what we actually wanted
instead of a generic layout. Specifying the exact background hex colour tied
it directly to our theme.
 
---
 
### Prompt 5 — Fixing the JSON Parsing Bug
**Used in:** Debugging groq_service.py (Claude)
**Purpose:** Fix crashes caused by markdown-wrapped JSON responses
 
````
My Python code calls the Groq API and expects the model to return a JSON object.
I then do json.loads(response) to parse it.
 
Sometimes the model wraps the JSON in markdown code blocks like this:
```json
{"sentiment": "Negative", "urgency_score": 9}
```
 
This causes json.loads() to throw a JSONDecodeError because the backticks
are not valid JSON.
 
How do I handle this reliably without just removing all backticks blindly
(which could corrupt valid JSON that happens to contain backtick characters)?
````
 
**Why this worked:** Describing what the bug was, what the failure looked like,
and specifically mentioning the constraint ("without removing all backticks
blindly") made Claude give a targeted solution — split on triple backticks
and take the middle section — rather than a naive find-and-replace.
 
---
 
### Prompt 6 — Writing Test Cases
**Used in:** Writing test_analyzer.py (Claude)
**Purpose:** Identify what to test and generate the test structure
 
````
I have a Python function called analyze_ticket(ticket_text) that:
- Takes a string of complaint text
- Calls the Groq API with LLaMA 3.3
- Returns a plain text string in this format:
  Sentiment: Negative
  Urgency: High
  Churn Risk: High
 
I need to write pytest test cases for this function.
What are the most important scenarios to test?
The function calls a real external API so tests will be slow —
that is acceptable for now.
 
Write the test file with 5 test cases covering the most important scenarios
including at least one edge case.
````
 
**Why this worked:** Describing the exact output format of the function
upfront meant Claude wrote tests that matched the actual string format
("Sentiment: Negative") instead of testing for JSON keys that don't exist
in this function.
 
---
 
### Prompt 7 — Writing the README
**Used in:** Writing README.md (Claude)
**Purpose:** Generate the README structure and boilerplate
 
````
Write a README.md for a Python + Streamlit project called Complaint Prioritizer.
 
The project is an AI-powered customer complaint prioritization system built
for a hackathon in 24 hours.
 
The README must include these exact sections:
1. Overview (2-3 sentences)
2. Features (bullet list)
3. Architecture Overview (folder tree + flow diagram in ASCII)
4. Tech Stack (table)
5. Setup Instructions (step by step with code blocks for every command)
6. Run Instructions (how to submit a complaint, view dashboard, load sample data)
7. Assumptions and Limitations (two separate subsections)
8. Team information
 
The setup instructions must cover: cloning, installing dependencies,
creating a .env file, getting a Groq API key, and running the app.
Include the command to run if streamlit is not on PATH.
 
Write it in a professional but readable tone.
Do not use any filler phrases like "of course" or "certainly".
````
 
**Why this worked:** Listing every section by number with a brief description
of what should be in it gave Claude a precise outline to follow. The instruction
to avoid filler phrases kept the output clean and direct.
 
---
 
## Summary
 
| Area | AI Used | Human Override Needed |
|---|---|---|
| Architecture planning | Claude | No — adopted directly |
| groq_service.py | Claude | Yes — added clamping fix, fallback parser |
| Scoring prompt | Claude + iteration | Yes — rewrote 3 times to get reliable JSON |
| db_service.py | Claude | Minor — simplified SQLite suggestion to JSON |
| Dashboard cards | Claude | Yes — simplified nested layout |
| Test cases | Claude | Yes — rewrote to match actual function output |
| README | Claude | Yes — filled in all real project details |
| Dark theme CSS | Self-written | N/A |
| Sample data | Self-written | N/A |
| Bug fixes | Claude (diagnosis) | Yes — we wrote the actual fix |
 
---
 
*Team Infinia Squad | Infinite Computer Solutions Hackathon | June 2026*