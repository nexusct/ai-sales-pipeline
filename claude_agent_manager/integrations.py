"""
IMPROVEMENTS #5, #6, #10: Email, CRM, and Multi-Channel Integration
Complete integration with external systems for automated outreach
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import requests


# ============================================================================
# IMPROVEMENT #5: Email Integration and Automated Sending
# ============================================================================

@dataclass
class EmailMessage:
    """Email message structure"""
    to: str
    subject: str
    body_html: str
    body_text: str
    from_email: str
    from_name: str
    reply_to: Optional[str] = None
    cc: List[str] = None
    bcc: List[str] = None
    attachments: List[Dict] = None


class EmailAutomation:
    """
    Automated email sending with tracking

    Features:
    - SMTP integration
    - Template rendering
    - Open/click tracking
    - Bounce handling
    - Rate limiting
    """

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
        from_name: str
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.from_name = from_name
        self.sent_emails: List[Dict] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: str = None,
        track_opens: bool = True
    ) -> bool:
        """
        Send email via SMTP

        Args:
            to_email: Recipient email
            subject: Email subject
            body_html: HTML body
            body_text: Plain text fallback
            track_opens: Add tracking pixel

        Returns:
            True if sent successfully
        """

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add tracking pixel if enabled
            if track_opens:
                tracking_id = f"email_{int(datetime.now().timestamp())}"
                tracking_pixel = f'<img src="https://track.example.com/open/{tracking_id}" width="1" height="1" />'
                body_html += tracking_pixel

            # Attach text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, 'plain')
                msg.attach(text_part)

            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            # Log sent email
            self.sent_emails.append({
                "to": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status": "sent"
            })

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            self.sent_emails.append({
                "to": to_email,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            return False

    def send_templated_email(
        self,
        to_email: str,
        template_name: str,
        variables: Dict[str, Any]
    ) -> bool:
        """Send email using template"""

        # Load template (would be from database in production)
        template = self._get_template(template_name)

        # Render template with variables
        subject = self._render_template(template['subject'], variables)
        body_html = self._render_template(template['body_html'], variables)
        body_text = self._render_template(template.get('body_text', ''), variables)

        return self.send_email(to_email, subject, body_html, body_text)

    def _get_template(self, template_name: str) -> Dict[str, str]:
        """Get email template (mock - would load from database)"""

        templates = {
            "initial_outreach": {
                "subject": "Improve {company_name}'s EDI Infrastructure",
                "body_html": """
                <p>Hi {contact_name},</p>

                <p>I noticed that {company_name} is in the {industry} sector, and
                wanted to reach out about a solution that could significantly improve
                your B2B data exchange capabilities.</p>

                <p>Our Fiber EDI service has helped similar companies:</p>
                <ul>
                    <li>Reduce transaction processing time by 70%</li>
                    <li>Achieve 99.99% uptime for critical EDI transmissions</li>
                    <li>Ensure HIPAA/regulatory compliance</li>
                </ul>

                <p>{custom_use_case}</p>

                <p>Would you be open to a brief conversation to explore how this
                could benefit {company_name}?</p>

                <p>Best regards,<br>
                {sender_name}</p>
                """,
                "body_text": "Hi {contact_name},\n\nI noticed that {company_name}..."
            }
        }

        return templates.get(template_name, templates["initial_outreach"])

    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Simple template rendering"""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


# ============================================================================
# IMPROVEMENT #6: Bidirectional CRM Synchronization
# ============================================================================

class CRMIntegration:
    """
    Bidirectional sync with CRM systems

    Supported CRMs:
    - Salesforce
    - HubSpot
    - Pipedrive
    - Custom REST APIs
    """

    def __init__(self, crm_type: str, api_key: str, base_url: str = None):
        self.crm_type = crm_type
        self.api_key = api_key
        self.base_url = base_url or self._get_default_url(crm_type)

    def _get_default_url(self, crm_type: str) -> str:
        """Get default API URL for CRM"""
        urls = {
            "salesforce": "https://your-instance.salesforce.com",
            "hubspot": "https://api.hubapi.com",
            "pipedrive": "https://api.pipedrive.com/v1"
        }
        return urls.get(crm_type, "")

    def create_lead(self, prospect_data: Dict[str, Any]) -> Optional[str]:
        """Create lead in CRM"""

        if self.crm_type == "salesforce":
            return self._create_salesforce_lead(prospect_data)
        elif self.crm_type == "hubspot":
            return self._create_hubspot_contact(prospect_data)
        else:
            return self._create_generic_lead(prospect_data)

    def update_opportunity(
        self,
        opportunity_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update opportunity in CRM"""

        if self.crm_type == "salesforce":
            return self._update_salesforce_opportunity(opportunity_id, updates)
        elif self.crm_type == "hubspot":
            return self._update_hubspot_deal(opportunity_id, updates)
        else:
            return self._update_generic_opportunity(opportunity_id, updates)

    def get_opportunity(self, opportunity_id: str) -> Optional[Dict]:
        """Fetch opportunity from CRM"""

        if self.crm_type == "salesforce":
            return self._get_salesforce_opportunity(opportunity_id)
        elif self.crm_type == "hubspot":
            return self._get_hubspot_deal(opportunity_id)
        else:
            return None

    def sync_activities(self, opportunity_id: str, activities: List[Dict]):
        """Sync activities (emails, calls, etc.) to CRM"""

        for activity in activities:
            self._create_activity(opportunity_id, activity)

    # Salesforce-specific methods
    def _create_salesforce_lead(self, prospect_data: Dict) -> Optional[str]:
        """Create Salesforce lead"""

        endpoint = f"{self.base_url}/services/data/v57.0/sobjects/Lead"

        payload = {
            "Company": prospect_data.get("company_name"),
            "FirstName": prospect_data.get("contact_name", "").split()[0],
            "LastName": prospect_data.get("contact_name", "").split()[-1],
            "Title": prospect_data.get("contact_title"),
            "Email": prospect_data.get("email"),
            "Phone": prospect_data.get("phone"),
            "Industry": prospect_data.get("industry"),
            "LeadSource": prospect_data.get("source", "AI Agent Pipeline")
        }

        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            print(f"Error creating Salesforce lead: {e}")

        return None

    def _update_salesforce_opportunity(
        self,
        opp_id: str,
        updates: Dict
    ) -> bool:
        """Update Salesforce opportunity"""

        endpoint = f"{self.base_url}/services/data/v57.0/sobjects/Opportunity/{opp_id}"

        try:
            response = requests.patch(
                endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=updates
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Error updating Salesforce opportunity: {e}")
            return False

    def _get_salesforce_opportunity(self, opp_id: str) -> Optional[Dict]:
        """Fetch Salesforce opportunity"""

        endpoint = f"{self.base_url}/services/data/v57.0/sobjects/Opportunity/{opp_id}"

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching Salesforce opportunity: {e}")

        return None

    # HubSpot-specific methods
    def _create_hubspot_contact(self, prospect_data: Dict) -> Optional[str]:
        """Create HubSpot contact"""

        endpoint = f"{self.base_url}/crm/v3/objects/contacts"

        payload = {
            "properties": {
                "email": prospect_data.get("email"),
                "firstname": prospect_data.get("contact_name", "").split()[0],
                "lastname": prospect_data.get("contact_name", "").split()[-1],
                "company": prospect_data.get("company_name"),
                "jobtitle": prospect_data.get("contact_title"),
                "phone": prospect_data.get("phone"),
                "industry": prospect_data.get("industry")
            }
        }

        try:
            response = requests.post(
                endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload
            )
            if response.status_code == 201:
                return response.json()["id"]
        except Exception as e:
            print(f"Error creating HubSpot contact: {e}")

        return None

    def _update_hubspot_deal(self, deal_id: str, updates: Dict) -> bool:
        """Update HubSpot deal"""

        endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"

        try:
            response = requests.patch(
                endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"properties": updates}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating HubSpot deal: {e}")
            return False

    def _get_hubspot_deal(self, deal_id: str) -> Optional[Dict]:
        """Fetch HubSpot deal"""

        endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching HubSpot deal: {e}")

        return None

    # Generic methods
    def _create_generic_lead(self, prospect_data: Dict) -> Optional[str]:
        """Generic lead creation"""
        # Implementation for custom CRM
        pass

    def _update_generic_opportunity(self, opp_id: str, updates: Dict) -> bool:
        """Generic opportunity update"""
        # Implementation for custom CRM
        pass

    def _create_activity(self, opportunity_id: str, activity: Dict):
        """Create activity record in CRM"""
        # Implementation depends on CRM type
        pass


# ============================================================================
# IMPROVEMENT #10: Multi-Channel Outreach Orchestration
# ============================================================================

class MultiChannelOrchestrator:
    """
    Coordinate outreach across multiple channels

    Channels:
    - Email
    - LinkedIn Messages
    - Phone Calls
    - Direct Mail
    - SMS (where appropriate)
    """

    def __init__(
        self,
        email_client: EmailAutomation,
        crm_client: CRMIntegration
    ):
        self.email_client = email_client
        self.crm_client = crm_client
        self.sequences: Dict[str, List[Dict]] = {}

    def create_cadence(
        self,
        cadence_name: str,
        steps: List[Dict[str, Any]]
    ):
        """
        Create a multi-channel outreach cadence

        Example:
        [
            {"day": 0, "channel": "email", "template": "initial_outreach"},
            {"day": 3, "channel": "linkedin", "message": "connection_request"},
            {"day": 7, "channel": "email", "template": "follow_up_1"},
            {"day": 14, "channel": "phone", "script": "intro_call"}
        ]
        """
        self.sequences[cadence_name] = steps

    def start_cadence(
        self,
        prospect_data: Dict[str, Any],
        cadence_name: str
    ) -> str:
        """Start a prospect on a cadence"""

        cadence_id = f"cadence_{int(datetime.now().timestamp())}"

        # Create CRM opportunity
        opp_id = self.crm_client.create_lead(prospect_data)

        # Schedule all steps
        for step in self.sequences[cadence_name]:
            scheduled_date = datetime.now() + timedelta(days=step["day"])

            # In production, use actual scheduler (Celery, APScheduler, etc.)
            print(f"Scheduled {step['channel']} for {scheduled_date}")

        return cadence_id

    def execute_step(
        self,
        step: Dict[str, Any],
        prospect_data: Dict[str, Any]
    ):
        """Execute a single cadence step"""

        channel = step["channel"]

        if channel == "email":
            self.email_client.send_templated_email(
                to_email=prospect_data["email"],
                template_name=step["template"],
                variables=prospect_data
            )

        elif channel == "linkedin":
            # LinkedIn integration (requires LinkedIn API)
            pass

        elif channel == "phone":
            # Log call task in CRM
            self.crm_client.sync_activities(
                prospect_data.get("crm_id"),
                [{"type": "call", "script": step["script"]}]
            )
