#!/usr/bin/env python3
"""
Simple Email Configuration Test
Tests Gmail SMTP connection and sends test email
"""

import os
import sys
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import socket

load_dotenv()

# Get email configuration
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')

print("=" * 70)
print("📧 LANDVISTA EMAIL CONFIGURATION TEST (SIMPLE)")
print("=" * 70)
print()

# Step 1: Check configuration
print("✓ Step 1: Checking email configuration...")
print(f"  - MAIL_SERVER: {MAIL_SERVER}")
print(f"  - MAIL_PORT: {MAIL_PORT}")
print(f"  - MAIL_USE_TLS: {MAIL_USE_TLS}")
print(f"  - MAIL_USERNAME: {MAIL_USERNAME}")
print(f"  - MAIL_PASSWORD: {'*' * (len(MAIL_PASSWORD)-3) + MAIL_PASSWORD[-3:]}")
print(f"  - ADMIN_EMAIL: {ADMIN_EMAIL}")
print()

# Validate configuration
if not MAIL_USERNAME:
    print("❌ ERROR: MAIL_USERNAME not set in .env file")
    sys.exit(1)

if not MAIL_PASSWORD:
    print("❌ ERROR: MAIL_PASSWORD not set in .env file")
    sys.exit(1)

if "your-app-password" in MAIL_PASSWORD.lower():
    print("❌ ERROR: MAIL_PASSWORD still contains placeholder text")
    sys.exit(1)

print("✓ Configuration looks good!")
print()

# Step 2: Test network connectivity
print("✓ Step 2: Testing network connectivity...")
try:
    # Try to resolve the hostname
    ip = socket.gethostbyname(MAIL_SERVER)
    print(f"  - Resolved {MAIL_SERVER} to {ip}")
    
    # Try to connect to the port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((MAIL_SERVER, MAIL_PORT))
    sock.close()
    
    if result == 0:
        print(f"  - Successfully connected to {MAIL_SERVER}:{MAIL_PORT}")
    else:
        print(f"  ⚠️  Could not connect to {MAIL_SERVER}:{MAIL_PORT}")
        print(f"     Error code: {result}")
        print(f"     This might be a firewall or network issue")
        
except socket.gaierror:
    print(f"❌ ERROR: Could not resolve {MAIL_SERVER}")
    print(f"   Check your internet connection")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Network test failed: {e}")

print()

# Step 3: Test SMTP connection
print("✓ Step 3: Testing SMTP connection and authentication...")
try:
    # Create server connection with longer timeout
    print(f"  - Connecting to {MAIL_SERVER}:{MAIL_PORT}...")
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    print(f"  - Connected successfully")
    
    # Start TLS
    if MAIL_USE_TLS:
        print(f"  - Starting TLS encryption...")
        server.starttls()
        print(f"  - TLS started successfully")
    
    # Try to login
    print(f"  - Authenticating as {MAIL_USERNAME}...")
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print(f"  - Authentication successful!")
    
    server.quit()
    print()
    print("✓ SMTP connection successful!")
    print()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ ERROR: Authentication failed!")
    print(f"   Details: {e}")
    print()
    print("   Possible solutions:")
    print("   1. Check if MAIL_PASSWORD is correct")
    print("   2. Make sure 2-Step Verification is enabled")
    print("   3. Make sure you're using App Password, not regular password")
    print("   4. Check that MAIL_USERNAME is tabbsndua2@gmail.com")
    sys.exit(1)
    
except smtplib.SMTPException as e:
    print(f"❌ ERROR: SMTP Error - {e}")
    sys.exit(1)
    
except socket.timeout:
    print(f"❌ ERROR: Connection timeout")
    print(f"   Could not connect to {MAIL_SERVER}:{MAIL_PORT}")
    print(f"   This might be a firewall or network issue")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ ERROR: Connection failed - {e}")
    sys.exit(1)

# Step 4: Send test email
print("✓ Step 4: Sending test email...")
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
    print(f"  - Connecting to send email...")
    server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
    if MAIL_USE_TLS:
        server.starttls()
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    
    print(f"  - Sending email to {ADMIN_EMAIL}...")
    server.send_message(msg)
    server.quit()
    
    print(f"✓ Test email sent successfully!")
    print()
    
except Exception as e:
    print(f"❌ ERROR: Failed to send email - {e}")
    sys.exit(1)

# Final result
print("=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print()
print("Email configuration is ready to use:")
print(f"  - From: {MAIL_USERNAME}")
print(f"  - To: {ADMIN_EMAIL}")
print()
print(f"📧 Check your inbox at {ADMIN_EMAIL} for the test email.")
print()
print("Your Landvista website is ready to send emails! ✨")
print()
