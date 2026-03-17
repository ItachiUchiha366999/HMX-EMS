# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class TransportRoute(Document):
    """Transport Route master with stops"""

    def validate(self):
        self.calculate_totals()
        self.validate_stops()

    def calculate_totals(self):
        """Calculate total distance and duration from stops"""
        if self.stops:
            self.total_stops = len(self.stops)

            # Calculate total distance from last stop
            last_stop = max(self.stops, key=lambda x: x.stop_sequence)
            if last_stop.distance_from_start:
                self.total_distance = last_stop.distance_from_start

    def validate_stops(self):
        """Validate stop sequences are unique"""
        if not self.stops:
            return

        sequences = [stop.stop_sequence for stop in self.stops]
        if len(sequences) != len(set(sequences)):
            frappe.throw(_("Stop sequences must be unique"))

        # Ensure sequences are in order
        sorted_stops = sorted(self.stops, key=lambda x: x.stop_sequence)
        for i, stop in enumerate(sorted_stops):
            stop.stop_sequence = i + 1


@frappe.whitelist()
def get_route_stops(route):
    """Get all stops for a route in order"""
    return frappe.db.sql("""
        SELECT
            stop_name,
            stop_sequence,
            pickup_time,
            drop_time,
            distance_from_start,
            fare_from_start
        FROM `tabTransport Route Stop`
        WHERE parent = %s
        ORDER BY stop_sequence
    """, (route,), as_dict=True)


@frappe.whitelist()
def get_active_routes():
    """Get all active routes"""
    return frappe.get_all(
        "Transport Route",
        filters={"is_active": 1},
        fields=["name", "route_name", "route_code", "start_point", "end_point",
                "departure_time", "monthly_fare", "assigned_vehicle"]
    )


@frappe.whitelist()
def get_route_schedule(route):
    """Get complete route schedule"""
    route_doc = frappe.get_doc("Transport Route", route)

    return {
        "route_name": route_doc.route_name,
        "start_point": route_doc.start_point,
        "end_point": route_doc.end_point,
        "departure_time": route_doc.departure_time,
        "arrival_time": route_doc.arrival_time,
        "return_departure_time": route_doc.return_departure_time,
        "return_arrival_time": route_doc.return_arrival_time,
        "stops": [
            {
                "stop_name": stop.stop_name,
                "pickup_time": stop.pickup_time,
                "drop_time": stop.drop_time,
                "fare": stop.fare_from_start
            }
            for stop in route_doc.stops
        ],
        "vehicle": route_doc.assigned_vehicle,
        "driver": route_doc.driver,
        "driver_contact": route_doc.driver_contact
    }
