from app.database import Base, engine, SessionLocal
from app import models
from app.recommender import reindex_all_products

CATALOG = [
    # -- Footwear & Outdoor --
    ("Trail Runner 2.0", "Lightweight trail running shoe with aggressive grip and a breathable mesh upper, built for muddy technical terrain.", "Footwear", 118.00),
    ("Summit Hiking Boot", "Waterproof leather hiking boot with ankle support and a Vibram outsole for multi-day backpacking trips.", "Footwear", 189.00),
    ("Cloudwalk Sneaker", "Everyday cushioned sneaker with a knit upper, designed for all-day comfort on city streets.", "Footwear", 89.00),
    ("Alpine Insulated Boot", "Cozy winter boot rated to -25C with a removable felt liner, for deep snow and cold commutes.", "Footwear", 145.00),
    ("Studio Flex Trainer", "Low-profile cross-training shoe with a flat sole, built for weightlifting and studio classes.", "Footwear", 99.00),

    # -- Electronics --
    ("Pulse Wireless Earbuds", "True wireless earbuds with active noise cancellation and 30-hour battery life in the case.", "Electronics", 129.00),
    ("Aperture 4K Action Camera", "Rugged waterproof action camera with 4K60 video, image stabilization, and voice control.", "Electronics", 249.00),
    ("Nomad Power Bank 20K", "20,000mAh USB-C power bank with fast charging, enough for multiple phone charges on the go.", "Electronics", 39.00),
    ("Keystone Mechanical Keyboard", "Hot-swappable mechanical keyboard with tactile switches and per-key RGB lighting.", "Electronics", 109.00),
    ("Horizon Smart Watch", "Fitness smartwatch with heart-rate tracking, GPS, and a 7-day battery life.", "Electronics", 199.00),
    ("Drift Bluetooth Speaker", "Compact waterproof speaker with 360-degree sound and 12 hours of playback.", "Electronics", 59.00),
    ("Vector Laptop Stand", "Aluminum adjustable laptop stand that raises your screen to eye level for better posture.", "Electronics", 45.00),

    # -- Home & Kitchen --
    ("Ember Ceramic Mug Set", "Set of four hand-glazed ceramic mugs, dishwasher and microwave safe.", "Home & Kitchen", 34.00),
    ("Cascade Pour-Over Kettle", "Gooseneck kettle with precise temperature control for pour-over coffee brewing.", "Home & Kitchen", 65.00),
    ("Hearth Cast Iron Skillet", "Pre-seasoned 12-inch cast iron skillet that goes from stovetop to oven.", "Home & Kitchen", 42.00),
    ("Linen Weave Throw Blanket", "Soft cotton-linen throw blanket, woven in a breathable open-weave pattern.", "Home & Kitchen", 58.00),
    ("Aroma Diffuser Lamp", "Ultrasonic essential oil diffuser with a warm ambient LED light and auto shut-off.", "Home & Kitchen", 36.00),
    ("Meridian Chef's Knife", "8-inch forged high-carbon steel chef's knife with a balanced walnut handle.", "Home & Kitchen", 79.00),

    # -- Apparel --
    ("Alloy Merino Base Layer", "Odor-resistant merino wool base layer top, warm without overheating during activity.", "Apparel", 68.00),
    ("Fieldnote Flannel Shirt", "Brushed cotton flannel shirt with a relaxed fit, soft after every wash.", "Apparel", 54.00),
    ("Ridgeline Softshell Jacket", "Windproof and water-resistant softshell jacket built for cold-weather hikes.", "Apparel", 138.00),
    ("Everyday Jogger Pant", "Tapered fleece jogger with a stretch waistband, made for lounging or light training.", "Apparel", 49.00),
    ("Prairie Wool Beanie", "Ribbed wool-blend beanie that holds its shape and keeps ears covered in winter wind.", "Apparel", 22.00),
    ("Traverse Packable Vest", "Ultralight down vest that packs into its own pocket for travel.", "Apparel", 84.00),

    # -- Books --
    ("Atlas of Forgotten Rivers", "A travel memoir following disappearing waterways across three continents.", "Books", 19.00),
    ("The Algorithmic Mind", "An accessible tour of machine learning concepts, written for curious non-specialists.", "Books", 24.00),
    ("Kitchen Chemistry", "A cookbook explaining the science behind everyday cooking techniques.", "Books", 28.00),
    ("Quiet Mountains", "A poetry collection about solitude, weather, and long walks.", "Books", 15.00),
    ("Founders at Dawn", "A narrative history of five startups that shaped the last decade of tech.", "Books", 22.00),

    # -- Sports & Fitness --
    ("Coil Adjustable Dumbbell Set", "Space-saving dumbbells that adjust from 5 to 50 lbs with a twist of the dial.", "Sports & Fitness", 299.00),
    ("Balance Cork Yoga Mat", "Non-slip cork-topped yoga mat with natural grip that improves when damp.", "Sports & Fitness", 68.00),
    ("Momentum Jump Rope", "Ball-bearing speed rope with a weighted handle for cardio and double-unders.", "Sports & Fitness", 24.00),
    ("Anchor Resistance Band Set", "Five-band resistance set with a door anchor for full-body strength training anywhere.", "Sports & Fitness", 32.00),
    ("Glide Foam Roller", "High-density foam roller for post-workout muscle recovery and mobility work.", "Sports & Fitness", 29.00),
    ("Basecamp Insulated Bottle", "Vacuum-insulated steel bottle that keeps drinks cold for 24 hours or hot for 12.", "Sports & Fitness", 38.00),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Product).count() > 0:
            print("Products already exist - skipping catalog insert (still reindexing embeddings).")
        else:
            for i, (name, description, category, price) in enumerate(CATALOG, start=1):
                db.add(models.Product(
                    name=name,
                    description=description,
                    category=category,
                    price=price,
                    image_seed=f"product-{i}",
                    stock=50,
                ))
            db.commit()
            print(f"Inserted {len(CATALOG)} products.")

        count = reindex_all_products(db)
        print(f"Computed embeddings for {count} products.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
