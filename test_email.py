#!/usr/bin/env python3
"""
Email Configuration Test Script
Verifies that Gmail SMTP is properly configured and working
"""

import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

load_dotenv()

# Get email configuration
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')

print("=" * 60)
print("📧 LANDVISTA EMAIL CONFIGURATION TEST")
print("=" * 60)
print()

# Step 1: Check configuration
print("✓ Step 1: Checking email configuration...")
print(f"  - MAIL_SERVER: {MAIL_SERVER}")
print(f"  - MAIL_PORT: {MAIL_PORT}")
print(f"  - MAIL_USE_TLS: {MAIL_USE_TLS}")
print(f"  - MAIL_USERNAME: {MAIL_USERNAME}")
print(f"  - ADMIN_EMAIL: {ADMIN_EMAIL}")
print()

# Validate configuration
if not MAIL_USERNAME:
    print("❌ ERROR: MAIL_USERNAME not set in .env file")
    exit(1)

if not MAIL_PASSWORD:
    print("❌ ERROR: MAIL_PASSWORD not set in .env file")
    print("   Please add your Gmail App Password to .env")
    print()
    print("   Steps to create Gmail App Password:")
    print("   1. Go to https://myaccount.google.com/")
    print("   2. Select 'Security' from left menu")
    print("   3. Enable 2-Step Verification (if not enabled)")
    print("   4. Go to 'App passwords'")
    print("   5. Select 'Mail' and 'Windows Computer'")
    print("   6. Copy the 16-character password")
    print("   7. Paste into MAIL_PASSWORD in .env file")
    exit(1)

if "your-app-password" in MAIL_PASSWORD.lower():
    print("❌ ERROR: MAIL_PASSWORD still contains placeholder text")
    print("   Please replace 'your-app-password-here' with actual password")
    exit(1)

print("✓ Configuration looks good!")
print()

# Step 2: Test SMTP connection
print("✓ Step 2: Testing SMTP connection...")
try:
    # Create server connection
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    server.starttls() if MAIL_USE_TLS else None
    
    print(f"  - Connected to {MAIL_SERVER}:{MAIL_PORT}")
    
    # Try to login
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print(f"  - Authentication successful for {MAIL_USERNAME}")
    
    server.quit()
    print("✓ SMTP connection successful!")
    print()
    
except smtplib.SMTPAuthenticationError:
    print("❌ ERROR: Authentication failed!")
    print("   - Check if MAIL_USERNAME is correct")
    print("   - Check if MAIL_PASSWORD is correct (use App Password, not regular password)")
    print("   - Make sure 2-Step Verification is enabled on Gmail account")
    exit(1)
    
except smtplib.SMTPException as e:
    print(f"❌ ERROR: SMTP Error - {e}")
    exit(1)
    
except Exception as e:
    print(f"❌ ERROR: Connection failed - {e}")
    exit(1)

# Step 3: Send test email
print("✓ Step 3: Sending test email...")
try:
    # Create email
    msg = MIMEMultipart('alternative')
    msg['From'] = MAIL_USERNAME
    msg['To'] = ADMIN_EMAIL
    msg['Subject'] = f'Landvista Email Test - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    
    # HTML body
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">🎉 Landvista Email Configuration Test</h2>
            
            <p>Hello Admin,</p>
            
            <p>This is a test email to verify that the email configuration is working correctly.</p>
            
            <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>✓ Test Details</h3>
                <ul>
                    <li><strong>Sender:</strong> {MAIL_USERNAME}</li>
                    <li><strong>Recipient:</strong> {ADMIN_EMAIL}</li>
                    <li><strong>Server:</strong> {MAIL_SERVER}:{MAIL_PORT}</li>
                    <li><strong>Test Time:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
                </ul>
            </div>
            
            <p>If you're reading this email, your email configuration is <strong>working correctly!</strong></p>
            
            <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                This is an automated test email from Landvista. Please do not reply to this email.
            </p>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Send email
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
    server.starttls() if MAIL_USE_TLS else None
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print(f"✓ Test email sent to {ADMIN_EMAIL}")
    print()
    
except Exception as e:
    print(f"❌ ERROR: Failed to send email - {e}")
    exit(1)

# Final result
print("=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print()
print("Email configuration is ready to use:")
print(f"  - From: {MAIL_USERNAME}")
print(f"  - To: {ADMIN_EMAIL}")
print()
print("📧 Check your inbox at {ADMIN_EMAIL} for the test email.")
print()
print("Your Landvista website is ready to send emails!")
print()
