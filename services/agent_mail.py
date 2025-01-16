from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from domain.models import PressMentionSignal, Action
from agents import PressMentionAgent


def agent_mail(
    signals: list[PressMentionSignal],
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipient_email: str,
):
    """

    parm：
    - signals: treat PressMentionSignal list
    - smtp_server: SMTP
    - smtp_port: SMTP
    - sender_email:
    - sender_password:
    - recipient_email:
    """
    agent = PressMentionAgent()
    actions = agent.process_signals(signals)

    # set SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    for action in actions:
        # create message object
        subject = f"New Press Mention: {action.title}"
        body = f"""
        Hi,

        Here's an important press mention that might interest you:

        Title: {action.title}
        Description: {action.description}
        URL: {action.url if action.url else 'No URL provided'}
        Priority Score: {action.score}

        Best regards,
        Your Assistant
        """

        # make message object
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # send message via server
        server.send_message(message)
        print(f"Email sent for action: {action.title}")

    server.quit()
