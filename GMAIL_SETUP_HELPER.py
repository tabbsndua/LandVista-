#!/usr/bin/env python3
"""
Interactive Gmail App Password Setup Helper
Guides you through getting the correct password
"""

print("=" * 70)
print("🔐 GMAIL APP PASSWORD SETUP HELPER")
print("=" * 70)
print()

print("❌ Current Status: Gmail rejected your password")
print()

print("This usually means one of these:")
print()
print("1. ❌ Using regular Gmail password instead of App Password")
print("2. ❌ 2-Step Verification not enabled")
print("3. ❌ Less Secure Apps access not enabled")
print()

print("-" * 70)
print()

print("📋 QUICK CHECKLIST:")
print()

print("Option A: Generate Gmail App Password (RECOMMENDED)")
print("=" * 70)
print()
print("Steps:")
print("1. Go to https://myaccount.google.com/")
print("2. Click 'Security' on the left")
print("3. Enable 2-Step Verification (if not enabled)")
print("4. Scroll to 'App passwords'")
print("5. Select Mail + Windows Computer")
print("6. Click Generate")
print("7. Copy the 16-character password")
print("8. Update .env file: MAIL_PASSWORD=<paste-here>")
print("9. Run: python test_email_simple.py")
print()

print("-" * 70)
print()

print("Option B: Enable Less Secure Apps")
print("=" * 70)
print()
print("If you want to use your regular Gmail password:")
print()
print("1. Go to https://myaccount.google.com/u/0/security")
print("2. Find 'Less secure app access'")
print("3. Turn it ON")
print("4. Keep your current password in .env")
print("5. Run: python test_email_simple.py")
print()

print("-" * 70)
print()

print("🚨 IMPORTANT:")
print()
print("• Gmail App Password = 16 characters (like: a1b2 c3d4 e5f6 g7h8)")
print("• Regular password = Your Gmail login (won't work for apps)")
print("• Always use App Password unless Less Secure Apps is enabled")
print()

print("=" * 70)
print()
print("Ready? Follow one of the options above, then run:")
print("  python test_email_simple.py")
print()
