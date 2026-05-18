from flask_mail import Mail, Message
import requests
from datetime import datetime

class NotificationService:
    def __init__(self, app=None, webhook_url=None):
        self.app = app
        self.webhook_url = webhook_url
        self.mail = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize email configuration"""
        app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = 'your_email@gmail.com'      # CHANGE
        app.config['MAIL_PASSWORD'] = 'your_app_password'         # CHANGE
        app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'
        self.mail = Mail(app)

    # ===================== PUBLIC ENTRY POINT =====================

    def send_threat_alert(self, threat_data, recipient=None):
        """
        Unified alert sender:
        - Email (if recipient + mail configured)
        - Webhook (if webhook_url configured)
        """
        email_sent = False
        webhook_sent = False

        if recipient and self.mail:
            email_sent = self._send_email(threat_data, recipient)

        if self.webhook_url:
            webhook_sent = self._send_webhook(threat_data)

        return email_sent or webhook_sent

    # ===================== EMAIL =====================

    def _send_email(self, threat_data, recipient):
        """Send threat alert email"""
        try:
            msg = Message(
                subject=f"🚨 Cybersecurity Alert: {threat_data['risk_level'].upper()} Risk Detected",
                recipients=[recipient]
            )

            msg.html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #ef4444;">Security Threat Detected</h2>
                    <p><strong>Time:</strong> {threat_data.get('timestamp')}</p>
                    <p><strong>Source IP:</strong> {threat_data.get('source_ip')}</p>
                    <p><strong>Risk Level:</strong> {threat_data.get('risk_level')}</p>
                    <p><strong>Attack Type:</strong> {threat_data.get('attack_type', 'Unknown')}</p>
                    <p><strong>Actions Taken:</strong> {', '.join(threat_data.get('actions', []))}</p>
                    <hr>
                    <p style="color: #64748b;">
                        This is an automated alert from the Autonomous Cybersecurity AI System.
                    </p>
                </body>
            </html>
            """

            self.mail.send(msg)
            return True

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    # ===================== WEBHOOK (SLACK / DISCORD) =====================

    def _send_webhook(self, threat_data):
        """Send alert via Slack / Discord webhook"""
        payload = {
            "text": "🚨 *Security Alert*",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {
                        "title": "Source IP",
                        "value": threat_data.get('source_ip', 'Unknown'),
                        "short": True
                    },
                    {
                        "title": "Risk Level",
                        "value": threat_data.get('risk_level', 'unknown').upper(),
                        "short": True
                    },
                    {
                        "title": "Attack Type",
                        "value": threat_data.get('attack_type', 'Unknown'),
                        "short": True
                    },
                    {
                        "title": "Actions",
                        "value": ', '.join(threat_data.get('actions', [])),
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": threat_data.get(
                            'timestamp',
                            datetime.now().isoformat()
                        ),
                        "short": False
                    }
                ]
            }]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            return response.status_code in (200, 204)
        except Exception as e:
            print(f"❌ Webhook failed: {e}")
            return False
