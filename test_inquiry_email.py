#!/usr/bin/env python3
"""
Test sending an inquiry email directly
"""

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@landvista.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')

print("=" * 70)
print("📧 TEST INQUIRY EMAIL")
print("=" * 70)
print()

print("Configuration:")
print(f"  From: {MAIL_DEFAULT_SENDER}")
print(f"  To: {ADMIN_EMAIL}")
print(f"  SMTP: {MAIL_SERVER}:{MAIL_PORT}")
print()

# Create inquiry data
inquiry_data = {
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+254712345678",
    "property_title": "Test Property",
    "inquiry_type": "buyer",
    "message": "This is a test inquiry email to verify the system is working."
}

# Create email
msg = MIMEMultipart('alternative')
msg['Subject'] = f"New Inquiry: {inquiry_data['property_title']}"
msg['From'] = MAIL_DEFAULT_SENDER
msg['To'] = ADMIN_EMAIL

# Plain text
body = f"""
New Inquiry Received:

Name: {inquiry_data['name']}
Email: {inquiry_data['email']}
Phone: {inquiry_data['phone']}
Property: {inquiry_data['property_title']}
Type: {inquiry_data['inquiry_type']}

Message:
{inquiry_data['message']}
"""

# HTML
html_body = f"""
<html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0a3c28; border-bottom: 3px solid #10b981; padding-bottom: 10px;">New Inquiry Received</h2>
            <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Name:</strong> {inquiry_data['name']}</p>
                <p><strong>Email:</strong> {inquiry_data['email']}</p>
                <p><strong>Phone:</strong> {inquiry_data['phone']}</p>
                <p><strong>Property:</strong> {inquiry_data['property_title']}</p>
                <p><strong>Type:</strong> {inquiry_data['inquiry_type']}</p>
            </div>
            <h3>Message:</h3>
            <p style="white-space: pre-wrap; background: #f0f5f3; padding: 15px; border-radius: 8px;">{inquiry_data['message']}</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
            <p style="color: #6b7280; font-size: 12px;">LandVista Admin Notification</p>
        </div>
    </body>
</html>
"""

msg.attach(MIMEText(body, 'plain'))
msg.attach(MIMEText(html_body, 'html'))

# Send
print("Sending test inquiry email...")
try:
    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
        if MAIL_USE_TLS:
            server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
    
    print("✅ Email sent successfully!")
    print()
    print(f"Subject: {msg['Subject']}")
    print(f"From: {msg['From']}")
    print(f"To: {msg['To']}")
    print()
    print(f"Check your inbox at {ADMIN_EMAIL} for the test inquiry email.")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
