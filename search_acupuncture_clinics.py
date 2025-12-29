#!/usr/bin/env python3
"""
Search for acupuncture clinics in the Hudson River Valley using Google Maps Places API (New).
"""

import requests
import csv
import time
import json
from typing import Dict, List, Set

API_KEY = "AIzaSyDF-_Pih4JP7FjQ5seV4sH59T8kGy8DODc"

# Hudson River Valley cities from NYC to Albany
CITIES = [
    # Westchester County (East Bank)
    ("Yonkers", "NY"),
    ("Hastings-on-Hudson", "NY"),
    ("Dobbs Ferry", "NY"),
    ("Irvington", "NY"),
    ("Tarrytown", "NY"),
    ("Sleepy Hollow", "NY"),
    ("Ossining", "NY"),
    ("Croton-on-Hudson", "NY"),
    ("Peekskill", "NY"),
    # Rockland County (West Bank)
    ("Nyack", "NY"),
    ("Upper Nyack", "NY"),
    ("Piermont", "NY"),
    ("Haverstraw", "NY"),
    ("Stony Point", "NY"),
    # Putnam County (East Bank)
    ("Cold Spring", "NY"),
    ("Garrison", "NY"),
    # Orange County (West Bank)
    ("Highland Falls", "NY"),
    ("West Point", "NY"),
    ("Cornwall-on-Hudson", "NY"),
    ("Newburgh", "NY"),
    ("New Windsor", "NY"),
    # Dutchess County (East Bank)
    ("Beacon", "NY"),
    ("Fishkill", "NY"),
    ("Wappingers Falls", "NY"),
    ("Poughkeepsie", "NY"),
    ("Hyde Park", "NY"),
    ("Rhinebeck", "NY"),
    ("Red Hook", "NY"),
    ("Tivoli", "NY"),
    # Ulster County (West Bank)
    ("Highland", "NY"),
    ("Milton", "NY"),
    ("Marlboro", "NY"),
    ("Kingston", "NY"),
    ("Saugerties", "NY"),
    # Columbia County (East Bank)
    ("Hudson", "NY"),
    ("Stuyvesant", "NY"),
    ("Stockport", "NY"),
    # Greene County (West Bank)
    ("Catskill", "NY"),
    ("Athens", "NY"),
    ("Coxsackie", "NY"),
    # Albany & Rensselaer Counties
    ("Coeymans", "NY"),
    ("Ravena", "NY"),
    ("Castleton-on-Hudson", "NY"),
    ("Albany", "NY"),
    ("Rensselaer", "NY"),
]

# Search terms for acupuncture and Chinese medicine
SEARCH_TERMS = [
    "acupuncture",
    "chinese medicine",
    "acupuncturist",
    "traditional chinese medicine",
]


def search_places_new_api(query: str, location: str) -> List[Dict]:
    """Search Google Maps Places API (New) for a query at a location."""
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.businessStatus,places.types"
    }

    all_results = []
    next_page_token = None

    while True:
        body = {
            "textQuery": f"{query} in {location}",
            "languageCode": "en"
        }

        if next_page_token:
            body["pageToken"] = next_page_token
            time.sleep(2)  # Required delay for pagination

        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        if response.status_code == 200:
            places = data.get("places", [])
            all_results.extend(places)
        else:
            error_message = data.get("error", {}).get("message", "Unknown error")
            print(f"  API Error: {error_message}")
            break

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

    return all_results


def main():
    """Main function to search for acupuncture clinics."""
    seen_place_ids: Set[str] = set()
    all_clinics: List[Dict] = []

    print("Searching for acupuncture and Chinese medicine clinics in Hudson River Valley...")
    print("=" * 70)

    for city, state in CITIES:
        location = f"{city}, {state}"
        print(f"\nSearching in {location}...")

        city_results = []

        for search_term in SEARCH_TERMS:
            results = search_places_new_api(search_term, location)

            for place in results:
                place_id = place.get("id")
                if place_id and place_id not in seen_place_ids:
                    seen_place_ids.add(place_id)
                    city_results.append(place)

            time.sleep(0.2)  # Rate limiting between searches

        print(f"  Found {len(city_results)} unique places")

        # Process each place
        for place in city_results:
            display_name = place.get("displayName", {})
            clinic_data = {
                "name": display_name.get("text", "") if isinstance(display_name, dict) else str(display_name),
                "address": place.get("formattedAddress", ""),
                "phone": place.get("nationalPhoneNumber", ""),
                "website": place.get("websiteUri", ""),
                "rating": place.get("rating", ""),
                "total_ratings": place.get("userRatingCount", ""),
                "business_status": place.get("businessStatus", ""),
                "search_city": city,
                "search_county": get_county(city),
            }
            all_clinics.append(clinic_data)

    print("\n" + "=" * 70)
    print(f"Total unique clinics found: {len(all_clinics)}")

    # Write to CSV
    csv_filename = "hudson_valley_acupuncture_clinics.csv"

    if all_clinics:
        fieldnames = ["name", "address", "phone", "website", "rating", "total_ratings",
                      "business_status", "search_city", "search_county"]

        with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_clinics)

        print(f"\nResults saved to {csv_filename}")
    else:
        print("\nNo clinics found.")

    return all_clinics


def get_county(city: str) -> str:
    """Return the county for a given city."""
    county_map = {
        "Yonkers": "Westchester",
        "Hastings-on-Hudson": "Westchester",
        "Dobbs Ferry": "Westchester",
        "Irvington": "Westchester",
        "Tarrytown": "Westchester",
        "Sleepy Hollow": "Westchester",
        "Ossining": "Westchester",
        "Croton-on-Hudson": "Westchester",
        "Peekskill": "Westchester",
        "Nyack": "Rockland",
        "Upper Nyack": "Rockland",
        "Piermont": "Rockland",
        "Haverstraw": "Rockland",
        "Stony Point": "Rockland",
        "Cold Spring": "Putnam",
        "Garrison": "Putnam",
        "Highland Falls": "Orange",
        "West Point": "Orange",
        "Cornwall-on-Hudson": "Orange",
        "Newburgh": "Orange",
        "New Windsor": "Orange",
        "Beacon": "Dutchess",
        "Fishkill": "Dutchess",
        "Wappingers Falls": "Dutchess",
        "Poughkeepsie": "Dutchess",
        "Hyde Park": "Dutchess",
        "Rhinebeck": "Dutchess",
        "Red Hook": "Dutchess",
        "Tivoli": "Dutchess",
        "Highland": "Ulster",
        "Milton": "Ulster",
        "Marlboro": "Ulster",
        "Kingston": "Ulster",
        "Saugerties": "Ulster",
        "Hudson": "Columbia",
        "Stuyvesant": "Columbia",
        "Stockport": "Columbia",
        "Catskill": "Greene",
        "Athens": "Greene",
        "Coxsackie": "Greene",
        "Coeymans": "Albany",
        "Ravena": "Albany",
        "Castleton-on-Hudson": "Rensselaer",
        "Albany": "Albany",
        "Rensselaer": "Rensselaer",
    }
    return county_map.get(city, "Unknown")


if __name__ == "__main__":
    main()
