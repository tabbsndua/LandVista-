# 💻 EXACT CODE TO ADD - COPY & PASTE READY

## 📋 FILE: app.py

### Addition 1: Add Legal Guides Public Route

**Location:** After the `@app.route("/news")` function (around line 250)

```python
@app.route("/legal-guides")
def legal_guides_page():
    """Legal Guides page - show published legal guides"""
    guides = list(db.legal_guides.find({"status": "published"}).sort("created_at", -1))
    for g in guides:
        g["_id"] = str(g["_id"])
    return render_template("legal_guides.html", guides=guides)
```

---

### Addition 2: Add Article Detail Route

**Location:** After legal_guides_page function

```python
@app.route("/news/<slug>")
def article_detail(slug):
    """Display single news article"""
    article = db.news.find_one({"slug": slug, "status": "published"})
    if not article:
        return render_template("404.html"), 404
    article["_id"] = str(article["_id"])
    return render_template("article_detail.html", article=article)
```

---

### Addition 3: Add Guide Detail Route

**Location:** After article_detail function

```python
@app.route("/legal-guides/<slug>")
def guide_detail(slug):
    """Display single legal guide"""
    guide = db.legal_guides.find_one({"slug": slug, "status": "published"})
    if not guide:
        return render_template("404.html"), 404
    guide["_id"] = str(guide["_id"])
    return render_template("guide_detail.html", guide=guide)
```

---

### Addition 4: Add Socket.IO Broadcasting to add_news_article()

**Location:** In `add_news_article()` function, just before `return jsonify({"success": True, "_id": str(result.inserted_id)})`

```python
        # Broadcast to all connected clients
        try:
            socketio.emit('news_added', {
                "_id": str(result.inserted_id),
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
                "featured": featured
            }, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

### Addition 5: Add Socket.IO Broadcasting to update_news_article()

**Location:** In `update_news_article()` function, just before `return jsonify({"success": True})`

```python
        # Broadcast update to all connected clients
        try:
            socketio.emit('news_updated', {
                "_id": article_id,
                "title": title,
                "slug": slug,
                "author": author,
                "category": category,
                "date": date,
                "readTime": read_time,
                "excerpt": excerpt,
                "content": content,
                "status": status,
                "featured": featured
            }, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

### Addition 6: Add Socket.IO Broadcasting to delete_news_article()

**Location:** In `delete_news_article()` function, just before `return jsonify({"success": True})`

```python
        # Broadcast deletion to all connected clients
        try:
            socketio.emit('news_deleted', {"_id": article_id}, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

### Addition 7: Add Socket.IO Broadcasting to add_legal_guide()

**Location:** In `add_legal_guide()` function, just before `return jsonify({"success": True, "_id": str(result.inserted_id)})`

```python
        # Broadcast to all connected clients
        try:
            socketio.emit('guide_added', {
                "_id": str(result.inserted_id),
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
                "featured": featured
            }, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

### Addition 8: Add Socket.IO Broadcasting to update_legal_guide()

**Location:** In `update_legal_guide()` function, just before `return jsonify({"success": True})`

```python
        # Broadcast update to all connected clients
        try:
            socketio.emit('guide_updated', {
                "_id": guide_id,
                "title": title,
                "slug": slug,
                "author": author,
                "category": category,
                "date": date,
                "readTime": read_time,
                "excerpt": excerpt,
                "content": content,
                "status": status,
                "featured": featured
            }, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

### Addition 9: Add Socket.IO Broadcasting to delete_legal_guide()

**Location:** In `delete_legal_guide()` function, just before `return jsonify({"success": True})`

```python
        # Broadcast deletion to all connected clients
        try:
            socketio.emit('guide_deleted', {"_id": guide_id}, broadcast=True)
        except Exception as e:
            print(f"Socket.IO broadcast error: {e}")
```

---

## 📋 FILE: templates/news.html

### Addition 1: Add Socket.IO Listeners

**Location:** Just before `{% endblock %}` at the very end of the file

```html
<script src="/socket.io/socket.io.js"></script>
<script>
// Real-time news updates via Socket.IO
let __news_socket = null;
try {
    if (typeof io !== 'undefined') {
        __news_socket = io();
        __news_socket.on('connect', () => console.log('News socket connected'));
        
        // Listen for new articles
        __news_socket.on('news_added', function(article) {
            console.log('New article added:', article.title);
            // Reload articles from API
            fetch('/api/news')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('articlesContainer');
                    if (data.length === 0) {
                        container.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; color: #6b7280; padding: 40px;">No articles available yet.</p>';
                        return;
                    }
                    
                    container.innerHTML = data.map(article => `
                        <article class="blog-card">
                            ${article.featured_image ? `<img src="${article.featured_image}" alt="${article.title}">` : '<div style="width: 100%; height: 250px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; font-weight: bold;">📰</div>'}
                            <div class="blog-content">
                                <div class="metadata">
                                    <span>📅 ${article.date}</span>
                                    <span>• ${article.readTime} min read</span>
                                </div>
                                <button class="category-tag">${article.category}</button>
                                <h3>${article.title}</h3>
                                <p>${article.excerpt}</p>
                                <div class="blog-footer">
                                    <span class="author">✍️ ${article.author}</span>
                                    <a href="/news/${article.slug}" class="read-more">Read Article →</a>
                                </div>
                            </div>
                        </article>
                    `).join('');
                })
                .catch(err => console.error('Error loading articles:', err));
        });
        
        // Listen for updated articles
        __news_socket.on('news_updated', function(article) {
            console.log('Article updated:', article.title);
            // Reload articles
            location.reload();
        });
        
        // Listen for deleted articles
        __news_socket.on('news_deleted', function(data) {
            console.log('Article deleted');
            // Reload articles
            location.reload();
        });
    }
} catch (e) {
    console.warn('Socket.IO not available:', e);
}
</script>
```

---

### Addition 2: Change Read More Links for Database Articles

**Location:** In the article loop (around line 35-40), change:

**FROM:**
```html
<a href="#" class="read-more">Read Article →</a>
```

**TO:**
```html
<a href="/news/{{ article.slug }}" class="read-more">Read Article →</a>
```

---

## 📋 FILE: templates/legal_guides.html (NEW FILE)

**Create new file:** `templates/legal_guides.html`

```html
{% extends "base.html" %} 

{% block title %}Legal Guides | LandVista{% endblock %}

{% block content %}

<!-- =========================
   HERO SECTION
========================= -->
<section class="news-hero">
    <div class="news-hero-overlay"></div>
    <div class="news-hero-content">
        <h1>Legal Guides</h1>
        <p>Expert guidance on land ownership and property law</p>
    </div>
</section>

<div class="curve-divider"></div>

<!-- =========================
   FEATURED GUIDES
========================= -->
<section class="featured-articles container">
    <div class="section-title">
        <h2>Latest Legal Guides</h2>
    </div>

    <div class="articles-grid" id="guidesContainer">
        <!-- Guides will be loaded here -->
        {% if guides %}
            {% for guide in guides %}
            <article class="blog-card">
                {% if guide.featured_image %}
                    <img src="{{ guide.featured_image }}" alt="{{ guide.title }}">
                {% else %}
                    <div style="width: 100%; height: 250px; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; font-weight: bold;">
                        ⚖️
                    </div>
                {% endif %}
                <div class="blog-content">
                    <div class="metadata">
                        <span>📅 {{ guide.date }}</span>
                        <span>• {{ guide.readTime }} min read</span>
                    </div>
                    <button class="category-tag">{{ guide.category }}</button>
                    <h3>{{ guide.title }}</h3>
                    <p>{{ guide.excerpt }}</p>
                    <div class="blog-footer">
                        <span class="author">✍️ {{ guide.author }}</span>
                        <a href="/legal-guides/{{ guide.slug }}" class="read-more">Read Guide →</a>
                    </div>
                </div>
            </article>
            {% endfor %}
        {% else %}
            <p style="grid-column: 1 / -1; text-align: center; color: #6b7280; padding: 40px;">No guides available yet.</p>
        {% endif %}
    </div>
</section>

<!-- =========================
   NEWSLETTER SECTION
========================= -->
<section class="newsletter-section">
    <div class="newsletter-container">
        <div class="newsletter-content">
            <h2>Stay Updated</h2>
            <p>Subscribe to our newsletter and get the latest legal guides delivered to your inbox.</p>

            <form class="newsletter-form" method="POST" action="/subscribe-newsletter">
                <input type="text" name="email" placeholder="Enter your email address" required>
                <button type="submit">Subscribe Now</button>
            </form>

            <p class="sub-count">✓ Join 5,000+ investors getting weekly insights</p>
        </div>
    </div>
</section>

<script src="/socket.io/socket.io.js"></script>
<script>
// Real-time legal guides updates via Socket.IO
let __guides_socket = null;
try {
    if (typeof io !== 'undefined') {
        __guides_socket = io();
        __guides_socket.on('connect', () => console.log('Legal guides socket connected'));
        
        // Listen for new guides
        __guides_socket.on('guide_added', function(guide) {
            console.log('New guide added:', guide.title);
            // Reload guides
            fetch('/api/legal-guides')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('guidesContainer');
                    if (data.length === 0) {
                        container.innerHTML = '<p style="grid-column: 1 / -1; text-align: center; color: #6b7280; padding: 40px;">No guides available yet.</p>';
                        return;
                    }
                    
                    container.innerHTML = data.map(guide => `
                        <article class="blog-card">
                            ${guide.featured_image ? `<img src="${guide.featured_image}" alt="${guide.title}">` : '<div style="width: 100%; height: 250px; background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; font-weight: bold;">⚖️</div>'}
                            <div class="blog-content">
                                <div class="metadata">
                                    <span>📅 ${guide.date}</span>
                                    <span>• ${guide.readTime} min read</span>
                                </div>
                                <button class="category-tag">${guide.category}</button>
                                <h3>${guide.title}</h3>
                                <p>${guide.excerpt}</p>
                                <div class="blog-footer">
                                    <span class="author">✍️ ${guide.author}</span>
                                    <a href="/legal-guides/${guide.slug}" class="read-more">Read Guide →</a>
                                </div>
                            </div>
                        </article>
                    `).join('');
                })
                .catch(err => console.error('Error loading guides:', err));
        });
        
        // Listen for updated guides
        __guides_socket.on('guide_updated', function(guide) {
            console.log('Guide updated:', guide.title);
            location.reload();
        });
        
        // Listen for deleted guides
        __guides_socket.on('guide_deleted', function(data) {
            console.log('Guide deleted');
            location.reload();
        });
    }
} catch (e) {
    console.warn('Socket.IO not available:', e);
}
</script>

{% endblock %}
```

---

## 📋 FILE: templates/article_detail.html (NEW FILE)

**Create new file:** `templates/article_detail.html`

```html
{% extends "base.html" %}

{% block title %}{{ article.title }} | LandVista{% endblock %}

{% block content %}

<div class="article-detail-page">
    <!-- Hero Section -->
    <section class="article-hero">
        {% if article.featured_image %}
            <img src="{{ article.featured_image }}" alt="{{ article.title }}" class="hero-image">
        {% else %}
            <div class="hero-image-placeholder" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"></div>
        {% endif %}
        
        <div class="article-hero-overlay">
            <div class="article-hero-content">
                <span class="category-tag">{{ article.category }}</span>
                <h1>{{ article.title }}</h1>
                <div class="article-meta">
                    <span>📅 {{ article.date }}</span>
                    <span>✍️ {{ article.author }}</span>
                    <span>⏱️ {{ article.readTime }} min read</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Main Content -->
    <section class="article-content-section container">
        <div class="article-wrapper">
            <article class="article-body">
                <div class="article-excerpt">
                    <p class="lead">{{ article.excerpt }}</p>
                </div>

                <div class="article-content" style="line-height: 1.8; color: #333; font-size: 16px; word-wrap: break-word; white-space: pre-wrap;">
                    {{ article.content }}
                </div>

                <div class="article-footer">
                    <p>
                        <strong>About the author:</strong><br>
                        {{ article.author }} is a content contributor at LandVista Properties, sharing insights on land investment and property management.
                    </p>
                </div>
            </article>

            <!-- Sidebar -->
            <aside class="article-sidebar">
                <div class="sidebar-card">
                    <h3>Share This Article</h3>
                    <div class="share-buttons">
                        <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.url }}" target="_blank" class="share-btn facebook">f</a>
                        <a href="https://twitter.com/intent/tweet?url={{ request.url }}&text={{ article.title }}" target="_blank" class="share-btn twitter">𝕏</a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={{ request.url }}" target="_blank" class="share-btn linkedin">in</a>
                    </div>
                </div>

                <div class="sidebar-card">
                    <h3>Article Info</h3>
                    <p><strong>Category:</strong> {{ article.category }}</p>
                    <p><strong>Published:</strong> {{ article.date }}</p>
                    <p><strong>Author:</strong> {{ article.author }}</p>
                </div>

                <div class="sidebar-card cta">
                    <h3>Need More Info?</h3>
                    <p>Contact our team for personalized advice on land investment.</p>
                    <a href="/contact" class="btn-primary">Get in Touch</a>
                </div>
            </aside>
        </div>
    </section>

    <!-- Related Articles -->
    <section class="related-articles container">
        <h2>More Articles</h2>
        <div class="articles-grid" id="relatedContainer">
            <!-- Will load related articles here -->
        </div>
    </section>
</div>

<style>
.article-detail-page {
    min-height: 100vh;
}

.article-hero {
    position: relative;
    height: 400px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hero-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
}

.hero-image-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
}

.article-hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
}

.article-hero-content {
    text-align: center;
    color: white;
}

.article-hero-content h1 {
    font-size: 2.5rem;
    margin: 15px 0;
    max-width: 800px;
}

.article-meta {
    display: flex;
    gap: 20px;
    justify-content: center;
    font-size: 14px;
}

.article-content-section {
    padding: 60px 20px;
}

.article-wrapper {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 40px;
    max-width: 1000px;
    margin: 0 auto;
}

.article-body {
    font-size: 16px;
    line-height: 1.8;
}

.article-excerpt {
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
    border-left: 4px solid #0a3c28;
    padding-left: 20px;
}

.article-content {
    margin: 30px 0;
}

.article-footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
    color: #666;
}

.sidebar-card {
    background: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.sidebar-card h3 {
    color: #0a3c28;
    margin-bottom: 15px;
}

.share-buttons {
    display: flex;
    gap: 10px;
}

.share-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    color: white;
    text-decoration: none;
    font-weight: bold;
    transition: transform 0.2s;
}

.share-btn:hover {
    transform: scale(1.1);
}

.share-btn.facebook {
    background: #1877f2;
}

.share-btn.twitter {
    background: #000;
}

.share-btn.linkedin {
    background: #0a66c2;
}

.sidebar-card.cta {
    background: linear-gradient(135deg, #0a3c28 0%, #0f5d3f 100%);
    color: white;
}

.sidebar-card.cta h3 {
    color: white;
}

.btn-primary {
    display: block;
    background: white;
    color: #0a3c28;
    padding: 10px 20px;
    border-radius: 5px;
    text-align: center;
    text-decoration: none;
    font-weight: bold;
    margin-top: 15px;
}

.related-articles {
    padding: 60px 20px;
    background: #f9fafb;
}

.related-articles h2 {
    margin-bottom: 40px;
    color: #0a3c28;
}

.articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
}

@media (max-width: 768px) {
    .article-wrapper {
        grid-template-columns: 1fr;
    }

    .article-hero-content h1 {
        font-size: 1.8rem;
    }

    .article-meta {
        flex-direction: column;
        gap: 10px;
    }
}
</style>

<script>
// Load related articles
function loadRelatedArticles() {
    fetch('/api/news')
        .then(response => response.json())
        .then(data => {
            const filtered = data.filter(a => a.category === '{{ article.category }}').slice(0, 3);
            const container = document.getElementById('relatedContainer');
            container.innerHTML = filtered.map(article => `
                <article class="blog-card">
                    <img src="${article.featured_image || 'https://via.placeholder.com/300x200'}" alt="${article.title}">
                    <div class="blog-content">
                        <h3>${article.title}</h3>
                        <p>${article.excerpt}</p>
                        <div class="blog-footer">
                            <span class="author">✍️ ${article.author}</span>
                            <a href="/news/${article.slug}" class="read-more">Read →</a>
                        </div>
                    </div>
                </article>
            `).join('');
        })
        .catch(err => console.error('Error loading related:', err));
}

loadRelatedArticles();
</script>

{% endblock %}
```

---

## 📋 FILE: templates/guide_detail.html (NEW FILE)

**Create new file:** `templates/guide_detail.html`

```html
{% extends "base.html" %}

{% block title %}{{ guide.title }} | LandVista{% endblock %}

{% block content %}

<div class="guide-detail-page">
    <!-- Hero Section -->
    <section class="guide-hero">
        {% if guide.featured_image %}
            <img src="{{ guide.featured_image }}" alt="{{ guide.title }}" class="hero-image">
        {% else %}
            <div class="hero-image-placeholder" style="background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);"></div>
        {% endif %}
        
        <div class="guide-hero-overlay">
            <div class="guide-hero-content">
                <span class="category-tag legal-tag">{{ guide.category }}</span>
                <h1>{{ guide.title }}</h1>
                <div class="guide-meta">
                    <span>⚖️ Legal Guide</span>
                    <span>📅 {{ guide.date }}</span>
                    <span>✍️ {{ guide.author }}</span>
                    <span>⏱️ {{ guide.readTime }} min read</span>
                </div>
            </div>
        </div>
    </section>

    <!-- Main Content -->
    <section class="guide-content-section container">
        <div class="guide-wrapper">
            <article class="guide-body">
                <div class="guide-excerpt">
                    <p class="lead">{{ guide.excerpt }}</p>
                </div>

                <div class="guide-content" style="line-height: 1.8; color: #333; font-size: 16px; word-wrap: break-word; white-space: pre-wrap;">
                    {{ guide.content }}
                </div>

                <div class="important-notice">
                    <h3>⚠️ Legal Disclaimer</h3>
                    <p>This guide is for informational purposes only and does not constitute legal advice. Please consult with a qualified legal professional before making any property-related decisions.</p>
                </div>

                <div class="guide-footer">
                    <p>
                        <strong>About the author:</strong><br>
                        {{ guide.author }} is a legal expert at LandVista Properties, providing guidance on property law and land investment.
                    </p>
                </div>
            </article>

            <!-- Sidebar -->
            <aside class="guide-sidebar">
                <div class="sidebar-card">
                    <h3>Share This Guide</h3>
                    <div class="share-buttons">
                        <a href="https://www.facebook.com/sharer/sharer.php?u={{ request.url }}" target="_blank" class="share-btn facebook">f</a>
                        <a href="https://twitter.com/intent/tweet?url={{ request.url }}&text={{ guide.title }}" target="_blank" class="share-btn twitter">𝕏</a>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={{ request.url }}" target="_blank" class="share-btn linkedin">in</a>
                    </div>
                </div>

                <div class="sidebar-card">
                    <h3>Guide Info</h3>
                    <p><strong>Category:</strong> {{ guide.category }}</p>
                    <p><strong>Published:</strong> {{ guide.date }}</p>
                    <p><strong>Author:</strong> {{ guide.author }}</p>
                </div>

                <div class="sidebar-card cta">
                    <h3>Need Legal Assistance?</h3>
                    <p>Our team can help with all your property legal needs.</p>
                    <a href="/contact" class="btn-primary">Contact Us</a>
                </div>
            </aside>
        </div>
    </section>

    <!-- Related Guides -->
    <section class="related-guides container">
        <h2>More Legal Guides</h2>
        <div class="guides-grid" id="relatedContainer">
            <!-- Will load related guides here -->
        </div>
    </section>
</div>

<style>
.guide-detail-page {
    min-height: 100vh;
}

.guide-hero {
    position: relative;
    height: 400px;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.hero-image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 0;
}

.hero-image-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
}

.guide-hero-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
}

.guide-hero-content {
    text-align: center;
    color: white;
}

.guide-hero-content h1 {
    font-size: 2.5rem;
    margin: 15px 0;
    max-width: 800px;
}

.legal-tag {
    background: #06b6d4;
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    display: inline-block;
}

.guide-meta {
    display: flex;
    gap: 20px;
    justify-content: center;
    font-size: 14px;
    margin-top: 15px;
}

.guide-content-section {
    padding: 60px 20px;
}

.guide-wrapper {
    display: grid;
    grid-template-columns: 1fr 300px;
    gap: 40px;
    max-width: 1000px;
    margin: 0 auto;
}

.guide-body {
    font-size: 16px;
    line-height: 1.8;
}

.guide-excerpt {
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
    border-left: 4px solid #06b6d4;
    padding-left: 20px;
}

.guide-content {
    margin: 30px 0;
}

.important-notice {
    background: #fef3c7;
    border-left: 4px solid #f59e0b;
    padding: 20px;
    border-radius: 5px;
    margin: 30px 0;
}

.important-notice h3 {
    color: #d97706;
    margin-bottom: 10px;
}

.guide-footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #e5e7eb;
    color: #666;
}

.sidebar-card {
    background: #f9fafb;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.sidebar-card h3 {
    color: #0a3c28;
    margin-bottom: 15px;
}

.share-buttons {
    display: flex;
    gap: 10px;
}

.share-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    color: white;
    text-decoration: none;
    font-weight: bold;
    transition: transform 0.2s;
}

.share-btn:hover {
    transform: scale(1.1);
}

.share-btn.facebook {
    background: #1877f2;
}

.share-btn.twitter {
    background: #000;
}

.share-btn.linkedin {
    background: #0a66c2;
}

.sidebar-card.cta {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    color: white;
}

.sidebar-card.cta h3 {
    color: white;
}

.btn-primary {
    display: block;
    background: white;
    color: #06b6d4;
    padding: 10px 20px;
    border-radius: 5px;
    text-align: center;
    text-decoration: none;
    font-weight: bold;
    margin-top: 15px;
}

.related-guides {
    padding: 60px 20px;
    background: #f9fafb;
}

.related-guides h2 {
    margin-bottom: 40px;
    color: #0a3c28;
}

.guides-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
}

@media (max-width: 768px) {
    .guide-wrapper {
        grid-template-columns: 1fr;
    }

    .guide-hero-content h1 {
        font-size: 1.8rem;
    }

    .guide-meta {
        flex-direction: column;
        gap: 10px;
    }
}
</style>

<script>
// Load related guides
function loadRelatedGuides() {
    fetch('/api/legal-guides')
        .then(response => response.json())
        .then(data => {
            const filtered = data.filter(g => g.category === '{{ guide.category }}').slice(0, 3);
            const container = document.getElementById('relatedContainer');
            container.innerHTML = filtered.map(guide => `
                <article class="blog-card">
                    <img src="${guide.featured_image || 'https://via.placeholder.com/300x200'}" alt="${guide.title}">
                    <div class="blog-content">
                        <h3>${guide.title}</h3>
                        <p>${guide.excerpt}</p>
                        <div class="blog-footer">
                            <span class="author">✍️ ${guide.author}</span>
                            <a href="/legal-guides/${guide.slug}" class="read-more">Read →</a>
                        </div>
                    </div>
                </article>
            `).join('');
        })
        .catch(err => console.error('Error loading related:', err));
}

loadRelatedGuides();
</script>

{% endblock %}
```

---

## ✅ SUMMARY OF CHANGES

**Total files to modify:** 2  
**Total files to create:** 3  
**Total lines of code:** ~800  
**Estimated time:** 2-3 hours  

### Files to Modify:
1. `app.py` - Add 9 additions
2. `templates/news.html` - Add 2 additions

### Files to Create:
1. `templates/legal_guides.html` - New file
2. `templates/article_detail.html` - New file
3. `templates/guide_detail.html` - New file

---

**IMPLEMENTATION TIP:** Copy and paste this code section by section. Test after each addition to catch any issues early!
