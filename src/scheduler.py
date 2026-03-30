"""
Scheduler - Orchestrates the daily loops (morning/midday/evening).
Uses APScheduler to trigger Claude + Grok agents at configured times,
fetches calendar data, and sends notifications via Twilio.
"""

import json
import datetime
from pathlib import Path
import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings
from calendar_service import CalendarService
from claude_agent import ClaudeAgent
from grok_agent import GrokAgent
from twilio_service import TwilioService

log = structlog.get_logger()

# Daily log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class OpsScheduler:
      """Main orchestrator that runs the daily loops."""

    def __init__(self):
              self.calendar = CalendarService()
              self.claude = ClaudeAgent()
              self.grok = GrokAgent()
              self.twilio = TwilioService()
              self.scheduler = BlockingScheduler(timezone=settings.user_timezone)
              self.daily_log = {}

    def _get_events_text(self) -> str:
              """Fetch and format today's events."""
              events = self.calendar.get_all_today_events()
              return self.calendar.format_events_for_prompt(events)

    def _save_daily_log(self):
              """Save the daily log to a JSON file."""
              today = datetime.date.today().isoformat()
              log_path = LOG_DIR / f"{today}.json"
              with open(log_path, "w") as f:
                            json.dump(self.daily_log, f, indent=2, default=str)
                        log.info("Daily log saved", path=str(log_path))

    def morning_loop(self):
              """Morning loop - Claude plans the day, sends brief via SMS."""
        log.info("=== MORNING LOOP START ===")
        events_text = self._get_events_text()

        # Claude generates the plan
        claude_response = self.claude.morning_plan(events_text)
        claude_text = self.claude.format_response(claude_response)
        log.info("Claude morning plan", response=claude_text)

        # Send morning brief via SMS
        self.twilio.send_morning_brief(claude_text)

        # Store in daily log
        self.daily_log["morning"] = {
                      "timestamp": datetime.datetime.now().isoformat(),
                      "events": events_text,
                      "claude_plan": claude_response,
        }
        self._save_daily_log()
        log.info("=== MORNING LOOP COMPLETE ===")

    def midday_loop(self):
              """Midday loop - Grok critiques progress, sends alerts if needed."""
        log.info("=== MIDDAY LOOP START ===")
        events_text = self._get_events_text()

        # Get Claude's earlier plan for context
        morning_plan = self.daily_log.get("morning", {}).get("claude_plan", {})
        claude_plan_text = self.claude.format_response(morning_plan) if morning_plan else ""

        # Claude midday check
        claude_response = self.claude.midday_check(events_text)
        claude_text = self.claude.format_response(claude_response)

        # Grok pressure check
        grok_response = self.grok.midday_critique(events_text, claude_plan_text)
        grok_text = self.grok.format_response(grok_response)

        # Send combined check-in
        combined = f"CLAUDE:\n{claude_text}\n\nGROK:\n{grok_text}"
        self.twilio.send_midday_check(combined)

        # Store in daily log
        self.daily_log["midday"] = {
                      "timestamp": datetime.datetime.now().isoformat(),
                      "events": events_text,
                      "claude_check": claude_response,
                      "grok_critique": grok_response,
        }
        self._save_daily_log()
        log.info("=== MIDDAY LOOP COMPLETE ===")

    def evening_loop(self):
              """Evening loop - Both agents review the day, log results."""
        log.info("=== EVENING LOOP START ===")
        events_text = self._get_events_text()

        # Claude evening review
        claude_response = self.claude.evening_review(events_text)
        claude_text = self.claude.format_response(claude_response)

        # Grok evening critique
        grok_response = self.grok.evening_critique(events_text)
        grok_text = self.grok.format_response(grok_response)

        # Send evening summary
        combined = f"REVIEW:\n{claude_text}\n\nCRITIQUE:\n{grok_text}"
        self.twilio.send_evening_summary(combined)

        # Store in daily log
        self.daily_log["evening"] = {
                      "timestamp": datetime.datetime.now().isoformat(),
                      "events": events_text,
                      "claude_review": claude_response,
                      "grok_critique": grok_response,
        }
        self._save_daily_log()
        log.info("=== EVENING LOOP COMPLETE ===")

    def setup_schedules(self):
              """Configure the cron-based schedules."""
              # Morning loop
              self.scheduler.add_job(
                            self.morning_loop,
                            CronTrigger(hour=settings.morning_hour, minute=0),
                            id="morning_loop",
                            name="Morning Planning Loop",
              )

        # Midday loop
        self.scheduler.add_job(
                      self.midday_loop,
                      CronTrigger(hour=settings.midday_hour, minute=0),
                      id="midday_loop",
                      name="Midday Check-In Loop",
        )

        # Evening loop
        self.scheduler.add_job(
                      self.evening_loop,
                      CronTrigger(hour=settings.evening_hour, minute=0),
                      id="evening_loop",
                      name="Evening Review Loop",
        )

        log.info(
                      "Schedules configured",
                      morning=f"{settings.morning_hour}:00",
                      midday=f"{settings.midday_hour}:00",
                      evening=f"{settings.evening_hour}:00",
                      timezone=settings.user_timezone,
        )

    def run(self):
              """Start the scheduler."""
              self.setup_schedules()
              log.info("Personal Ops Assistant running. Press Ctrl+C to stop.")
              try:
                            self.scheduler.start()
except (KeyboardInterrupt, SystemExit):
            log.info("Scheduler stopped")

    def run_once(self, loop: str = "morning"):
              """Run a single loop manually (for testing)."""
              if loop == "morning":
                            self.morning_loop()
elif loop == "midday":
            self.midday_loop()
elif loop == "evening":
            self.evening_loop()
else:
            log.error("Unknown loop", loop=loop)
