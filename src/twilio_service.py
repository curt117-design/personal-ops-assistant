"""
Twilio Service - SMS and Voice call notifications.
Sends text messages and makes phone calls with TTS.
"""

import time
import structlog
from twilio.rest import Client

from config import settings

log = structlog.get_logger()


class TwilioService:
      """Handles SMS and voice call notifications via Twilio."""

    def __init__(self):
              self.client = None
              if settings.twilio_account_sid and settings.twilio_auth_token:
                            self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
                            log.info("Twilio client initialized")
else:
            log.warning("Twilio not configured - notifications disabled")

    def send_sms(self, message: str, to: str = None) -> bool:
              """Send an SMS message."""
              if not self.client:
                            log.warning("Twilio not configured, skipping SMS")
                            print(f"[SMS MOCK] {message}")
                            return False

              to_number = to or settings.user_phone_number
              try:
                            msg = self.client.messages.create(
                                              body=message,
                                              from_=settings.twilio_phone_number,
                                              to=to_number,
                            )
                            log.info("SMS sent", sid=msg.sid, to=to_number)
                            time.sleep(1)  # Rate limiting: ~1 SMS/sec
            return True
except Exception as e:
            log.error("Failed to send SMS", error=str(e))
            return False

    def make_call(self, message: str, to: str = None) -> bool:
              """Make a voice call with text-to-speech."""
              if not self.client:
                            log.warning("Twilio not configured, skipping call")
                            print(f"[CALL MOCK] {message}")
                            return False

              to_number = to or settings.user_phone_number
              twiml = f'<Response><Say voice="alice">{message}</Say></Response>'

        try:
                      call = self.client.calls.create(
                                        twiml=twiml,
                                        to=to_number,
                                        from_=settings.twilio_phone_number,
                      )
                      log.info("Call initiated", sid=call.sid, to=to_number)
                      return True
except Exception as e:
              log.error("Failed to make call", error=str(e))
              return False

    def send_morning_brief(self, plan: str):
              """Send the morning execution plan via SMS."""
              message = f"Good morning {settings.user_name}!\n\n{plan}"
              if len(message) > 1500:
                            message = message[:1497] + "..."
                        self.send_sms(message)

    def send_midday_check(self, status: str):
              """Send midday check-in - can be SMS or call."""
        message = f"Midday check: {status}"
        self.send_sms(message)

    def send_evening_summary(self, summary: str):
              """Send evening review summary."""
        message = f"Evening review:\n{summary}"
        self.send_sms(message)

    def send_alert(self, alert: str):
              """Send an urgent alert - uses both SMS and call."""
        self.send_sms(f"ALERT: {alert}")
        self.make_call(f"Attention. {alert}")
