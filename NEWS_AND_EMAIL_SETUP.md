# LandVista - Admin News & Blogs + Email Setup Guide

## 🎉 What's New

### 1. **Admin News & Blogs Management**
Complete redesign of the news administration dashboard with:
- **Beautiful Card-Based Grid Layout** - Articles displayed as professional cards with images
- **View Functionality** - Read full articles in a modal without leaving the admin panel
- **Full CRUD Operations** - Create, read, update, and delete articles
- **Search & Filtering** - Filter by title, category, and publication status
- **Featured Articles** - Mark articles as featured for homepage prominence
- **Rich Text Support** - Store complete article content with formatting
- **Featured Images** - Upload and display article thumbnail images
- **Status Management** - Draft and Published states

### 2. **Email Functionality**
Automated email system with real-time notifications:
- **Inquiry Confirmations** - Automatic confirmation emails sent to customers
- **Admin Notifications** - Admin receives detailed notification about new inquiries
- **Admin Email Console** - Send custom emails to users/customers from admin dashboard
- **Background Processing** - Non-blocking asynchronous email sending
- **HTML Email Templates** - Professional, branded email layouts
- **Real-time Socket Events** - Email sending events broadcast in real-time

## 📋 Database Schema

### News Collection
```javascript
{
  "_id": ObjectId,
  "title": String,
  "slug": String,
  "author": String,
  "category": String,
  "date": String,
  "readTime": Number,
  "excerpt": String,
  "content": String,
  "featured_image": String,
  "status": String, // "draft" or "published"
  "featured": Boolean,
  "created_at": DateTime,
  "updated_at": DateTime
}
```

## 🔧 Configuration

### Step 1: Configure Email Credentials

Create or update your `.env` file with email settings:

```env
# Email Configuration (Required for email features to work)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@landvista.com
ADMIN_EMAIL=admin@landvista.com
```

### Step 2: Using Gmail

If using Gmail:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use the App Password (not your Gmail password) for `MAIL_PASSWORD`
4. Keep `MAIL_SERVER=smtp.gmail.com` and `MAIL_PORT=587`

### Step 3: Alternative Email Providers

For other providers, adjust:
- **Outlook/Hotmail**: `smtp-mail.outlook.com:587`
- **SendGrid**: `smtp.sendgrid.net:587`
- **AWS SES**: `email-smtp.[region].amazonaws.com:587`

## 📚 API Endpoints

### News Management
- `GET /api/news` - Get all published articles
- `POST /admin/news/add` - Create new article (requires form data with files)
- `POST /admin/news/update/<id>` - Update article
- `DELETE /admin/news/delete/<id>` - Delete article

### Email Sending
- `POST /admin/send-email` - Send custom email from admin panel

```javascript
// Example: Send custom email
fetch('/admin/send-email', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    recipient: 'user@example.com',
    subject: 'Important Update',
    message: 'Your message here'
  })
})
```

## 🎨 UI/UX Features

### News Admin Page
- **Responsive Grid Layout** - Adapts to 1-4 columns based on screen size
- **Card Hover Effects** - Smooth animations and elevation on hover
- **Status Badges** - Color-coded status indicators (Green for Published, Yellow for Draft)
- **Category Tags** - Visual category badges on each card
- **Image Previews** - Featured image thumbnails in the grid
- **Action Buttons** - View, Edit, Delete buttons on each card
- **Search Bar** - Real-time article search
- **Category Filter** - Filter by article category
- **Status Filter** - Show all, published, or draft articles

### View Modal
- **Full Article Display** - Complete article content in a modal
- **Article Metadata** - Author, date, read time, and category visible
- **Professional Styling** - Clean, readable typography

### Edit Modal
- **All Fields Editable** - Title, slug, author, category, date, content, excerpt
- **Featured Image Upload** - Replace or update article images
- **Status Toggle** - Quick publish/draft switching
- **Featured Toggle** - Mark as featured article
- **Validation** - Required field validation

## 📧 Email Features

### Automatic Inquiry Emails
When a user submits an inquiry on the property details page:
1. **Customer receives**: Confirmation email thanking them for their inquiry
2. **Admin receives**: Detailed notification with customer details and message

### Admin Email Console
Send custom emails to customers from the admin dashboard:
- Professional HTML templates
- Automatic styling and formatting
- Real-time delivery status
- Asynchronous processing (doesn't block admin interface)

## 🔄 Real-time Features

Socket.IO integration provides:
- Real-time email sending notifications
- Live inquiry updates
- Instant article publish/unpublish effects
- Real-time dashboard synchronization

## 🚀 Performance Optimizations

- **Asynchronous Email Sending** - Emails sent in background threads
- **Image Optimization** - Automatic filename timestamping
- **Database Indexing** - Efficient queries for large datasets
- **Grid Rendering** - Responsive grid with CSS Grid for better performance
- **Modal-based Editing** - Faster UX compared to page reloads

## 📱 Responsive Design

The news admin page is fully responsive:
- **Desktop**: 3-column grid
- **Tablet**: 2-column grid
- **Mobile**: 1-column grid (100% width)

## 🔒 Security

- **SMTP TLS Encryption** - All emails sent securely
- **Input Validation** - All form inputs validated
- **Secure Filename Handling** - Werkzeug secure_filename for uploads
- **CORS Enabled** - Socket.IO CORS allowed origins configured

## 📝 File Changes Summary

### New Files
- `.env.example` - Email configuration template

### Modified Files
- `app.py` - Added news routes, email functions, admin endpoint
- `requirements.txt` - No new dependencies (using built-in smtplib)
- `templates/admin/news.html` - Redesigned with grid layout and view modal
- `static/css/admin/news.css` - Complete style overhaul

### Backend Routes Added
- `/api/news` - Public news API
- `/admin/news/add` - Create article
- `/admin/news/update/<id>` - Update article
- `/admin/news/delete/<id>` - Delete article
- `/admin/send-email` - Send custom email

## 🧪 Testing

1. **Navigate to Admin Dashboard**: `/admin`
2. **Click "News & Blogs"** in sidebar
3. **Create Article**: Click "+ Create New Article"
4. **Upload Featured Image**: Select an image file
5. **Fill in Details**: Title, content, category, etc.
6. **Save**: Click "Save Article"
7. **View**: Click "View" button on any article card
8. **Edit**: Click "Edit" to modify article
9. **Delete**: Click "Delete" to remove article

## ⚙️ Troubleshooting

### Emails Not Sending
1. Check `.env` file has MAIL_USERNAME and MAIL_PASSWORD
2. Verify SMTP credentials are correct
3. Check Flask server logs for error messages
4. For Gmail, ensure App Password is used (not regular password)

### Images Not Uploading
1. Ensure `static/uploads/` directory exists
2. Check file permissions on uploads folder
3. Verify image file size is reasonable

### Grid Layout Issues
1. Clear browser cache (Ctrl+Shift+Delete)
2. Check CSS file is loaded (`static/css/admin/news.css`)
3. Verify screen resolution (may need wider screen for multi-column view)

## 📞 Support

For issues or questions:
1. Check Flask server logs for error messages
2. Verify all environment variables are set
3. Test with sample data first
4. Check browser console for JavaScript errors

---

**LandVista Admin System** - Professional real estate management platform
