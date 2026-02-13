#!/usr/bin/env python3
"""Check if articles exist in database"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'), tlsAllowInvalidCertificates=True)
db = client['landvista']

# Check articles
articles = list(db.news.find().sort('created_at', -1))
print(f'Total articles in database: {len(articles)}')
print()

if articles:
    for i, article in enumerate(articles, 1):
        print(f'{i}. {article.get("title", "No title")}')
        print(f'   Status: {article.get("status", "N/A")}')
        print(f'   Author: {article.get("author", "N/A")}')
        print()
else:
    print('No articles found in database!')
    print()
    print('To create an article:')
    print('1. Go to http://localhost:5000/admin/news')
    print('2. Click "+ Create New Article"')
    print('3. Fill in the form and click Save')
