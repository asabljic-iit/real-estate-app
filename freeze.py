# frozen demo page
import app as app_module
from flask_frozen import Freezer

app = app_module.app

MOCK_PROPERTIES = [
    {
        "property_id": 1,
        "street": "742 Evergreen Terrace",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60616",
        "description": "Sun-drenched single-family home near the lakefront with hardwood floors.",
        "prop_type": "House",
        "price": 3200,
        "num_rooms": 4,
        "sq_footage": 2400,
        "availability": True,
        "agency": "Windy City Realty",
        "neighborhood_id": 1,
        "name": "Bronzeville",
        "crime_rate": "Low",
        "school_rating": 8,
        "building_type": None,
        "business_type": None,
        "zoning_type": None,
    },
    {
        "property_id": 2,
        "street": "233 S Wacker Dr, Apt 42B",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60606",
        "description": "Modern high-rise apartment with skyline views and 24-hour concierge.",
        "prop_type": "Apartment",
        "price": 2450,
        "num_rooms": 2,
        "sq_footage": 1150,
        "availability": True,
        "agency": "Loop Living",
        "neighborhood_id": 2,
        "name": "The Loop",
        "crime_rate": "Low",
        "school_rating": 9,
        "building_type": "High-Rise",
        "business_type": None,
        "zoning_type": None,
    },
    {
        "property_id": 3,
        "street": "1060 W Addison St",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60613",
        "description": "Prime retail and commercial storefront in a high-foot-traffic corridor.",
        "prop_type": "CommercialBuilding",
        "price": 5800,
        "num_rooms": 6,
        "sq_footage": 4200,
        "availability": True,
        "agency": "Northside Commercial",
        "neighborhood_id": 3,
        "name": "Lakeview",
        "crime_rate": "Low",
        "school_rating": 8,
        "building_type": None,
        "business_type": "Retail / Office",
        "zoning_type": None,
    },
    {
        "property_id": 4,
        "street": "88 Harbor Point Rd",
        "city": "Lake Geneva",
        "state": "WI",
        "zip_code": "53147",
        "description": "Waterfront vacation retreat with private dock and wrap-around deck.",
        "prop_type": "VacationHome",
        "price": 4100,
        "num_rooms": 3,
        "sq_footage": 1950,
        "availability": True,
        "agency": "Lakeshore Escapes",
        "neighborhood_id": 4,
        "name": "Geneva Shore",
        "crime_rate": "Very Low",
        "school_rating": 9,
        "building_type": None,
        "business_type": None,
        "zoning_type": None,
    },
    {
        "property_id": 5,
        "street": "4500 N Western Ave",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60625",
        "description": "Cleared corner lot zoned for mixed-use residential development.",
        "prop_type": "Land",
        "price": 1900,
        "num_rooms": 0,
        "sq_footage": 6500,
        "availability": True,
        "agency": "Metro Land Group",
        "neighborhood_id": 5,
        "name": "Lincoln Square",
        "crime_rate": "Low",
        "school_rating": 9,
        "building_type": None,
        "business_type": None,
        "zoning_type": "Mixed-Use (B3-2)",
    },
]

def mock_get_random_properties():
    headers = [
        "property_id", "street", "city", "state",
        "description", "prop_type", "price", "num_rooms"
    ]
    rows = [tuple(p[col] for col in headers) for p in MOCK_PROPERTIES[:4]]
    return headers, rows


def mock_search_properties(*args, **kwargs):
    headers = [
        "property_id", "street", "city", "state", "zip_code",
        "description", "prop_type", "num_rooms", "price", "availability"
    ]
    rows = [tuple(p[col] for col in headers) for p in MOCK_PROPERTIES]
    return headers, rows


def mock_get_property_details(property_id):
    for p in MOCK_PROPERTIES:
        if str(p["property_id"]) == str(property_id):
            return p
    return None


app_module.get_random_properties = mock_get_random_properties
app_module.search_properties = mock_search_properties
app_module.get_property_details = mock_get_property_details

app.config["FREEZER_DESTINATION"] = "build"
app.config["FREEZER_RELATIVE_URLS"] = True
app.config["FREEZER_IGNORE_404_NOT_FOUND"] = True
app.config["FREEZER_REDIRECT_POLICY"] = "follow"

freezer = Freezer(app)


# Generate static HTML pages for every property ID
@freezer.register_generator
def book_property():
    for p in MOCK_PROPERTIES:
        yield {"property_id": str(p["property_id"])}


if __name__ == "__main__":
    freezer.freeze()
    print("Static portfolio preview successfully frozen to ./build/")
