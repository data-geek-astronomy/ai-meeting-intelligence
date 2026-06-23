import os
import json
import gradio as gr

ENV_OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# ---------------------------------------------------------------------------
# HTML card builder helpers
# ---------------------------------------------------------------------------

def card(bg, border, content_html, padding="20px"):
    return (
        f'<div style="background:{bg};border:1px solid {border};border-radius:12px;'
        f'padding:{padding};margin-bottom:16px;">{content_html}</div>'
    )


def label(text, color):
    return (
        f'<div style="font-size:11px;font-weight:700;letter-spacing:0.08em;'
        f'text-transform:uppercase;color:{color};margin-bottom:10px;">{text}</div>'
    )


def render_meeting_output(
    meeting_title,
    attendees_list,
    duration,
    action_items,      # list of {"task", "owner", "due_date", "priority"}
    decisions,         # list of str
    summary,           # str (may contain \n for paragraphs)
    email_subject,     # str
    email_body,        # str
    sentiment="productive",
):
    sentiment_colors = {
        "productive": ("#86efac", "rgba(34,197,94,0.2)"),
        "neutral": ("#fde68a", "rgba(234,179,8,0.2)"),
        "tense": ("#fca5a5", "rgba(239,68,68,0.2)"),
    }
    sent_color, sent_bg = sentiment_colors.get(sentiment, sentiment_colors["productive"])

    priority_badge = {"high": "#fca5a5", "medium": "#fde68a", "low": "#86efac"}

    # ── Header card ──────────────────────────────────────────────────────────
    attendees_str = ", ".join(attendees_list) if isinstance(attendees_list, list) else attendees_list
    header_html = (
        label("Meeting", "#a5b4fc")
        + f'<div style="font-size:22px;font-weight:700;color:#e0e7ff;margin-bottom:8px;">{meeting_title}</div>'
        + f'<div style="color:#c4b5fd;font-size:14px;">🕐 {duration} &nbsp;·&nbsp; 👥 {attendees_str}</div>'
        + f'<div style="margin-top:10px;display:inline-block;background:{sent_bg};border:1px solid {sent_color};'
        + f'border-radius:20px;padding:3px 12px;font-size:12px;color:{sent_color};font-weight:600;">'
        + f'Sentiment: {sentiment.capitalize()}</div>'
    )
    header_card = card("rgba(99,102,241,0.15)", "rgba(129,140,248,0.4)", header_html)

    # ── Action items card ────────────────────────────────────────────────────
    items_html = label("Action Items", "#fca5a5")
    for item in action_items:
        pri = item.get("priority", "medium")
        badge_color = priority_badge.get(pri, "#fde68a")
        items_html += (
            f'<div style="margin-bottom:10px;padding:10px 14px;background:rgba(0,0,0,0.2);'
            f'border-radius:8px;border-left:3px solid {badge_color};">'
            f'<span style="color:#fee2e2;font-weight:500;">• {item["task"]}</span>'
            f'<span style="color:#fca5a5;font-size:13px;"> → Owner: <strong style="color:#fecaca;">{item["owner"]}</strong>'
            f' · Due: {item["due_date"]}'
            f' &nbsp;<span style="background:{badge_color}22;color:{badge_color};border-radius:10px;'
            f'padding:1px 8px;font-size:11px;font-weight:700;text-transform:uppercase;">{pri}</span></span>'
            f'</div>'
        )
    action_card = card("rgba(239,68,68,0.12)", "rgba(248,113,113,0.4)", items_html)

    # ── Decisions card ───────────────────────────────────────────────────────
    dec_html = label("Decisions Made", "#86efac")
    for i, d in enumerate(decisions, 1):
        dec_html += (
            f'<div style="margin-bottom:8px;color:#d1fae5;font-size:14px;">'
            f'<span style="color:#4ade80;font-weight:700;">{i}.</span> {d}</div>'
        )
    decisions_card = card("rgba(34,197,94,0.12)", "rgba(34,197,94,0.4)", dec_html)

    # ── Summary card ─────────────────────────────────────────────────────────
    paragraphs = summary.strip().split("\n")
    sum_inner = "".join(
        f'<p style="color:#e2e8f0;font-size:14px;line-height:1.7;margin:0 0 10px 0;">{p.strip()}</p>'
        for p in paragraphs if p.strip()
    )
    summary_html = label("Meeting Summary", "#94a3b8") + sum_inner
    summary_card = card("rgba(255,255,255,0.07)", "rgba(255,255,255,0.15)", summary_html)

    # ── Email draft card ──────────────────────────────────────────────────────
    email_html = (
        label("Email Draft", "#93c5fd")
        + f'<div style="color:#bfdbfe;font-size:13px;margin-bottom:8px;">'
        + f'<strong style="color:#93c5fd;">Subject:</strong> {email_subject}</div>'
        + f'<pre style="color:#dbeafe;font-family:\'Courier New\',monospace;font-size:13px;'
        + f'white-space:pre-wrap;word-break:break-word;background:rgba(0,0,0,0.25);'
        + f'border-radius:8px;padding:14px;margin:0;line-height:1.6;">{email_body}</pre>'
    )
    email_card = card("rgba(59,130,246,0.15)", "rgba(96,165,250,0.4)", email_html)

    return (
        '<div style="font-family:\'Inter\',sans-serif;max-width:860px;">'
        + header_card
        + action_card
        + decisions_card
        + summary_card
        + email_card
        + "</div>"
    )


# ---------------------------------------------------------------------------
# Pre-computed demo scenarios
# ---------------------------------------------------------------------------

DEMO_SCENARIOS = {
    "🗺️ Product Roadmap Planning": {
        "meeting_title": "Q3 Product Roadmap Planning",
        "attendees": ["Sarah Chen (CPO)", "Marcus Webb (VP Eng)", "Priya Nair (Design Lead)",
                      "Tom Alvarez (PM)", "Jess Park (Data)", "Liam O'Brien (Backend Lead)"],
        "duration": "45 minutes",
        "action_items": [
            {"task": "Finalize Q3 feature prioritization matrix and share with stakeholders",
             "owner": "Tom Alvarez", "due_date": "2025-07-05", "priority": "high"},
            {"task": "Draft technical feasibility report for the AI recommendation engine",
             "owner": "Marcus Webb", "due_date": "2025-07-08", "priority": "high"},
            {"task": "Conduct user research sessions on the new onboarding flow (min 10 interviews)",
             "owner": "Priya Nair", "due_date": "2025-07-12", "priority": "medium"},
            {"task": "Pull churn analysis data and segment by product tier for roadmap context",
             "owner": "Jess Park", "due_date": "2025-07-06", "priority": "medium"},
            {"task": "Set up weekly roadmap sync cadence — recurring invite to all stakeholders",
             "owner": "Tom Alvarez", "due_date": "2025-07-03", "priority": "low"},
        ],
        "decisions": [
            "AI-powered recommendation engine is the top Q3 priority over the mobile redesign.",
            "Feature freeze for Q2 is confirmed for June 30 — no new scope after that date.",
            "Design and Engineering will co-own the new onboarding flow starting July 8.",
        ],
        "summary": (
            "The Q3 product roadmap planning session brought together product, engineering, design, and data "
            "to align on the company's strategic priorities for the upcoming quarter. After reviewing Q2 performance "
            "metrics — including a 12% uptick in trial-to-paid conversion and persistent churn at the 60-day mark — "
            "the team agreed that the AI recommendation engine should take the top slot in Q3. The mobile redesign, "
            "previously earmarked as co-priority, was pushed to Q4 given engineering bandwidth constraints.\n"
            "Key tension arose around the onboarding flow, which Priya flagged as a root cause of early churn. "
            "The group resolved this by tasking Design and Engineering to co-own a lightweight onboarding revamp "
            "in parallel with the AI engine work. Tom will publish the prioritization matrix by July 5 to lock in "
            "stakeholder alignment before the July 8 sprint kick-off."
        ),
        "email_subject": "Re: Q3 Product Roadmap Planning — Action Items & Decisions",
        "email_body": (
            "Hi team,\n\n"
            "Thanks for a focused and productive roadmap session today. Here's a quick recap of what we decided "
            "and what's on each of us to do next.\n\n"
            "DECISIONS\n"
            "• AI Recommendation Engine is our #1 Q3 priority (mobile redesign moves to Q4)\n"
            "• Q2 feature freeze: June 30 — hard stop, no exceptions\n"
            "• Design + Engineering co-own new onboarding flow starting July 8\n\n"
            "ACTION ITEMS\n"
            "• Tom → Feature prioritization matrix → Jul 5\n"
            "• Marcus → Technical feasibility report (AI engine) → Jul 8\n"
            "• Priya → 10 user research interviews on onboarding → Jul 12\n"
            "• Jess → Churn analysis by product tier → Jul 6\n"
            "• Tom → Set up weekly roadmap sync invite → Jul 3\n\n"
            "Next sync is July 8 at our usual time. Please come prepared with your deliverables.\n\n"
            "Best,\nTom Alvarez · Product Manager"
        ),
        "sentiment": "productive",
    },

    "🔁 Engineering Sprint Retrospective": {
        "meeting_title": "Sprint 24 Retrospective — Backend Platform Team",
        "attendees": ["Marcus Webb (EM)", "Liam O'Brien", "Ana Ruiz", "Dev Patel",
                      "Chloe Kim", "Raj Singh", "Noah Carter", "Fatima Al-Hassan"],
        "duration": "30 minutes",
        "action_items": [
            {"task": "Document the database migration runbook and add to team wiki",
             "owner": "Liam O'Brien", "due_date": "2025-07-04", "priority": "high"},
            {"task": "Set up automated regression tests for the payments service",
             "owner": "Ana Ruiz", "due_date": "2025-07-07", "priority": "high"},
            {"task": "Investigate and resolve intermittent CI timeout failures in the build pipeline",
             "owner": "Dev Patel", "due_date": "2025-07-05", "priority": "high"},
            {"task": "Create on-call rotation schedule for Q3 and share in #engineering",
             "owner": "Marcus Webb", "due_date": "2025-07-03", "priority": "medium"},
            {"task": "Add sprint capacity buffer (20%) for unplanned incidents in Sprint 25 planning",
             "owner": "Marcus Webb", "due_date": "2025-07-08", "priority": "medium"},
            {"task": "Refactor authentication middleware to remove deprecated token logic",
             "owner": "Chloe Kim", "due_date": "2025-07-11", "priority": "low"},
        ],
        "decisions": [
            "Sprint velocity target reduced from 42 to 36 story points to account for recurring incident load.",
            "All database migrations must be reviewed by two senior engineers before merging — effective immediately.",
            "CI pipeline will be rebuilt using GitHub Actions by end of Q3; Jenkins to be deprecated.",
        ],
        "summary": (
            "Sprint 24 closed with 31 of 42 planned story points completed — a 74% velocity. The shortfall was "
            "attributed primarily to two unplanned incidents: a payments service outage on Tuesday (6 hours) and "
            "a database migration that had to be rolled back on Thursday (4 hours). The team surfaced strong "
            "consensus that the current lack of a migration runbook and automated regression coverage are the "
            "two highest-leverage problems to fix.\n"
            "On the positive side, the new feature flag system shipped cleanly and the API response time "
            "improvements (avg. -38ms) were celebrated as a genuine team win. Going into Sprint 25, the team "
            "agreed to reduce the velocity target to 36 points, institute a two-engineer review gate for all "
            "migrations, and allocate 20% buffer capacity for incidents. The CI rebuild was formally approved "
            "as a Q3 initiative."
        ),
        "email_subject": "Sprint 24 Retro Summary — Action Items & Process Changes",
        "email_body": (
            "Hey team,\n\n"
            "Great retro today — honest and action-oriented. Here's the summary for Sprint 24.\n\n"
            "WHAT WENT WELL\n"
            "• Feature flag system shipped on time ✅\n"
            "• API response time improved by avg. 38ms 🚀\n"
            "• Team communication during incidents was solid\n\n"
            "WHAT TO IMPROVE\n"
            "• No runbook for DB migrations → Liam to fix by Jul 4\n"
            "• Zero regression test coverage on payments → Ana on it by Jul 7\n"
            "• CI timeouts burning developer time → Dev investigating by Jul 5\n\n"
            "PROCESS CHANGES (effective now)\n"
            "• DB migrations require 2 senior engineer approvals before merge\n"
            "• Sprint 25 velocity target: 36 points (was 42)\n"
            "• 20% capacity buffer reserved for incidents\n\n"
            "Sprint 25 planning is Monday at 10am. See you there.\n\n"
            "— Marcus Webb, Engineering Manager"
        ),
        "sentiment": "neutral",
    },

    "🤝 Client Onboarding Call": {
        "meeting_title": "Acme Corp — Enterprise Onboarding Kickoff",
        "attendees": ["Jordan Blake (CSM)", "Rachel Torres (Solutions Eng)",
                      "David Kim (Acme IT Lead)", "Sandra Okonkwo (Acme VP Operations)"],
        "duration": "60 minutes",
        "action_items": [
            {"task": "Send SSO configuration guide (SAML 2.0) and sandbox credentials to David Kim",
             "owner": "Rachel Torres", "due_date": "2025-07-02", "priority": "high"},
            {"task": "Schedule technical deep-dive session with Acme IT team for SSO integration",
             "owner": "Jordan Blake", "due_date": "2025-07-03", "priority": "high"},
            {"task": "Provide employee CSV export (name, email, department) for bulk user provisioning",
             "owner": "David Kim", "due_date": "2025-07-07", "priority": "high"},
            {"task": "Prepare customized training deck tailored to Acme's ops workflow",
             "owner": "Rachel Torres", "due_date": "2025-07-10", "priority": "medium"},
            {"task": "Share onboarding project timeline and milestone tracker with Sandra",
             "owner": "Jordan Blake", "due_date": "2025-07-02", "priority": "medium"},
            {"task": "Confirm executive sponsorship for internal change management rollout",
             "owner": "Sandra Okonkwo", "due_date": "2025-07-09", "priority": "medium"},
        ],
        "decisions": [
            "Go-live target is set for August 1 — all onboarding milestones must be hit by July 25.",
            "SSO via SAML 2.0 is the agreed authentication method; no username/password login for Acme users.",
            "Phased rollout: Operations team (120 users) first, then company-wide by August 15.",
        ],
        "summary": (
            "The Acme Corp enterprise onboarding kickoff was a productive 60-minute session establishing the "
            "foundations for a smooth go-live on August 1. Sandra Okonkwo confirmed executive buy-in and "
            "emphasized that the Operations team of 120 users is the priority cohort — they have the most "
            "time-sensitive workflows that the platform will replace. David Kim raised SSO as a hard "
            "requirement; his IT team will not allow password-based auth. Rachel confirmed SAML 2.0 support "
            "and will send sandbox credentials and the configuration guide by Wednesday.\n"
            "The team agreed on a phased rollout: Operations first (target: August 1), then full company "
            "(target: August 15). Jordan will own the milestone tracker and weekly status cadence. A key risk "
            "flagged was Acme's internal change management — Sandra committed to confirming executive "
            "sponsorship by July 9. The technical deep-dive for SSO integration is being scheduled this week."
        ),
        "email_subject": "Acme Corp Onboarding Kickoff — Next Steps & Timeline",
        "email_body": (
            "Hi Sandra and David,\n\n"
            "Thank you for joining today's kickoff — we're excited to get Acme Corp live on the platform. "
            "Here's a summary of what we covered and what's coming next.\n\n"
            "GO-LIVE TARGETS\n"
            "• Operations team (120 users): August 1\n"
            "• Company-wide rollout: August 15\n\n"
            "KEY DECISIONS\n"
            "• Authentication: SAML 2.0 SSO (no username/password login)\n"
            "• Phased rollout starting with Operations team\n\n"
            "YOUR ACTION ITEMS\n"
            "• David → Employee CSV (name, email, department) → Jul 7\n"
            "• Sandra → Confirm executive sponsorship for change management → Jul 9\n\n"
            "OUR ACTION ITEMS\n"
            "• Rachel → SSO config guide + sandbox credentials → Jul 2\n"
            "• Jordan → Onboarding milestone tracker → Jul 2\n"
            "• Jordan → Technical deep-dive invite → Jul 3\n"
            "• Rachel → Custom training deck → Jul 10\n\n"
            "We'll touch base on Friday for a quick status check. Don't hesitate to reach out with questions.\n\n"
            "Best regards,\nJordan Blake · Customer Success Manager"
        ),
        "sentiment": "productive",
    },

    "📈 Investor Update Meeting": {
        "meeting_title": "Q2 Investor Update — Series B Portfolio Review",
        "attendees": ["Elena Vasquez (CEO)", "Carlos Mend (CFO)",
                      "Ingrid Hofer (Lead Investor, Apex Ventures)",
                      "Peter Ng (Analyst, Apex Ventures)", "Diana Ross (Board Observer)"],
        "duration": "30 minutes",
        "action_items": [
            {"task": "Send updated financial model (Q2 actuals + Q3 forecast) to Ingrid and Peter",
             "owner": "Carlos Mend", "due_date": "2025-07-04", "priority": "high"},
            {"task": "Prepare and share the Series B use-of-funds breakdown slide deck",
             "owner": "Elena Vasquez", "due_date": "2025-07-07", "priority": "high"},
            {"task": "Provide warm introductions to three enterprise pilot candidates from Apex portfolio",
             "owner": "Ingrid Hofer", "due_date": "2025-07-14", "priority": "medium"},
            {"task": "Draft board memo on Q3 hiring plan — focus on GTM and ML engineering headcount",
             "owner": "Elena Vasquez", "due_date": "2025-07-10", "priority": "medium"},
            {"task": "Schedule next quarterly board meeting for mid-October",
             "owner": "Diana Ross", "due_date": "2025-07-05", "priority": "low"},
        ],
        "decisions": [
            "Series B close is targeted for September 30; lead investor term sheet expected by August 15.",
            "Q3 burn rate will be held at $780K/month — no new headcount without board approval above this.",
            "Enterprise GTM motion takes priority over PLG expansion through end of year.",
        ],
        "summary": (
            "The Q2 investor update covered financial performance, strategic direction, and Series B timing. "
            "Elena opened with Q2 highlights: ARR grew 34% quarter-over-quarter to $4.2M, NRR hit 118%, "
            "and the company closed four new enterprise logos including a Fortune 500 pilot. Gross margin "
            "improved to 71% driven by infrastructure optimizations. The team is on a 14-month runway at "
            "the current burn rate of $780K/month. Ingrid expressed strong confidence in the trajectory and "
            "confirmed Apex's intent to co-lead the Series B.\n"
            "Carlos walked through Q3 projections targeting $5.6M ARR, contingent on closing three pipeline "
            "deals currently in legal. The board aligned on keeping burn flat at $780K/month and prioritizing "
            "enterprise GTM over self-serve growth through year-end. The Series B process will formally "
            "kick off in August with a target close of September 30. Ingrid committed to portfolio "
            "introductions for enterprise pilot expansion."
        ),
        "email_subject": "Q2 Investor Update — Follow-ups & Series B Next Steps",
        "email_body": (
            "Hi Ingrid, Peter, and Diana,\n\n"
            "Thank you for your time and continued confidence in the company. Q2 was a strong quarter "
            "and we're energized heading into our Series B process. Here's a summary of today's discussion.\n\n"
            "Q2 HIGHLIGHTS\n"
            "• ARR: $4.2M (+34% QoQ)\n"
            "• NRR: 118%\n"
            "• Gross Margin: 71%\n"
            "• New Enterprise Logos: 4 (incl. 1 Fortune 500 pilot)\n"
            "• Runway: 14 months at $780K/month burn\n\n"
            "KEY DECISIONS\n"
            "• Series B target close: September 30 (term sheet by August 15)\n"
            "• Burn rate held at $780K/month through Series B close\n"
            "• Enterprise GTM is the strategic focus through year-end\n\n"
            "ACTION ITEMS\n"
            "• Carlos → Q2 actuals + Q3 forecast model → Jul 4\n"
            "• Elena → Use-of-funds deck → Jul 7\n"
            "• Elena → Q3 hiring plan board memo → Jul 10\n"
            "• Ingrid → 3 enterprise pilot intros from Apex portfolio → Jul 14\n"
            "• Diana → Q4 board meeting invite → Jul 5\n\n"
            "We'll be in touch as the Series B process kicks off. Thank you for your partnership.\n\n"
            "Warm regards,\nElena Vasquez · CEO"
        ),
        "sentiment": "productive",
    },
}


def load_demo(scenario_name):
    s = DEMO_SCENARIOS[scenario_name]
    return render_meeting_output(
        meeting_title=s["meeting_title"],
        attendees_list=s["attendees"],
        duration=s["duration"],
        action_items=s["action_items"],
        decisions=s["decisions"],
        summary=s["summary"],
        email_subject=s["email_subject"],
        email_body=s["email_body"],
        sentiment=s["sentiment"],
    )


# ---------------------------------------------------------------------------
# Live analysis via OpenAI
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert meeting analyst. Given a meeting transcript or notes, extract structured intelligence.

Return ONLY valid JSON matching this exact schema — no markdown, no extra keys:
{
  "action_items": [
    {"task": "string", "owner": "string", "due_date": "YYYY-MM-DD", "priority": "high|medium|low"}
  ],
  "decisions": ["string"],
  "summary": "string (2-3 paragraphs separated by \\n)",
  "email_subject": "string",
  "email_body": "string (ready to send, plain text)",
  "meeting_sentiment": "productive|neutral|tense"
}

Guidelines:
- Extract every concrete action item with an explicit owner (guess a reasonable owner if not stated)
- Due dates: use relative offsets from today if not stated (e.g. +3 days for urgent, +7 for normal)
- summary: two paragraphs — first covers what was discussed, second covers outcomes and next steps
- email_body: professional, concise, includes decisions and all action items with owners and dates
- meeting_sentiment: judge overall tone from language and outcomes"""


def analyze_meeting(meeting_title, attendees, transcript, openai_key):
    key = openai_key.strip() if openai_key else ENV_OPENAI_KEY.strip()
    if not key:
        return (
            '<div style="background:rgba(239,68,68,0.15);border:1px solid rgba(248,113,113,0.5);'
            'border-radius:12px;padding:20px;color:#fca5a5;font-family:Inter,sans-serif;">'
            '<strong style="font-size:16px;">⚠️ OpenAI API Key Required</strong><br><br>'
            'Please enter your OpenAI API key in the field above to analyze a meeting transcript.<br>'
            'Your key is never stored — it is used only for this request.<br><br>'
            '<span style="color:#fda4af;">You can use the <strong>🎬 Live Demo</strong> tab to explore '
            'pre-computed examples without an API key.</span></div>'
        )
    if not transcript.strip():
        return (
            '<div style="background:rgba(234,179,8,0.12);border:1px solid rgba(234,179,8,0.4);'
            'border-radius:12px;padding:20px;color:#fde68a;font-family:Inter,sans-serif;">'
            '<strong>⚠️ No Transcript Provided</strong><br><br>'
            'Please paste your meeting transcript or notes in the text area above.</div>'
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)

        user_content = f"""Meeting Title: {meeting_title or "Untitled Meeting"}
Attendees: {attendees or "Not specified"}

TRANSCRIPT / NOTES:
{transcript}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            max_tokens=2000,
        )

        data = json.loads(response.choices[0].message.content)

        attendees_list = [a.strip() for a in attendees.split(",") if a.strip()] if attendees else []

        return render_meeting_output(
            meeting_title=meeting_title or "Meeting Analysis",
            attendees_list=attendees_list,
            duration="—",
            action_items=data.get("action_items", []),
            decisions=data.get("decisions", []),
            summary=data.get("summary", ""),
            email_subject=data.get("email_subject", "Meeting Summary"),
            email_body=data.get("email_body", ""),
            sentiment=data.get("meeting_sentiment", "neutral"),
        )

    except Exception as exc:
        err = str(exc)
        if "authentication" in err.lower() or "api key" in err.lower() or "invalid" in err.lower():
            msg = "Invalid API key. Please check your OpenAI API key and try again."
        elif "rate limit" in err.lower():
            msg = "Rate limit reached. Please wait a moment and try again."
        elif "quota" in err.lower():
            msg = "OpenAI quota exceeded. Please check your billing at platform.openai.com."
        else:
            msg = f"Error: {err}"
        return (
            f'<div style="background:rgba(239,68,68,0.15);border:1px solid rgba(248,113,113,0.5);'
            f'border-radius:12px;padding:20px;color:#fca5a5;font-family:Inter,sans-serif;">'
            f'<strong>❌ Analysis Failed</strong><br><br>{msg}</div>'
        )


# ---------------------------------------------------------------------------
# How It Works markdown
# ---------------------------------------------------------------------------

HOW_IT_WORKS_MD = """
## 🧠 AI Meeting Intelligence Agent

This tool uses **GPT-4o-mini** to transform unstructured meeting transcripts into structured intelligence:
action items with owners and deadlines, key decisions, a prose summary, and a ready-to-send follow-up email.

---

### n8n Automation Workflow

The production version runs as an automated n8n pipeline triggered by Zoom webhooks:

```
Zoom Webhook (recording.completed)
    ↓
Download Transcript  [HTTP Request → Zoom API]
    ↓
Prepare Transcript   [Set Node — formats prompt]
    ↓
GPT-4o-mini Agent    [OpenAI Chat Model]
    ↓
Extract Structured Data  [Output Parser → JSON]
    ↓
Split Action Items   [SplitInBatches]
    ↓
Create Asana Task    [Asana Node — one per action item]
    ↓
Send Summary Email   [Gmail → all attendees]
```

---

### What the AI Extracts

| Field | Description |
|---|---|
| **Action Items** | Task description, assigned owner, due date, priority (high/medium/low) |
| **Decisions** | Key decisions made — what was agreed upon |
| **Summary** | 2-paragraph prose summary: discussion + outcomes |
| **Email Draft** | Subject line + full email body ready to send |
| **Sentiment** | Overall meeting tone: productive / neutral / tense |

---

### Tips for Best Results

- **Paste the full transcript** — the more context, the better the action item extraction
- **Include speaker names** — helps the AI assign owners accurately
- **Mention deadlines** — if dates are discussed, include them so the AI captures them
- **Works with rough notes** — bullet points and abbreviated notes work fine too

---

### Privacy

Your transcript is sent to OpenAI's API for processing. Do not paste confidential or legally privileged content
unless your organization has an appropriate OpenAI data processing agreement in place.
"""


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

SCENARIO_NAMES = list(DEMO_SCENARIOS.keys())

theme = gr.themes.Soft(primary_hue="violet", secondary_hue="purple")

with gr.Blocks(theme=theme, title="🧠 AI Meeting Intelligence Agent") as demo:
    gr.HTML(
        '<div style="text-align:center;padding:28px 0 8px;font-family:Inter,sans-serif;">'
        '<div style="font-size:42px;margin-bottom:6px;">🧠</div>'
        '<h1 style="font-size:28px;font-weight:700;color:#e0e7ff;margin:0 0 8px;">AI Meeting Intelligence Agent</h1>'
        '<p style="color:#a5b4fc;font-size:15px;margin:0;">Transform any meeting transcript into action items, '
        'decisions, summaries &amp; follow-up emails</p></div>'
    )

    with gr.Tabs():
        # ── Tab 1: Live Demo ──────────────────────────────────────────────
        with gr.TabItem("🎬 Live Demo"):
            gr.HTML(
                '<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(129,140,248,0.3);'
                'border-radius:10px;padding:14px 18px;margin-bottom:4px;font-family:Inter,sans-serif;">'
                '<span style="color:#a5b4fc;font-weight:600;">✨ No API key needed</span>'
                '<span style="color:#c4b5fd;"> — explore pre-computed outputs for 4 real meeting types</span>'
                '</div>'
            )
            with gr.Row():
                scenario_dropdown = gr.Dropdown(
                    choices=SCENARIO_NAMES,
                    value=SCENARIO_NAMES[0],
                    label="Select a Meeting Scenario",
                    interactive=True,
                )
                load_btn = gr.Button("▶ Load Demo", variant="primary", scale=0, min_width=140)

            demo_info = gr.HTML(
                value=(
                    '<div style="display:flex;gap:16px;flex-wrap:wrap;font-family:Inter,sans-serif;margin:4px 0 8px;">'
                    + "".join(
                        f'<div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);'
                        f'border-radius:8px;padding:8px 14px;">'
                        f'<span style="color:#a5b4fc;font-size:12px;font-weight:600;">Scenario {i+1}</span>'
                        f'<span style="color:#e0e7ff;font-size:13px;"> {name}</span></div>'
                        for i, name in enumerate(SCENARIO_NAMES)
                    )
                    + "</div>"
                )
            )

            demo_output = gr.HTML(label="Meeting Analysis Output", value=load_demo(SCENARIO_NAMES[0]))

            load_btn.click(fn=load_demo, inputs=[scenario_dropdown], outputs=[demo_output])
            scenario_dropdown.change(fn=load_demo, inputs=[scenario_dropdown], outputs=[demo_output])

        # ── Tab 2: Analyze Meeting ────────────────────────────────────────
        with gr.TabItem("🧠 Analyze Meeting"):
            gr.HTML(
                '<div style="background:rgba(59,130,246,0.1);border:1px solid rgba(96,165,250,0.3);'
                'border-radius:10px;padding:14px 18px;margin-bottom:4px;font-family:Inter,sans-serif;">'
                '<span style="color:#93c5fd;font-weight:600;">🔑 Requires OpenAI API key</span>'
                '<span style="color:#bfdbfe;"> — paste any meeting transcript to get instant structured output</span>'
                '</div>'
            )
            with gr.Row():
                with gr.Column(scale=1):
                    meeting_title_input = gr.Textbox(
                        label="Meeting Title",
                        placeholder="e.g. Q3 Product Planning, Sprint 24 Retro, Client Kickoff...",
                        lines=1,
                    )
                    attendees_input = gr.Textbox(
                        label="Attendees (comma-separated)",
                        placeholder="e.g. Alice (PM), Bob (Eng), Carol (Design)",
                        lines=1,
                    )
                    openai_key_input = gr.Textbox(
                        label="OpenAI API Key",
                        placeholder="sk-...",
                        type="password",
                        lines=1,
                        value=ENV_OPENAI_KEY,
                    )

            transcript_input = gr.Textbox(
                label="Meeting Transcript or Notes",
                placeholder=(
                    "Paste your meeting transcript, notes, or rough bullet points here...\n\n"
                    "Example:\n"
                    "[10:02] Alice: Let's kick off. Main agenda is the Q3 roadmap.\n"
                    "[10:05] Bob: Engineering can handle the API work but needs 3 weeks.\n"
                    "[10:08] Carol: Design is ready to start the new onboarding mockups this week.\n"
                    "Decision: We're going with Option B for the checkout flow.\n"
                    "Action: Bob to send capacity estimates by Friday."
                ),
                lines=12,
            )

            analyze_btn = gr.Button("🧠 Analyze Meeting", variant="primary", size="lg")

            analysis_output = gr.HTML(label="Analysis Results")

            analyze_btn.click(
                fn=analyze_meeting,
                inputs=[meeting_title_input, attendees_input, transcript_input, openai_key_input],
                outputs=[analysis_output],
            )

        # ── Tab 3: How It Works ───────────────────────────────────────────
        with gr.TabItem("📖 How It Works"):
            gr.Markdown(HOW_IT_WORKS_MD)

    gr.HTML(
        '<div style="text-align:center;padding:20px 0 8px;font-family:Inter,sans-serif;">'
        '<span style="color:#6b7280;font-size:13px;">Built with Gradio 5 · Powered by GPT-4o-mini · '
        'Part of the n8n AI Agent Toolkit</span></div>'
    )

if __name__ == "__main__":
    demo.launch()
