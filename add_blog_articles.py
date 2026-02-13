"""
Script to add blog articles to the database
"""
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client["landvista"]

# Blog articles to insert
articles = [
    {
        "title": "Juja Farm: Prime Land Investment Opportunity Near Thika Superhighway",
        "slug": "juja-farm-prime-investment",
        "category": "Featured Locations",
        "author": "Sarah Mwangi",
        "date": "2024-12-14",
        "read_time": 6,
        "featured": True,
        "status": "published",
        "featured_image": "/static/images/blog1.jpg",
        "excerpt": "Nestled off the Thika Superhighway and just a short drive from Nairobi CBD, Juja Farm has rapidly evolved from a quiet agricultural area to one of Kenya's most sought-after land investment destinations.",
        "content": """Juja Farm: Prime Land Investment Opportunity Near Thika Superhighway

Nestled off the Thika Superhighway and just a short drive from Nairobi CBD, Juja Farm has rapidly evolved from a quiet agricultural area to one of Kenya's most sought-after land investment destinations. With improved infrastructure, proximity to key amenities, and rising residential demand, Juja Farm presents a compelling case for both first-time land buyers and seasoned investors seeking long-term capital growth.

Strategic Location and Road Accessibility

One of Juja Farm's biggest advantages is its strategic location along the Thika Superhighway, which offers smooth connectivity to Nairobi CBD, Ruiru, Thika Town, Juja Town, and the Jomo Kenyatta University of Agriculture and Technology (JKUAT). Recent road upgrades, such as the tarmacking of Juja Farm Road and improved bypass access points, have made travel more efficient and contributed to the region's growing appeal.

Accessible roads often correlate strongly with land value appreciation—and Juja Farm is a prime example. Improved connectivity has not only attracted new residents but also encouraged commercial development in retail, hospitality, and residential sectors.

Growing Residential Demand

As Nairobi expands outward and housing prices rise, more families and investors are seeking affordable and accessible land options. Juja Farm offers larger plots at competitive prices, making it attractive for homeowners building residential houses, developers constructing rental units, student housing investors, and buy-and-hold investors.

The area has seen gated communities, hostels, and rental developments, demonstrating the growing appetite for housing options within reach of Nairobi and its satellite towns.

Access to Amenities

Juja Farm benefits from easy access to a wide range of amenities, including primary and secondary schools, healthcare facilities, shopping centers, water and electricity access, and places of worship.

Land Appreciation and Investment Benefits

Over the past decade, Juja Farm has experienced significant land value appreciation driven by road and infrastructure development, population growth, demand for housing, and urban expansion away from Nairobi. Investors who purchased land earlier have already seen impressive returns.""",
        "created_at": datetime.now()
    },
    {
        "title": "Kithioko: Affordable Land Parcels in Machakos County",
        "slug": "kithioko-affordable-land",
        "category": "Featured Locations",
        "author": "James Kamau",
        "date": "2024-12-11",
        "read_time": 7,
        "featured": True,
        "status": "published",
        "featured_image": "/static/images/blog2.jpg",
        "excerpt": "Located in the southeastern region of Kenya, Kithioko has become one of Machakos County's most promising land investment zones — especially for buyers seeking affordability, clean documentation, and long-term value.",
        "content": """Kithioko: Affordable Land Parcels in Machakos County

Located in the southeastern region of Kenya, Kithioko has become one of Machakos County's most promising land investment zones — especially for buyers seeking affordability, clean documentation, and long-term value. As Nairobi and its satellite towns continue to expand, Kithioko's strategic position along key transport links has made it increasingly attractive to both residential and commercial investors.

Strategic Location and Accessibility

Kithioko is well situated with access to major road networks connecting the area to Machakos Town, Nairobi, Mombasa Road, Tala, Kangundo, Athi River, and surrounding commercial centers. This connectivity enhances the region's desirability for commuters, students, and businesses.

As ongoing road upgrades and county development initiatives continue to improve accessibility, properties in Kithioko are experiencing positive appreciation in value.

Affordable Land Prices and Flexible Payment Options

Compared to Nairobi and Kiambu, where land prices have seen steep increases, Kithioko remains affordable and accessible. LandVista emphasizes transparency, proper documentation, and payment flexibility—helping investors secure property at competitive rates.

Availability of Clean Title Deeds

One of the standout strengths of Kithioko is the availability of land with ready title deeds and documented ownership history. Buyers are encouraged to perform due diligence and partner with reputable land-selling firms to ensure transparency.""",
        "created_at": datetime.now()
    },
    {
        "title": "Kivandini: Strategic Location for Agricultural & Residential Development",
        "slug": "kivandini-agricultural-residential",
        "category": "Featured Locations",
        "author": "Grace Wanjiru",
        "date": "2024-12-09",
        "read_time": 5,
        "featured": True,
        "status": "published",
        "featured_image": "/static/images/blog3.jpg",
        "excerpt": "Situated within Machakos County, Kivandini has emerged as a high-potential region for land buyers seeking fertile agricultural land, residential opportunities, and long-term value appreciation.",
        "content": """Kivandini: Strategic Location for Agricultural & Residential Development

Situated within Machakos County, Kivandini has emerged as a high-potential region for land buyers seeking fertile agricultural land, residential opportunities, and long-term value appreciation. With expanding infrastructure, productive soils, and its proximity to key towns and highways, Kivandini offers a unique blend of rural investment appeal and modern accessibility.

Agricultural Potential and Fertile Soil

One of Kivandini's strongest advantages is its fertile soil, making it ideal for horticulture, subsistence farming, livestock rearing, and small-scale commercial crops. The region benefits from moderate rainfall and accessible water sources, supporting both traditional and modern agricultural ventures.

Strategic Location and Accessibility

Kivandini enjoys convenient access to major transport networks, linking it to Machakos Town, Thika, Nairobi, Matuu, and Tala. This strategic positioning supports both residential commuting and market access for farm produce.

Residential Growth & Community Development

Land buyers are increasingly considering Kivandini for affordable residential development due to its peaceful environment, growing amenities, and easy access to towns.

Clean Documentation & Title Deeds

LandVista prioritizes secure land ownership, and Kivandini shines due to properly surveyed and beaconed plots with verified documentation — offering buyers confidence and smooth transfer processes.

Long-Term Investment Potential

Kivandini's value appreciation is driven by county infrastructure improvements, agricultural viability, increasing residential demand, and proximity to growth towns.""",
        "created_at": datetime.now()
    }
]

# Insert articles
try:
    result = db.news.insert_many(articles)
    print(f"✅ Successfully inserted {len(result.inserted_ids)} blog articles!")
    for idx, article_id in enumerate(result.inserted_ids):
        print(f"   - {articles[idx]['title']}")
except Exception as e:
    print(f"❌ Error inserting articles: {e}")

client.close()
