#!/usr/bin/env python3
"""
Personal Ops Assistant - Main Entry Point
==========================================
Fully automated AI personal assistant system.
- Claude (primary): Daily planning, execution guidance, proactive management
- Grok (secondary): Unfiltered pressure advisor, blind spot detection

Usage:
    python main.py              # Start the scheduler (runs continuously)
        python main.py --test morning   # Test a single loop
            python main.py --test midday
                python main.py --test evening
                    python main.py --ask "What should I focus on?"
"""

import sys
import argparse
import structlog

structlog.configure(
      processors=[
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
                structlog.dev.ConsoleRenderer(),
      ],
)

log = structlog.get_logger()


def main():
      parser = argparse.ArgumentParser(description="Personal Ops Assistant")
      parser.add_argument(
          "--test",
          choices=["morning", "midday", "evening"],
          help="Run a single loop for testing",
      )
      parser.add_argument(
          "--ask",
          type=str,
          help="Ask Claude a one-off question",
      )
      args = parser.parse_args()

    from scheduler import OpsScheduler
    from claude_agent import ClaudeAgent
    from calendar_service import CalendarService

    if args.ask:
              # One-off question mode
              claude = ClaudeAgent()
              calendar = CalendarService()
              events = calendar.get_all_today_events()
              events_text = calendar.format_events_for_prompt(events)
              response = claude.on_demand(args.ask, events_text)
              print("\n" + claude.format_response(response))
              return

    if args.test:
              # Test a single loop
              scheduler = OpsScheduler()
              log.info(f"Running {args.test} loop (test mode)")
              scheduler.run_once(args.test)
              return

    # Normal mode: run the scheduler continuously
    log.info("Starting Personal Ops Assistant")
    scheduler = OpsScheduler()
    scheduler.run()


if __name__ == "__main__":
      main()
