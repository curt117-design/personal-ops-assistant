"""
Claude Agent - Primary personal operations system.
Uses Anthropic's Claude API for structured daily planning,
execution guidance, and proactive management.
"""

import json
import datetime
import structlog
from anthropic import Anthropic

from config import settings

log = structlog.get_logger()

CLAUDE_SYSTEM_PROMPT = f"""You are an autonomous personal operations system for {settings.user_name}.

CONTEXT:
- Active duty Air Force, stationed at Del Rio AFB
- Structured schedule: Mon-Fri duty {settings.user_duty_start}-{settings.user_duty_end}
- Values: discipline, growth, financial freedom, self-mastery
- Gym schedule: Push/Pull/Legs rotation, 0600-0700 daily
- Uses Google Calendar and Outlook for scheduling

OBJECTIVES:
1. Manage calendar and tasks aligned to values: discipline, health, relationships, growth
2. Provide structured next actions and risk assessment
3. Reduce decision fatigue and increase execution consistency
4. Challenge weak thinking when detected

OPERATING LOOPS:
- Morning: Generate clear execution plan (schedule + priorities)
- Midday: Check alignment (on track or drifting?)
- Evening: Review + adjust (what worked, what didn't)

TRIGGER BEHAVIOR:
- If idle -> suggest next high-value task
- If overwhelmed -> simplify into 1-3 actions
- If off-track -> correct directly, no softness
- If consistent -> reinforce behavior

PRIORITY SYSTEM:
1. Duty / responsibilities
2. Long-term growth (education, finances)
3. Physical health
4. Mental clarity / presence

OUTPUT FORMAT (always JSON):
{{
    "current_plan": "what matters right now",
        "next_action": "clear, immediate step",
            "risk": "what will go wrong if ignored",
                "optimization": "optional high-value suggestion"
}}

STYLE: Direct. No filler. No generic advice. Challenge weak thinking."""


class ClaudeAgent:
      """Primary AI agent using Anthropic's Claude for personal operations."""

    def __init__(self):
              self.client = None
              if settings.anthropic_api_key:
                            self.client = Anthropic(api_key=settings.anthropic_api_key)
                            log.info("Claude agent initialized")
else:
            log.warning("Anthropic API key not set - Claude agent disabled")

    def _call(self, user_message: str) -> dict:
              """Make a Claude API call and parse JSON response."""
              if not self.client:
                            log.warning("Claude agent not configured")
                            return {"current_plan": "Agent not configured", "next_action": "Set ANTHROPIC_API_KEY", "risk": "No AI guidance", "optimization": "N/A"}

              try:
                            response = self.client.messages.create(
                                              model="claude-sonnet-4-20250514",
                                              max_tokens=1024,
                                              system=CLAUDE_SYSTEM_PROMPT,
                                              messages=[{"role": "user", "content": user_message}],
                            )

                  text = response.content[0].text
            log.info("Claude response received", length=len(text))

            # Try to parse as JSON
            try:
                              return json.loads(text)
except json.JSONDecodeError:
                # If not valid JSON, wrap it
                return {
                                      "current_plan": text,
                                      "next_action": "Review above",
                                      "risk": "N/A",
                                      "optimization": "N/A",
                }

except Exception as e:
            log.error("Claude API call failed", error=str(e))
            return {"current_plan": f"Error: {str(e)}", "next_action": "Check API key", "risk": "Agent offline", "optimization": "N/A"}

    def morning_plan(self, events_text: str) -> dict:
              """Generate the morning execution plan."""
        now = datetime.datetime.now()
        prompt = f"""It is {now.strftime('%A, %B %d %Y at %H:%M')}.

        TODAY'S SCHEDULE:
        {events_text}

        Generate my morning execution plan. What matters today? What's the first thing I should focus on? Identify any risks or conflicts in the schedule."""

        return self._call(prompt)

    def midday_check(self, events_text: str, notes: str = "") -> dict:
              """Midday alignment check."""
        prompt = f"""MIDDAY CHECK-IN.

        TODAY'S REMAINING SCHEDULE:
        {events_text}

        USER NOTES: {notes if notes else 'None provided'}

        Am I on track or drifting? What should I adjust for the rest of the day? Be direct."""

        return self._call(prompt)

    def evening_review(self, events_text: str, notes: str = "") -> dict:
              """Evening review and next-day prep."""
        prompt = f"""EVENING REVIEW.

        TODAY'S SCHEDULE WAS:
        {events_text}

        USER NOTES: {notes if notes else 'None provided'}

        Review the day: What was accomplished? What was avoided? What needs to change tomorrow? Be honest and direct."""

        return self._call(prompt)

    def on_demand(self, question: str, events_text: str = "") -> dict:
              """Handle ad-hoc questions from the user."""
        context = f"\nCURRENT SCHEDULE:\n{events_text}" if events_text else ""
        prompt = f"""{question}{context}"""
        return self._call(prompt)

    def format_response(self, response: dict) -> str:
              """Format a Claude response into a human-readable string."""
        parts = []
        if response.get("current_plan"):
                      parts.append(f"PLAN: {response['current_plan']}")
                  if response.get("next_action"):
                                parts.append(f"NEXT: {response['next_action']}")
                            if response.get("risk"):
                                          parts.append(f"RISK: {response['risk']}")
                                      if response.get("optimization") and response["optimization"] != "N/A":
                                                    parts.append(f"OPT: {response['optimization']}")
                                                return "\n".join(parts)
