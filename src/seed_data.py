from faker import Faker
import random
from datetime import datetime, timedelta
from . import db as database

fake = Faker()

# Realistic firmware versions for different product types
FIRMWARE_VERSIONS = {
    "wireless": {
        "current": "wireless-28-7",
        "legacy": ["wireless-27-6", "wireless-26-8", "wireless-28-5", "wireless-27-7"],
    },
    "switch": {
        "current": "switch-14-33",
        "legacy": ["switch-14-32", "switch-14-31", "switch-13-24", "switch-14-30"],
    },
    "appliance": {
        "current": "appliance-18-107",
        "legacy": ["appliance-18-106", "appliance-17-10", "appliance-18-105", "appliance-17-9"],
    }
}

# Realistic Meraki models
MODELS = {
    "wireless": ["MR36", "MR46", "MR56", "MR33", "MR42", "MR44", "MR53", "MR20", "MR30H"],
    "switch": ["MS220-8P", "MS225-48FP", "MS250-48FP", "MS350-24X", "MS120-8FP", "MS210-48FP", "MS410-32"],
    "appliance": ["MX64", "MX67", "MX68", "MX75", "MX84", "MX95", "MX100", "MX250", "Z3"]
}

# Sample customer names
CUSTOMERS = [
    "Acme Corporation",
    "TechStart Industries",
    "Global Retail Co",
    "Healthcare Solutions LLC",
    "Metro School District",
    "Downtown Hotel Group",
    "Riverside Manufacturing",
    "Pacific Financial Services",
    "Mountain View Logistics",
    "Summit Consulting Partners"
]

# Device name patterns
DEVICE_NAME_PATTERNS = [
    "{building}-{floor}F-{type}-{num}",
    "{location}-{type}-{num}",
    "{building}-{type}{num}",
]

BUILDINGS = ["HQ", "Building-A", "Building-B", "Warehouse", "Office", "Store", "Campus"]
FLOORS = ["1", "2", "3", "4", "5", "G"]
LOCATIONS = ["Reception", "Lobby", "Conference", "IT-Room", "Storage", "Workshop", "Cafeteria"]


def generate_device_name(product_type):
    """Generate realistic device names"""
    pattern = random.choice(DEVICE_NAME_PATTERNS)
    type_abbrev = {"wireless": "AP", "switch": "SW", "appliance": "MX"}
    
    return pattern.format(
        building=random.choice(BUILDINGS),
        floor=random.choice(FLOORS),
        location=random.choice(LOCATIONS),
        type=type_abbrev.get(product_type, "DEV"),
        num=random.randint(1, 99)
    )


def generate_serial(model):
    """Generate realistic Meraki serial numbers"""
    # Meraki serials are typically like: Q2XX-XXXX-XXXX
    prefix = "Q2" + "".join([random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ234567") for _ in range(2)])
    suffix = "-".join(["".join([random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ234567") for _ in range(4)]) for _ in range(2)])
    return f"{prefix}-{suffix}"


def generate_mac():
    """Generate realistic MAC address"""
    return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])


def generate_network_id():
    """Generate realistic Meraki network ID"""
    return "N_" + "".join([random.choice("0123456789") for _ in range(15)])


def generate_device(customer_name, product_type):
    """Generate a single device record"""
    model = random.choice(MODELS[product_type])
    
    # 70% chance of being on current firmware, 30% on legacy
    if random.random() < 0.7:
        firmware = FIRMWARE_VERSIONS[product_type]["current"]
    else:
        firmware = random.choice(FIRMWARE_VERSIONS[product_type]["legacy"])
    
    # Generate timestamps
    config_updated = (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat()
    
    # Geographic spread (US-focused)
    lat = round(random.uniform(25.0, 48.0), 6)
    lng = round(random.uniform(-125.0, -65.0), 6)
    
    device_name = generate_device_name(product_type)
    serial = generate_serial(model)
    
    # Generate optional fields (some devices have them, some don't)
    address = fake.address().replace("\n", " ") if random.random() > 0.3 else None
    lanip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" if random.random() > 0.2 else None
    notes = fake.sentence() if random.random() > 0.7 else None
    tags = " ".join(random.sample(["production", "office", "warehouse", "guest", "iot", "security"], k=random.randint(0, 3))) if random.random() > 0.5 else None
    
    return database.DeviceDB(
        customer=customer_name,
        address=address,
        configupdated=config_updated,
        details=None,  # Typically empty in Meraki
        firmware=firmware,
        lanip=lanip,
        lat=lat,
        lng=lng,
        mac=generate_mac(),
        model=model,
        name=device_name,
        networkid=generate_network_id(),
        notes=notes,
        producttype=product_type,
        serial=serial,
        tags=tags,
        url=f"https://n149.meraki.com/o/-/manage/nodes/new_wired_status/{serial}"
    )


def seed_database(num_customers=10, devices_per_customer=15):
    """Seed the database with fake Meraki device data"""
    print("Initializing database...")
    database.init_db()
    
    db = database.SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(database.DeviceDB).delete()
        db.commit()
        
        print(f"Generating data for {num_customers} customers...")
        total_devices = 0
        
        for customer in CUSTOMERS[:num_customers]:
            print(f"  Creating devices for {customer}...")
            
            # Each customer gets a mix of device types
            for _ in range(devices_per_customer):
                # Distribution: 50% wireless, 30% switch, 20% appliance
                rand = random.random()
                if rand < 0.5:
                    product_type = "wireless"
                elif rand < 0.8:
                    product_type = "switch"
                else:
                    product_type = "appliance"
                
                device = generate_device(customer, product_type)
                db.add(device)
                total_devices += 1
        
        db.commit()
        print(f"\n✅ Successfully created {total_devices} devices for {num_customers} customers!")
        
        # Print summary
        print("\n📊 Summary:")
        for product_type in ["wireless", "switch", "appliance"]:
            count = db.query(database.DeviceDB).filter(database.DeviceDB.producttype == product_type).count()
            print(f"  {product_type.capitalize()}: {count} devices")
        
        # Print firmware compliance
        print("\n🔧 Firmware Compliance:")
        for product_type in ["wireless", "switch", "appliance"]:
            current_fw = FIRMWARE_VERSIONS[product_type]["current"]
            total = db.query(database.DeviceDB).filter(database.DeviceDB.producttype == product_type).count()
            compliant = db.query(database.DeviceDB).filter(
                database.DeviceDB.producttype == product_type,
                database.DeviceDB.firmware == current_fw
            ).count()
            if total > 0:
                percentage = (compliant / total) * 100
                print(f"  {product_type.capitalize()}: {compliant}/{total} ({percentage:.1f}% compliant)")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()