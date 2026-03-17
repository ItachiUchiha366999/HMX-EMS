# University Transport Module

## Overview

The University Transport module manages transportation services including routes, vehicles, student allocations, and trip logging. It provides complete fleet management for university bus services.

## Module Location
```
university_erp/university_transport/
```

## DocTypes (5 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Transport Route | Main | Bus route definitions |
| Transport Route Stop | Child | Stops along route |
| Transport Vehicle | Main | Vehicle inventory |
| Transport Allocation | Main | Student-route assignment |
| Transport Trip Log | Main | Daily trip records |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                   UNIVERSITY TRANSPORT MODULE                     |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  | TRANSPORT ROUTE   |       | TRANSPORT VEHICLE |                |
|  +-------------------+       +-------------------+                |
|  | - Route name      |       | - Vehicle number  |                |
|  | - Stops           |       | - Capacity        |                |
|  | - Timings         |       | - Driver          |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           +-------------+-------------+                           |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              |    TRANSPORT      |                                |
|              |   ALLOCATION      |                                |
|              +-------------------+                                |
|              | - Student         |                                |
|              | - Route           |                                |
|              | - Pickup point    |                                |
|              +-------------------+                                |
|                         |                                         |
|                         v                                         |
|              +-------------------+                                |
|              | TRANSPORT TRIP    |                                |
|              |      LOG          |                                |
|              +-------------------+                                |
|              | - Date            |                                |
|              | - Vehicle         |                                |
|              | - Route           |                                |
|              | - Passengers      |                                |
|              +-------------------+                                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### Module Dependencies
```
+--------------------+       +--------------------+
|    TRANSPORT       |       |    EDUCATION       |
|     (Custom)       |------>|       (App)        |
+--------------------+       +--------------------+
|                    |       |                    |
| Transport          |       | Student            |
| Allocation --------|------>| (passenger)        |
|                    |       |                    |
+--------------------+       +--------------------+

+--------------------+       +--------------------+
|    TRANSPORT       |       |    FINANCE         |
|     (Custom)       |------>|                    |
+--------------------+       +--------------------+
|                    |       |                    |
| Allocation --------|------>| Fee Generation     |
| (on confirm)       |       | (Transport Fee)    |
+--------------------+       +--------------------+
```

## DocType Details

### 1. Transport Route
**Purpose**: Define bus routes

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| route_name | Data | e.g., "Route A - City Center" |
| route_code | Data | Short code |
| route_type | Select | Regular/Express/Special |
| start_point | Data | Origin location |
| end_point | Data | Destination |
| total_distance | Float | Distance in km |
| estimated_duration | Int | Minutes |
| morning_departure | Time | Morning start time |
| evening_departure | Time | Evening start time |
| stops | Table | Route stops |
| monthly_fee | Currency | Route fee |
| assigned_vehicle | Link (Transport Vehicle) | Primary vehicle |
| status | Select | Active/Inactive |

### 2. Transport Route Stop (Child Table)
**Purpose**: Stops along route

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| stop_name | Data | Stop location |
| stop_order | Int | Sequence number |
| pickup_time | Time | Morning pickup |
| drop_time | Time | Evening drop |
| distance_from_start | Float | Distance in km |
| landmark | Data | Nearby landmark |
| additional_fee | Currency | Extra charge |

### 3. Transport Vehicle
**Purpose**: Vehicle fleet inventory

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| vehicle_number | Data | Registration number |
| vehicle_type | Select | Bus/Mini Bus/Van |
| make | Data | Manufacturer |
| model | Data | Model name |
| year | Int | Manufacturing year |
| seating_capacity | Int | Passenger capacity |
| driver | Link (Employee) | Primary driver |
| conductor | Link (Employee) | Conductor |
| insurance_expiry | Date | Insurance validity |
| fitness_expiry | Date | Fitness certificate |
| fuel_type | Select | Diesel/Petrol/CNG/Electric |
| assigned_route | Link (Transport Route) | Default route |
| status | Select | Active/Maintenance/Retired |

### 4. Transport Allocation
**Purpose**: Student transport registration

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| student | Link (Student) | Student |
| student_name | Data | Name (fetched) |
| academic_year | Link | Academic year |
| route | Link (Transport Route) | Assigned route |
| pickup_stop | Data | Boarding point |
| drop_stop | Data | Alighting point |
| allocation_date | Date | Registration date |
| from_date | Date | Service start |
| to_date | Date | Service end |
| pass_number | Data | Transport pass ID |
| monthly_fee | Currency | Monthly charges |
| fee_status | Select | Paid/Pending |
| status | Select | Active/Suspended/Cancelled |

**Auto-Naming**: TRP-.YYYY.-#####

### 5. Transport Trip Log
**Purpose**: Daily trip records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| trip_date | Date | Trip date |
| route | Link (Transport Route) | Route |
| vehicle | Link (Transport Vehicle) | Vehicle used |
| driver | Link (Employee) | Driver |
| trip_type | Select | Morning/Evening |
| departure_time | Time | Actual departure |
| arrival_time | Time | Actual arrival |
| start_odometer | Float | Starting reading |
| end_odometer | Float | Ending reading |
| total_passengers | Int | Passenger count |
| fuel_consumed | Float | Liters |
| remarks | Text | Trip notes |
| status | Select | Scheduled/Completed/Cancelled |

## Data Flow Diagrams

### Transport Registration Flow
```
+----------------+     +------------------+     +------------------+
|   Student      |---->|   Select Route   |---->|   Select Stop    |
|   Applies      |     |   & Schedule     |     |   Pickup/Drop    |
+----------------+     +------------------+     +------------------+
                                                        |
                                                        v
+----------------+     +------------------+     +------------------+
|   TRANSPORT    |<----|   Verify         |<----|   Check          |
|   ALLOCATION   |     |   Capacity       |     |   Availability   |
|   Created      |     +------------------+     +------------------+
+----------------+
       |
       v
+----------------+
| Fee Generated  |
| (Transport Fee)|
+----------------+
       |
       v
+----------------+
| Pass Issued    |
| to Student     |
+----------------+
```

### Daily Trip Flow
```
+----------------+     +------------------+     +------------------+
|   Morning      |---->|   Trip Log       |---->|   Route          |
|   Departure    |     |   Created        |     |   Completed      |
+----------------+     +------------------+     +------------------+
                              |
                              v
                    +------------------+
                    |   Record         |
                    |   - Passengers   |
                    |   - Odometer     |
                    |   - Time         |
                    +------------------+
```

### Route Visualization
```
Route A: University <---> City Center

+----------+    +----------+    +----------+    +------------+
|University|    |  Stop 1  |    |  Stop 2  |    |City Center |
|  Campus  |--->|  Market  |--->|  Station |--->|   (End)    |
+----------+    +----------+    +----------+    +------------+
   7:00 AM       7:15 AM        7:30 AM         7:45 AM

   5:00 PM       5:15 PM        5:30 PM         5:45 PM
   (Return)     <----           <----           <----
```

## Integration Points

### With Finance Module
```python
# Generate transport fee on allocation
def on_transport_allocation_confirm(doc, method):
    if doc.status == "Active":
        from university_erp.fees_finance.api import create_transport_fee

        fee = create_transport_fee(
            student=doc.student,
            route=doc.route,
            from_date=doc.from_date,
            to_date=doc.to_date,
            monthly_fee=doc.monthly_fee
        )
        doc.fee_reference = fee.name
        doc.save()
```

### Capacity Check
```python
def check_route_capacity(route, stop):
    """Check if route has capacity at given stop"""
    route_doc = frappe.get_doc("Transport Route", route)
    vehicle = frappe.get_doc("Transport Vehicle", route_doc.assigned_vehicle)

    current_allocations = frappe.db.count("Transport Allocation", {
        "route": route,
        "pickup_stop": stop,
        "status": "Active"
    })

    return {
        "capacity": vehicle.seating_capacity,
        "allocated": current_allocations,
        "available": vehicle.seating_capacity - current_allocations
    }
```

### Pass Generation
```python
def generate_transport_pass(allocation):
    """Generate transport pass for student"""
    pass_number = frappe.generate_hash(allocation.name, 8).upper()

    allocation.pass_number = f"TRP-{pass_number}"
    allocation.save()

    # Can integrate with ID card printing system
    return allocation.pass_number
```

## API Endpoints

### Route Management
```python
@frappe.whitelist()
def get_routes_with_availability():
    """Get all routes with current availability"""
    routes = frappe.get_all("Transport Route", {"status": "Active"},
        ["name", "route_name", "monthly_fee", "assigned_vehicle"])

    for route in routes:
        vehicle = frappe.get_doc("Transport Vehicle", route.assigned_vehicle)
        allocations = frappe.db.count("Transport Allocation", {
            "route": route.name, "status": "Active"
        })
        route["capacity"] = vehicle.seating_capacity
        route["allocated"] = allocations
        route["available"] = vehicle.seating_capacity - allocations

    return routes

@frappe.whitelist()
def get_route_stops(route):
    """Get stops for a route"""
    return frappe.get_all("Transport Route Stop",
        filters={"parent": route},
        fields=["stop_name", "pickup_time", "drop_time", "additional_fee"],
        order_by="stop_order"
    )
```

### Allocation
```python
@frappe.whitelist()
def allocate_transport(student, route, pickup_stop, drop_stop):
    """Allocate transport to student"""
    # Check capacity
    capacity = check_route_capacity(route, pickup_stop)
    if capacity["available"] <= 0:
        frappe.throw("No seats available on this route")

    allocation = frappe.new_doc("Transport Allocation")
    allocation.student = student
    allocation.route = route
    allocation.pickup_stop = pickup_stop
    allocation.drop_stop = drop_stop
    allocation.from_date = frappe.utils.today()
    allocation.insert()

    return allocation
```

### Trip Logging
```python
@frappe.whitelist()
def log_trip(route, vehicle, trip_type, departure_time, arrival_time, passengers):
    """Log completed trip"""
    trip = frappe.new_doc("Transport Trip Log")
    trip.trip_date = frappe.utils.today()
    trip.route = route
    trip.vehicle = vehicle
    trip.trip_type = trip_type
    trip.departure_time = departure_time
    trip.arrival_time = arrival_time
    trip.total_passengers = passengers
    trip.status = "Completed"
    trip.insert()

    return trip
```

## Reports

1. **Route Utilization Report** - Capacity vs usage
2. **Vehicle Maintenance Schedule** - Due services
3. **Student Transport List** - Route-wise students
4. **Trip Log Report** - Daily/monthly trips
5. **Fee Collection Report** - Transport fee status
6. **Fuel Consumption Report** - Vehicle-wise fuel usage

## Related Files

```
university_erp/
+-- university_transport/
    +-- doctype/
    |   +-- transport_route/
    |   |   +-- transport_route.json
    |   |   +-- transport_route.py
    |   +-- transport_route_stop/
    |   +-- transport_vehicle/
    |   +-- transport_allocation/
    |   +-- transport_trip_log/
    +-- api.py
```

## See Also

- [University Hostel Module](07_UNIVERSITY_HOSTEL.md)
- [University Finance Module](05_UNIVERSITY_FINANCE.md)
- [Student Info Module](03_STUDENT_INFO.md)
