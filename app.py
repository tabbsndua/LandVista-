from flask import Flask, render_template, request, redirect, Response, jsonify, session
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from urllib import request as urlrequest, error as urlerror
try:
    import certifi
    CA_BUNDLE = certifi.where()
except Exception:
    certifi = None
    CA_BUNDLE = None
    print("certifi not installed; proceeding without explicit tlsCAFile. Install 'certifi' to avoid TLS CA issues.")
from datetime import datetime
from werkzeug.utils import secure_filename
from bson import ObjectId
import json
import time
from flask_socketio import SocketIO
import platform
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
# On Windows, eventlet can cause ConnectionAbortedError (WinError 10053).
# Use threading mode on Windows to avoid green-IO issues. On non-Windows
# platforms, let Flask-SocketIO choose the best available async mode.
async_mode = None
if platform.system().lower().startswith('win'):
    async_mode = 'threading'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode=async_mode)

# ============================
# EMAIL CONFIG
# ============================
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@landvista.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')

# ============================
# ADMIN AUTHENTICATION CONFIG
# ============================
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'landvista2025')  # Change in .env file
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')  # Change in .env file

# ============================
# PAYSTACK CONFIG
# ============================
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY", "").strip()
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY", "").strip()
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL", "").strip()
PAYSTACK_BASE_URL = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co").strip()

# ============================
# DISABLE CACHING FOR DEVELOPMENT
# ============================
@app.after_request
def set_cache_headers(response):
    # Improve frontend performance while keeping admin pages fresh.
    path = request.path or ""
    if path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)
    elif path.startswith("/admin"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    else:
        response.headers["Cache-Control"] = "public, max-age=300, stale-while-revalidate=60"
        response.headers.pop("Pragma", None)
        response.headers.pop("Expires", None)
    return response

# ============================
# FILE UPLOAD CONFIG
# ============================
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ============================
# MONGODB ATLAS CONNECTION
# ============================
MONGO_URI = os.getenv("MONGO_URI")

# Configure MongoClient to use the system CA bundle from certifi.
# This avoids OpenSSL/CA mismatch issues that cause TLS handshake failures
# when connecting to MongoDB Atlas from some environments (especially on
# Windows with alternate OpenSSL builds).
client = None
db = None

try:
    if not MONGO_URI:
        raise ValueError("MONGO_URI is not set in environment")

    # MongoDB connection options - optimized for various network conditions
    client_kwargs = {
        'serverSelectionTimeoutMS': 3000,
        'connectTimeoutMS': 3000,
        'socketTimeoutMS': 3000,
        'retryWrites': False,
        'tlsInsecure': True,  # Disable TLS verification - use for development only
        'connect': False,  # Don't connect immediately, defer connection
        'maxPoolSize': 1,  # Limit pool size for reliability
        'minPoolSize': 0,  # Allow pool to shrink
    }

    client = MongoClient(MONGO_URI, **client_kwargs)

    # Perform a quick ping to validate the connection and fail fast with
    # a clear error message if TLS/connection problems occur.
    try:
        client.admin.command('ping', timeoutMS=2000)
        db = client["landvista"]
        print("Connected to MongoDB successfully")
    except Exception as ping_error:
        print(f"MongoDB ping failed: {ping_error}")
        print("WARNING: MongoDB is not available. The application will start but database operations may fail.")
        db = None
except Exception as e:
    # Provide a clear diagnostic message for TLS handshake errors
    print(f"Error connecting to MongoDB: {e}")
    print("WARNING: MongoDB connection failed. The application will start without database features.")
    db = None
    client = None

# COLLECTION REFERENCES
testimonials = db.testimonials if db is not None else None
inquiries = db.inquiries if db is not None else None
site_visits = db.site_visits if db is not None else None
payments = db.payments if db is not None else None

# ============================
# DATABASE HELPER FUNCTION
# ============================
def safe_db_operation(operation, default=None):
    """Safely execute database operations with error handling"""
    try:
        if db is None:
            print("WARNING: Database is not available")
            return default
        return operation()
    except Exception as e:
        print(f"Database operation error: {e}")
        return default


def serialize_content_item(item):
    """Normalize news/legal-guide records into JSON-safe payloads."""
    if not isinstance(item, dict):
        return {
            "_id": "",
            "title": "",
            "excerpt": "",
            "content": "",
            "slug": "",
            "category": "General",
            "author": "LandVista Team",
            "date": "",
            "readTime": 5,
            "featured_image": "",
            "status": "published",
            "created_at": ""
        }

    def as_text(value, default=""):
        if value is None:
            return default
        if isinstance(value, str):
            return value
        try:
            return str(value)
        except Exception:
            return default

    def as_date_text(value):
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except Exception:
                pass
        return as_text(value, "")

    read_time_raw = item.get("readTime", item.get("read_time", 5))
    try:
        read_time = int(read_time_raw)
        if read_time <= 0:
            read_time = 5
    except Exception:
        read_time = 5

    item_id = as_text(item.get("_id"), "")
    slug = as_text(item.get("slug"), item_id)
    if not slug:
        slug = item_id

    return {
        "_id": item_id,
        "title": as_text(item.get("title"), "Untitled"),
        "excerpt": as_text(item.get("excerpt"), ""),
        "content": as_text(item.get("content"), ""),
        "slug": slug,
        "category": as_text(item.get("category"), "General"),
        "author": as_text(item.get("author"), "LandVista Team"),
        "date": as_text(item.get("date"), as_date_text(item.get("created_at"))),
        "readTime": read_time,
        "featured_image": as_text(item.get("featured_image"), ""),
        "status": as_text(item.get("status"), "published"),
        "created_at": as_date_text(item.get("created_at"))
    }

def paystack_api_request(path, method="GET", payload=None):
    """Make authenticated requests to the Paystack API."""
    if not PAYSTACK_SECRET_KEY:
        return {"status": False, "message": "PAYSTACK_SECRET_KEY is not configured"}

    try:
        endpoint = f"{PAYSTACK_BASE_URL.rstrip('/')}{path}"
        body = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        req = urlrequest.Request(endpoint, data=body, method=method.upper())
        req.add_header("Authorization", f"Bearer {PAYSTACK_SECRET_KEY}")
        req.add_header("Content-Type", "application/json")

        with urlrequest.urlopen(req, timeout=20) as response:
            response_text = response.read().decode("utf-8")

        return json.loads(response_text) if response_text else {"status": False, "message": "Empty response from Paystack"}

    except urlerror.HTTPError as exc:
        raw_error = ""
        try:
            raw_error = exc.read().decode("utf-8")
        except Exception:
            raw_error = str(exc)

        try:
            parsed = json.loads(raw_error)
            return {
                "status": False,
                "message": parsed.get("message", "Paystack API request failed"),
                "raw": parsed
            }
        except Exception:
            return {"status": False, "message": raw_error or "Paystack API request failed"}
    except Exception as exc:
        return {"status": False, "message": str(exc)}

# ============================
# EMAIL UTILITY FUNCTIONS
# ============================
def send_email_async(recipient, subject, body, html_body=None):
    """Send email asynchronously using SMTP"""
    def send():
        try:
            if not MAIL_USERNAME or not MAIL_PASSWORD:
                print("Email credentials not configured. Skipping email send.")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = MAIL_DEFAULT_SENDER
            msg['To'] = recipient if isinstance(recipient, str) else ', '.join(recipient)
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
                if MAIL_USE_TLS:
                    server.starttls()
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"Email sent successfully to {recipient}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    # Send email in background thread
    thread = threading.Thread(target=send)
    thread.daemon = True
    thread.start()
    return True

def send_email(recipient, subject, body, html_body=None):
    """Send email using SMTP"""
    try:
        if not MAIL_USERNAME or not MAIL_PASSWORD:
            print("Email credentials not configured. Skipping email send.")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = MAIL_DEFAULT_SENDER
        msg['To'] = recipient if isinstance(recipient, str) else ', '.join(recipient)
        
        # Attach plain text version
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach HTML version if provided
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Send via SMTP
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_inquiry_confirmation_email(customer_email, customer_name, property_title):
    """Send confirmation email to customer"""
    subject = "Your Inquiry Has Been Received - LandVista"
    body = f"""
Hi {customer_name},

Thank you for your inquiry about {property_title}. We have received your message and will get back to you shortly.

Best regards,
LandVista Team
    """
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0a3c28;">Thank You for Your Inquiry!</h2>
                <p>Hi <strong>{customer_name}</strong>,</p>
                <p>We have received your inquiry about <strong>{property_title}</strong>.</p>
                <p>Our team will review your message and contact you shortly with more information.</p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="color: #6b7280; font-size: 12px;">Best regards,<br>LandVista Team</p>
            </div>
        </body>
    </html>
    """
    return send_email_async(customer_email, subject, body, html_body)

def send_inquiry_notification_to_admin(inquiry_data):
    """Send notification to admin about new inquiry"""
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')
    subject = f"New Inquiry: {inquiry_data.get('property_title', 'General Inquiry')}"
    body = f"""
New Inquiry Received:

Name: {inquiry_data.get('name')}
Email: {inquiry_data.get('email')}
Phone: {inquiry_data.get('phone')}
Property: {inquiry_data.get('property_title', 'N/A')}
Type: {inquiry_data.get('inquiry_type', 'N/A')}

Message:
{inquiry_data.get('message')}
    """
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0a3c28; border-bottom: 3px solid #10b981; padding-bottom: 10px;">New Inquiry Received</h2>
                <div style="background: #f9fafb; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Name:</strong> {inquiry_data.get('name')}</p>
                    <p><strong>Email:</strong> {inquiry_data.get('email')}</p>
                    <p><strong>Phone:</strong> {inquiry_data.get('phone')}</p>
                    <p><strong>Property:</strong> {inquiry_data.get('property_title', 'N/A')}</p>
                    <p><strong>Inquiry Type:</strong> {inquiry_data.get('inquiry_type', 'N/A')}</p>
                </div>
                <h3>Message:</h3>
                <p style="white-space: pre-wrap; background: #f0f5f3; padding: 15px; border-radius: 8px;">{inquiry_data.get('message')}</p>
            </div>
        </body>
    </html>
    """
    return send_email_async(admin_email, subject, body, html_body)


def send_site_visit_confirmation_email(customer_email, customer_name, property_title, visit_date):
    """Send confirmation email to customer for scheduled site visit"""
    subject = "Your Site Visit is Scheduled - LandVista"
    body = f"""
Hi {customer_name},

Your site visit for {property_title} is scheduled for {visit_date}.

We look forward to meeting you.

Best regards,
LandVista Team
    """
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h3>Site Visit Scheduled</h3>
            <p>Hi <strong>{customer_name}</strong>,</p>
            <p>Your site visit for <strong>{property_title}</strong> is scheduled for <strong>{visit_date}</strong>.</p>
            <p>We look forward to meeting you.</p>
        </body>
    </html>
    """
    return send_email_async(customer_email, subject, body, html_body)


def send_site_visit_notification_to_admin(visit_doc):
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@landvista.com')
    # Also notify the secondary monitoring email requested by the user
    additional_email = 'tabbsndua02@gmail.com'
    recipients = [admin_email]
    if additional_email not in recipients:
        recipients.append(additional_email)

    subject = f"New Site Visit: {visit_doc.get('property_title', 'Property')}"
    body = (
        "New Site Visit Scheduled\n\n"
        f"Name: {visit_doc.get('name')}\n"
        f"Email: {visit_doc.get('email')}\n"
        f"Phone: {visit_doc.get('phone')}\n"
        f"Property: {visit_doc.get('property_title')}\n"
        f"Visit Date: {visit_doc.get('visit_date')}\n\n"
        f"Message: {visit_doc.get('notes')}"
    )
    # Send to both configured admin and the additional monitoring address
    return send_email_async(recipients, subject, body)


# ============================
# ADMIN AUTHENTICATION
# ============================
def require_admin_login(f):
    """Decorator to protect admin routes"""
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Validate credentials
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect('/admin')
        else:
            return render_template('admin_login.html', error="Invalid username or password")
    
    return render_template('admin_login.html')

@app.route("/admin/logout")
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect('/admin/login')

@app.before_request
def track_page_views():
    if request.path.startswith("/admin") or request.path.startswith("/static"):
        return
    
    if db is not None:
        try:
            db.analytics.update_one(
                {"page": "site"},
                {"$inc": {"count": 1}},
                upsert=True
            )
        except Exception as e:
            print(f"Error tracking page views: {e}")

# ============================
# PUBLIC ROUTES
# ============================

@app.route("/")
def landing():
    return redirect("/home")

@app.route("/home")
def home():
    properties = safe_db_operation(lambda: list(db.properties.find({"status": {"$ne": "draft"}}).sort("_id", -1).limit(4)), [])
    testimonials = safe_db_operation(lambda: list(db.testimonials.find().limit(5)), [])
    return render_template("home.html", properties=properties, testimonials=testimonials)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/terms-of-use")
def terms_of_use():
    return render_template("terms-of-use.html")

@app.route("/terms-of-service")
def terms_of_service():
    return render_template("terms-of-service.html")

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/properties")
def properties_page():
    properties = safe_db_operation(
        lambda: list(db.properties.find({"status": {"$ne": "draft"}}).sort("_id", -1)),
        []
    )
    return render_template("properties.html", properties=properties)
@app.route("/properties/<property_id>")
def public_property_details(property_id):
    try:
        property_item = db.properties.find_one({"_id": ObjectId(property_id)})
        if not property_item or property_item.get("status") == "draft":
            return render_template("404.html"), 404
    except Exception:
        return render_template("404.html"), 404

    return render_template(
        "property_details.html",
        property=property_item
    )

@app.route("/news")
def news():
    """News & Blogs page - show published articles"""
    article_rows = safe_db_operation(
        lambda: list(db.news.find({"status": "published"}).sort("created_at", -1)),
        []
    )
    guide_rows = safe_db_operation(
        lambda: list(db.legal_guides.find({"status": "published"}).sort("created_at", -1)),
        []
    )

    articles = [serialize_content_item({**a, "_id": str(a.get("_id", ""))}) for a in article_rows]
    guides = [serialize_content_item({**g, "_id": str(g.get("_id", ""))}) for g in guide_rows]

    return render_template(
        "news.html",
        articles=articles or [],
        guides=guides or []
    )


@app.route("/news/<slug>")
def news_detail(slug):
    """Public article detail page by slug (fallback to _id)"""
    try:
        article = db.news.find_one({"slug": slug, "status": "published"})
        if not article:
            # fallback to lookup by id
            try:
                article = db.news.find_one({"_id": ObjectId(slug), "status": "published"})
            except:
                article = None

        if not article:
            return render_template("404.html"), 404

        # ensure _id is string
        article["_id"] = str(article["_id"])
        return render_template("news_detail.html", article=article)
    except Exception as e:
        print(f"Error loading article detail: {e}")
        return render_template("404.html"), 404

@app.route("/legal-guides")
def legal_guides():
    """Legal Guides page - show published guides"""
    guides = safe_db_operation(
        lambda: list(db.legal_guides.find({"status": "published"}).sort("created_at", -1)),
        []
    )
    for g in guides:
        g["_id"] = str(g["_id"])
    return render_template("legal_guides.html", guides=guides)


@app.route("/legal-guides/<slug>")
def legal_guide_detail(slug):
    """Public legal guide detail page by slug (fallback to _id)"""
    try:
        guide = db.legal_guides.find_one({"slug": slug, "status": "published"})
        if not guide:
            try:
                guide = db.legal_guides.find_one({"_id": ObjectId(slug), "status": "published"})
            except:
                guide = None

        if not guide:
            return render_template("404.html"), 404

        guide["_id"] = str(guide["_id"])
        return render_template("legal_guide_detail.html", guide=guide)
    except Exception as e:
        print(f"Error loading guide detail: {e}")
        return render_template("404.html"), 404

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/submit-inquiry", methods=["POST"])
def submit_inquiry():
    """Handle property inquiry form submissions from property details page"""
    try:
        # Get form data
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        inquiry_type = request.form.get("inquiry_type", "buyer").strip()
        property_id = request.form.get("property_id", "").strip()
        property_title = request.form.get("property_title", "").strip()
        
        # Validate required fields
        if not all([name, phone, email, message]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Create inquiry document
        inquiry_doc = {
            "name": name,
            "phone": phone,
            "email": email,
            "message": message,
            "inquiry_type": inquiry_type,
            "property_id": property_id,
            "property_title": property_title,
            "created_at": datetime.now(),
            "status": "new"
        }
        
        # Save to database
        try:
            if db is None:
                return jsonify({"success": False, "error": "Database not available"}), 500
            result = db.inquiries.insert_one(inquiry_doc)
            
            if result.inserted_id:
                # Send confirmation email to customer (async)
                try:
                    send_inquiry_confirmation_email(email, name, property_title or "Your Property")
                except Exception as e:
                    print(f"Error sending confirmation email: {e}")
                
                # Send notification email to admin (async)
                try:
                    send_inquiry_notification_to_admin(inquiry_doc)
                except Exception as e:
                    print(f"Error sending admin notification: {e}")
                
                # Emit socket event for admin dashboard in real-time
                try:
                    socketio.emit('inquiry_created', {
                        "_id": str(result.inserted_id),
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "message": message,
                        "property_title": property_title,
                        "inquiry_type": inquiry_type,
                        "created_at": datetime.now().isoformat()
                    }, broadcast=True)
                except:
                    pass
                
                # Return success response
                return jsonify({
                    "success": True, 
                    "message": "Inquiry submitted successfully! We will contact you soon.",
                    "inquiry_id": str(result.inserted_id)
                }), 200
            else:
                return jsonify({"success": False, "error": "Failed to save inquiry"}), 500
        except Exception as db_error:
            print(f"Database error during inquiry submission: {db_error}")
            return jsonify({"success": False, "error": "Failed to submit inquiry. Please try again later."}), 500
            
    except Exception as e:
        print(f"Error submitting inquiry: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/submit-site-visit", methods=["POST"])
def submit_site_visit():
    """Handle site visit scheduling from public forms and emit real-time updates."""
    try:
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        property_id = request.form.get("property_id", "").strip()
        property_title = request.form.get("property_title", "").strip()
        visit_date = request.form.get("visit_date", "").strip()
        notes = request.form.get("notes", "").strip()

        # property_id is optional when booking from the contact page
        if not all([name, email, phone, visit_date]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        visit_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "property_id": property_id,
            "property_title": property_title,
            "visit_date": visit_date,
            "notes": notes,
            "status": "scheduled",
            "created_at": datetime.now()
        }

        result = site_visits.insert_one(visit_doc)

        if result.inserted_id:
            visit_doc["_id"] = str(result.inserted_id)

            # Send confirmation and admin notification async
            try:
                send_site_visit_confirmation_email(email, name, property_title or "Property", visit_date)
            except Exception as e:
                print(f"Error sending confirmation email for site visit: {e}")

            try:
                send_site_visit_notification_to_admin(visit_doc)
            except Exception as e:
                print(f"Error sending admin notification for site visit: {e}")

            # Emit socket event for real-time admin UI updates
            try:
                socketio.emit('site_visit_new', {
                    "_id": visit_doc["_id"],
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "property_title": property_title,
                    "visit_date": visit_date,
                    "notes": notes,
                    "created_at": visit_doc["created_at"].isoformat()
                }, broadcast=True)
            except Exception as e:
                print(f"Socket emit error for site_visit_new: {e}")

            return jsonify({"success": True, "visit_id": visit_doc["_id"], "message": "Scheduled successfully"}), 201

        return jsonify({"success": False, "error": "Failed to save site visit"}), 500

    except Exception as e:
        print(f"Error submitting site visit: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# Removed static blog pages (managed via admin articles)

# ===========================
# PUBLIC API ENDPOINTS (Real-time data)
# ===========================

@app.route("/api/properties")
def api_properties():
    """Fetch published properties for real-time display"""
    try:
        if db is None:
            return jsonify([])
        properties = list(db.properties.find({"status": {"$ne": "draft"}}).sort("_id", -1))
        for p in properties:
            p["_id"] = str(p["_id"])
        return jsonify(properties)
    except Exception as e:
        print(f"Error fetching properties: {e}")
        return jsonify([])

@app.route("/api/testimonials")
def api_testimonials():
    """Fetch published testimonials for real-time display on user side"""
    try:
        if db is None:
            return jsonify([])
        # For public API: only return published testimonials
        testimonials_list = list(db.testimonials.find({"status": "published"}).sort("created_at", -1))
        for t in testimonials_list:
            t["_id"] = str(t["_id"])
        return jsonify(testimonials_list)
    except Exception as e:
        print(f"Error fetching testimonials: {e}")
        return jsonify([])

@app.route("/api/testimonials/admin")
def api_testimonials_admin():
    """Fetch all testimonials (admin view) - both published and draft"""
    testimonials_list = list(db.testimonials.find().sort("created_at", -1))
    for t in testimonials_list:
        t["_id"] = str(t["_id"])
    return jsonify(testimonials_list)


# ============================
# ADMIN PAYMENTS (PAYSTACK)
# ============================

@app.route("/admin/payments")
@require_admin_login
def admin_payments_page():
    payment_records = safe_db_operation(
        lambda: list(db.payments.find().sort("created_at", -1).limit(50)),
        []
    )

    for record in payment_records:
        record["_id"] = str(record.get("_id", ""))
        amount_kobo = int(record.get("amount_kobo", 0) or 0)
        record["amount_major"] = amount_kobo / 100

    return render_template(
        "admin/payments.html",
        payments=payment_records,
        paystack_enabled=bool(PAYSTACK_SECRET_KEY and PAYSTACK_PUBLIC_KEY),
        paystack_public_key=PAYSTACK_PUBLIC_KEY
    )

@app.route("/admin/payments/initialize", methods=["POST"])
@require_admin_login
def admin_initialize_paystack_payment():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    customer_name = (data.get("customer_name") or "").strip()
    note = (data.get("note") or "").strip()
    phone = (data.get("phone") or "").strip()
    currency = (data.get("currency") or "KES").strip().upper()

    if not email or "@" not in email:
        return jsonify({"success": False, "message": "A valid customer email is required"}), 400

    try:
        amount_major = float(data.get("amount") or 0)
    except Exception:
        return jsonify({"success": False, "message": "Amount must be numeric"}), 400

    if amount_major <= 0:
        return jsonify({"success": False, "message": "Amount must be greater than zero"}), 400

    amount_kobo = int(round(amount_major * 100))
    reference = f"LV-{int(time.time())}-{uuid.uuid4().hex[:8]}".upper()

    callback_url = PAYSTACK_CALLBACK_URL or f"{request.url_root.rstrip('/')}/admin/payments"
    metadata = {
        "source": "admin_panel",
        "created_by": session.get("admin_username", "admin"),
        "customer_name": customer_name,
        "note": note
    }
    if phone:
        metadata["phone"] = phone

    payload = {
        "email": email,
        "amount": amount_kobo,
        "reference": reference,
        "currency": currency,
        "callback_url": callback_url,
        "metadata": metadata
    }

    paystack_response = paystack_api_request("/transaction/initialize", method="POST", payload=payload)
    if not paystack_response.get("status"):
        return jsonify({
            "success": False,
            "message": paystack_response.get("message", "Failed to initialize transaction")
        }), 400

    payment_data = paystack_response.get("data", {})
    payment_doc = {
        "reference": reference,
        "email": email,
        "customer_name": customer_name,
        "phone": phone,
        "note": note,
        "currency": currency,
        "amount_kobo": amount_kobo,
        "status": "initialized",
        "authorization_url": payment_data.get("authorization_url"),
        "access_code": payment_data.get("access_code"),
        "created_by": session.get("admin_username", "admin"),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    if payments is not None:
        safe_db_operation(
            lambda: payments.update_one(
                {"reference": reference},
                {"$set": payment_doc},
                upsert=True
            ),
            None
        )

    return jsonify({
        "success": True,
        "message": "Payment link created",
        "reference": reference,
        "authorization_url": payment_data.get("authorization_url"),
        "access_code": payment_data.get("access_code"),
        "public_key": PAYSTACK_PUBLIC_KEY
    })

@app.route("/admin/payments/verify", methods=["POST"])
@require_admin_login
def admin_verify_paystack_payment():
    data = request.get_json(silent=True) or {}
    reference = (data.get("reference") or "").strip()

    if not reference:
        return jsonify({"success": False, "message": "Transaction reference is required"}), 400

    paystack_response = paystack_api_request(f"/transaction/verify/{reference}", method="GET")
    if not paystack_response.get("status"):
        return jsonify({
            "success": False,
            "message": paystack_response.get("message", "Unable to verify transaction")
        }), 400

    result = paystack_response.get("data", {})
    status = (result.get("status") or "unknown").lower()
    amount_kobo = int(result.get("amount") or 0)
    email = result.get("customer", {}).get("email", "")
    paid_at = result.get("paid_at") or result.get("created_at")
    gateway_response = result.get("gateway_response", "")

    update_doc = {
        "status": status,
        "amount_kobo": amount_kobo,
        "email": email,
        "currency": result.get("currency", "KES"),
        "paid_at": paid_at,
        "gateway_response": gateway_response,
        "channel": result.get("channel"),
        "updated_at": datetime.utcnow(),
        "raw_response": result
    }

    if payments is not None:
        safe_db_operation(
            lambda: payments.update_one(
                {"reference": reference},
                {
                    "$set": update_doc,
                    "$setOnInsert": {
                        "reference": reference,
                        "created_by": session.get("admin_username", "admin"),
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            ),
            None
        )

    return jsonify({
        "success": True,
        "message": "Transaction verified",
        "payment": {
            "reference": reference,
            "status": status,
            "amount_kobo": amount_kobo,
            "amount_major": amount_kobo / 100,
            "currency": result.get("currency", "KES"),
            "email": email,
            "paid_at": paid_at,
            "gateway_response": gateway_response
        }
    })


# ============================
# ADMIN DASHBOARD
# ============================

@app.route("/admin")
@require_admin_login
def admin_dashboard():
    if db is None:
        return render_template(
            "admin/dashboard.html",
            total_properties=0,
            active_clients=0,
            total_testimonials=0,
            total_sales=0,
            properties_sold=0,
            page_views=0,
            recent_properties=[],
            recent_inquiries=[],
            latest_news=[],
            latest_guides=[]
        )

    try:
        total_properties = db.properties.count_documents({})
        active_clients = db.clients.count_documents({})
        total_testimonials = db.testimonials.count_documents({})

        sales_cursor = db.transactions.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        sales_result = list(sales_cursor)
        total_sales = sales_result[0]["total"] if sales_result else 0

        properties_sold = db.properties.count_documents({
            "status": {"$regex": "^sold$", "$options": "i"}
        })

        page_views_doc = db.analytics.find_one({"page": "site"})
        page_views = page_views_doc["count"] if page_views_doc else 0

        recent_properties = list(db.properties.find().sort("_id", -1).limit(4))
        recent_inquiries = list(db.inquiries.find().sort("_id", -1).limit(4))
        latest_news = list(db.news.find({"status": "published"}).sort("created_at", -1).limit(5))
        latest_guides = list(db.legal_guides.find({"status": "published"}).sort("created_at", -1).limit(5))

        return render_template(
            "admin/dashboard.html",
            total_properties=total_properties,
            active_clients=active_clients,
            total_testimonials=total_testimonials,
            total_sales=total_sales,
            properties_sold=properties_sold,
            page_views=page_views,
            recent_properties=recent_properties,
            recent_inquiries=recent_inquiries,
            latest_news=latest_news,
            latest_guides=latest_guides
        )
    except Exception as e:
        print(f"Error loading admin dashboard: {e}")
        return render_template(
            "admin/dashboard.html",
            total_properties=0,
            active_clients=0,
            total_testimonials=0,
            total_sales=0,
            properties_sold=0,
            page_views=0,
            recent_properties=[],
            recent_inquiries=[],
            latest_news=[],
            latest_guides=[]
        )

# ============================
# ADMIN – PROPERTIES MANAGEMENT
# ============================

@app.route("/admin/properties")
@require_admin_login
def admin_properties():
    if db is None:
        return render_template("admin/properties.html", properties=[])
    try:
        properties = list(db.properties.find().sort("_id", -1))
        for p in properties:
            p["_id"] = str(p["_id"])
        return render_template("admin/properties.html", properties=properties)
    except Exception as e:
        print(f"Error fetching admin properties: {e}")
        return render_template("admin/properties.html", properties=[])

@app.route("/admin/properties/add", methods=["POST"])
@require_admin_login
def add_property():
    try:
        file = request.files.get("media")

        if not file or file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        # Validate required fields
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        price_str = request.form.get("price", "").strip()
        area = request.form.get("area", "").strip()

        if not all([title, location, price_str, area]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Validate price
        try:
            price = int(price_str)
            if price <= 0:
                return jsonify({"success": False, "error": "Price must be greater than 0"}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Price must be a number"}), 400

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        is_draft = request.form.get("draft") == "1"

        res = db.properties.insert_one({
            "title": title,
            "location": location,
            "price": price,
            "area": area,
            "description": request.form.get("description", "").strip(),
            "features": request.form.get("features", "").strip(),
            "contact_name": request.form.get("contact_name", "").strip(),
            "contact_email": request.form.get("contact_email", "").strip(),
            "contact_phone": request.form.get("contact_phone", "").strip(),
            "media": filename,
            "status": "draft" if is_draft else "published",
            "created_at": datetime.now().strftime("%Y-%m-%d")
        })

        # Emit real-time event for new property
        try:
            new_id = str(res.inserted_id)
            payload = {
                "_id": new_id,
                "title": title,
                "location": location,
                "price": price,
                "area": area,
                "description": request.form.get("description", "").strip(),
                "features": request.form.get("features", "").strip(),
                "contact_name": request.form.get("contact_name", "").strip(),
                "contact_email": request.form.get("contact_email", "").strip(),
                "contact_phone": request.form.get("contact_phone", "").strip(),
                "media": filename,
                "status": "draft" if is_draft else "published",
                "created_at": datetime.now().strftime("%Y-%m-%d")
            }
            socketio.emit('property_created', payload, broadcast=True)
        except Exception:
            pass

        # Notify newsletter subscribers when a property is published
        try:
            if not is_draft:
                host = request.host_url.rstrip('/')
                subscribers = list(db.newsletter_subscribers.find({"status": "active"}))
                emails = [s["email"] for s in subscribers if s.get("email")]
                if emails:
                    subject = f"New Property Listed: {title}"
                    body = f"A new property has been listed: {title}\n\nLocation: {location}\nPrice: {price}\n\nView: {host}/properties/{new_id}\n\nVisit LandVista for more details."
                    html_body = f"<html><body><h2>New Property Listed: {title}</h2><p>Location: {location}</p><p>Price: {price}</p><p><a href=\"{host}/properties/{new_id}\">View Property</a></p></body></html>"
                    # send asynchronously in background thread
                    threading.Thread(target=send_email_async, args=(emails, subject, body, html_body)).start()
        except Exception as e:
            print(f"Error notifying subscribers about new property: {e}")

        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})
        return redirect("/admin/properties")
    except Exception as e:
        print(f"Error adding property: {e}")
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": str(e)}), 500
        return redirect("/admin/properties?error=1")

@app.route("/admin/properties/view/<property_id>")
@require_admin_login
def view_property(property_id):
    if db is None:
        return render_template("admin/view-property.html", property=None)
    try:
        property_item = db.properties.find_one({"_id": ObjectId(property_id)})
        return render_template("admin/view-property.html", property=property_item)
    except Exception as e:
        print(f"Error viewing property: {e}")
        return render_template("admin/view-property.html", property=None)

@app.route("/admin/properties/get-data")
@require_admin_login
def get_properties_data():
    """Fetch properties as JSON for real-time updates"""
    properties = list(db.properties.find().sort("_id", -1))
    for p in properties:
        p["_id"] = str(p["_id"])
    return jsonify(properties)

@app.route("/admin/properties/update/<property_id>", methods=["POST"])
@require_admin_login
def update_property(property_id):
    """Update property (modal edit)"""
    try:
        try:
            obj_id = ObjectId(property_id)
        except:
            return jsonify({"success": False, "error": "Invalid property ID"}), 400

        # Validate required fields
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        price_str = request.form.get("price", "").strip()
        area = request.form.get("area", "").strip()

        if not all([title, location, price_str, area]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # Validate price
        try:
            price = int(price_str)
            if price <= 0:
                return jsonify({"success": False, "error": "Price must be greater than 0"}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Price must be a number"}), 400

        files = request.files.getlist("media")
        
        # Get all form fields
        contact_email = request.form.get("contact_email", "").strip()
        contact_name = request.form.get("contact_name", "").strip()
        contact_phone = request.form.get("contact_phone", "").strip()
        
        print(f"DEBUG - Updating property {property_id}")
        print(f"DEBUG - Contact Email: '{contact_email}'")
        print(f"DEBUG - Contact Name: '{contact_name}'")
        print(f"DEBUG - Contact Phone: '{contact_phone}'")
        
        update_data = {
            "title": title,
            "location": location,
            "county": request.form.get("county", "").strip(),
            "property_type": request.form.get("property_type", "").strip(),
            "price": price,
            "area": area,
            "description": request.form.get("description", "").strip(),
            "features": request.form.get("features", "").strip(),
            "contact_name": contact_name,
            "contact_email": contact_email,
            "contact_phone": contact_phone,
        }
        
        print(f"DEBUG - Update data: {update_data}")
        
        # Handle multiple file uploads
        if files and files[0].filename != "":
            saved_files = []
            for file in files:
                if file and file.filename != "":
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    saved_files.append(filename)
            
            if saved_files:
                # If multiple files, store as array; if single, keep as string for backward compatibility
                if len(saved_files) == 1:
                    update_data["media"] = saved_files[0]
                else:
                    update_data["media"] = saved_files
        
        result = db.properties.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        print(f"DEBUG - Update result: {result.matched_count} matched, {result.modified_count} modified")

        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Property not found"}), 404

        # Emit updated property to clients
        try:
            updated = db.properties.find_one({"_id": obj_id})
            if updated:
                updated['_id'] = str(updated['_id'])
                socketio.emit('property_updated', updated, broadcast=True)
        except Exception:
            pass

        # Always return JSON for AJAX requests
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating property: {e}")
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": False, "error": str(e)}), 500
        return redirect("/admin/properties?error=1")



@app.route("/admin/inquiries")
@require_admin_login
def admin_inquiries():
    return render_template("admin/inquiries.html")


@app.route('/admin/site-visits')
@require_admin_login
def admin_site_visits():
    """Render admin page listing scheduled site visits."""
    return render_template('admin/site_visits.html')


@app.route('/admin/api/site-visits')
@require_admin_login
def admin_api_site_visits():
    """Return JSON list of site visits for admin UI."""
    data = list(site_visits.find().sort('created_at', -1))
    for v in data:
        v['_id'] = str(v['_id'])
        if isinstance(v.get('created_at'), datetime):
            v['created_at'] = v['created_at'].isoformat()
    return jsonify({'success': True, 'visits': data})


@app.route('/admin/site-visits/create', methods=['GET', 'POST'])
@require_admin_login
def admin_create_site_visit():
    if request.method == 'GET':
        return render_template('admin/site_visit_create.html')

    try:
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        property_title = request.form.get('property_title', '').strip()
        visit_date = request.form.get('visit_date', '').strip()
        notes = request.form.get('notes', '').strip()

        if not all([name, email, phone, visit_date]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        visit_doc = {
            'name': name,
            'email': email,
            'phone': phone,
            'property_id': request.form.get('property_id', '').strip(),
            'property_title': property_title,
            'visit_date': visit_date,
            'notes': notes,
            'status': 'scheduled',
            'created_at': datetime.now()
        }

        result = site_visits.insert_one(visit_doc)
        if result.inserted_id:
            visit_doc['_id'] = str(result.inserted_id)
            try:
                send_site_visit_notification_to_admin(visit_doc)
            except Exception as e:
                print(f"Error sending admin notification: {e}")
            try:
                socketio.emit('site_visit_new', {
                    '_id': visit_doc['_id'],
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'property_title': property_title,
                    'visit_date': visit_date,
                    'notes': notes,
                    'created_at': visit_doc['created_at'].isoformat()
                }, broadcast=True)
            except Exception as e:
                print(f"Socket emit error on admin create: {e}")

            return jsonify({'success': True, 'visit_id': visit_doc['_id'], 'message': 'Scheduled successfully'})

        return jsonify({'success': False, 'error': 'Failed to save visit'}), 500
    except Exception as e:
        print(f"Error creating admin site visit: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    

@app.route("/admin/inquiries/get-data")
@require_admin_login
def get_inquiries_data():
    """Fetch all inquiries as JSON"""
    try:
        inq_list = list(inquiries.find().sort("created_at", -1))
        for inq in inq_list:
            inq["_id"] = str(inq["_id"])
        return jsonify(inq_list)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/inquiries/delete/<inquiry_id>", methods=["POST"])
@require_admin_login
def delete_inquiry(inquiry_id):
    """Delete an inquiry"""
    try:
        obj_id = ObjectId(inquiry_id)
        result = inquiries.delete_one({"_id": obj_id})
        
        if result.deleted_count > 0:
            try:
                socketio.emit('inquiry_deleted', {'inquiry_id': inquiry_id}, broadcast=True)
            except:
                pass
            return jsonify({'success': True, 'message': 'Inquiry deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Inquiry not found'}), 404
    except Exception as e:
        print(f"Error deleting inquiry: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route("/admin/inquiries/update/<inquiry_id>", methods=["POST"])
@require_admin_login
def update_inquiry(inquiry_id):
    """Update inquiry status"""
    try:
        obj_id = ObjectId(inquiry_id)
    except:
        return jsonify({"success": False, "error": "Invalid inquiry ID"}), 400

    data = request.json or {}
    new_status = data.get("status", "").strip()

    if new_status not in ["new", "contacted", "resolved"]:
        return jsonify({"success": False, "error": "Invalid status"}), 400

    try:
        inquiries.update_one(
            {"_id": obj_id},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}}
        )
        return jsonify({"success": True, "message": f"Status updated to {new_status}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/inquiries/stream")
@require_admin_login
def inquiries_stream():
    def stream():
        last_count = 0
        while True:
            current = inquiries.count_documents({})
            if current != last_count:
                data = list(inquiries.find().sort("created_at", -1))
                for q in data:
                    q["_id"] = str(q["_id"])
                    # format date
                    q["date"] = q.get("created_at", "") if isinstance(q.get("created_at", ""), str) else q.get("created_at", "")
                yield f"data:{json.dumps(data)}\n\n"
                last_count = current
            time.sleep(2)

    return Response(stream(), mimetype="text/event-stream")


@app.route("/inquiries/add", methods=["POST"])
def add_inquiry():
    try:
        data = request.form or request.json or {}
        
        # Validate required fields
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        message = data.get("message", "").strip()
        
        if not all([name, email, phone, message]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Basic email validation
        if "@" not in email or "." not in email:
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        inquiry = {
            "name": name,
            "email": email,
            "phone": phone,
            "property": data.get("property", "").strip(),
            "message": message,
            "priority": data.get("priority", "").strip() or "medium",
            "status": "new",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        res = inquiries.insert_one(inquiry)

        # Notify admin by email (async)
        try:
            send_inquiry_notification_to_admin(inquiry)
        except Exception as e:
            print(f"Error sending admin notification: {e}")

        # Emit new inquiry to admins
        try:
            latest = inquiries.find_one({"_id": res.inserted_id})
            if latest:
                latest["_id"] = str(latest["_id"]) 
                socketio.emit('inquiry_created', latest, broadcast=True)
        except Exception:
            pass

        # Return JSON for AJAX; redirect for non-AJAX form posts
        content_type = request.headers.get('Content-Type', '')
        accept = request.headers.get('Accept', '')
        if request.is_json or 'multipart/form-data' in content_type or 'application/json' in accept:
            return jsonify({"success": True})
        return redirect('/contact')
    except Exception as e:
        print(f"Error adding inquiry: {e}")
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 500
        return redirect('/contact?error=1')

@app.route("/admin/send-email", methods=["POST"])
@require_admin_login
def admin_send_email():
    """Admin endpoint to send custom emails"""
    try:
        data = request.json or {}
        
        recipient = data.get("recipient", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()
        
        if not all([recipient, subject, message]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Validate email
        if "@" not in recipient or "." not in recipient:
            return jsonify({"success": False, "error": "Invalid email format"}), 400
        
        # Send email
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #0a3c28; border-bottom: 3px solid #10b981; padding-bottom: 10px;">{subject}</h2>
                    <p style="white-space: pre-wrap; margin-top: 20px; line-height: 1.8;">{message}</p>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    <p style="color: #6b7280; font-size: 12px;">Sent by LandVista Team</p>
                </div>
            </body>
        </html>
        """
        
        success = send_email(recipient, subject, message, html_body)
        
        if success:
            # Emit real-time notification
            try:
                socketio.emit('email_sent', {
                    "recipient": recipient,
                    "subject": subject,
                    "timestamp": datetime.now().isoformat()
                }, broadcast=True)
            except:
                pass
            
            return jsonify({"success": True, "message": "Email sent successfully!"})
        else:
            return jsonify({"success": False, "error": "Failed to send email"}), 500
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/properties/edit/<property_id>", methods=["GET", "POST"])
@require_admin_login
def edit_property(property_id):
    if db is None:
        return render_template("admin/edit-property.html", property=None)
    
    property_item = db.properties.find_one({"_id": ObjectId(property_id)})

    if request.method == "POST":
        if db is None:
            return redirect("/admin/properties?error=Database+unavailable")
        try:
            # Validate required fields
            title = request.form.get("title", "").strip()
            location = request.form.get("location", "").strip()
            price_str = request.form.get("price", "").strip()
            area = request.form.get("area", "").strip()

            if not all([title, location, price_str, area]):
                return redirect("/admin/properties?error=Missing+required+fields")

            # Validate price
            try:
                price = int(price_str)
                if price <= 0:
                    return redirect("/admin/properties?error=Price+must+be+greater+than+0")
            except ValueError:
                return redirect("/admin/properties?error=Price+must+be+a+number")

            files = request.files.getlist("media")
            
            # Get all form fields
            contact_email = request.form.get("contact_email", "").strip()
            contact_name = request.form.get("contact_name", "").strip()
            contact_phone = request.form.get("contact_phone", "").strip()
            
            update_data = {
                "title": title,
                "location": location,
                "county": request.form.get("county", "").strip(),
                "property_type": request.form.get("property_type", "").strip(),
                "price": price,
                "area": area,
                "description": request.form.get("description", "").strip(),
                "features": request.form.get("features", "").strip(),
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
            }
            
            # Handle multiple file uploads
            if files and files[0].filename != "":
                saved_files = []
                for file in files:
                    if file and file.filename != "":
                        orig = secure_filename(file.filename)
                        # make filename unique to avoid overwriting existing files
                        unique_name = f"{int(time.time()*1000)}_{orig}"
                        file.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
                        saved_files.append(unique_name)
                
                if saved_files:
                    # Merge with existing media (append new uploads)
                    # reload property from DB to ensure we have the latest media list
                    try:
                        property_item = db.properties.find_one({"_id": ObjectId(property_id)}) or property_item
                    except Exception:
                        pass

                    current_media = property_item.get("media", [])
                    # Normalize to list
                    if isinstance(current_media, str):
                        current_media = [current_media]
                    elif not isinstance(current_media, list):
                        current_media = []

                    # Normalize filenames (strip any leading path or URL parts)
                    normalized_current = [os.path.basename(str(x)) for x in current_media]

                    merged = normalized_current + saved_files
                    # Remove duplicates while preserving order
                    seen = set()
                    merged_unique = []
                    for f in merged:
                        if f not in seen:
                            seen.add(f)
                            merged_unique.append(f)

                    # Debug logging
                    try:
                        print(f"Saved files: {saved_files}")
                        print(f"Current media (normalized): {normalized_current}")
                        print(f"Merged unique media: {merged_unique}")
                    except Exception:
                        pass

                    # Store as string if single for backward compatibility
                    if len(merged_unique) == 1:
                        update_data["media"] = merged_unique[0]
                    else:
                        update_data["media"] = merged_unique
            
            result = db.properties.update_one(
                {"_id": ObjectId(property_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return redirect("/admin/properties?error=Property+not+found")

            # Emit updated property to clients
            try:
                updated = db.properties.find_one({"_id": ObjectId(property_id)})
                if updated:
                    updated['_id'] = str(updated['_id'])
                    socketio.emit('property_updated', updated, broadcast=True)
            except Exception:
                pass

            return redirect("/admin/properties")
        except Exception as e:
            print(f"Error updating property: {e}")
            return redirect("/admin/properties?error=Update+failed")

    return render_template("admin/edit-property.html", property=property_item)

@require_admin_login
@app.route("/admin/properties/delete/<property_id>", methods=["POST"])
def delete_property(property_id):
    try:
        obj_id = ObjectId(property_id)
    except Exception:
        return redirect("/admin/properties")

    db.properties.delete_one({"_id": obj_id})
    try:
        socketio.emit('property_deleted', {"_id": str(obj_id)}, broadcast=True)
    except Exception:
        pass
    return redirect("/admin/properties")


# Admin: delete individual image from property
@require_admin_login
@app.route("/admin/properties/<property_id>/delete-image/<image_name>", methods=["POST"])
@require_admin_login
def delete_image(property_id, image_name):
    try:
        print(f"Delete image request: property_id={property_id}, image_name={image_name}")
        
        # Get the property
        property_item = db.properties.find_one({"_id": ObjectId(property_id)})
        if not property_item:
            print(f"Property not found: {property_id}")
            return jsonify({"success": False, "error": "Property not found"}), 404
        
        # Get current media
        media = property_item.get("media", [])
        
        # Normalize media to list for consistent handling
        if isinstance(media, str):
            media = [media]
        elif not isinstance(media, list):
            media = []
        
        print(f"Current media list: {media}")
        print(f"Looking for image: {image_name}")
        
        # Remove the image from media list
        if image_name in media:
            media.remove(image_name)
            print(f"Image found and removed. Remaining media: {media}")
            
            # Update database - store as string if single file, array if multiple
            if len(media) == 0:
                db.properties.update_one(
                    {"_id": ObjectId(property_id)},
                    {"$unset": {"media": ""}}
                )
                print("All media removed, unsetting field")
            elif len(media) == 1:
                db.properties.update_one(
                    {"_id": ObjectId(property_id)},
                    {"$set": {"media": media[0]}}
                )
                print(f"One media remaining, stored as string: {media[0]}")
            else:
                db.properties.update_one(
                    {"_id": ObjectId(property_id)},
                    {"$set": {"media": media}}
                )
                print(f"Multiple media remaining, stored as array")
            
            # Delete file from filesystem
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            print(f"Attempting to delete file: {file_path}")
            
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"File deleted successfully: {file_path}")
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")
            else:
                print(f"File not found at path: {file_path}")
            
            return jsonify({"success": True, "message": "Image deleted successfully"})
        else:
            print(f"Image not found in media list")
            return jsonify({"success": False, "error": "Image not found"}), 404
            
    except Exception as e:
        print(f"Error deleting image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/admin/properties/<property_id>/delete-image-form", methods=["POST"])
@require_admin_login
def delete_image_form(property_id):
    """Fallback form-based delete (redirects back to edit page)."""
    try:
        image_name = request.form.get('image_name', '').strip()
        if not image_name:
            return redirect(f"/admin/properties/edit/{property_id}?error=No+image+specified")

        # reuse same deletion logic as JSON endpoint
        property_item = db.properties.find_one({"_id": ObjectId(property_id)})
        if not property_item:
            return redirect(f"/admin/properties/edit/{property_id}?error=Property+not+found")

        media = property_item.get('media', [])
        if isinstance(media, str):
            media = [media]
        elif not isinstance(media, list):
            media = []

        if image_name in media:
            media.remove(image_name)
            if len(media) == 0:
                db.properties.update_one({"_id": ObjectId(property_id)}, {"$unset": {"media": ""}})
            elif len(media) == 1:
                db.properties.update_one({"_id": ObjectId(property_id)}, {"$set": {"media": media[0]}})
            else:
                db.properties.update_one({"_id": ObjectId(property_id)}, {"$set": {"media": media}})

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file in form endpoint {file_path}: {e}")

            return redirect(f"/admin/properties/edit/{property_id}?success=Image+deleted")
        else:
            return redirect(f"/admin/properties/edit/{property_id}?error=Image+not+found")
    except Exception as e:
        print(f"Error in delete_image_form: {e}")
        return redirect(f"/admin/properties/edit/{property_id}?error=Delete+failed")


# Admin: mark property sold
@require_admin_login
@app.route('/admin/properties/mark-sold/<property_id>', methods=['POST'])
def mark_property_sold(property_id):
    try:
        obj_id = ObjectId(property_id)
    except Exception:
        return jsonify({"success": False, "error": "Invalid property id"}), 400

    try:
        update = {"$set": {"status": "sold", "sold_at": datetime.utcnow().isoformat()}}
        res = db.properties.update_one({"_id": obj_id}, update)
        if res.matched_count == 0:
            return jsonify({"success": False, "error": "Property not found"}), 404

        updated = db.properties.find_one({"_id": obj_id})
        if updated:
            updated['_id'] = str(updated['_id'])
            try:
                socketio.emit('property_updated', updated, broadcast=True)
            except Exception:
                pass

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error marking property sold: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Admin: mark property available/published again
@require_admin_login
@app.route('/admin/properties/mark-available/<property_id>', methods=['POST'])
def mark_property_available(property_id):
    try:
        obj_id = ObjectId(property_id)
    except Exception:
        return jsonify({"success": False, "error": "Invalid property id"}), 400

    try:
        update = {"$set": {"status": "published"}, "$unset": {"sold_at": ""}}
        res = db.properties.update_one({"_id": obj_id}, update)
        if res.matched_count == 0:
            return jsonify({"success": False, "error": "Property not found"}), 404

        updated = db.properties.find_one({"_id": obj_id})
        if updated:
            updated['_id'] = str(updated['_id'])
            try:
                socketio.emit('property_updated', updated, broadcast=True)
            except Exception:
                pass

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error marking property available: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ============================
# ADMIN – CLIENTS MANAGEMENT
# ============================

@app.route("/admin/clients")
@require_admin_login
def admin_clients():
    """Display all clients"""
    try:
        clients = list(db.clients.find().sort("created_at", -1))
        # Normalize clients for template rendering (ensure _id is string and created_at is datetime)
        for c in clients:
            try:
                c['_id'] = str(c.get('_id'))
            except:
                c['_id'] = c.get('_id')
            # Ensure created_at is a datetime for strftime in template
            if isinstance(c.get('created_at'), str):
                try:
                    # attempt to parse ISO format
                    from datetime import datetime as _dt
                    c['created_at'] = _dt.fromisoformat(c['created_at'])
                except Exception:
                    c['created_at'] = None
        return render_template("admin/clients.html", clients=clients)
    except Exception as e:
        print(f"Error loading clients: {e}")
        return render_template("admin/clients.html", clients=[])

@app.route("/admin/clients/get-data")
@require_admin_login
def get_clients_data():
    """Fetch all clients as JSON"""
    try:
        clients = list(db.clients.find().sort("created_at", -1))
        out = []
        for client in clients:
            client_obj = dict(client)
            client_obj["_id"] = str(client_obj.get("_id"))
            ca = client_obj.get('created_at')
            try:
                client_obj['created_at'] = ca.isoformat() if hasattr(ca, 'isoformat') else str(ca or '')
            except Exception:
                client_obj['created_at'] = str(ca or '')
            out.append(client_obj)
        return jsonify(out)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/clients/add", methods=["GET", "POST"])
@require_admin_login
def add_client():
    """Add new client"""
    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            client_type = request.form.get("client_type", "buyer").strip()
            budget = request.form.get("budget", "").strip()
            notes = request.form.get("notes", "").strip()

            if not all([name, email, phone]):
                return redirect("/admin/clients?error=Missing+required+fields")

            db.clients.insert_one({
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "client_type": client_type,
                "budget": budget,
                "notes": notes,
                "status": "Active",
                "interested_properties": [],
                "inquiries_count": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            })

            try:
                socketio.emit('client_added', {
                    "name": name,
                    "email": email,
                    "timestamp": datetime.now().isoformat()
                }, broadcast=True)
            except:
                pass

            return redirect("/admin/clients?success=Client+added+successfully")
        except Exception as e:
            print(f"Error adding client: {e}")
            return redirect("/admin/clients?error=Failed+to+add+client")

    return render_template("admin/add_client.html")

@app.route("/admin/clients/view/<client_id>")
@require_admin_login
def view_client(client_id):
    """View client details"""
    try:
        client = db.clients.find_one({"_id": ObjectId(client_id)})
        if not client:
            return redirect("/admin/clients?error=Client+not+found")
        return render_template("admin/view_client.html", client=client)
    except Exception as e:
        print(f"Error viewing client: {e}")
        return redirect("/admin/clients?error=Invalid+client+ID")

@app.route("/admin/clients/edit/<client_id>", methods=["GET", "POST"])
@require_admin_login
def edit_client(client_id):
    """Edit client details"""
    try:
        obj_id = ObjectId(client_id)
    except:
        return redirect("/admin/clients?error=Invalid+client+ID")

    if db is None:
        return redirect("/admin/clients?error=Database+unavailable")
    
    client = db.clients.find_one({"_id": obj_id})
    if not client:
        return redirect("/admin/clients?error=Client+not+found")

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            client_type = request.form.get("client_type", "buyer").strip()
            budget = request.form.get("budget", "").strip()
            status = request.form.get("status", "Active").strip()
            notes = request.form.get("notes", "").strip()

            if not all([name, email, phone]):
                return render_template("admin/edit_client.html", client=client, error="Missing required fields")

            update_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "client_type": client_type,
                "budget": budget,
                "status": status,
                "notes": notes,
                "updated_at": datetime.now()
            }

            db.clients.update_one({"_id": obj_id}, {"$set": update_data})

            try:
                socketio.emit('client_updated', {
                    "client_id": str(obj_id),
                    "name": name,
                    "timestamp": datetime.now().isoformat()
                }, broadcast=True)
            except:
                pass

            return redirect("/admin/clients?success=Client+updated+successfully")
        except Exception as e:
            print(f"Error updating client: {e}")
            return render_template("admin/edit_client.html", client=client, error="Failed to update client")

    return render_template("admin/edit_client.html", client=client)

@app.route("/admin/clients/delete/<client_id>", methods=["POST"])
@require_admin_login
def delete_client(client_id):
    """Delete client"""
    try:
        obj_id = ObjectId(client_id)
        result = db.clients.delete_one({"_id": obj_id})
        
        if result.deleted_count > 0:
            try:
                socketio.emit('client_deleted', {
                    "client_id": client_id,
                    "timestamp": datetime.now().isoformat()
                }, broadcast=True)
            except:
                pass
            return redirect("/admin/clients?success=Client+deleted+successfully")
        else:
            return redirect("/admin/clients?error=Client+not+found")
    except Exception as e:
        print(f"Error deleting client: {e}")
        return redirect("/admin/clients?error=Failed+to+delete+client")

# ============================
# DASHBOARD DATA API
# ============================

@app.route("/admin/dashboard-data")
@require_admin_login
def dashboard_data():
    if db is None:
        return jsonify({"error": "Database not available"}), 500
    
    try:
        total_properties = db.properties.count_documents({})
        active_clients = db.clients.count_documents({})
        total_testimonials = db.testimonials.count_documents({})

        sales_cursor = db.transactions.aggregate([
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ])
        sales_result = list(sales_cursor)
        total_sales = sales_result[0]["total"] if sales_result else 0

        page_views_doc = db.analytics.find_one({"page": "site"})
        page_views = page_views_doc["count"] if page_views_doc else 0

        properties_sold = db.properties.count_documents({
            "status": {"$regex": "^sold$", "$options": "i"}
        })

        recent_properties = []
        for p in db.properties.find().sort("_id", -1).limit(4):
            p["_id"] = str(p["_id"])
            recent_properties.append(p)

        recent_inquiries = []
        for i in db.inquiries.find().sort("created_at", -1).limit(4):
            i["_id"] = str(i["_id"])
            recent_inquiries.append(i)

        # Get latest news articles
        latest_news = []
        for article in db.news.find({"status": "published"}).sort("created_at", -1).limit(5):
            article["_id"] = str(article["_id"])
            latest_news.append(article)

        # Get latest legal guides
        latest_guides = []
        for guide in db.legal_guides.find({"status": "published"}).sort("created_at", -1).limit(5):
            guide["_id"] = str(guide["_id"])
            latest_guides.append(guide)

        return jsonify({
            "total_properties": total_properties,
            "active_clients": active_clients,
            "total_testimonials": total_testimonials,
            "total_sales": total_sales,
            "page_views": page_views,
            "properties_sold": properties_sold,
            "recent_properties": recent_properties,
            "recent_inquiries": recent_inquiries,
            "latest_news": latest_news,
            "latest_guides": latest_guides
        })
    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({"error": "Failed to fetch dashboard data"}), 500

# =========================
# TESTIMONIALS
# =========================

@app.route("/admin/testimonials")
@require_admin_login
def admin_testimonials():
    return render_template("admin/testimonials.html")

@app.route("/admin/testimonials/add-new")
@require_admin_login
def add_testimonial_form():
    # ✅ FIX: template name matches your file
    return render_template("admin/add_testimonial.html")

# =========================
# NEWS & BLOGS
# =========================

@require_admin_login
@app.route("/admin/news")
def admin_news():
     return render_template("admin/news.html")

@app.route("/api/news")
def api_news():
    """Get published news articles (public API)"""
    try:
        rows = list(db.news.find({"status": "published"}).sort("created_at", -1))
        articles = [serialize_content_item({**row, "_id": str(row.get("_id", ""))}) for row in rows]
        return jsonify(articles)
    except:
        return jsonify([])

@app.route("/api/news/admin")
def api_news_admin():
    """Get all news articles (admin view - draft + published)"""
    try:
        articles = list(db.news.find().sort("created_at", -1))
        for article in articles:
            article["_id"] = str(article["_id"])
        return jsonify(articles)
    except:
        return jsonify([])

@app.route("/api/newsletter/subscribe", methods=["POST"])
def subscribe_newsletter():
    """Subscribe email to newsletter"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        
        if not email or "@" not in email:
            return jsonify({"success": False, "message": "Invalid email address"}), 400
        
        # Check if already subscribed
        existing = db.newsletter_subscribers.find_one({"email": email})
        if existing:
            return jsonify({"success": False, "message": "Email already subscribed"}), 400
        
        # Add to newsletter
        subscriber = {
            "email": email,
            "subscribed_at": datetime.now(),
            "status": "active"
        }
        result = db.newsletter_subscribers.insert_one(subscriber)
        
        # Send confirmation email to subscriber
        confirmation_body = f"""Hello,

Thank you for subscribing to LandVista's newsletter!

You will now receive the latest insights on land investment, property market updates, and exclusive offers delivered to your inbox.

Best regards,
LandVista Team
tabbsndua2@gmail.com

---
To unsubscribe, click: http://localhost:5000/newsletter/unsubscribe/{email}"""
        
        confirmation_html = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0a3c28;">Welcome to LandVista Newsletter!</h2>
        <p>Thank you for subscribing to LandVista's newsletter!</p>
        <p>You will now receive the latest insights on land investment, property market updates, and exclusive offers delivered to your inbox.</p>
        <p style="margin-top: 30px; color: #666;">Best regards,<br><strong>LandVista Team</strong><br>tabbsndua2@gmail.com</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #999; text-align: center;">
            <a href="http://localhost:5000/newsletter/unsubscribe/{email}" style="color: #0a3c28; text-decoration: none;">Unsubscribe from newsletter</a>
        </p>
    </div>
</body>
</html>"""
        
        # Send async so it doesn't block
        threading.Thread(
            target=send_email_async,
            args=(email, "Welcome to LandVista Newsletter!", confirmation_body, confirmation_html)
        ).start()
        
        # Send notification to admin
        admin_body = f"""New Newsletter Subscriber

Email: {email}
Subscribed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total subscribers: {db.newsletter_subscribers.count_documents({})}"""
        
        threading.Thread(
            target=send_email_async,
            args=(ADMIN_EMAIL, "New Newsletter Subscriber", admin_body)
        ).start()
        
        # Broadcast real-time update (non-critical)
        try:
            socketio.emit('newsletter_new_subscriber', {
                'email': email,
                'count': db.newsletter_subscribers.count_documents({})
            }, broadcast=True, skip_sid=None)
        except Exception as emit_error:
            print(f"Socket emit error (non-critical): {emit_error}")
        
        return jsonify({"success": True, "message": "Successfully subscribed to newsletter"}), 201
    except Exception as e:
        print(f"Newsletter error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/subscribe-newsletter", methods=["POST"])
def subscribe_newsletter_form():
    """Handle form-based newsletter subscription for backwards compatibility"""
    try:
        email = request.form.get("email", "").strip().lower()
        
        if not email or "@" not in email:
            return redirect("/news?error=invalid_email")
        
        # Check if already subscribed
        existing = db.newsletter_subscribers.find_one({"email": email})
        if existing:
            return redirect("/news?error=already_subscribed")
        
        # Add to newsletter
        subscriber = {
            "email": email,
            "subscribed_at": datetime.now(),
            "status": "active"
        }
        result = db.newsletter_subscribers.insert_one(subscriber)
        
        # Send confirmation email to subscriber
        confirmation_body = f"""Hello,

Thank you for subscribing to LandVista's newsletter!

You will now receive the latest insights on land investment, property market updates, and exclusive offers delivered to your inbox.

Best regards,
LandVista Team
tabbsndua2@gmail.com

---
To unsubscribe, click: http://localhost:5000/newsletter/unsubscribe/{email}"""
        
        confirmation_html = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0a3c28;">Welcome to LandVista Newsletter!</h2>
        <p>Thank you for subscribing to LandVista's newsletter!</p>
        <p>You will now receive the latest insights on land investment, property market updates, and exclusive offers delivered to your inbox.</p>
        <p style="margin-top: 30px; color: #666;">Best regards,<br><strong>LandVista Team</strong><br>tabbsndua2@gmail.com</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="font-size: 12px; color: #999; text-align: center;">
            <a href="http://localhost:5000/newsletter/unsubscribe/{email}" style="color: #0a3c28; text-decoration: none;">Unsubscribe from newsletter</a>
        </p>
    </div>
</body>
</html>"""
        
        # Send async so it doesn't block
        threading.Thread(
            target=send_email_async,
            args=(email, "Welcome to LandVista Newsletter!", confirmation_body, confirmation_html)
        ).start()
        
        # Send notification to admin
        admin_body = f"""New Newsletter Subscriber

Email: {email}
Subscribed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total subscribers: {db.newsletter_subscribers.count_documents({})}"""
        
        threading.Thread(
            target=send_email_async,
            args=(ADMIN_EMAIL, "New Newsletter Subscriber", admin_body)
        ).start()
        
        return redirect("/news?success=subscribed")
    except Exception as e:
        print(f"Newsletter error: {e}")
        return redirect("/news?error=subscription_failed")

@app.route("/newsletter/unsubscribe/<email>", methods=["GET"])
def unsubscribe_newsletter(email):
    """Unsubscribe email from newsletter"""
    try:
        email = email.strip().lower()
        
        if not email or "@" not in email:
            return render_template("unsubscribe.html", success=False, message="Invalid email address")
        
        # Remove from newsletter
        result = db.newsletter_subscribers.delete_one({"email": email})
        
        if result.deleted_count > 0:
            return render_template("unsubscribe.html", success=True, message=f"You have been unsubscribed from LandVista's newsletter. Sorry to see you go!")
        else:
            return render_template("unsubscribe.html", success=False, message="Email not found in our newsletter list")
    except Exception as e:
        print(f"Unsubscribe error: {e}")
        return render_template("unsubscribe.html", success=False, message="Error processing unsubscribe request")

@app.route("/admin/news/add", methods=["POST"])
@require_admin_login
def add_news_article():
    """Add new news article"""
    try:
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        read_time = int(request.form.get("read_time", 0))
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft").strip()
        featured = request.form.get("featured") == "true"
        
        if not all([title, slug, author, category, date, read_time, excerpt, content]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Handle featured image
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = int(datetime.now().timestamp())
                filename = f"article_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                featured_image = f"/static/uploads/{filename}"
        
        article = {
            "title": title,
            "slug": slug,
            "author": author,
            "category": category,
            "date": date,
            "readTime": read_time,
            "excerpt": excerpt,
            "content": content,
            "featured_image": featured_image,
            "status": status,
            "featured": featured,
            "created_at": datetime.now()
        }
        
        result = db.news.insert_one(article)
        
        # REAL-TIME: Broadcast new article to all users
        try:
            article["_id"] = str(result.inserted_id)
            socketio.emit('news_added', article, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting news_added event: {e}")
        
        # Notify newsletter subscribers when an article is published
        try:
            if article.get("status") == "published":
                host = request.host_url.rstrip('/')
                subscribers = list(db.newsletter_subscribers.find({"status": "active"}))
                emails = [s["email"] for s in subscribers if s.get("email")]
                if emails:
                    subject = f"New Article: {article.get('title')}"
                    body = f"{article.get('excerpt')}\n\nRead more: {host}/news/{article.get('slug') or article.get('_id')}"
                    html_body = f"<html><body><h2>{article.get('title')}</h2><p>{article.get('excerpt')}</p><p><a href=\"{host}/news/{article.get('slug') or article.get('_id')}\">Read the full article</a></p></body></html>"
                    threading.Thread(target=send_email_async, args=(emails, subject, body, html_body)).start()
        except Exception as e:
            print(f"Error notifying subscribers about new article: {e}")
        
        return jsonify({"success": True, "_id": str(result.inserted_id)})
    except Exception as e:
        print(f"Error adding article: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/news/update/<article_id>", methods=["POST"])
@require_admin_login
def update_news_article(article_id):
    """Update news article"""
    try:
        try:
            obj_id = ObjectId(article_id)
        except:
            return jsonify({"success": False, "error": "Invalid article ID"}), 400
        
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        read_time = int(request.form.get("read_time", 0))
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft").strip()
        featured = request.form.get("featured") == "true"
        
        if not all([title, slug, author, category, date, read_time, excerpt, content]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        update_data = {
            "title": title,
            "slug": slug,
            "author": author,
            "category": category,
            "date": date,
            "readTime": read_time,
            "excerpt": excerpt,
            "content": content,
            "status": status,
            "featured": featured,
            "updated_at": datetime.now()
        }
        
        # Handle featured image
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = int(datetime.now().timestamp())
                filename = f"article_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_data["featured_image"] = f"/static/uploads/{filename}"
        
        result = db.news.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Article not found"}), 404
        
        # REAL-TIME: Broadcast article update to all users
        try:
            update_data["_id"] = str(obj_id)
            socketio.emit('news_updated', update_data, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting news_updated event: {e}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating article: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@require_admin_login
@app.route("/admin/news/delete/<article_id>", methods=["DELETE"])
def delete_news_article(article_id):
    """Delete news article"""
    try:
        try:
            obj_id = ObjectId(article_id)
        except:
            return jsonify({"success": False, "error": "Invalid article ID"}), 400
        
        result = db.news.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Article not found"}), 404
        
        # REAL-TIME: Broadcast article deletion to all users
        try:
            socketio.emit('news_deleted', {"_id": str(obj_id)}, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting news_deleted event: {e}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting article: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =========================
# LEGAL GUIDES
# =========================
@app.route("/admin/legal-guides")
@require_admin_login
def admin_legal_guides():
    return render_template("admin/legal_guides.html")

@app.route("/api/legal-guides")
def api_legal_guides():
    """Get published legal guides (public API)"""
    try:
        rows = list(db.legal_guides.find({"status": "published"}).sort("created_at", -1))
        guides = [serialize_content_item({**row, "_id": str(row.get("_id", ""))}) for row in rows]
        return jsonify(guides)
    except:
        return jsonify([])

@app.route("/api/legal-guides/admin")
def api_legal_guides_admin():
    """Get all legal guides (admin view - draft + published)"""
    try:
        guides = list(db.legal_guides.find().sort("created_at", -1))

        # Return whatever exists in the DB; do NOT auto-insert sample guides here.
        for guide in guides:
            guide["_id"] = str(guide["_id"])
        return jsonify(guides)
    except Exception as e:
        print(f"Error loading guides: {e}")
        return jsonify([])

@app.route("/admin/legal-guides/add", methods=["POST"])
@require_admin_login
def add_legal_guide():
    """Add new legal guide"""
    try:
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        read_time = int(request.form.get("read_time", 0))
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft").strip()
        featured = request.form.get("featured") == "true"
        
        if not all([title, slug, author, category, date, read_time, excerpt, content]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Handle featured image
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = int(datetime.now().timestamp())
                filename = f"guide_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                featured_image = f"/static/uploads/{filename}"
        
        guide = {
            "title": title,
            "slug": slug,
            "author": author,
            "category": category,
            "date": date,
            "readTime": read_time,
            "excerpt": excerpt,
            "content": content,
            "featured_image": featured_image,
            "status": status,
            "featured": featured,
            "created_at": datetime.now()
        }
        
        result = db.legal_guides.insert_one(guide)
        
        # REAL-TIME: Broadcast new guide to all users
        try:
            guide["_id"] = str(result.inserted_id)
            socketio.emit('guide_added', guide, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting guide_added event: {e}")
        
        return jsonify({"success": True, "_id": str(result.inserted_id)})
    except Exception as e:
        print(f"Error adding legal guide: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/legal-guides/update/<guide_id>", methods=["POST"])
@require_admin_login
def update_legal_guide(guide_id):
    """Update legal guide"""
    try:
        try:
            obj_id = ObjectId(guide_id)
        except:
            return jsonify({"success": False, "error": "Invalid guide ID"}), 400
        
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        read_time = int(request.form.get("read_time", 0))
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        status = request.form.get("status", "draft").strip()
        featured = request.form.get("featured") == "true"
        
        if not all([title, slug, author, category, date, read_time, excerpt, content]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        update_data = {
            "title": title,
            "slug": slug,
            "author": author,
            "category": category,
            "date": date,
            "readTime": read_time,
            "excerpt": excerpt,
            "content": content,
            "status": status,
            "featured": featured,
            "updated_at": datetime.now()
        }
        
        # Handle featured image
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                timestamp = int(datetime.now().timestamp())
                filename = f"guide_{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                update_data["featured_image"] = f"/static/uploads/{filename}"
        
        result = db.legal_guides.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Guide not found"}), 404
        
        # REAL-TIME: Broadcast guide update to all users
        try:
            update_data["_id"] = str(obj_id)
            socketio.emit('guide_updated', update_data, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting guide_updated event: {e}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating legal guide: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/legal-guides/delete/<guide_id>", methods=["DELETE"])
@require_admin_login
def delete_legal_guide(guide_id):
    """Delete legal guide"""
    try:
        try:
            obj_id = ObjectId(guide_id)
        except:
            return jsonify({"success": False, "error": "Invalid guide ID"}), 400
        
        deleted = db.legal_guides.find_one_and_delete({"_id": obj_id})

        if not deleted:
            return jsonify({"success": False, "error": "Guide not found"}), 404
        
        # REAL-TIME: Broadcast guide deletion to all users
        try:
            socketio.emit('guide_deleted', {"_id": str(obj_id)}, broadcast=True)
        except Exception as e:
            print(f"Error broadcasting guide_deleted event: {e}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting legal guide: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =========================
# ADD TESTIMONIAL
# =========================

@app.route("/admin/testimonials/add", methods=["POST"])
@require_admin_login
def add_testimonial():
    try:
        data = request.json or {}
        
        # Validate required fields
        name = data.get("name", "").strip()
        location = data.get("location", "").strip()
        testimonial = data.get("testimonial", "").strip()
        rating_str = str(data.get("rating", "")).strip()
        
        if not all([name, location, testimonial, rating_str]):
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        # Validate rating
        try:
            rating = int(rating_str)
            if rating < 1 or rating > 5:
                return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Rating must be a number"}), 400
        
        new_testimonial = {
            "name": name,
            "location": location,
            "rating": rating,
            "testimonial": testimonial,
            "property": data.get("property", "").strip(),
            "featured": False,
            "status": data.get("status", "draft"),
            "created_at": datetime.utcnow()
        }
        
        result = db.testimonials.insert_one(new_testimonial)
        
        # Broadcast to all users if published
        if new_testimonial["status"] == "published":
            try:
                new_testimonial["_id"] = str(result.inserted_id)
                socketio.emit('testimonial_added', new_testimonial, broadcast=True)
            except Exception as e:
                print(f"Socket.IO error: {e}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error adding testimonial: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# =========================
# UPDATE / DELETE / STREAM
# =========================

@app.route("/admin/testimonials/update/<id>", methods=["POST"])
@require_admin_login
def update_testimonial(id):
    try:
        data = request.json or {}
        
        # Validate ObjectId
        try:
            obj_id = ObjectId(id)
        except:
            return jsonify({"success": False, "error": "Invalid testimonial ID"}), 400
        
        # Validate rating if provided
        if "rating" in data:
            try:
                rating = int(data["rating"])
                if rating < 1 or rating > 5:
                    return jsonify({"success": False, "error": "Rating must be between 1 and 5"}), 400
                data["rating"] = rating
            except ValueError:
                return jsonify({"success": False, "error": "Rating must be a number"}), 400
        
        # Update in database
        result = testimonials.update_one(
            {"_id": obj_id},
            {"$set": data}
        )
        
        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Testimonial not found"}), 404
        
        # Get updated testimonial
        updated = testimonials.find_one({"_id": obj_id})
        if updated:
            updated["_id"] = str(updated["_id"])
            # Broadcast update to all users
            socketio.emit('testimonial_updated', updated, broadcast=True)
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error updating testimonial: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/admin/testimonials/delete/<id>", methods=["DELETE"])
@require_admin_login
def delete_testimonial(id):
    try:
        try:
            obj_id = ObjectId(id)
        except:
            return jsonify({"success": False, "error": "Invalid testimonial ID"}), 400
        
        result = testimonials.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            return jsonify({"success": False, "error": "Testimonial not found"}), 404
        
        # Broadcast deletion to all users
        socketio.emit('testimonial_deleted', {"_id": str(obj_id)}, broadcast=True)
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error deleting testimonial: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@require_admin_login
@app.route("/admin/testimonials/stream")
def testimonials_stream():
    def stream():
        last_count = 0
        while True:
            current = testimonials.count_documents({})
            if current != last_count:
                data = list(testimonials.find().sort("created_at", -1))
                for t in data:
                    t["_id"] = str(t["_id"])
                yield f"data:{json.dumps(data)}\n\n"
                last_count = current
            time.sleep(2)

    return Response(stream(), mimetype="text/event-stream")

# ============================
# APP RUN
# ============================

if __name__ == "__main__":
    # Use SocketIO's runner for websocket support
    # On Windows the Werkzeug reloader can cause "not a socket" errors
    # in background threads. Disable the reloader when running on Windows.
    use_reloader = False if platform.system().lower().startswith('win') else True
    socketio.run(app, host='127.0.0.1', port=5000, debug=True, use_reloader=use_reloader)
