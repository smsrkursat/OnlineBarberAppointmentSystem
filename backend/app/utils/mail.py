from flask_mail import Message
from flask import current_app
from app.extensions import mail

def send_verification_email(to_email, verify_url):
    subject = "Email Doğrulama"

    html_body = f"""
    <p>Merhaba,</p>
    <p>Email adresinizi doğrulamak için aşağıdaki bağlantıya tıklayın:</p>
    <p><a href="{verify_url}">{verify_url}</a></p>
    <p>Teşekkürler!</p>
    """

    sender = current_app.config.get("MAIL_DEFAULT_SENDER")

    msg = Message(
        subject=subject,
        recipients=[to_email],
        html=html_body,
        sender=sender
    )

    mail.send(msg)