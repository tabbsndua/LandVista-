#!/usr/bin/env python3
"""
Add sample legal guides to MongoDB
"""

import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/landvista")
client = MongoClient(MONGO_URI)
db = client.get_default_database()

legal_guides = [
    {
        "title": "Understanding Land Title Deeds in Kenya",
        "slug": "understanding-land-title-deeds",
        "author": "Lucy Njeri",
        "category": "Documentation",
        "excerpt": "A comprehensive guide to understanding land ownership documentation in Kenya, including freehold, leasehold, and customary lands.",
        "content": """
<h2>What are Land Title Deeds?</h2>
<p>A land title deed is a legal document that proves ownership of a piece of land. In Kenya, land titles are issued by the Ministry of Lands and Physical Planning.</p>

<h3>Types of Land Ownership in Kenya</h3>
<ul>
<li><strong>Freehold Land:</strong> Land owned in perpetuity with no annual rent</li>
<li><strong>Leasehold Land:</strong> Land leased for a specific period (typically 99 years)</li>
<li><strong>Customary Land:</strong> Land held under customary law and practice</li>
<li><strong>Community Land:</strong> Held in trust for community members</li>
</ul>

<h2>How to Verify Land Ownership</h2>
<p>Always verify land ownership through the Land Registry Office before making any purchase. You can request a search certificate which shows the current owner and any encumbrances on the property.</p>

<h2>Common Land Disputes</h2>
<p>Land disputes often arise from unclear boundaries, duplicate titles, or forged documents. It's crucial to conduct proper due diligence.</p>
        """,
        "date": "2024-01-15",
        "read_time": 8,
        "status": "published",
        "featured": True,
        "featured_image": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "title": "Steps to Register Property in Your Name",
        "slug": "steps-to-register-property",
        "author": "John Kamau",
        "category": "Legal Process",
        "excerpt": "Learn the step-by-step process of registering property ownership in Kenya, including required documents and timelines.",
        "content": """
<h2>Property Registration Process</h2>
<p>Registering property in your name is essential to protect your ownership rights. Here's how to do it:</p>

<h3>Step 1: Conduct a Property Search</h3>
<p>Before purchasing, conduct a search at the Land Registry to verify the seller's ownership and check for any encumbrances.</p>

<h3>Step 2: Prepare Required Documents</h3>
<ul>
<li>Original title deed of the seller</li>
<li>Clearance certificate from the local authority</li>
<li>Letter of recommendation from your lender (if financing)</li>
<li>Identification documents (ID/Passport)</li>
<li>Signed sale agreement</li>
</ul>

<h3>Step 3: Submit Application</h3>
<p>Submit your application to the Land Registry office with all required documents. Processing typically takes 60-90 days.</p>

<h3>Step 4: Pay Transfer Fees</h3>
<p>Pay the required stamp duty and transfer fees as per the current rates set by the government.</p>

<h3>Step 5: Receive New Title Deed</h3>
<p>Once processed, collect your new title deed from the Land Registry office.</p>
        """,
        "date": "2024-02-10",
        "read_time": 10,
        "status": "published",
        "featured": True,
        "featured_image": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "title": "Property Tax and Compliance Requirements",
        "slug": "property-tax-compliance",
        "author": "Sarah Mwangi",
        "category": "Compliance",
        "excerpt": "Understanding your tax obligations and compliance requirements as a property owner in Kenya.",
        "content": """
<h2>Property Owner Taxes in Kenya</h2>
<p>As a property owner in Kenya, you have several tax obligations that must be met annually.</p>

<h3>Main Property Taxes</h3>
<ul>
<li><strong>Property Tax (Rates):</strong> Paid annually to the local county government</li>
<li><strong>Income Tax:</strong> On rental income from the property</li>
<li><strong>Stamp Duty:</strong> Paid during property transfer</li>
<li><strong>Land Transfer Tax:</strong> Calculated on the property value</li>
</ul>

<h2>Property Tax Calculation</h2>
<p>Property tax rates vary by county and location. Contact your county government office for the specific rates applicable to your property.</p>

<h2>Important Compliance Deadlines</h2>
<ul>
<li>Annual property tax returns must be filed and paid by June 30</li>
<li>Income tax returns for rental income by June 30</li>
<li>Maintain updated property documentation and insurance</li>
</ul>

<h2>Consequences of Non-Compliance</h2>
<p>Failure to pay property taxes can result in penalties, interest charges, and potential auction of the property.</p>
        """,
        "date": "2024-02-20",
        "read_time": 7,
        "status": "published",
        "featured": False,
        "featured_image": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "title": "Landlord and Tenant Rights in Kenya",
        "slug": "landlord-tenant-rights",
        "author": "Peter Kipchoge",
        "category": "Property Rights",
        "excerpt": "A guide to understanding the rights and responsibilities of landlords and tenants under Kenyan law.",
        "content": """
<h2>Landlord and Tenant Act</h2>
<p>The Landlord and Tenant Act in Kenya provides the legal framework governing rental relationships between property owners and tenants.</p>

<h3>Tenant Rights</h3>
<ul>
<li>Right to peaceful enjoyment of the property</li>
<li>Protection against arbitrary eviction</li>
<li>Right to a written lease agreement</li>
<li>Protection against unlawful increases in rent</li>
<li>Right to maintenance of the property</li>
</ul>

<h3>Landlord Responsibilities</h3>
<ul>
<li>Provide a habitable property</li>
<li>Make necessary repairs within reasonable time</li>
<li>Maintain structural integrity</li>
<li>Provide safe water and sanitation</li>
<li>Not unlawfully evict tenants</li>
</ul>

<h2>Eviction Process</h2>
<p>A landlord must follow proper legal procedures for eviction, including providing written notice and obtaining a court order. Unlawful eviction is punishable by law.</p>

<h2>Dispute Resolution</h2>
<p>Disputes between landlords and tenants can be resolved through negotiation, mediation, or court proceedings.</p>
        """,
        "date": "2024-03-05",
        "read_time": 9,
        "status": "published",
        "featured": True,
        "featured_image": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

# Insert guides
try:
    result = db.legal_guides.insert_many(legal_guides)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} legal guides!")
    for i, guide in enumerate(legal_guides, 1):
        print(f"   {i}. {guide['title']}")
except Exception as e:
    print(f"❌ Error inserting guides: {e}")
