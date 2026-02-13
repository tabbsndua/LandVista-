# LandVista Admin Login Guide

## Quick Start

### Accessing the Admin Dashboard

1. **Go to:** `http://yoursite.com/admin`
2. **You'll see:** Login page with username and password fields
3. **Enter credentials:**
   - Username: `admin`
   - Password: `landvista2025` (or your custom password from `.env`)
4. **Click:** "Login to Admin Dashboard"
5. **You're in!** Full access to manage everything

---

## Admin Dashboard Overview

### Sidebar Menu

Once logged in, you'll see the admin sidebar with:

| Menu Item | What You Can Do |
|-----------|-----------------|
| 🎛️ Dashboard | View real-time statistics and overview |
| 🏢 Properties | Add, edit, delete properties with images/videos |
| 👥 Clients | Manage client information and details |
| 💬 Testimonials | Add and manage client testimonials |
| 📰 News & Blogs | Create and manage news articles |
| 📚 Legal Guides | Create and manage legal guides |
| 📧 Inquiries | View and respond to client inquiries |
| ← Back to Website | Return to public site |
| 🚪 Logout | Sign out and return to login |

---

## Key Features

### 1. Dashboard
- View total properties count
- View total clients count
- View recent inquiries
- View latest testimonials
- Real-time updates

### 2. Properties Management
**Add Property:**
- Title, description, location
- Price (in KSh)
- Upload image or video
- Property details

**Edit Property:**
- Change any field
- Update media

**Delete Property:**
- Remove from system

### 3. Inquiries Management
**View Inquiries:**
- See all client inquiries
- View customer details and message

**Response Options:**
- Mark as responded/pending
- Send custom email response
- Delete inquiry

**Real-time Notifications:**
- See new inquiries instantly
- Socket.IO live updates

### 4. Clients Management
**Add Client:**
- Client name
- Email address
- Phone number
- Property interests

**Edit Client:**
- Update any information

**View Client:**
- See client full details

**Delete Client:**
- Remove client record

### 5. News & Blogs
**Create Article:**
- Title
- Content/Description
- Featured image upload
- Publish immediately

**Edit Article:**
- Update content
- Change featured image

**Delete Article:**
- Remove from public site

### 6. Testimonials
**Add Testimonial:**
- Client name
- Message/review
- Rating (stars)
- Upload client photo (optional)

**Edit Testimonial:**
- Update any field

**Delete Testimonial:**
- Remove from display

### 7. Legal Guides
**Create Guide:**
- Title
- Content/Description
- Category
- Featured image

**Edit Guide:**
- Update content
- Change category

**Delete Guide:**
- Remove from library

---

## Common Tasks

### I received an inquiry - how do I respond?

1. Go to **Inquiries** in sidebar
2. Find the inquiry in the list
3. Click on it to view details
4. Click **"Send Email"**
5. Write your response
6. Click **"Send"**
7. The client gets your email automatically

### I want to add a new property

1. Go to **Properties** in sidebar
2. Click **"Add New Property"**
3. Fill in all details:
   - Title
   - Description
   - Location
   - Price
   - Features
4. Upload property image/video
5. Click **"Add Property"**
6. Property appears on public site immediately

### I want to add a testimonial from a client

1. Go to **Testimonials** in sidebar
2. Click **"Add New Testimonial"**
3. Enter:
   - Client name
   - Their message/review
   - Rating (1-5 stars)
   - Client photo (optional)
4. Click **"Add Testimonial"**
5. Shows on homepage for visitors

### I want to write a news article

1. Go to **News & Blogs** in sidebar
2. Click **"Add New Article"**
3. Enter:
   - Title
   - Content
   - Featured image
4. Click **"Publish"**
5. Article appears in News section

### I want to create a legal guide

1. Go to **Legal Guides** in sidebar
2. Click **"Add New Guide"**
3. Enter:
   - Title
   - Content/Description
   - Category
   - Featured image
4. Click **"Create Guide"**
5. Guide available in Legal Guides section

---

## Logging Out

Simply click the **"Logout"** button at the bottom of the sidebar.

This:
- Ends your session
- Takes you back to login page
- You'll need to login again to access admin

---

## Password Change

To change your admin password:

1. Contact your system administrator
2. Have them update `.env` file:
   ```env
   ADMIN_PASSWORD=your-new-password
   ```
3. Restart the Flask application

---

## Important Notes

### Public vs Admin

**Public visitors (no login needed):**
- Browse properties
- Read news
- View legal guides
- Send inquiries/contact forms
- View testimonials

**Admin only (login required):**
- Everything on dashboard
- Add/edit/delete properties
- Manage inquiries
- Manage testimonials
- Manage news & guides
- View client information

### Real-time Updates

When multiple admins are logged in:
- Property changes update for everyone
- New inquiries notify all admins
- Changes to testimonials/news sync immediately

### File Uploads

When uploading images/videos:
- Images: JPG, PNG, JPEG
- Videos: MP4, WebM, MOV
- Max size: Recommended under 10MB
- Will resize automatically for display

### Email Configuration

- Inquiries are sent to: `ADMIN_EMAIL` in `.env`
- Make sure Gmail account is verified
- Check spam folder if emails missing
- Use Gmail App Password (not regular password)

---

## Troubleshooting

### "Invalid username or password"
- Check `.env` file for correct credentials
- Verify ADMIN_USERNAME and ADMIN_PASSWORD
- Make sure you're entering them exactly (case-sensitive)

### "Cannot add property - upload failed"
- Check file size (under 10MB)
- Ensure `static/uploads/` directory exists
- Verify it has write permissions

### "Email not sending"
- Verify Gmail credentials in `.env`
- Check MAIL_USERNAME and MAIL_PASSWORD
- Check internet connection
- Try again after 30 seconds

### "Real-time updates not working"
- Refresh the page
- Check internet connection
- Try different browser
- Check browser console for errors

### "Changes not appearing on public site"
- Hard refresh the public page (Ctrl+F5)
- Wait 30 seconds for cache to clear
- Check if property/content was actually saved

---

## Security Tips

✓ **Good Practices:**
- Never share your admin password
- Logout when done using admin
- Use strong passwords
- Keep `.env` file secret

✗ **Avoid:**
- Sharing login credentials
- Leaving admin page open
- Using simple passwords like "123456"
- Committing `.env` to git

---

## Contact & Support

For technical support or issues:
- Check the documentation files
- Review the app logs
- Contact system administrator

---

**LandVista Properties Limited**  
Admin Dashboard User Guide v1.0
