#!/usr/bin/env python3
"""
Check news articles in database
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client["landvista"]

print("=" * 70)
print("📰 CHECKING NEWS ARTICLES IN DATABASE")
print("=" * 70)
print()

# Get all articles
all_articles = list(db.news.find())
print(f"Total articles in database: {len(all_articles)}")
print()

if len(all_articles) == 0:
    print("❌ No articles found in database!")
    print()
    print("Articles need to be created to display on the news page.")
    print()
else:
    # Group by status
    published = [a for a in all_articles if a.get("status") == "published"]
    drafts = [a for a in all_articles if a.get("status") == "draft"]
    
    print(f"Published articles: {len(published)}")
    print(f"Draft articles: {len(drafts)}")
    print()
    
    # Show articles
    for i, article in enumerate(all_articles, 1):
        print(f"{i}. {article.get('title', 'Untitled')}")
        print(f"   Status: {article.get('status', 'unknown')}")
        print(f"   Category: {article.get('category', 'N/A')}")
        print(f"   Author: {article.get('author', 'N/A')}")
        print()

print("=" * 70)
print("APIS TO CHECK:")
print("=" * 70)
print("Public (published only):   http://localhost:5000/api/news")
print("Admin (all articles):       http://localhost:5000/api/news/admin")
print()
