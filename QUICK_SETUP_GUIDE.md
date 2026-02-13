# 🚀 Quick Setup & Email Configuration Guide

## ⚡ Quick Start

### Prerequisites:
- Python 3.8+
- MongoDB Atlas account
- Gmail account with App Password
- Flask & Flask-SocketIO installed

---

## 📧 Gmail Email Setup (Step-by-Step)

### Step 1: Create Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (if not already enabled)
3. Go back to Security settings
4. Find "App passwords" (appears after 2FA is enabled)
5. Select "Mail" and "Windows Computer" (or your device)
6. Google generates a **16-character password**
7. Copy this password (you'll use it in .env file)

**Example App Password:** `abc defghi jkl mno`

### Step 2: Update .env File

Create or update `.env` file in your project root:

```env
# MongoDB Connection
MONGO_URI=mongodb+srv://landvista_user:landvista123@landvista.mongodb.net/landvista?retryWrites=true&w=majority

# Flask
SECRET_KEY=your-super-secret-key-change-this

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tabbsndua2@gmail.com
MAIL_PASSWORD=abc defghi jkl mno
MAIL_DEFAULT_SENDER=noreply@landvista.com
ADMIN_EMAIL=tabbsndua2@gmail.com
```

### Step 3: Test Email Configuration

Run this Python script to test:

```python
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

try:
    with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
    print("✅ Email configuration is working!")
except Exception as e:
    print(f"❌ Email configuration failed: {e}")
```

---

## 🎯 Features You Now Have

### 1. Property Management
```python
# Admin can edit properties including email
PATCH /admin/properties/update/<id>
Fields: title, location, county, price, area, 
        description, features, contact_name, 
        contact_email ✨, contact_phone
```

### 2. News & Blogs System
```python
# Create, read, update, delete news articles
GET    /api/news           # Public: published only
GET    /api/news/admin     # Admin: all articles
POST   /admin/news/add     # Create article
POST   /admin/news/update/<id>  # Update article
DELETE /admin/news/delete/<id>  # Delete article
```

### 3. Professional Emails
When user submits inquiry:
- ✅ Confirmation email to user
- ✅ Notification email to tabbsndua2@gmail.com
- ✅ Inquiry saved to database
- ✅ Real-time update on admin dashboard

### 4. Success Notifications
```javascript
// User sees professional toast notifications
"✓ Inquiry submitted successfully! We will contact you soon."
// No more raw JSON displayed
```

---

## 🔧 Running the Application

### Option 1: Development Mode

```bash
# Terminal 1: Start Flask with SocketIO
python app.py

# App runs on: http://localhost:5000
```

### Option 2: Production Mode

```bash
# Using Gunicorn with SocketIO
gunicorn --worker-class eventlet -w 1 app:app
```

---

## 📋 Testing the Complete Flow

### Test 1: Property Email Editing
1. Go to: `http://localhost:5000/admin/properties`
2. Click on any property
3. Edit the **Contact Email** field
4. Click **Save Changes**
5. ✅ Verify email is saved in database

### Test 2: News Article Publishing
1. Go to: `http://localhost:5000/admin/news`
2. Click **+ Create New Article**
3. Fill in all fields
4. Set Status to **Published**
5. Click **Save**
6. Go to: `http://localhost:5000/news`
7. ✅ Article should appear immediately

### Test 3: Email Sending & Inquiry
1. Go to: `http://localhost:5000/properties/<any-property-id>`
2. Scroll to **"Request Information"** form
3. Fill in: Name, Email, Phone, Message, Type
4. Click **Request Information**
5. ✅ See green success notification
6. ✅ Emails should arrive in:
   - User's email inbox (confirmation)
   - tabbsndua2@gmail.com (admin notification)
7. ✅ Check Admin → Inquiries to see new inquiry

### Test 4: Real-time Dashboard
1. Have two windows open:
   - Window 1: `http://localhost:5000/admin/inquiries`
   - Window 2: `http://localhost:5000/properties/<id>`
2. Submit inquiry in Window 2
3. ✅ Inquiry appears in Window 1 instantly (no refresh!)

---

## 🐛 Troubleshooting

### Problem: Emails Not Sending

**Solution 1: Check App Password**
- Ensure you're using App Password (not regular Gmail password)
- App Password should be from Google Security settings
- Should be 16 characters with spaces

**Solution 2: Enable Less Secure App Access**
```
Go to: https://myaccount.google.com/security
Look for: "Less secure app access"
Turn it ON (if App Password doesn't work)
```

**Solution 3: Check .env File**
```bash
# Open .env and verify:
MAIL_USERNAME=tabbsndua2@gmail.com
MAIL_PASSWORD=your-app-password (no quotes)
ADMIN_EMAIL=tabbsndua2@gmail.com
```

**Solution 4: Check Server Logs**
```bash
# Look for error messages in terminal when app runs
# Check specifically for SMTP connection errors
```

### Problem: News Not Showing on Public Page

**Solution:**
1. Ensure article status is "Published" (not Draft)
2. Verify `/api/news` returns published articles
3. Check browser console for JavaScript errors
4. Clear browser cache (Ctrl+Shift+Delete)

### Problem: Inquiries Not Appearing in Dashboard

**Solution:**
1. Verify `/submit-inquiry` route is correct
2. Check MongoDB connection is working
3. Ensure Socket.IO is connected (check console)
4. Try refreshing the inquiries page

### Problem: Property Email Not Saving

**Solution:**
1. Verify form includes `contact_email` field
2. Check that update_property function saves it
3. Ensure contact_email field in edit-property.html
4. Check Flask logs for any errors

---

## 📊 Environment Variables Explained

```env
# MongoDB - Your database connection string
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/dbname

# Flask - Change this to a random string for production
SECRET_KEY=my-super-secret-key-12345

# Email Server Settings (Gmail)
MAIL_SERVER=smtp.gmail.com          # Gmail's SMTP server
MAIL_PORT=587                       # Gmail's SMTP port
MAIL_USE_TLS=true                   # Use TLS encryption

# Gmail Account
MAIL_USERNAME=tabbsndua2@gmail.com  # Your Gmail address
MAIL_PASSWORD=abc defghi jkl mno    # Your App Password (NOT regular password)

# Email Configuration
MAIL_DEFAULT_SENDER=noreply@landvista.com  # From address
ADMIN_EMAIL=tabbsndua2@gmail.com           # Where inquiry emails go
```

---

## 🎨 Email Template Examples

### Confirmation Email (to user)
```
Subject: Your Inquiry Has Been Received - LandVista

Hi [Name],

Thank you for your inquiry about [Property Title]. 
We have received your message and will get back to you shortly.

Best regards,
LandVista Team
```

### Admin Notification Email
```
Subject: New Inquiry: [Property Title]

New Inquiry Received

Name: John Doe
Email: john@example.com
Phone: +254 712 345678
Property: Prime Land in Juja Farm
Inquiry Type: Buyer

Message:
"I am very interested in this property..."
```

---

## 🔐 Security Best Practices

### 1. Protect Your App Password
- Don't commit `.env` file to Git
- Don't share App Password publicly
- Regenerate it if compromised
- Use different passwords for different apps

### 2. CORS & Origins
```python
socketio = SocketIO(app, cors_allowed_origins="*")
# In production, specify exact origins:
socketio = SocketIO(app, cors_allowed_origins=["https://yoursite.com"])
```

### 3. Rate Limiting (Recommended)
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/submit-inquiry", methods=["POST"])
@limiter.limit("5 per hour")  # Max 5 inquiries per hour per IP
def submit_inquiry():
    ...
```

### 4. Input Validation
All forms are validated on both frontend and backend:
- Required fields checked
- Email format verified
- XSS prevention with HTML escaping
- SQL injection prevention (using MongoDB)

---

## 📱 Mobile Testing

### Test on Mobile Device:

```bash
# Get your computer's IP address
# Windows: ipconfig
# Mac/Linux: ifconfig

# Run Flask on all interfaces
python app.py --host 0.0.0.0

# Access from mobile: http://<your-ip>:5000
```

---

## 📦 Dependencies

Make sure these are installed:

```bash
pip install flask
pip install flask-pymongo
pip install python-dotenv
pip install flask-socketio
pip install eventlet
pip install werkzeug
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

---

## 🚀 Deployment Checklist

Before going live:

- [ ] Email credentials configured in .env
- [ ] Gmail App Password created (not regular password)
- [ ] Database backups configured
- [ ] HTTPS/SSL certificate installed
- [ ] Domain pointing to server
- [ ] Environment variables secure
- [ ] Test all forms end-to-end
- [ ] Check email deliverability
- [ ] Monitor server logs
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure CDN for static files

---

## 💡 Pro Tips

### Tip 1: Batch Email Sending
For newsletters to many users, batch emails:
```python
for user in users:
    send_email_async(user.email, subject, body, html)
    time.sleep(1)  # 1 second delay between emails
```

### Tip 2: Email Log Tracking
Add email logging:
```python
# Log all sent emails to database
db.email_logs.insert_one({
    "recipient": email,
    "subject": subject,
    "sent_at": datetime.now(),
    "status": "sent"
})
```

### Tip 3: Email Templates
Use Jinja2 for email templates:
```python
html_body = render_template('emails/inquiry_confirmation.html', 
                            name=name, 
                            property=property_title)
```

### Tip 4: Testing Emails Locally
Use Mailtrap or similar for testing without sending real emails:
```
https://mailtrap.io/
```

---

## 📞 Support Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Flask-SocketIO: https://flask-socketio.readthedocs.io/
- MongoDB: https://docs.mongodb.com/
- Gmail SMTP: https://support.google.com/mail/answer/7126229

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Can admin edit property email
- [ ] Can admin create news article  
- [ ] Can admin publish article (appears on public site)
- [ ] Can user fill property inquiry form
- [ ] User sees success notification
- [ ] User receives confirmation email
- [ ] Admin receives notification email
- [ ] Inquiry appears on admin dashboard
- [ ] News article appears in real-time
- [ ] All forms have validation
- [ ] No raw JSON shown to users
- [ ] Mobile forms work properly

---

**Status:** ✅ COMPLETE & READY TO DEPLOY
**Last Updated:** December 28, 2025
