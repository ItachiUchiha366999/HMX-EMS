# Copyright (c) 2026, University ERP and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_time, time_diff_in_hours


class TransportTripLog(Document):
    """Transport Trip Log for tracking vehicle trips"""

    def validate(self):
        self.validate_odometer()
        self.calculate_distance()
        self.calculate_delay()
        self.set_route_timing()

    def validate_odometer(self):
        """Validate odometer readings"""
        if self.start_odometer and self.end_odometer:
            if self.end_odometer < self.start_odometer:
                frappe.throw(_("End odometer cannot be less than start odometer"))

        # Validate against vehicle's current odometer
        if self.vehicle and self.start_odometer:
            vehicle_odometer = frappe.db.get_value(
                "Transport Vehicle", self.vehicle, "current_odometer"
            )
            if vehicle_odometer and self.start_odometer < vehicle_odometer - 10:
                frappe.msgprint(
                    _("Start odometer ({0}) is less than vehicle's recorded odometer ({1})").format(
                        self.start_odometer, vehicle_odometer
                    ),
                    alert=True
                )

    def calculate_distance(self):
        """Calculate distance covered"""
        if self.start_odometer and self.end_odometer:
            self.distance_covered = self.end_odometer - self.start_odometer

    def calculate_delay(self):
        """Calculate delay in minutes"""
        if self.scheduled_arrival and self.actual_arrival:
            scheduled = get_time(self.scheduled_arrival)
            actual = get_time(self.actual_arrival)

            delay_hours = time_diff_in_hours(str(actual), str(scheduled))
            self.delay_minutes = int(delay_hours * 60)

            if self.delay_minutes < 0:
                self.delay_minutes = 0  # Arrived early

    def set_route_timing(self):
        """Set scheduled timing from route"""
        if self.route and not self.scheduled_departure:
            route = frappe.get_doc("Transport Route", self.route)
            if self.trip_type == "Morning":
                self.scheduled_departure = route.departure_time
                self.scheduled_arrival = route.arrival_time
            else:
                self.scheduled_departure = route.return_departure_time
                self.scheduled_arrival = route.return_arrival_time

    def on_update(self):
        """Update vehicle odometer on completion"""
        if self.status == "Completed" and self.end_odometer:
            frappe.db.set_value(
                "Transport Vehicle", self.vehicle,
                "current_odometer", self.end_odometer
            )


@frappe.whitelist()
def start_trip(trip_log, actual_departure=None, start_odometer=None):
    """Start a trip"""
    trip = frappe.get_doc("Transport Trip Log", trip_log)

    if trip.status != "Scheduled":
        frappe.throw(_("Trip is not in Scheduled status"))

    trip.status = "In Progress"
    if actual_departure:
        trip.actual_departure = actual_departure
    if start_odometer:
        trip.start_odometer = start_odometer

    trip.save()

    return {"message": _("Trip started successfully")}


@frappe.whitelist()
def complete_trip(trip_log, actual_arrival=None, end_odometer=None, passengers=None, remarks=None):
    """Complete a trip"""
    trip = frappe.get_doc("Transport Trip Log", trip_log)

    if trip.status != "In Progress":
        frappe.throw(_("Trip is not in progress"))

    trip.status = "Completed"
    if actual_arrival:
        trip.actual_arrival = actual_arrival
    if end_odometer:
        trip.end_odometer = end_odometer
    if passengers:
        trip.passengers_alighted = passengers
    if remarks:
        trip.remarks = remarks

    trip.save()

    return {"message": _("Trip completed successfully")}


@frappe.whitelist()
def get_daily_trips(date=None, route=None):
    """Get all trips for a date"""
    from frappe.utils import nowdate

    date = date or nowdate()
    conditions = ["trip_date = %s"]
    values = [date]

    if route:
        conditions.append("route = %s")
        values.append(route)

    where_clause = " AND ".join(conditions)

    return frappe.db.sql("""
        SELECT
            name,
            trip_type,
            route,
            vehicle,
            status,
            scheduled_departure,
            actual_departure,
            scheduled_arrival,
            actual_arrival,
            delay_minutes,
            passengers_boarded
        FROM `tabTransport Trip Log`
        WHERE {where_clause}
        ORDER BY scheduled_departure
    """.format(where_clause=where_clause), values, as_dict=True)
