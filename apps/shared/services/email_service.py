import json
import requests
from django.conf import settings


class EmailService:
    """
    Service to send emails using Brevo's transactional email API.
    """

    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, "BREVO_API_KEY", None)
        if not self.api_key:
            raise ValueError("Brevo API key is not configured.")

    def send_email(self, sender_name, sender_email, recipient_name, recipient_email, subject, html_content):
        """
        Send an email via Brevo.
        """
        payload = {
            "sender": {
                "name": sender_name,
                "email": sender_email
            },
            "to": [
                {
                    "email": recipient_email,
                    "name": recipient_name
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        }

        headers = {
            "accept": "application/json",
            "api-key": self.api_key,
            "content-type": "application/json"
        }

        try:
            response = requests.post(
                self.BREVO_API_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e)
            }
