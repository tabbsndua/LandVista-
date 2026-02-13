# Site Visit Booking Email & Success Message Guide

## Current Implementation

When a user books a site visit from the **Contact page** (clicking "Schedule Now" button), the following happens:

### 1. **User Flow**
- User clicks "Schedule Now" button on Contact page
- Modal form opens (`#bookingModal`)
- User fills out: Name, Email, Phone, Date, Time, Message (optional)
- Form submits to `/submit-site-visit` endpoint

### 2. **Backend Processing** 
- **File:** [app.py](app.py#L573-L632)
- **Route:** `POST /submit-site-visit`
- **Steps:**
  1. Extracts form data: `name`, `email`, `phone`, `visit_date`, `property_title`, `notes`
  2. Creates visit document in MongoDB (`site_visits` collection)
  3. **Sends confirmation email** to customer via `send_site_visit_confirmation_email()`
  4. **Sends admin notification email** to admin via `send_site_visit_notification_to_admin()`
  5. Returns JSON response: `{"success": true, "visit_id": "...", "message": "Scheduled successfully"}`

### 3. **Email Sending Functions**
Location: [app.py](app.py#L275-L332)

#### **A. Customer Confirmation Email**
- **Function:** `send_site_visit_confirmation_email()` (lines 275-290)
- **Sends to:** Customer's email address
- **Subject:** "Your Site Visit is Scheduled - LandVista"
- **Contains:** Visit date, property title, invitation to meet

#### **B. Admin Notification Email**
- **Function:** `send_site_visit_notification_to_admin()` (lines 301-332)
- **Sends to:** 
  - Primary: `ADMIN_EMAIL` from `.env` (tabbsndua2@gmail.com)
  - Secondary: Additional monitoring email (tabbsndua2@gmail.com)
- **Subject:** "New Site Visit: [Property Name]"
- **Contains:** Customer name, email, phone, property, visit date, notes

### 4. **Email Configuration**
Location: [.env](../.env) file

```env
# SMTP Server Settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true

# Gmail Credentials
MAIL_USERNAME=tabbsndua2@gmail.com
MAIL_PASSWORD=idislsfjfpzuzypw  # Gmail App Password

# Admin Email Settings
ADMIN_EMAIL=tabbsndua2@gmail.com
MAIL_DEFAULT_SENDER=noreply@landvista.com
```

### 5. **Frontend Success Message**
Location: [contact.html](templates/contact.html#L292-L320)

- **Shows green toast notification** when booking succeeds
- **Message:** "✓ Scheduled successfully. Check your email for confirmation."
- **Auto-dismisses** after 4 seconds
- **Modal closes** and form resets

---

## How to Verify It's Working

1. **Test Site Visit Booking:**
   - Go to `/contact` page
   - Click "Schedule Now" button
   - Fill form and submit
   - Check for:
     - Green success message on page
     - Customer confirmation email in inbox
     - Admin notification email at tabbsndua2@gmail.com

2. **Check Email Configuration:**
   ```bash
   # From workspace root, run:
   python test_email_simple.py
   ```
   This verifies SMTP credentials are correct.

3. **Monitor Email Logs:**
   - Check terminal for `Email sent successfully` messages
   - Any errors will print `Error sending email: ...`

---

## Key Files & Line References

| Component | File | Lines | Description |
|-----------|------|-------|-------------|
| Site Visit Route | `app.py` | 573-632 | POST handler for booking |
| Customer Email Function | `app.py` | 275-290 | Sends confirmation |
| Admin Email Function | `app.py` | 301-332 | Sends admin notification |
| Email Utility (Async) | `app.py` | 140-173 | Background thread sender |
| Email Config | `app.py` | 40-47 | SMTP settings from .env |
| Environment Variables | `.env` | - | Gmail credentials |
| Frontend Form | `contact.html` | 228-320 | Modal & submission |
| Frontend Success Logic | `contact.html` | 292-320 | Shows toast, closes modal |

---

## Database Schema

**Collection:** `site_visits`

```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+254784666927",
  "property_id": "",
  "property_title": "Contact Page Booking",
  "visit_date": "2026-02-19 14:00",
  "notes": "Interested in agricultural land",
  "status": "scheduled",
  "created_at": "2026-02-12T10:30:45.123Z"
}
```

---

## Testing the Email

Run this to test email setup:
```bash
cd c:\Users\User\Desktop\Landvista
.venv\Scripts\python test_email_simple.py
```

Expected output:
```
✅ Email conditions OK
📧 Sending test email...
✅ Email sent successfully!
```

---

## What Happens When User Books Visit

```
1. User clicks "Schedule Now" → Modal opens
2. User fills form & clicks "Schedule Visit"
   ↓
3. POST /submit-site-visit receives form data
   ↓
4. Data saved to MongoDB (site_visits)
   ↓
5. Two emails sent (async threads):
   a) Customer: "Your Site Visit is Scheduled"
   b) Admin: "New Site Visit: [Property]"
   ↓
6. Response sent back: {"success": true, "message": "Scheduled successfully"}
   ↓
7. Frontend shows green toast: "✓ Scheduled successfully. Check email..."
   ↓
8. Modal closes, form resets
```

---

## If Emails Don't Send

**Check in this order:**

1. **MongoDB running & connected?**
   - Look for "Connected to MongoDB successfully" in startup logs
   - If not, check `MONGO_URI` in `.env`

2. **Email credentials configured?**
   - Check `test_email_simple.py` output
   - Verify `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`
   - Gmail password must be **App Password**, not regular password

3. **Python environment active?**
   ```bash
   .venv\Scripts\activate
   ```

4. **Required packages installed?**
   ```bash
   pip install -r requirements.txt
   ```

5. **Check app.py logs:**
   - "Email sent successfully" = working
   - "Error sending email:" = check credentials

---

## Summary

✅ **Success Message:** Green toast shows immediately on contact page  
✅ **Customer Email:** Sent to visitor's email automatically  
✅ **Admin Email:** Sent to tabbsndua2@gmail.com automatically  
✅ **Database:** Visit recorded in MongoDB for dashboard tracking  
✅ **Configuration:** All settings in [.env](.env)

The system is **already fully implemented**. The code automatically:
- Sends confirmation to customer
- Sends notification to admin
- Shows success message on page
- Stores visit record in database

No additional code changes needed—just ensure `.env` credentials are correct!
