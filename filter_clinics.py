#!/usr/bin/env python3
"""
Filter acupuncture clinic results to remove duplicates and non-relevant entries.
Focus on Hudson River Valley region clinics only.
"""

import csv
import re

# Valid NY counties in the Hudson River Valley region
VALID_COUNTIES = [
    'westchester', 'rockland', 'putnam', 'orange', 'dutchess',
    'ulster', 'columbia', 'greene', 'albany', 'rensselaer'
]

# Valid NY cities/towns in the region (including nearby areas that might appear)
VALID_LOCATIONS = [
    # Westchester
    'yonkers', 'hastings-on-hudson', 'hastings on hudson', 'dobbs ferry', 'irvington',
    'tarrytown', 'sleepy hollow', 'ossining', 'croton-on-hudson', 'croton on hudson',
    'peekskill', 'white plains', 'scarsdale', 'bronxville', 'eastchester', 'tuckahoe',
    'hartsdale', 'ardsley', 'elmsford', 'mount vernon', 'mt vernon', 'new rochelle',
    'mamaroneck', 'larchmont', 'pelham', 'port chester', 'rye', 'mount kisco', 'chappaqua',
    'pleasantville', 'briarcliff', 'bedford', 'katonah', 'somers', 'yorktown',
    # Rockland
    'nyack', 'upper nyack', 'piermont', 'haverstraw', 'stony point', 'new city',
    'nanuet', 'spring valley', 'suffern', 'pearl river', 'tappan', 'orangeburg',
    'sparkill', 'palisades', 'west nyack', 'valley cottage', 'congers', 'garnerville',
    # Putnam
    'cold spring', 'garrison', 'brewster', 'carmel', 'mahopac', 'putnam valley', 'patterson',
    # Orange
    'highland falls', 'west point', 'cornwall-on-hudson', 'cornwall on hudson',
    'cornwall', 'newburgh', 'new windsor', 'middletown', 'monroe', 'warwick',
    'goshen', 'chester', 'washingtonville', 'montgomery', 'walden', 'maybrook',
    # Dutchess
    'beacon', 'fishkill', 'wappingers falls', 'wappingers', 'poughkeepsie',
    'hyde park', 'rhinebeck', 'red hook', 'tivoli', 'pleasant valley', 'lagrangeville',
    'hopewell junction', 'millbrook', 'pawling', 'amenia', 'millerton', 'dover plains',
    # Ulster
    'highland', 'milton', 'marlboro', 'kingston', 'saugerties', 'woodstock',
    'new paltz', 'rosendale', 'esopus', 'port ewen', 'ellenville', 'stone ridge',
    'high falls', 'accord', 'phoenicia',
    # Columbia
    'hudson', 'stuyvesant', 'stockport', 'chatham', 'kinderhook', 'valatie',
    'philmont', 'claverack', 'germantown', 'elizaville', 'copake', 'hillsdale',
    # Greene
    'catskill', 'athens', 'coxsackie', 'tannersville', 'hunter', 'windham',
    'cairo', 'durham', 'greenville', 'jewett', 'prattsville',
    # Albany area
    'coeymans', 'ravena', 'castleton-on-hudson', 'castleton on hudson', 'albany',
    'rensselaer', 'delmar', 'latham', 'guilderland', 'colonie', 'loudonville',
    'troy', 'cohoes', 'watervliet', 'menands', 'slingerlands', 'voorheesville',
    # Bronx (close to Yonkers)
    'riverdale', 'bronx'
]

# Keywords that indicate an acupuncture/Chinese medicine clinic
RELEVANT_KEYWORDS = [
    'acupuncture', 'acupuncturist', 'chinese medicine', 'tcm', 'oriental medicine',
    'eastern medicine', 'asian medicine', 'herbal medicine', 'herbal', 'herbs',
    'qi ', 'moxibustion', 'cupping', 'traditional medicine', 'l.ac', 'lac',
    'daom', 'dipl.ac', 'holistic', 'integrative', 'wellness', 'healing',
    'naturopath', 'natural medicine', 'five element', 'medicine center'
]

# Keywords that indicate NOT primarily an acupuncture clinic
EXCLUDE_KEYWORDS = [
    'veterinary', 'vet ', 'pets', 'animal', 'pet hospital', 'for pets',
    'dental', 'dentist', 'optical', 'optometry', 'pharmacy', 'urgent care',
    'hospital', 'imaging', 'radiology', 'surgery', 'podiatry', 'podiatrist',
    'dermatology', 'dermatologist', 'plastic surgery', 'restaurant', 'szechuan',
    'empire', 'kitchen', 'buffet', 'takeout', 'grocery', 'supermarket',
    'store', 'shop', 'boutique', 'salon', 'spa only', 'hair', 'nail',
    'body balance massage'  # just massage, not acupuncture
]


def is_in_hudson_valley(address):
    """Check if address is in the Hudson River Valley region of NY."""
    address_lower = address.lower()

    # Must be in NY (but not NYC except Bronx/Riverdale)
    if ', ny ' not in address_lower and ', new york ' not in address_lower:
        return False

    # Check if it's in a valid location
    for location in VALID_LOCATIONS:
        if location in address_lower:
            return True

    # Also check for zip codes in the region (approximate ranges)
    # Westchester: 105xx, 106xx, 107xx, 108xx
    # Rockland: 109xx
    # Putnam: 105xx
    # Orange: 109xx, 124xx, 125xx
    # Dutchess: 125xx, 126xx
    # Ulster: 124xx, 125xx
    # Columbia: 125xx
    # Greene: 124xx
    # Albany area: 120xx, 121xx, 122xx
    zip_match = re.search(r'\b(105\d{2}|106\d{2}|107\d{2}|108\d{2}|109\d{2}|120\d{2}|121\d{2}|122\d{2}|124\d{2}|125\d{2}|126\d{2})\b', address_lower)
    if zip_match:
        return True

    return False


def is_relevant(row):
    """Check if a business is likely an acupuncture/Chinese medicine clinic."""
    name_lower = row['name'].lower()

    # Exclude veterinary and other non-human medical services
    for keyword in EXCLUDE_KEYWORDS:
        if keyword in name_lower:
            return False

    # Check if address is in Hudson Valley
    if not is_in_hudson_valley(row['address']):
        return False

    # Include if name contains relevant keywords
    for keyword in RELEVANT_KEYWORDS:
        if keyword in name_lower:
            return True

    # Include L.Ac or LAc practitioners (licensed acupuncturist)
    if re.search(r'\bl\.?ac\.?\b', name_lower):
        return True

    # Include if business seems relevant based on name patterns
    if 'acu' in name_lower:  # catches acupuncture, acu-care, etc.
        return True

    return False


def main():
    input_file = 'hudson_valley_acupuncture_clinics.csv'
    output_file = 'hudson_valley_acupuncture_clinics_filtered.csv'

    seen_addresses = set()
    filtered_clinics = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip if we've already seen this exact address
            address = row['address'].strip()

            # Create a normalized key to detect duplicates
            address_key = re.sub(r'[,\s]+', '', address.lower())

            if address_key in seen_addresses:
                continue

            if not is_relevant(row):
                continue

            seen_addresses.add(address_key)
            filtered_clinics.append(row)

    # Sort by county, then by city, then by name
    filtered_clinics.sort(key=lambda x: (x['search_county'], x['search_city'], x['name']))

    # Write filtered results
    if filtered_clinics:
        fieldnames = ['name', 'address', 'phone', 'website', 'rating', 'total_ratings',
                      'business_status', 'search_city', 'search_county']

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_clinics)

        print(f"Filtered to {len(filtered_clinics)} clinics in Hudson River Valley")
        print(f"Results saved to {output_file}")

        # Print county breakdown
        county_counts = {}
        for clinic in filtered_clinics:
            county = clinic['search_county']
            county_counts[county] = county_counts.get(county, 0) + 1

        print("\nBreakdown by county:")
        for county in sorted(county_counts.keys()):
            print(f"  {county}: {county_counts[county]} clinics")

    else:
        print("No clinics after filtering")


if __name__ == '__main__':
    main()
