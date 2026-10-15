# Curated realistic synthetic dataset for college database technology assessment
# 35 products across 5 categories with rich semantic descriptions

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Books",
    "Home Appliances",
    "Sports Equipment"
]

SAMPLE_PRODUCTS = [
    # Electronics (7)
    {
        "product_name": "Active Wireless Noise-Cancelling Headphones",
        "category": "Electronics",
        "description": "Over-ear Bluetooth headphones with active noise cancellation, 30-hour battery life, built-in microphone, and compact foldable design. Ideal affordable audio gear for frequent travelling, flights, and noisy office commutes.",
        "price": 79.99,
        "stock_quantity": 45
    },
    {
        "product_name": "Ultrabook 14-inch Developer Laptop",
        "category": "Electronics",
        "description": "Lightweight portable laptop featuring Intel Core i7 processor, 16GB RAM, 512GB SSD, backlit keyboard, and full HD display. Perfect for university students, software engineers, and programming on the go.",
        "price": 899.00,
        "stock_quantity": 20
    },
    {
        "product_name": "Ergonomic RGB Mechanical Gaming Keyboard",
        "category": "Electronics",
        "description": "Tenkeyless mechanical keyboard with customizable RGB backlighting, tactile blue switches, detachable USB-C cable, and anti-ghosting keys for high-speed typing and competitive gaming.",
        "price": 49.50,
        "stock_quantity": 60
    },
    {
        "product_name": "Smart Fitness Tracker Watch",
        "category": "Electronics",
        "description": "Waterproof fitness smart band featuring heart rate monitor, sleep tracking, step counter, AMOLED color touch screen, and 14-day battery life for athletic workouts.",
        "price": 39.99,
        "stock_quantity": 85
    },
    {
        "product_name": "USB-C Multiport Hub 7-in-1 Adapter",
        "category": "Electronics",
        "description": "Aluminum docking dongle with 4K HDMI output, 100W Power Delivery pass-through, SD card reader, and three USB 3.0 ports for modern thin laptops and tablets.",
        "price": 28.00,
        "stock_quantity": 110
    },
    {
        "product_name": "Portable Waterproof Bluetooth Outdoor Speaker",
        "category": "Electronics",
        "description": "Rugged IPX7 waterproof wireless speaker delivering deep punchy bass, 360-degree sound, 12 hours playtime, and durable carabiner clip for hiking, cycling, and travel.",
        "price": 34.95,
        "stock_quantity": 50
    },
    {
        "product_name": "1080P Pro Streaming HD Webcam",
        "category": "Electronics",
        "description": "Full HD desktop camera with dual noise-reduction microphones, privacy shutter, automatic low-light correction, and tripod stand for Zoom meetings, online lectures, and streaming.",
        "price": 45.00,
        "stock_quantity": 70
    },

    # Clothing (7)
    {
        "product_name": "Breathable Mesh Road Running Shoes",
        "category": "Clothing",
        "description": "Lightweight athletic running sneakers with responsive foam cushioning, breathable knit upper, non-slip rubber outsole, and arch support for comfortable long-distance jogging and gym sessions.",
        "price": 59.99,
        "stock_quantity": 55
    },
    {
        "product_name": "Thermal Polar Fleece Winter Jacket",
        "category": "Clothing",
        "description": "Warm full-zip outdoor fleece jacket with high collar, zippered security pockets, wind-resistant elastic cuffs, and soft brushed interior for cold weather layering and trekking.",
        "price": 64.50,
        "stock_quantity": 40
    },
    {
        "product_name": "Organic Cotton Crewneck Casual T-Shirt",
        "category": "Clothing",
        "description": "100% certified combed organic cotton unisex t-shirt. Pre-shrunk soft fabric, reinforced double-stitched collar, and minimalist classic fit suitable for everyday relaxed casual wear.",
        "price": 18.00,
        "stock_quantity": 150
    },
    {
        "product_name": "Water-Resistant Cargo Hiking Pants",
        "category": "Clothing",
        "description": "Durable stretch ripstop outdoor trousers with quick-dry coating, reinforced knees, articulated cut, and six utility cargo pockets for mountain climbing and backpacking adventures.",
        "price": 48.00,
        "stock_quantity": 35
    },
    {
        "product_name": "Quick-Dry Athletic Gym Shorts",
        "category": "Clothing",
        "description": "Lightweight performance workout shorts featuring moisture-wicking technology, elastic waistband with internal drawstring, and phone-safe zippered pockets for running and cross-training.",
        "price": 22.50,
        "stock_quantity": 90
    },
    {
        "product_name": "Merino Wool Blend Knitted Sweater",
        "category": "Clothing",
        "description": "Cozy fine-knit crewneck sweater crafted from ethically sourced merino wool and modal blend. Breathable, naturally odor-resistant, and stylish for semi-formal and casual settings.",
        "price": 75.00,
        "stock_quantity": 30
    },
    {
        "product_name": "Reflective Windbreaker Running Vest",
        "category": "Clothing",
        "description": "High-visibility sleeveless windbreaker vest with 360-degree reflective accents, mesh ventilation panels, and packable pocket for dusk and dawn outdoor sports.",
        "price": 29.99,
        "stock_quantity": 40
    },

    # Books (7)
    {
        "product_name": "Python Programming for Absolute Beginners",
        "category": "Books",
        "description": "Comprehensive practical textbook introducing Python 3, object-oriented programming, data structures, algorithms, and practical automation scripts. Highly recommended for university students starting coding.",
        "price": 32.00,
        "stock_quantity": 65
    },
    {
        "product_name": "Designing Data-Intensive Applications",
        "category": "Books",
        "description": "Authoritative guide exploring the fundamentals of relational databases, distributed storage systems, replication, partitioning, consistency models, and transaction management in modern architectures.",
        "price": 48.50,
        "stock_quantity": 40
    },
    {
        "product_name": "Clean Code: Agile Software Craftsmanship",
        "category": "Books",
        "description": "Legendary guide by Robert C. Martin teaching best practices in software development, readable code architecture, meaningful naming, functions, refactoring, and automated unit testing.",
        "price": 41.99,
        "stock_quantity": 50
    },
    {
        "product_name": "Full-Stack Web Development with HTML5, CSS3, and JavaScript",
        "category": "Books",
        "description": "Hands-on guide to building responsive web applications from scratch using modern frontend standards, asynchronous JavaScript, DOM manipulation, and RESTful API integration.",
        "price": 35.00,
        "stock_quantity": 45
    },
    {
        "product_name": "Hands-On Machine Learning and Vector Embeddings",
        "category": "Books",
        "description": "Practical manual covering neural networks, feature extraction, transformer models, semantic vector search, clustering, and deploying AI solutions in production environments.",
        "price": 54.00,
        "stock_quantity": 25
    },
    {
        "product_name": "Database Systems: Concepts and Design",
        "category": "Books",
        "description": "Foundational computer science textbook on entity-relationship modelling, normalization forms 1NF to BCNF, SQL query execution, indexing methods, and ACID transactions.",
        "price": 60.00,
        "stock_quantity": 30
    },
    {
        "product_name": "The Pragmatic Programmer: Your Journey to Mastery",
        "category": "Books",
        "description": "Classic computing book examining developer career growth, pragmatic thinking, modular design, debugging techniques, and automation principles for building enduring software systems.",
        "price": 44.00,
        "stock_quantity": 35
    },

    # Home Appliances (7)
    {
        "product_name": "Digital Air Fryer Oven 5.8-Quart",
        "category": "Home Appliances",
        "description": "Healthy oil-free countertop convection air fryer with touchscreen digital presets, rapid 360-degree heat circulation, nonstick dishwasher-safe basket, and auto shut-off safety sensor.",
        "price": 89.99,
        "stock_quantity": 28
    },
    {
        "product_name": "Robotic Smart Vacuum Cleaner with Gyro Navigation",
        "category": "Home Appliances",
        "description": "Intelligent automated robot vacuum with strong suction power, anti-drop cliff sensors, automatic self-recharging dock, and slim profile for pet hair and hardwood floors.",
        "price": 179.00,
        "stock_quantity": 15
    },
    {
        "product_name": "Stainless Steel Fast-Boil Electric Kettle",
        "category": "Home Appliances",
        "description": "1.7-liter cordless hot water electric kettle with 1500W rapid heating element, blue LED indicator, boil-dry protection, and automatic shutoff for tea and pour-over coffee.",
        "price": 27.50,
        "stock_quantity": 60
    },
    {
        "product_name": "High-Speed Countertop Smoothie Blender",
        "category": "Home Appliances",
        "description": "1000W professional kitchen blender with 6-blade stainless steel assembly, pulse mode, and 64-ounce BPA-free pitcher for crushing ice, frozen fruit smoothies, and vegetable purees.",
        "price": 65.00,
        "stock_quantity": 32
    },
    {
        "product_name": "Ultrasonic Cool Mist Room Humidifier",
        "category": "Home Appliances",
        "description": "Quiet 4-liter ultrasonic bedroom humidifier with adjustable mist nozzle, essential oil tray, nightlight function, and whisper-quiet operation for relieving dry winter air.",
        "price": 38.00,
        "stock_quantity": 48
    },
    {
        "product_name": "Programmable 12-Cup Drip Coffee Maker",
        "category": "Home Appliances",
        "description": "Classic drip coffee brewer with 24-hour advance programmable timer, glass carafe with ergonomic handle, keep-warm warming plate, and reusable permanent gold-tone mesh filter.",
        "price": 49.99,
        "stock_quantity": 40
    },
    {
        "product_name": "Cordless Handheld Garment Steamer",
        "category": "Home Appliances",
        "description": "Portable compact clothes fabric steamer producing rapid high-temperature steam in 30 seconds for removing wrinkles, refreshing suits, dresses, curtains, and travel outfits.",
        "price": 34.00,
        "stock_quantity": 55
    },

    # Sports Equipment (7)
    {
        "product_name": "Eco-Friendly Non-Slip Yoga Mat with Alignment Lines",
        "category": "Sports Equipment",
        "description": "High-density cushioned TPE exercise mat featuring dual-sided non-slip texture, laser-engraved body alignment markers, carrying strap, and tear-resistant core for yoga, Pilates, and stretching.",
        "price": 29.99,
        "stock_quantity": 75
    },
    {
        "product_name": "Adjustable Dumbbell Weight Set (5 to 52.5 lbs)",
        "category": "Sports Equipment",
        "description": "Space-saving rapid dial adjustable dumbbell with heavy-duty steel weight plates, knurled ergonomic handle grip, and storage tray for progressive home strength training workouts.",
        "price": 199.00,
        "stock_quantity": 12
    },
    {
        "product_name": "Carbon Fiber Lightweight Badminton Racket Set",
        "category": "Sports Equipment",
        "description": "High-modulus carbon graphite badminton rackets featuring high string tension, isometric head frame for enlarged sweet spot, two rackets, shuttlecocks, and protective padded bag.",
        "price": 42.50,
        "stock_quantity": 38
    },
    {
        "product_name": "Insulated Stainless Steel Sports Water Bottle 32oz",
        "category": "Sports Equipment",
        "description": "Double-wall vacuum insulated metal flask keeping drinks cold for 24 hours or hot for 12 hours. Features leakproof straw lid, wide mouth opening, and sweat-free powder coat exterior.",
        "price": 21.99,
        "stock_quantity": 120
    },
    {
        "product_name": "Heavy-Duty Resistance Loop Bands Set of 5",
        "category": "Sports Equipment",
        "description": "Set of 5 natural latex resistance workout exercise bands ranging from extra light to extra heavy. Includes travel pouch and exercise guide for physical therapy, leg, and glute training.",
        "price": 14.50,
        "stock_quantity": 140
    },
    {
        "product_name": "Pro Foam Muscle Massage Roller",
        "category": "Sports Equipment",
        "description": "High-density textured foam roller designed for deep tissue muscle recovery, myofascial release, relieving soreness, and stretching back and leg muscles after intense running or workouts.",
        "price": 19.99,
        "stock_quantity": 65
    },
    {
        "product_name": "High-Speed Steel Cable Jump Rope",
        "category": "Sports Equipment",
        "description": "Adjustable tangle-free steel wire speed rope with smooth 360-degree ball bearings and non-slip aluminum handles for cardio boxing training, double unders, and fitness conditioning.",
        "price": 12.99,
        "stock_quantity": 95
    }
]

SAMPLE_ORDERS = [
    {
        "customer_name": "Alice Johnson",
        "items": [
            {"product_name": "Ultrabook 14-inch Developer Laptop", "quantity": 1},
            {"product_name": "USB-C Multiport Hub 7-in-1 Adapter", "quantity": 1}
        ]
    },
    {
        "customer_name": "Brian Smith",
        "items": [
            {"product_name": "Active Wireless Noise-Cancelling Headphones", "quantity": 1},
            {"product_name": "Breathable Mesh Road Running Shoes", "quantity": 1}
        ]
    },
    {
        "customer_name": "Catherine Lee",
        "items": [
            {"product_name": "Python Programming for Absolute Beginners", "quantity": 2},
            {"product_name": "Clean Code: Agile Software Craftsmanship", "quantity": 1}
        ]
    }
]
