"""
Configuration module - loads all environment variables and provides
typed access to settings throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
      # Anthropic
      anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # xAI / Grok
      xai_api_key: str = os.getenv("XAI_API_KEY", "")

    # Google Calendar
      google_credentials_file: str = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
      google_token_file: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    # Microsoft / Azure
      azure_client_id: str = os.getenv("AZURE_CLIENT_ID", "")
      azure_client_secret: str = os.getenv("AZURE_CLIENT_SECRET", "")
      azure_tenant_id: str = os.getenv("AZURE_TENANT_ID", "")

    # Twilio
      twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
      twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
      twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
      user_phone_number: str = os.getenv("USER_PHONE_NUMBER", "")

    # Schedule
      morning_hour: int = int(os.getenv("MORNING_HOUR", "6"))
      midday_hour: int = int(os.getenv("MIDDAY_HOUR", "12"))
      evening_hour: int = int(os.getenv("EVENING_HOUR", "19"))

    # User context
      user_name: str = os.getenv("USER_NAME", "User")
      user_timezone: str = os.getenv("USER_TIMEZONE", "America/Chicago")
      user_duty_start: str = os.getenv("USER_DUTY_START", "0700")
      user_duty_end: str = os.getenv("USER_DUTY_END", "1700")


settings = Settings()
