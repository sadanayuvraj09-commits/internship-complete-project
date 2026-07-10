import json
import os
import time
from dotenv import load_dotenv

load_dotenv()


def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq

        return Groq(api_key=api_key)
    except Exception:
        return None


groq_client = _get_groq_client()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def _call_gemini(prompt: str, max_retries: int | None = None) -> str | None:
    """Kept this function name so every other function below (and any external
    imports) doesn't need to change. It now calls Groq under the hood instead
    of Gemini."""
    if groq_client is None:
        return None

    effective_retries = max(1, int(max_retries or os.getenv("AI_MAX_RETRIES", "1")))
    retry_delay = max(0.0, float(os.getenv("AI_RETRY_DELAY_SECONDS", "0")))

    for attempt in range(1, effective_retries + 1):
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Groq call failed] attempt {attempt}/{effective_retries}: {type(e).__name__}: {e}")
            if attempt == effective_retries:
                return None
            if retry_delay > 0:
                time.sleep(retry_delay)
    return None


def _fallback_summary(gap: dict, reason: str = "AI summary unavailable") -> str:
    developer = gap.get("developer_id", "UNKNOWN")
    date = gap.get("date", "UNKNOWN")
    return f"{reason} for {developer} on {date}."


def generate_ai_summary(gap: dict, max_retries: int = 3) -> str:
    """Takes one gap document (dict from MongoDB) and returns an AI-written summary."""
    result = _call_gemini(
        f"""You are reviewing developer activity to detect unbilled work hours.

Developer: {gap.get('developer_id', 'UNKNOWN')}
Date: {gap.get('date', 'UNKNOWN')}
GitHub commits: {gap.get('github_count', 0)}
Slack messages: {gap.get('slack_count', 0)}
Jira updates: {gap.get('jira_count', 0)}
Hours logged in timesheet: {gap.get('hours_logged', 0)}
Reason flagged: {gap.get('reason', 'unknown')}

Write exactly 1-2 sentences summarizing this discrepancy in plain, professional language.
Do not speculate about cause - just state the facts clearly.""",
        max_retries=max_retries,
    )

    return result or _fallback_summary(gap)


def generate_gap_priority(gap: dict, max_retries: int = 3) -> str:
    github = gap.get("github_count", 0) or 0
    slack = gap.get("slack_count", 0) or 0
    jira = gap.get("jira_count", 0) or 0
    hours_logged = gap.get("hours_logged", 0) or 0
    total_activity = github + slack + jira

    # Priority is decided by fixed rules, not by the AI, so it's consistent every time.
    if total_activity >= 6 and hours_logged == 0:
        computed_priority = "High"
    elif total_activity >= 3 or (hours_logged > 0 and total_activity > 0):
        computed_priority = "Medium"
    else:
        computed_priority = "Low"

    prompt = f"""You are an expert reviewer of developer activity and timesheet data.

Developer: {gap.get('developer_id', 'UNKNOWN')}
Date: {gap.get('date', 'UNKNOWN')}
GitHub commits: {github}
Slack messages: {slack}
Jira updates: {jira}
Hours logged: {hours_logged}
Reason flagged: {gap.get('reason', 'unknown')}

This gap has already been classified as {computed_priority} priority based on activity counts.
Write exactly one sentence explaining why, referencing the actual activity numbers above.
Return only that one sentence — do not restate the priority label."""

    explanation = _call_gemini(prompt, max_retries=max_retries)
    if explanation is None:
        developer = gap.get("developer_id", "UNKNOWN")
        date = gap.get("date", "UNKNOWN")
        explanation = f"AI explanation unavailable for {developer} on {date}."

    return f"{computed_priority} priority: {explanation}"


def suggest_timesheet_entry(activity: dict, max_retries: int = 3) -> dict[str, str | float]:
    prompt = f"""You are an AI assistant that writes suggested timesheet entries from developer activity.

Developer: {activity.get('developer_id', 'UNKNOWN')}
Date: {activity.get('date', 'UNKNOWN')}
GitHub commits: {activity.get('github_count', 0)}
Slack messages: {activity.get('slack_count', 0)}
Jira updates: {activity.get('jira_count', 0)}
Hours logged: {activity.get('hours_logged', 0)}
Activity summary: {activity.get('activity_summary', 'No summary provided.')}

Suggest a timesheet entry with:
- hours
- project or task name
- a short note

Write the answer in JSON with keys: hours, project, note."""

    result = _call_gemini(prompt, max_retries=max_retries)
    if not result:
        return {
            "hours": 0,
            "project": "Unknown",
            "note": "AI suggestion unavailable.",
        }

    # Strip markdown code fences (```json ... ```) if the model added them
    cleaned = result.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            parsed["hours"] = float(parsed.get("hours", 0))
            parsed["project"] = str(parsed.get("project", "Unknown"))
            parsed["note"] = str(parsed.get("note", "AI suggestion returned invalid format."))
            return parsed
    except Exception:
        pass

    return {
        "hours": 0,
        "project": "Unknown",
        "note": result,
    }


def match_activity_to_project(activity: dict, max_retries: int = 3) -> str:
    prompt = f"""You are an AI system that matches developer activity to projects.

Developer: {activity.get('developer_id', 'UNKNOWN')}
Date: {activity.get('date', 'UNKNOWN')}
Commit messages: {activity.get('commit_messages', 'None')}
Slack messages: {activity.get('slack_messages', 'None')}
Jira issues: {activity.get('jira_issues', 'None')}
Current project labels: {activity.get('current_projects', 'None')}

Suggest the most likely project or task for this activity.
Return a single project name and one sentence explaining your choice."""

    result = _call_gemini(prompt, max_retries=max_retries)
    if result is None:
        return "Unknown project: AI unavailable."
    return result


def answer_gap_question(details: dict, question: str, max_retries: int = 3) -> str:
    prompt = f"""You are an AI analyst for developer billing and timesheet gaps.

Data:
- Developer: {details.get('developer_id', 'UNKNOWN')}
- Date: {details.get('date', 'UNKNOWN')}
- GitHub commits: {details.get('github_count', 0)}
- Slack messages: {details.get('slack_count', 0)}
- Jira updates: {details.get('jira_count', 0)}
- Hours logged: {details.get('hours_logged', 0)}
- Gap reason: {details.get('reason', 'unknown')}
- Any other relevant activity details: {details.get('details', 'None')}

User question:
{question}

Answer in plain business language, using the data above.
If the question cannot be answered from these details, say "Not enough information."""

    result = _call_gemini(prompt, max_retries=max_retries)
    if result is None:
        return "Not enough information."
    return result


if __name__ == "__main__":
    fake_gap = {
        "developer_id": "YUVRAJ SADANA",
        "date": "2026-06-29",
        "github_count": 5,
        "slack_count": 0,
        "jira_count": 0,
        "hours_logged": 0,
        "reason": "Commit exists but no timesheet",
    }
    print(generate_ai_summary(fake_gap))