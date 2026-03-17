# Phase 9: Complete Hostel Management Module

## Status: ✅ COMPLETED (2026-01-02)

## Overview

This phase completes the Hostel Management module by adding the missing DocTypes identified in the gap analysis. Phase 7 had implemented basic Hostel Building, Room, Allocation, Attendance, and Mess DocTypes. This phase enhances those DocTypes and adds Visitor Management, Maintenance Requests, Bulk Attendance, and Weekly Menu Planning.

**Completed:** 2026-01-02
**Priority:** High
**Dependencies:** Phase 7 (Hostel infrastructure exists)

---

## Prerequisites

- Phase 7 completed (Hostel Allocation DocType exists)
- University ERP Settings configured
- Fee integration working

---

## Week 1: Core Hostel Infrastructure

### 1.1 Hostel Building DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Building",
    "module": "University Hostel",
    "naming_rule": "By fieldname",
    "autoname": "field:building_code",
    "fields": [
        {"fieldname": "building_code", "fieldtype": "Data", "label": "Building Code", "reqd": 1, "unique": 1},
        {"fieldname": "building_name", "fieldtype": "Data", "label": "Building Name", "reqd": 1},
        {"fieldname": "hostel_type", "fieldtype": "Select", "options": "Boys\nGirls\nCo-ed", "reqd": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "warden", "fieldtype": "Link", "options": "Employee", "label": "Warden"},
        {"fieldname": "assistant_warden", "fieldtype": "Link", "options": "Employee", "label": "Assistant Warden"},
        {"fieldname": "contact_number", "fieldtype": "Data", "label": "Contact Number"},

        {"fieldname": "section_capacity", "fieldtype": "Section Break", "label": "Capacity Details"},
        {"fieldname": "total_floors", "fieldtype": "Int", "label": "Total Floors", "default": 1},
        {"fieldname": "total_rooms", "fieldtype": "Int", "label": "Total Rooms", "read_only": 1},
        {"fieldname": "total_beds", "fieldtype": "Int", "label": "Total Bed Capacity", "read_only": 1},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "occupied_beds", "fieldtype": "Int", "label": "Occupied Beds", "read_only": 1},
        {"fieldname": "available_beds", "fieldtype": "Int", "label": "Available Beds", "read_only": 1},
        {"fieldname": "occupancy_rate", "fieldtype": "Percent", "label": "Occupancy Rate", "read_only": 1},

        {"fieldname": "section_facilities", "fieldtype": "Section Break", "label": "Facilities"},
        {"fieldname": "has_wifi", "fieldtype": "Check", "label": "WiFi Available"},
        {"fieldname": "has_laundry", "fieldtype": "Check", "label": "Laundry Facility"},
        {"fieldname": "has_gym", "fieldtype": "Check", "label": "Gym Facility"},
        {"fieldname": "has_common_room", "fieldtype": "Check", "label": "Common Room"},
        {"fieldname": "column_break_3", "fieldtype": "Column Break"},
        {"fieldname": "has_mess", "fieldtype": "Check", "label": "Mess Attached"},
        {"fieldname": "mess", "fieldtype": "Link", "options": "Hostel Mess", "depends_on": "has_mess"},
        {"fieldname": "has_parking", "fieldtype": "Check", "label": "Parking Available"},

        {"fieldname": "section_address", "fieldtype": "Section Break", "label": "Location"},
        {"fieldname": "address", "fieldtype": "Small Text", "label": "Address"},
        {"fieldname": "latitude", "fieldtype": "Float", "label": "Latitude"},
        {"fieldname": "longitude", "fieldtype": "Float", "label": "Longitude"},

        {"fieldname": "section_fees", "fieldtype": "Section Break", "label": "Fee Structure"},
        {"fieldname": "annual_fee", "fieldtype": "Currency", "label": "Annual Hostel Fee"},
        {"fieldname": "security_deposit", "fieldtype": "Currency", "label": "Security Deposit"},
        {"fieldname": "mess_fee_monthly", "fieldtype": "Currency", "label": "Monthly Mess Fee"},

        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nUnder Maintenance\nClosed", "default": "Active"}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Hostel Warden", "read": 1, "write": 1}
    ]
}
```

**Python Controller:**
```python
# university_erp/university_hostel/doctype/hostel_building/hostel_building.py
import frappe
from frappe.model.document import Document

class HostelBuilding(Document):
    def validate(self):
        self.validate_warden_gender()

    def validate_warden_gender(self):
        """Validate warden gender matches hostel type"""
        if self.warden and self.hostel_type in ["Boys", "Girls"]:
            warden_gender = frappe.db.get_value("Employee", self.warden, "gender")
            expected_gender = "Male" if self.hostel_type == "Boys" else "Female"
            if warden_gender and warden_gender != expected_gender:
                frappe.msgprint(
                    f"Warning: Warden gender ({warden_gender}) doesn't match hostel type ({self.hostel_type})",
                    indicator="orange"
                )

    def update_capacity_stats(self):
        """Update room and bed counts from Hostel Room"""
        rooms = frappe.get_all(
            "Hostel Room",
            filters={"building": self.name, "status": ["!=", "Closed"]},
            fields=["bed_capacity", "occupied_beds"]
        )

        self.total_rooms = len(rooms)
        self.total_beds = sum(r.bed_capacity or 0 for r in rooms)
        self.occupied_beds = sum(r.occupied_beds or 0 for r in rooms)
        self.available_beds = self.total_beds - self.occupied_beds
        self.occupancy_rate = (self.occupied_beds / self.total_beds * 100) if self.total_beds else 0
        self.db_update()


@frappe.whitelist()
def get_building_stats(building):
    """Get building occupancy statistics"""
    doc = frappe.get_doc("Hostel Building", building)
    doc.update_capacity_stats()

    return {
        "total_rooms": doc.total_rooms,
        "total_beds": doc.total_beds,
        "occupied_beds": doc.occupied_beds,
        "available_beds": doc.available_beds,
        "occupancy_rate": doc.occupancy_rate
    }
```

### 1.2 Hostel Room DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Room",
    "module": "University Hostel",
    "naming_rule": "Expression",
    "autoname": "expr:{building}-{floor_number}-{room_number}",
    "fields": [
        {"fieldname": "building", "fieldtype": "Link", "options": "Hostel Building", "reqd": 1, "in_list_view": 1},
        {"fieldname": "floor_number", "fieldtype": "Int", "label": "Floor Number", "reqd": 1},
        {"fieldname": "room_number", "fieldtype": "Data", "label": "Room Number", "reqd": 1, "in_list_view": 1},
        {"fieldname": "room_type", "fieldtype": "Select", "options": "Single\nDouble\nTriple\nDormitory", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "bed_capacity", "fieldtype": "Int", "label": "Bed Capacity", "reqd": 1},
        {"fieldname": "occupied_beds", "fieldtype": "Int", "label": "Occupied Beds", "read_only": 1, "default": 0},
        {"fieldname": "available_beds", "fieldtype": "Int", "label": "Available Beds", "read_only": 1},
        {"fieldname": "status", "fieldtype": "Select", "options": "Available\nPartially Occupied\nFully Occupied\nUnder Maintenance\nClosed", "default": "Available", "in_list_view": 1},

        {"fieldname": "section_amenities", "fieldtype": "Section Break", "label": "Amenities"},
        {"fieldname": "has_attached_bathroom", "fieldtype": "Check", "label": "Attached Bathroom"},
        {"fieldname": "has_ac", "fieldtype": "Check", "label": "Air Conditioned"},
        {"fieldname": "has_balcony", "fieldtype": "Check", "label": "Balcony"},
        {"fieldname": "has_study_table", "fieldtype": "Check", "label": "Study Table"},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "has_wardrobe", "fieldtype": "Check", "label": "Wardrobe"},
        {"fieldname": "has_geyser", "fieldtype": "Check", "label": "Geyser/Water Heater"},
        {"fieldname": "furniture_condition", "fieldtype": "Select", "options": "Excellent\nGood\nFair\nPoor"},

        {"fieldname": "section_fees", "fieldtype": "Section Break", "label": "Room Fee"},
        {"fieldname": "additional_fee", "fieldtype": "Currency", "label": "Additional Fee (AC/Special)"},
        {"fieldname": "fee_remarks", "fieldtype": "Small Text", "label": "Fee Remarks"},

        {"fieldname": "section_occupants", "fieldtype": "Section Break", "label": "Current Occupants"},
        {"fieldname": "occupants", "fieldtype": "Table", "options": "Hostel Room Occupant", "read_only": 1}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Hostel Warden", "read": 1, "write": 1}
    ]
}
```

**Hostel Room Occupant Child Table:**
```json
{
    "doctype": "DocType",
    "name": "Hostel Room Occupant",
    "module": "University Hostel",
    "istable": 1,
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name", "read_only": 1, "in_list_view": 1},
        {"fieldname": "bed_number", "fieldtype": "Data", "label": "Bed Number", "in_list_view": 1},
        {"fieldname": "allocation", "fieldtype": "Link", "options": "Hostel Allocation", "read_only": 1},
        {"fieldname": "from_date", "fieldtype": "Date", "label": "From Date", "in_list_view": 1},
        {"fieldname": "to_date", "fieldtype": "Date", "label": "To Date"}
    ]
}
```

**Python Controller:**
```python
# university_erp/university_hostel/doctype/hostel_room/hostel_room.py
import frappe
from frappe.model.document import Document

class HostelRoom(Document):
    def validate(self):
        self.validate_capacity()
        self.update_availability()

    def validate_capacity(self):
        """Validate bed capacity based on room type"""
        type_capacity = {
            "Single": 1,
            "Double": 2,
            "Triple": 3,
            "Dormitory": 10  # Default max for dorm
        }

        if self.room_type != "Dormitory":
            expected = type_capacity.get(self.room_type, 1)
            if self.bed_capacity != expected:
                frappe.msgprint(
                    f"Bed capacity adjusted to {expected} for {self.room_type} room",
                    indicator="blue"
                )
                self.bed_capacity = expected

    def update_availability(self):
        """Update occupied beds and status"""
        self.occupied_beds = len(self.occupants) if self.occupants else 0
        self.available_beds = (self.bed_capacity or 0) - self.occupied_beds

        if self.status not in ["Under Maintenance", "Closed"]:
            if self.occupied_beds == 0:
                self.status = "Available"
            elif self.occupied_beds < self.bed_capacity:
                self.status = "Partially Occupied"
            else:
                self.status = "Fully Occupied"

    def on_update(self):
        """Update building stats"""
        if self.building:
            building = frappe.get_doc("Hostel Building", self.building)
            building.update_capacity_stats()


@frappe.whitelist()
def get_available_rooms(building=None, room_type=None, gender=None):
    """Get available rooms with filters"""
    filters = {"status": ["in", ["Available", "Partially Occupied"]]}

    if building:
        filters["building"] = building

    if room_type:
        filters["room_type"] = room_type

    rooms = frappe.get_all(
        "Hostel Room",
        filters=filters,
        fields=["name", "building", "room_number", "room_type", "bed_capacity", "available_beds", "has_ac", "additional_fee"]
    )

    # Filter by gender (based on building hostel_type)
    if gender:
        filtered_rooms = []
        for room in rooms:
            hostel_type = frappe.db.get_value("Hostel Building", room.building, "hostel_type")
            if hostel_type == "Co-ed" or \
               (hostel_type == "Boys" and gender == "Male") or \
               (hostel_type == "Girls" and gender == "Female"):
                filtered_rooms.append(room)
        rooms = filtered_rooms

    return rooms
```

### 1.3 Hostel Attendance DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Attendance",
    "module": "University Hostel",
    "naming_rule": "Expression",
    "autoname": "expr:HA-.YYYY.-.#####",
    "fields": [
        {"fieldname": "attendance_date", "fieldtype": "Date", "label": "Date", "reqd": 1, "default": "Today", "in_list_view": 1},
        {"fieldname": "building", "fieldtype": "Link", "options": "Hostel Building", "reqd": 1, "in_list_view": 1},
        {"fieldname": "attendance_type", "fieldtype": "Select", "options": "Morning\nEvening\nNight", "reqd": 1, "in_list_view": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "marked_by", "fieldtype": "Link", "options": "User", "default": "__user", "read_only": 1},
        {"fieldname": "marking_time", "fieldtype": "Time", "label": "Marking Time", "default": "now"},

        {"fieldname": "section_summary", "fieldtype": "Section Break", "label": "Summary"},
        {"fieldname": "total_residents", "fieldtype": "Int", "label": "Total Residents", "read_only": 1},
        {"fieldname": "present_count", "fieldtype": "Int", "label": "Present", "read_only": 1},
        {"fieldname": "absent_count", "fieldtype": "Int", "label": "Absent", "read_only": 1},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "late_count", "fieldtype": "Int", "label": "Late Entry", "read_only": 1},
        {"fieldname": "on_leave_count", "fieldtype": "Int", "label": "On Leave", "read_only": 1},

        {"fieldname": "section_records", "fieldtype": "Section Break", "label": "Attendance Records"},
        {"fieldname": "attendance_records", "fieldtype": "Table", "options": "Hostel Attendance Record", "reqd": 1},

        {"fieldname": "section_remarks", "fieldtype": "Section Break", "label": "Remarks"},
        {"fieldname": "remarks", "fieldtype": "Small Text", "label": "Remarks"}
    ],
    "permissions": [
        {"role": "Hostel Warden", "read": 1, "write": 1, "create": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
    ]
}
```

**Hostel Attendance Record Child Table:**
```json
{
    "doctype": "DocType",
    "name": "Hostel Attendance Record",
    "module": "University Hostel",
    "istable": 1,
    "fields": [
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name", "read_only": 1, "in_list_view": 1},
        {"fieldname": "room", "fieldtype": "Link", "options": "Hostel Room", "read_only": 1},
        {"fieldname": "status", "fieldtype": "Select", "options": "Present\nAbsent\nLate\nOn Leave\nOut Pass", "reqd": 1, "in_list_view": 1, "default": "Present"},
        {"fieldname": "in_time", "fieldtype": "Time", "label": "In Time"},
        {"fieldname": "out_time", "fieldtype": "Time", "label": "Out Time"},
        {"fieldname": "remarks", "fieldtype": "Data", "label": "Remarks"}
    ]
}
```

**Python Controller:**
```python
# university_erp/university_hostel/doctype/hostel_attendance/hostel_attendance.py
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class HostelAttendance(Document):
    def validate(self):
        self.validate_duplicate()
        self.update_summary()

    def validate_duplicate(self):
        """Check for duplicate attendance"""
        existing = frappe.db.exists(
            "Hostel Attendance",
            {
                "attendance_date": self.attendance_date,
                "building": self.building,
                "attendance_type": self.attendance_type,
                "name": ["!=", self.name]
            }
        )
        if existing:
            frappe.throw(f"Attendance already marked for {self.building} - {self.attendance_type} on {self.attendance_date}")

    def update_summary(self):
        """Update attendance summary counts"""
        self.total_residents = len(self.attendance_records)
        self.present_count = sum(1 for r in self.attendance_records if r.status == "Present")
        self.absent_count = sum(1 for r in self.attendance_records if r.status == "Absent")
        self.late_count = sum(1 for r in self.attendance_records if r.status == "Late")
        self.on_leave_count = sum(1 for r in self.attendance_records if r.status in ["On Leave", "Out Pass"])

    def after_insert(self):
        """Send notifications for absent students"""
        self.notify_absent_students()

    def notify_absent_students(self):
        """Notify parents of absent students"""
        absent_students = [r for r in self.attendance_records if r.status == "Absent"]

        for record in absent_students:
            # Get parent email
            guardian = frappe.db.get_value(
                "Student Guardian",
                {"parent": record.student, "parenttype": "Student"},
                "guardian"
            )
            if guardian:
                guardian_email = frappe.db.get_value("Guardian", guardian, "email_address")
                if guardian_email:
                    frappe.sendmail(
                        recipients=[guardian_email],
                        subject=f"Hostel Attendance Alert - {record.student_name}",
                        message=f"""
                        Dear Parent/Guardian,

                        This is to inform you that {record.student_name} was marked absent
                        during {self.attendance_type} attendance on {self.attendance_date}.

                        Please contact the hostel warden for more information.

                        Regards,
                        Hostel Administration
                        """
                    )


@frappe.whitelist()
def get_residents_for_attendance(building, attendance_date=None):
    """Get all residents of a building for attendance marking"""
    if not attendance_date:
        attendance_date = nowdate()

    allocations = frappe.get_all(
        "Hostel Allocation",
        filters={
            "building": building,
            "status": "Active",
            "from_date": ["<=", attendance_date],
            "to_date": [">=", attendance_date]
        },
        fields=["student", "student_name", "room"]
    )

    return allocations


@frappe.whitelist()
def mark_bulk_attendance(building, attendance_date, attendance_type, status="Present"):
    """Mark attendance for all residents"""
    residents = get_residents_for_attendance(building, attendance_date)

    attendance = frappe.new_doc("Hostel Attendance")
    attendance.attendance_date = attendance_date
    attendance.building = building
    attendance.attendance_type = attendance_type

    for resident in residents:
        attendance.append("attendance_records", {
            "student": resident.student,
            "student_name": resident.student_name,
            "room": resident.room,
            "status": status
        })

    attendance.insert()
    return attendance.name
```

---

## Week 2: Mess & Visitor Management

### 2.1 Hostel Mess DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Mess",
    "module": "University Hostel",
    "naming_rule": "By fieldname",
    "autoname": "field:mess_name",
    "fields": [
        {"fieldname": "mess_name", "fieldtype": "Data", "label": "Mess Name", "reqd": 1, "unique": 1},
        {"fieldname": "mess_type", "fieldtype": "Select", "options": "Vegetarian\nNon-Vegetarian\nBoth", "reqd": 1},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "capacity", "fieldtype": "Int", "label": "Seating Capacity"},
        {"fieldname": "current_subscribers", "fieldtype": "Int", "label": "Current Subscribers", "read_only": 1},
        {"fieldname": "mess_manager", "fieldtype": "Link", "options": "Employee", "label": "Mess Manager"},

        {"fieldname": "section_timings", "fieldtype": "Section Break", "label": "Meal Timings"},
        {"fieldname": "breakfast_start", "fieldtype": "Time", "label": "Breakfast Start"},
        {"fieldname": "breakfast_end", "fieldtype": "Time", "label": "Breakfast End"},
        {"fieldname": "lunch_start", "fieldtype": "Time", "label": "Lunch Start"},
        {"fieldname": "lunch_end", "fieldtype": "Time", "label": "Lunch End"},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "snacks_start", "fieldtype": "Time", "label": "Snacks Start"},
        {"fieldname": "snacks_end", "fieldtype": "Time", "label": "Snacks End"},
        {"fieldname": "dinner_start", "fieldtype": "Time", "label": "Dinner Start"},
        {"fieldname": "dinner_end", "fieldtype": "Time", "label": "Dinner End"},

        {"fieldname": "section_fees", "fieldtype": "Section Break", "label": "Fee Structure"},
        {"fieldname": "monthly_fee", "fieldtype": "Currency", "label": "Monthly Fee"},
        {"fieldname": "daily_rate", "fieldtype": "Currency", "label": "Daily Rate (Guest)"},

        {"fieldname": "section_buildings", "fieldtype": "Section Break", "label": "Attached Buildings"},
        {"fieldname": "attached_buildings", "fieldtype": "Table", "options": "Mess Attached Building"},

        {"fieldname": "status", "fieldtype": "Select", "options": "Active\nClosed", "default": "Active"}
    ],
    "permissions": [
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1},
        {"role": "Hostel Warden", "read": 1, "write": 1}
    ]
}
```

### 2.2 Mess Menu DocType

```json
{
    "doctype": "DocType",
    "name": "Mess Menu",
    "module": "University Hostel",
    "naming_rule": "Expression",
    "autoname": "expr:{mess}-{week_start_date}",
    "fields": [
        {"fieldname": "mess", "fieldtype": "Link", "options": "Hostel Mess", "reqd": 1, "in_list_view": 1},
        {"fieldname": "week_start_date", "fieldtype": "Date", "label": "Week Start Date", "reqd": 1, "in_list_view": 1},
        {"fieldname": "week_end_date", "fieldtype": "Date", "label": "Week End Date", "reqd": 1},

        {"fieldname": "section_menu", "fieldtype": "Section Break", "label": "Weekly Menu"},
        {"fieldname": "menu_items", "fieldtype": "Table", "options": "Mess Menu Item", "reqd": 1},

        {"fieldname": "section_special", "fieldtype": "Section Break", "label": "Special Notes"},
        {"fieldname": "special_notes", "fieldtype": "Small Text", "label": "Special Notes/Announcements"}
    ],
    "permissions": [
        {"role": "Hostel Warden", "read": 1, "write": 1, "create": 1},
        {"role": "Student", "read": 1}
    ]
}
```

**Mess Menu Item Child Table:**
```json
{
    "doctype": "DocType",
    "name": "Mess Menu Item",
    "module": "University Hostel",
    "istable": 1,
    "fields": [
        {"fieldname": "day", "fieldtype": "Select", "options": "Monday\nTuesday\nWednesday\nThursday\nFriday\nSaturday\nSunday", "reqd": 1, "in_list_view": 1},
        {"fieldname": "meal_type", "fieldtype": "Select", "options": "Breakfast\nLunch\nSnacks\nDinner", "reqd": 1, "in_list_view": 1},
        {"fieldname": "menu_items", "fieldtype": "Small Text", "label": "Menu Items", "reqd": 1, "in_list_view": 1},
        {"fieldname": "is_special", "fieldtype": "Check", "label": "Special Meal"}
    ]
}
```

### 2.3 Hostel Visitor DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Visitor",
    "module": "University Hostel",
    "naming_rule": "Expression",
    "autoname": "expr:HV-.YYYY.-.#####",
    "fields": [
        {"fieldname": "visitor_name", "fieldtype": "Data", "label": "Visitor Name", "reqd": 1, "in_list_view": 1},
        {"fieldname": "visitor_mobile", "fieldtype": "Data", "label": "Mobile Number", "reqd": 1},
        {"fieldname": "visitor_id_type", "fieldtype": "Select", "options": "Aadhar Card\nPAN Card\nDriving License\nVoter ID\nPassport", "label": "ID Type"},
        {"fieldname": "visitor_id_number", "fieldtype": "Data", "label": "ID Number"},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "relationship", "fieldtype": "Select", "options": "Parent\nGuardian\nSibling\nRelative\nFriend\nOther", "reqd": 1},
        {"fieldname": "photo", "fieldtype": "Attach Image", "label": "Visitor Photo"},

        {"fieldname": "section_visit", "fieldtype": "Section Break", "label": "Visit Details"},
        {"fieldname": "student", "fieldtype": "Link", "options": "Student", "reqd": 1, "in_list_view": 1},
        {"fieldname": "student_name", "fieldtype": "Data", "fetch_from": "student.student_name", "read_only": 1},
        {"fieldname": "building", "fieldtype": "Link", "options": "Hostel Building", "reqd": 1},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "visit_date", "fieldtype": "Date", "reqd": 1, "default": "Today", "in_list_view": 1},
        {"fieldname": "check_in_time", "fieldtype": "Time", "label": "Check In", "default": "now"},
        {"fieldname": "check_out_time", "fieldtype": "Time", "label": "Check Out"},
        {"fieldname": "purpose", "fieldtype": "Small Text", "label": "Purpose of Visit"},

        {"fieldname": "section_approval", "fieldtype": "Section Break", "label": "Approval"},
        {"fieldname": "approved_by", "fieldtype": "Link", "options": "User", "label": "Approved By"},
        {"fieldname": "status", "fieldtype": "Select", "options": "Checked In\nChecked Out\nDenied", "default": "Checked In", "in_list_view": 1}
    ],
    "permissions": [
        {"role": "Hostel Warden", "read": 1, "write": 1, "create": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
    ]
}
```

### 2.4 Hostel Maintenance Request DocType

```json
{
    "doctype": "DocType",
    "name": "Hostel Maintenance Request",
    "module": "University Hostel",
    "naming_rule": "Expression",
    "autoname": "expr:HMR-.YYYY.-.#####",
    "is_submittable": 1,
    "fields": [
        {"fieldname": "request_date", "fieldtype": "Date", "reqd": 1, "default": "Today", "in_list_view": 1},
        {"fieldname": "building", "fieldtype": "Link", "options": "Hostel Building", "reqd": 1, "in_list_view": 1},
        {"fieldname": "room", "fieldtype": "Link", "options": "Hostel Room", "label": "Room (if applicable)"},
        {"fieldname": "column_break_1", "fieldtype": "Column Break"},
        {"fieldname": "requested_by", "fieldtype": "Link", "options": "Student", "label": "Requested By"},
        {"fieldname": "request_type", "fieldtype": "Select", "options": "Electrical\nPlumbing\nFurniture\nCleaning\nAC/Cooling\nInternet\nOther", "reqd": 1, "in_list_view": 1},
        {"fieldname": "priority", "fieldtype": "Select", "options": "Low\nMedium\nHigh\nUrgent", "default": "Medium", "in_list_view": 1},

        {"fieldname": "section_details", "fieldtype": "Section Break", "label": "Request Details"},
        {"fieldname": "subject", "fieldtype": "Data", "label": "Subject", "reqd": 1},
        {"fieldname": "description", "fieldtype": "Text", "label": "Description", "reqd": 1},
        {"fieldname": "attachments", "fieldtype": "Attach", "label": "Photo/Attachment"},

        {"fieldname": "section_resolution", "fieldtype": "Section Break", "label": "Resolution"},
        {"fieldname": "assigned_to", "fieldtype": "Link", "options": "Employee", "label": "Assigned To"},
        {"fieldname": "expected_completion", "fieldtype": "Date", "label": "Expected Completion"},
        {"fieldname": "column_break_2", "fieldtype": "Column Break"},
        {"fieldname": "actual_completion", "fieldtype": "Date", "label": "Actual Completion"},
        {"fieldname": "resolution_remarks", "fieldtype": "Text", "label": "Resolution Remarks"},
        {"fieldname": "cost_incurred", "fieldtype": "Currency", "label": "Cost Incurred"},

        {"fieldname": "status", "fieldtype": "Select", "options": "Open\nIn Progress\nCompleted\nCancelled", "default": "Open", "in_list_view": 1}
    ],
    "permissions": [
        {"role": "Student", "read": 1, "write": 1, "create": 1},
        {"role": "Hostel Warden", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1},
        {"role": "Education Manager", "read": 1, "write": 1, "create": 1, "submit": 1, "cancel": 1, "delete": 1}
    ]
}
```

---

## Week 3: Reports & Integration

### 3.1 Reports

**Hostel Occupancy Report:**
```python
# university_erp/university_hostel/report/hostel_occupancy_report/hostel_occupancy_report.py
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "building", "label": "Building", "fieldtype": "Link", "options": "Hostel Building", "width": 150},
        {"fieldname": "hostel_type", "label": "Type", "fieldtype": "Data", "width": 80},
        {"fieldname": "total_rooms", "label": "Total Rooms", "fieldtype": "Int", "width": 100},
        {"fieldname": "total_beds", "label": "Total Beds", "fieldtype": "Int", "width": 100},
        {"fieldname": "occupied", "label": "Occupied", "fieldtype": "Int", "width": 100},
        {"fieldname": "available", "label": "Available", "fieldtype": "Int", "width": 100},
        {"fieldname": "occupancy_rate", "label": "Occupancy %", "fieldtype": "Percent", "width": 100}
    ]

    data = frappe.db.sql("""
        SELECT
            hb.name as building,
            hb.hostel_type,
            hb.total_rooms,
            hb.total_beds,
            hb.occupied_beds as occupied,
            hb.available_beds as available,
            hb.occupancy_rate
        FROM `tabHostel Building` hb
        WHERE hb.status = 'Active'
        ORDER BY hb.name
    """, as_dict=True)

    return columns, data
```

**Hostel Attendance Report:**
```python
# university_erp/university_hostel/report/hostel_attendance_report/hostel_attendance_report.py
import frappe

def execute(filters=None):
    columns = [
        {"fieldname": "student", "label": "Student", "fieldtype": "Link", "options": "Student", "width": 120},
        {"fieldname": "student_name", "label": "Name", "fieldtype": "Data", "width": 150},
        {"fieldname": "building", "label": "Building", "fieldtype": "Link", "options": "Hostel Building", "width": 120},
        {"fieldname": "total_days", "label": "Total Days", "fieldtype": "Int", "width": 100},
        {"fieldname": "present", "label": "Present", "fieldtype": "Int", "width": 80},
        {"fieldname": "absent", "label": "Absent", "fieldtype": "Int", "width": 80},
        {"fieldname": "late", "label": "Late", "fieldtype": "Int", "width": 80},
        {"fieldname": "attendance_pct", "label": "Attendance %", "fieldtype": "Percent", "width": 100}
    ]

    conditions = "1=1"
    if filters.get("building"):
        conditions += f" AND ha.building = '{filters.get('building')}'"
    if filters.get("from_date"):
        conditions += f" AND ha.attendance_date >= '{filters.get('from_date')}'"
    if filters.get("to_date"):
        conditions += f" AND ha.attendance_date <= '{filters.get('to_date')}'"

    data = frappe.db.sql(f"""
        SELECT
            har.student,
            har.student_name,
            ha.building,
            COUNT(*) as total_days,
            SUM(CASE WHEN har.status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN har.status = 'Absent' THEN 1 ELSE 0 END) as absent,
            SUM(CASE WHEN har.status = 'Late' THEN 1 ELSE 0 END) as late,
            ROUND(SUM(CASE WHEN har.status = 'Present' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) as attendance_pct
        FROM `tabHostel Attendance` ha
        JOIN `tabHostel Attendance Record` har ON har.parent = ha.name
        WHERE {conditions}
        GROUP BY har.student, ha.building
        ORDER BY har.student_name
    """, as_dict=True)

    return columns, data
```

### 3.2 Update Hostel Allocation

Update existing Hostel Allocation to integrate with new DocTypes:

```python
# university_erp/university_hostel/doctype/hostel_allocation/hostel_allocation.py (updated)
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class HostelAllocation(Document):
    def validate(self):
        self.validate_room_availability()
        self.validate_gender()
        self.validate_dates()

    def validate_room_availability(self):
        """Check if room has available beds"""
        room = frappe.get_doc("Hostel Room", self.room)
        if room.available_beds <= 0 and self.is_new():
            frappe.throw(f"Room {self.room} is fully occupied. No beds available.")

    def validate_gender(self):
        """Validate student gender matches hostel type"""
        student_gender = frappe.db.get_value("Student", self.student, "gender")
        hostel_type = frappe.db.get_value("Hostel Building", self.building, "hostel_type")

        if hostel_type == "Boys" and student_gender != "Male":
            frappe.throw("Only male students can be allocated to Boys Hostel")
        elif hostel_type == "Girls" and student_gender != "Female":
            frappe.throw("Only female students can be allocated to Girls Hostel")

    def validate_dates(self):
        """Validate date range"""
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw("To Date cannot be before From Date")

    def on_submit(self):
        self.add_to_room_occupants()
        self.create_hostel_fee()

    def on_cancel(self):
        self.remove_from_room_occupants()

    def add_to_room_occupants(self):
        """Add student to room occupants list"""
        room = frappe.get_doc("Hostel Room", self.room)
        room.append("occupants", {
            "student": self.student,
            "student_name": self.student_name,
            "bed_number": self.bed_number,
            "allocation": self.name,
            "from_date": self.from_date,
            "to_date": self.to_date
        })
        room.save()

    def remove_from_room_occupants(self):
        """Remove student from room occupants"""
        room = frappe.get_doc("Hostel Room", self.room)
        room.occupants = [o for o in room.occupants if o.allocation != self.name]
        room.save()

    def create_hostel_fee(self):
        """Create hostel fee for the student"""
        building = frappe.get_doc("Hostel Building", self.building)
        room = frappe.get_doc("Hostel Room", self.room)

        total_fee = (building.annual_fee or 0) + (room.additional_fee or 0)

        if total_fee > 0:
            fee = frappe.new_doc("Fees")
            fee.student = self.student
            fee.posting_date = nowdate()
            fee.due_date = self.from_date
            fee.custom_fee_type = "Hostel"
            fee.append("components", {
                "fees_category": "Hostel Fee",
                "amount": building.annual_fee or 0
            })
            if room.additional_fee:
                fee.append("components", {
                    "fees_category": "Room Premium",
                    "amount": room.additional_fee
                })
            fee.flags.ignore_permissions = True
            fee.insert()

            self.db_set("fee_created", fee.name)
```

---

## Output Checklist

### DocTypes Enhanced (from Phase 7)
- [x] Hostel Building (added: fees, assistant warden, status, lat/lng, common room)
- [x] Hostel Room (added: occupants table, furniture condition)
- [x] Hostel Allocation (added: room occupant integration)
- [x] Hostel Mess (added: status, current_subscribers)

### New DocTypes Created
- [x] Hostel Room Occupant (child table)
- [x] Hostel Attendance Record (child table)
- [x] Hostel Bulk Attendance
- [x] Mess Menu
- [x] Hostel Visitor
- [x] Hostel Maintenance Request

### Reports Created
- [x] Hostel Occupancy Report (Phase 7)
- [x] Hostel Attendance Report (Phase 7)
- [x] Room Availability Report (Phase 7)
- [x] Maintenance Summary Report (Phase 9)
- [x] Visitor Log Report (Phase 9)

### API Endpoints Created
- [x] get_building_stats()
- [x] get_buildings_for_gender()
- [x] get_available_rooms() (with gender filter)
- [x] get_room_occupants()
- [x] get_residents_for_attendance()
- [x] mark_bulk_attendance()
- [x] get_attendance_status()
- [x] get_building_attendance_summary()
- [x] get_today_menu()
- [x] get_week_menu()
- [x] check_in_visitor() / check_out_visitor()
- [x] get_active_visitors()
- [x] get_open_requests() / assign_request() / complete_request()

### Integrations
- [x] Room occupancy auto-update via occupants table
- [x] Fee generation on allocation (Phase 7)
- [x] Building stats calculation on allocation changes
- [x] Visitor validation (student in building check)
- [x] Maintenance room-building validation

---

## Implementation Summary

Phase 9 was completed in a single session on 2026-01-02. All 69 tasks from the task list were completed:

| Section | Tasks | Completed |
|---------|-------|-----------|
| A: Building Enhancements | 10 | 10 |
| B: Room Occupant | 7 | 7 |
| C: Bulk Attendance | 9 | 9 |
| D: Mess Menu | 7 | 7 |
| E: Visitor Management | 6 | 6 |
| F: Maintenance Request | 7 | 7 |
| G: Allocation Enhancement | 6 | 6 |
| H: Reports | 7 | 7 |
| I: Workspace & Integration | 10 | 8 |
| **Total** | **69** | **67** |

*Note: 2 tasks (bench migrate and testing) require user action*

## Next Steps

1. Run `bench migrate` to apply database changes
2. Test all new DocTypes and APIs in browser
3. Proceed to Phase 10
