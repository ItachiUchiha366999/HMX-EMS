# University Hostel Module

## Overview

The University Hostel module manages hostel buildings, rooms, student allocations, attendance, mess management, and maintenance requests. It provides comprehensive residential facility management for universities.

## Module Location
```
university_erp/university_hostel/
```

## DocTypes (14 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Hostel Building | Main | Hostel/dormitory buildings |
| Hostel Room | Main | Individual rooms |
| Hostel Room Occupant | Child | Room occupancy details |
| Hostel Allocation | Main | Student room assignment |
| Hostel Attendance | Main | Daily attendance record |
| Hostel Attendance Record | Child | Individual attendance |
| Hostel Bulk Attendance | Main | Bulk attendance entry |
| Hostel Mess | Main | Mess/cafeteria management |
| Mess Menu | Main | Weekly menu |
| Mess Menu Item | Child | Daily meal items |
| Hostel Visitor | Main | Visitor log |
| Hostel Maintenance Request | Main | Maintenance tickets |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                    UNIVERSITY HOSTEL MODULE                       |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+                                            |
|  | HOSTEL BUILDING   |                                            |
|  +-------------------+                                            |
|           |                                                       |
|           v                                                       |
|  +-------------------+       +-------------------+                |
|  |   HOSTEL ROOM     |------>| Room Occupant     |                |
|  +-------------------+       | (Child Table)     |                |
|           |                  +-------------------+                |
|           v                                                       |
|  +-------------------+       +-------------------+                |
|  | HOSTEL ALLOCATION |------>|     STUDENT       |                |
|  +-------------------+       | (Education App)   |                |
|           |                  +-------------------+                |
|           v                                                       |
|  +-------------------+       +-------------------+                |
|  | HOSTEL ATTENDANCE |       |   HOSTEL MESS     |                |
|  +-------------------+       +-------------------+                |
|  | - Daily check-in  |       | - Cafeteria       |                |
|  | - Bulk entry      |       | - Menu planning   |                |
|  +-------------------+       +-------------------+                |
|                                      |                            |
|                                      v                            |
|                              +-------------------+                |
|                              |    MESS MENU      |                |
|                              +-------------------+                |
|                                                                   |
|  +-------------------+       +-------------------+                |
|  | HOSTEL VISITOR    |       | MAINTENANCE       |                |
|  +-------------------+       |    REQUEST        |                |
|  | - Guest log       |       +-------------------+                |
|  | - Approval        |       | - Repairs         |                |
|  +-------------------+       | - Complaints      |                |
|                              +-------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Education App Integration
```
+--------------------+       +--------------------+
|  UNIVERSITY        |       |    EDUCATION       |
|    HOSTEL          |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Hostel Allocation--|------>| Student            |
|                    |       | Program            |
|                    |       | Student Group      |
+--------------------+       +--------------------+
```

### Finance Integration
```
+--------------------+       +--------------------+
|  UNIVERSITY        |       |    FINANCE         |
|    HOSTEL          |------>|                    |
+--------------------+       +--------------------+
|                    |       |                    |
| Hostel Allocation--|------>| Fee Generation     |
|   (on confirm)     |       | (Hostel Fee)       |
+--------------------+       +--------------------+
```

## DocType Details

### 1. Hostel Building
**Purpose**: Building/dormitory master data

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| building_name | Data | e.g., "Men's Hostel A" |
| building_code | Data | Short code |
| hostel_type | Select | Boys/Girls/Co-ed |
| total_floors | Int | Number of floors |
| total_rooms | Int | Room count |
| warden | Link (Employee) | Chief warden |
| assistant_warden | Link (Employee) | Assistant |
| contact_number | Data | Emergency contact |
| address | Small Text | Location |
| amenities | Table MultiSelect | Available facilities |
| status | Select | Active/Under Maintenance |

### 2. Hostel Room
**Purpose**: Individual room inventory

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| room_number | Data | Room identifier |
| building | Link (Hostel Building) | Parent building |
| floor | Int | Floor number |
| room_type | Select | Single/Double/Triple/Dorm |
| capacity | Int | Maximum occupancy |
| current_occupancy | Int | Current students |
| room_status | Select | Available/Occupied/Maintenance |
| has_attached_bathroom | Check | Bathroom attached |
| has_ac | Check | Air conditioning |
| monthly_rent | Currency | Room charges |
| occupants | Table | Current occupants |

**Room Status Logic**:
```
Available: current_occupancy < capacity
Occupied: current_occupancy == capacity
Maintenance: Under repair/renovation
```

### 3. Hostel Room Occupant (Child Table)
**Purpose**: Track current room occupants

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| student_name | Data | Name |
| bed_number | Data | Bed assignment |
| from_date | Date | Occupancy start |
| to_date | Date | Expected end |

### 4. Hostel Allocation
**Purpose**: Assign student to hostel room

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| student_name | Data | Name |
| academic_year | Link | Academic year |
| building | Link (Hostel Building) | Building |
| room | Link (Hostel Room) | Assigned room |
| bed_number | Data | Bed number |
| allocation_date | Date | Assignment date |
| from_date | Date | Start date |
| to_date | Date | End date |
| allocation_type | Select | Fresh/Renewal |
| fee_status | Select | Paid/Pending |
| status | Select | Active/Vacated/Transferred |

**Workflow**:
```
Applied --> Approved --> Room Assigned --> Active
                                             |
        +----------------------------------+
        |                |                 |
        v                v                 v
   Transferred       Vacated          Renewed
```

### 5. Hostel Attendance
**Purpose**: Daily attendance tracking

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| building | Link (Hostel Building) | Building |
| attendance_date | Date | Date |
| attendance_time | Select | Morning/Evening/Night |
| attendance_records | Table | Student-wise attendance |
| present_count | Int | Present students |
| absent_count | Int | Absent students |
| taken_by | Link (User) | Warden/Staff |

### 6. Hostel Attendance Record (Child Table)
**Purpose**: Individual attendance entry

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| room | Link (Hostel Room) | Room |
| status | Select | Present/Absent/On Leave |
| remarks | Data | Notes |

### 7. Hostel Mess
**Purpose**: Mess/cafeteria management

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| mess_name | Data | e.g., "Main Mess" |
| building | Link (Hostel Building) | Serves which building |
| capacity | Int | Seating capacity |
| meal_times | Table | Breakfast/Lunch/Dinner timings |
| manager | Link (Employee) | Mess manager |
| monthly_charges | Currency | Mess fees |
| status | Select | Active/Closed |

### 8. Mess Menu
**Purpose**: Weekly meal planning

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| mess | Link (Hostel Mess) | Mess |
| week_start_date | Date | Week starting |
| week_end_date | Date | Week ending |
| menu_items | Table | Daily menu |
| special_notes | Text | Special occasions |

### 9. Mess Menu Item (Child Table)
**Purpose**: Daily meal items

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| day | Select | Monday-Sunday |
| meal_type | Select | Breakfast/Lunch/Snacks/Dinner |
| items | Small Text | Menu items |
| is_special | Check | Special menu |

### 10. Hostel Visitor
**Purpose**: Guest/visitor log

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student being visited |
| visitor_name | Data | Visitor name |
| visitor_relation | Select | Parent/Sibling/Friend |
| visitor_phone | Data | Contact |
| visitor_id | Data | ID proof number |
| purpose | Small Text | Visit reason |
| check_in | Datetime | Entry time |
| check_out | Datetime | Exit time |
| approved_by | Link (User) | Warden approval |
| status | Select | Pending/Approved/Checked Out |

### 11. Hostel Maintenance Request
**Purpose**: Maintenance and complaint tickets

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| request_type | Select | Electrical/Plumbing/Carpentry/Cleaning |
| building | Link (Hostel Building) | Building |
| room | Link (Hostel Room) | Room (if applicable) |
| reported_by | Link (Student) | Student reporting |
| description | Text | Issue description |
| priority | Select | Low/Medium/High/Urgent |
| assigned_to | Data | Maintenance staff |
| resolution_date | Date | Expected resolution |
| actual_resolution_date | Date | Actual completion |
| resolution_notes | Text | Work done |
| status | Select | Open/In Progress/Resolved/Closed |

## Data Flow Diagrams

### Hostel Allocation Flow
```
+----------------+     +------------------+     +------------------+
| Student        |---->| Hostel           |---->| Room             |
| Applies        |     | Application      |     | Availability     |
+----------------+     +------------------+     | Check            |
                                               +------------------+
                                                       |
+----------------+     +------------------+            |
|   ACTIVE       |<----| Hostel           |<-----------+
|   ALLOCATION   |     | Allocation       |
+----------------+     | Created          |
       |               +------------------+
       v
+----------------+
| Fee Generated  |
| (Hostel Fee)   |
+----------------+
```

### Attendance Flow
```
+----------------+     +------------------+     +------------------+
|   Warden/      |---->|     Select       |---->|   Mark           |
|   Staff        |     |     Building     |     |   Attendance     |
+----------------+     +------------------+     +------------------+
                                                       |
                                                       v
                                               +------------------+
                                               | Hostel           |
                                               | Attendance       |
                                               | Record Created   |
                                               +------------------+
                                                       |
                         +-----------------------------+
                         |                             |
                         v                             v
                +----------------+            +----------------+
                |   Absent       |            |   Report to    |
                |   Notification |            |   Parents      |
                +----------------+            +----------------+
```

### Room Hierarchy
```
+---------------------+
|   HOSTEL BUILDING   |
|   (Men's Hostel A)  |
+---------------------+
         |
         +-- Floor 1
         |      |
         |      +-- Room 101 (Double, 2/2 occupied)
         |      |      +-- Student A (Bed 1)
         |      |      +-- Student B (Bed 2)
         |      |
         |      +-- Room 102 (Triple, 2/3 occupied)
         |             +-- Student C (Bed 1)
         |             +-- Student D (Bed 2)
         |             +-- [Vacant] (Bed 3)
         |
         +-- Floor 2
                |
                +-- Room 201 (Single, 0/1 occupied)
                       +-- [Available]
```

## Integration Points

### With Finance Module
```python
# Generate hostel fee on allocation
def on_hostel_allocation_confirm(doc, method):
    if doc.status == "Active":
        # Create hostel fee
        from university_erp.fees_finance.api import create_hostel_fee

        fee = create_hostel_fee(
            student=doc.student,
            building=doc.building,
            room=doc.room,
            from_date=doc.from_date,
            to_date=doc.to_date
        )
        doc.fee_reference = fee.name
        doc.fee_status = "Pending"
        doc.save()
```

### Room Occupancy Update
```python
def update_room_occupancy(room):
    """Update room occupancy count"""
    count = frappe.db.count("Hostel Allocation", {
        "room": room,
        "status": "Active"
    })
    frappe.db.set_value("Hostel Room", room, "current_occupancy", count)

    # Update room status
    room_doc = frappe.get_doc("Hostel Room", room)
    if count >= room_doc.capacity:
        room_doc.room_status = "Occupied"
    elif count > 0:
        room_doc.room_status = "Partially Occupied"
    else:
        room_doc.room_status = "Available"
    room_doc.save()
```

### Attendance Notifications
```python
def send_absence_notification(attendance_record):
    """Notify parents of student absence"""
    if attendance_record.status == "Absent":
        student = frappe.get_doc("Student", attendance_record.student)
        guardian_email = get_guardian_email(student)

        frappe.sendmail(
            recipients=[guardian_email],
            subject=f"Hostel Absence Alert: {student.student_name}",
            message=f"Your ward was absent from hostel on {attendance_record.attendance_date}"
        )
```

## API Endpoints

### Room Availability
```python
@frappe.whitelist()
def get_available_rooms(building, room_type=None):
    """Get available rooms in building"""
    filters = {
        "building": building,
        "room_status": ["in", ["Available", "Partially Occupied"]]
    }
    if room_type:
        filters["room_type"] = room_type

    rooms = frappe.get_all("Hostel Room", filters=filters,
        fields=["name", "room_number", "room_type", "capacity",
                "current_occupancy", "monthly_rent"])

    return [r for r in rooms if r.current_occupancy < r.capacity]
```

### Allocation
```python
@frappe.whitelist()
def allocate_room(student, building, room, bed_number):
    """Allocate room to student"""
    # Check availability
    room_doc = frappe.get_doc("Hostel Room", room)
    if room_doc.current_occupancy >= room_doc.capacity:
        frappe.throw("Room is fully occupied")

    allocation = frappe.new_doc("Hostel Allocation")
    allocation.student = student
    allocation.building = building
    allocation.room = room
    allocation.bed_number = bed_number
    allocation.from_date = frappe.utils.today()
    allocation.insert()

    return allocation
```

## Reports

1. **Room Occupancy Report** - Building-wise occupancy
2. **Hostel Attendance Report** - Daily/monthly attendance
3. **Vacancy Report** - Available rooms
4. **Maintenance Report** - Open/resolved tickets
5. **Fee Collection Report** - Hostel fee status
6. **Visitor Log Report** - Guest records

## Related Files

```
university_erp/
+-- university_hostel/
    +-- doctype/
    |   +-- hostel_building/
    |   +-- hostel_room/
    |   +-- hostel_room_occupant/
    |   +-- hostel_allocation/
    |   +-- hostel_attendance/
    |   +-- hostel_attendance_record/
    |   +-- hostel_bulk_attendance/
    |   +-- hostel_mess/
    |   +-- mess_menu/
    |   +-- mess_menu_item/
    |   +-- hostel_visitor/
    |   +-- hostel_maintenance_request/
    +-- api.py
```

## See Also

- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [University Transport Module](08_UNIVERSITY_TRANSPORT.md)
- [Student Info Module](03_STUDENT_INFO.md)
