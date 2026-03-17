#!/usr/bin/env python3
"""List all venues"""

import frappe


def run():
    frappe.set_user("Administrator")

    venues = frappe.get_all("Venue", fields=["name", "venue_name", "room"], limit=20)

    print("=" * 70)
    print(f"VENUES IN DATABASE: {len(venues)}")
    print("=" * 70)

    for venue in venues:
        print(f"\n  Name (ID): {venue.name}")
        print(f"  Venue Name: {venue.venue_name}")
        print(f"  Room: {venue.room}")
        print(f"  ---")

    print("=" * 70)
