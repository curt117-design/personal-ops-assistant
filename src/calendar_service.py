"""
Calendar Service - Google Calendar & Microsoft Outlook integration.
Fetches today's events, creates events, and provides schedule context.
"""

import datetime
import os
import json
import structlog
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import msal
import requests

from config import settings

log = structlog.get_logger()

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class GoogleCalendarService:
      """Handles Google Calendar API interactions."""

    def __init__(self):
              self.creds = None
              self.service = None
              self._authenticate()

    def _authenticate(self):
              """Load or refresh Google OAuth2 credentials."""
              token_path = settings.google_token_file
              creds_path = settings.google_credentials_file

        if os.path.exists(token_path):
                      self.creds = Credentials.from_authorized_user_file(token_path, GOOGLE_SCOPES)

        if not self.creds or not self.creds.valid:
                      if self.creds and self.creds.expired and self.creds.refresh_token:
                                        self.creds.refresh(Request())
        else:
                if not os.path.exists(creds_path):
                                      log.error("Google credentials file not found", path=creds_path)
                                      return
                                  flow = InstalledAppFlow.from_client_secrets_file(creds_path, GOOGLE_SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(token_path, "w") as token:
                              token.write(self.creds.to_json())

        self.service = build("calendar", "v3", credentials=self.creds)
        log.info("Google Calendar authenticated")

    def get_today_events(self) -> List[Dict]:
              """Fetch all events for today."""
        if not self.service:
                      log.warning("Google Calendar not connected")
                      return []

        now = datetime.datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
        end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        try:
                      result = self.service.events().list(
                                        calendarId="primary",
                                        timeMin=start_of_day,
                                        timeMax=end_of_day,
                                        singleEvents=True,
                                        orderBy="startTime",
                      ).execute()

            events = result.get("items", [])
            log.info("Fetched Google Calendar events", count=len(events))
            return [self._parse_event(e) for e in events]
except Exception as e:
            log.error("Failed to fetch Google events", error=str(e))
            return []

    def _parse_event(self, event: dict) -> Dict:
              """Parse a Google Calendar event into a clean dict."""
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        return {
                      "source": "google",
                      "title": event.get("summary", "No Title"),
                      "start": start,
                      "end": end,
                      "location": event.get("location", ""),
                      "description": event.get("description", ""),
        }


class OutlookCalendarService:
      """Handles Microsoft Outlook Calendar via Graph API."""

    GRAPH_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self):
              self.access_token = None
        self._authenticate()

    def _authenticate(self):
              """Authenticate via MSAL device code flow or client credentials."""
        if not settings.azure_client_id:
                      log.info("Outlook not configured, skipping")
                      return

        app = msal.PublicClientApplication(
                      settings.azure_client_id,
                      authority=f"https://login.microsoftonline.com/{settings.azure_tenant_id}",
        )

        # Try cached token first
        accounts = app.get_accounts()
        if accounts:
                      result = app.acquire_token_silent(
                                        ["Calendars.Read"], account=accounts[0]
                      )
                      if result and "access_token" in result:
                                        self.access_token = result["access_token"]
                                        log.info("Outlook authenticated via cache")
                                        return

                  # Device code flow for first-time auth
                  flow = app.initiate_device_flow(scopes=["Calendars.Read"])
        if "user_code" in flow:
                      log.info("Outlook auth required", message=flow["message"])
                      result = app.acquire_token_by_device_flow(flow)
                      if "access_token" in result:
                                        self.access_token = result["access_token"]
                                        log.info("Outlook authenticated")

              def get_today_events(self) -> List[Dict]:
                        """Fetch today's Outlook calendar events."""
                        if not self.access_token:
                                      return []

                        now = datetime.datetime.utcnow()
                        start = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
                        end = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
                      "$filter": f"start/dateTime ge '{start}' and end/dateTime le '{end}'",
                      "$orderby": "start/dateTime",
        }

        try:
                      resp = requests.get(
                                        f"{self.GRAPH_URL}/me/events", headers=headers, params=params
                      )
                      resp.raise_for_status()
                      events = resp.json().get("value", [])
                      log.info("Fetched Outlook events", count=len(events))
                      return [self._parse_event(e) for e in events]
except Exception as e:
            log.error("Failed to fetch Outlook events", error=str(e))
            return []

    def _parse_event(self, event: dict) -> Dict:
              return {
                            "source": "outlook",
                            "title": event.get("subject", "No Title"),
                            "start": event["start"]["dateTime"],
                            "end": event["end"]["dateTime"],
                            "location": event.get("location", {}).get("displayName", ""),
                            "description": event.get("bodyPreview", ""),
              }


class CalendarService:
      """Unified calendar service that merges Google + Outlook events."""

    def __init__(self):
              self.google = GoogleCalendarService()
        self.outlook = OutlookCalendarService()

    def get_all_today_events(self) -> List[Dict]:
              """Get merged, sorted events from all calendar sources."""
        events = self.google.get_today_events() + self.outlook.get_today_events()
        events.sort(key=lambda e: e.get("start", ""))
        return events

    def format_events_for_prompt(self, events: List[Dict]) -> str:
              """Format events into a clean string for LLM prompts."""
        if not events:
                      return "No events scheduled for today."

        lines = []
        for e in events:
                      time_str = e["start"]
                      if "T" in time_str:
                                        time_str = time_str.split("T")[1][:5]
                                    lines.append(f"- {time_str} | {e['title']} ({e['source']})")
            if e.get("location"):
                              lines.append(f"  Location: {e['location']}")

        return "\n".join(lines)
