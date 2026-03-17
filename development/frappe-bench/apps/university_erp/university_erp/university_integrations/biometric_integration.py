# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

"""
Biometric Device Integration Module
Supports: ZKTeco, ESSL, BioMax, Mantra, Hikvision
"""

import frappe
from frappe import _
from frappe.utils import getdate, now_datetime, get_datetime
from datetime import datetime, timedelta


class BiometricDevice:
    """Base biometric device handler"""

    def __init__(self, device_name):
        self.device = frappe.get_doc("Biometric Device", device_name)

    def connect(self):
        """Establish connection to device"""
        raise NotImplementedError

    def disconnect(self):
        """Close connection"""
        raise NotImplementedError

    def get_attendance(self, start_date=None, end_date=None):
        """Fetch attendance logs from device"""
        raise NotImplementedError

    def sync_users(self, users):
        """Sync user data to device"""
        raise NotImplementedError

    def get_all_users(self):
        """Get all users from device"""
        raise NotImplementedError

    def clear_attendance(self):
        """Clear attendance logs from device"""
        raise NotImplementedError


class ZKTecoDevice(BiometricDevice):
    """ZKTeco device integration using pyzk library"""

    def __init__(self, device_name):
        super().__init__(device_name)
        self.conn = None

    def _get_zk_instance(self):
        """Get ZK instance"""
        try:
            from zk import ZK
            password = self.device.get_password("communication_password")
            return ZK(
                self.device.ip_address,
                port=self.device.port or 4370,
                timeout=self.device.connection_timeout or 5,
                password=int(password) if password and password.isdigit() else 0
            )
        except ImportError:
            frappe.throw(_("pyzk library not installed. Run: pip install pyzk"))

    def connect(self):
        """Connect to ZKTeco device"""
        try:
            zk = self._get_zk_instance()
            self.conn = zk.connect()
            return True
        except Exception as e:
            frappe.log_error(f"ZKTeco connection failed: {str(e)}", "Biometric Integration")
            return False

    def disconnect(self):
        """Disconnect from device"""
        if self.conn:
            try:
                self.conn.disconnect()
            except Exception:
                pass
            self.conn = None

    def get_attendance(self, start_date=None, end_date=None):
        """Get attendance logs from ZKTeco device"""
        if not self.connect():
            return []

        try:
            attendance = self.conn.get_attendance()
            logs = []

            for record in attendance:
                punch_time = record.timestamp

                # Filter by date range if specified
                if start_date and punch_time.date() < start_date:
                    continue
                if end_date and punch_time.date() > end_date:
                    continue

                logs.append({
                    "user_id": str(record.user_id),
                    "punch_time": punch_time,
                    "punch_type": self._get_punch_type(record.punch),
                    "verification_type": self._get_verification_type(record.status)
                })

            return logs

        except Exception as e:
            frappe.log_error(f"Failed to get attendance: {str(e)}", "Biometric Integration")
            return []
        finally:
            self.disconnect()

    def _get_punch_type(self, punch_code):
        """Convert punch code to type"""
        mapping = {
            0: "Check In",
            1: "Check Out",
            2: "Break Start",
            3: "Break End",
            4: "Overtime Start",
            5: "Overtime End"
        }
        return mapping.get(punch_code, "Check In")

    def _get_verification_type(self, status_code):
        """Convert verification status to type"""
        mapping = {
            0: "Password",
            1: "Fingerprint",
            2: "Card",
            15: "Face"
        }
        return mapping.get(status_code, "")

    def get_all_users(self):
        """Get all users from device"""
        if not self.connect():
            return []

        try:
            users = self.conn.get_users()
            return [
                {
                    "uid": user.uid,
                    "user_id": user.user_id,
                    "name": user.name,
                    "privilege": user.privilege
                }
                for user in users
            ]
        except Exception as e:
            frappe.log_error(f"Failed to get users: {str(e)}", "Biometric Integration")
            return []
        finally:
            self.disconnect()

    def sync_users(self, users):
        """Sync users to device"""
        if not self.connect():
            return False

        try:
            for user in users:
                self.conn.set_user(
                    uid=user.get("uid"),
                    name=user.get("name"),
                    privilege=user.get("privilege", 0),
                    password=user.get("password", ""),
                    group_id=user.get("group_id", ""),
                    user_id=user.get("user_id")
                )
            return True
        except Exception as e:
            frappe.log_error(f"User sync failed: {str(e)}", "Biometric Integration")
            return False
        finally:
            self.disconnect()

    def clear_attendance(self):
        """Clear attendance logs from device"""
        if not self.connect():
            return False

        try:
            self.conn.clear_attendance()
            return True
        except Exception as e:
            frappe.log_error(f"Clear attendance failed: {str(e)}", "Biometric Integration")
            return False
        finally:
            self.disconnect()


class ESSLDevice(BiometricDevice):
    """ESSL device integration (placeholder for HTTP API based devices)"""

    def __init__(self, device_name):
        super().__init__(device_name)

    def connect(self):
        """Test connection via HTTP"""
        import requests
        try:
            url = f"http://{self.device.ip_address}:{self.device.port or 80}/iclock/cdata"
            response = requests.get(url, timeout=self.device.connection_timeout or 5)
            return response.status_code == 200
        except Exception:
            return False

    def disconnect(self):
        pass

    def get_attendance(self, start_date=None, end_date=None):
        """ESSL devices typically push data; implement pull if supported"""
        frappe.msgprint(_("ESSL devices use push mode. Configure device to push attendance data."))
        return []


# Factory function
def get_biometric_device(device_name):
    """Get appropriate device handler"""
    device = frappe.get_doc("Biometric Device", device_name)

    if device.device_type == "ZKTeco":
        return ZKTecoDevice(device_name)
    elif device.device_type == "ESSL":
        return ESSLDevice(device_name)
    else:
        frappe.throw(_("Unsupported device type: {0}").format(device.device_type))


# Sync Functions

@frappe.whitelist()
def sync_attendance(device_name, start_date=None, end_date=None):
    """Sync attendance from biometric device"""
    device_handler = get_biometric_device(device_name)
    device = frappe.get_doc("Biometric Device", device_name)

    logs = device_handler.get_attendance(
        start_date=getdate(start_date) if start_date else None,
        end_date=getdate(end_date) if end_date else None
    )

    created = 0
    duplicates = 0

    for log in logs:
        # Check if already exists
        existing = frappe.db.exists("Biometric Attendance Log", {
            "device": device_name,
            "user_id": log["user_id"],
            "punch_time": log["punch_time"]
        })

        if existing:
            duplicates += 1
            continue

        bio_log = frappe.get_doc({
            "doctype": "Biometric Attendance Log",
            "device": device_name,
            "user_id": log["user_id"],
            "punch_time": log["punch_time"],
            "punch_type": log["punch_type"],
            "verification_type": log.get("verification_type", "")
        })

        # Try to match with employee or student
        bio_log.employee = get_employee_by_biometric_id(log["user_id"])
        bio_log.student = get_student_by_biometric_id(log["user_id"])

        bio_log.insert(ignore_permissions=True)
        created += 1

    # Update device sync status
    device.last_sync = now_datetime()
    device.last_sync_status = "Success" if created > 0 or duplicates > 0 else "Partial"
    device.save(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "synced": created,
        "duplicates": duplicates,
        "total": len(logs)
    }


def get_employee_by_biometric_id(biometric_id):
    """Get employee linked to biometric ID"""
    return frappe.db.get_value(
        "Employee",
        {"custom_biometric_id": biometric_id, "status": "Active"},
        "name"
    )


def get_student_by_biometric_id(biometric_id):
    """Get student linked to biometric ID"""
    return frappe.db.get_value(
        "Student",
        {"custom_biometric_id": biometric_id, "enabled": 1},
        "name"
    )


@frappe.whitelist()
def process_attendance_logs(from_date=None, to_date=None, device=None):
    """Process biometric logs into attendance records"""
    filters = {"processed": 0}

    if from_date:
        filters["punch_time"] = [">=", from_date]
    if to_date:
        if "punch_time" in filters:
            filters["punch_time"] = ["between", [from_date, to_date + " 23:59:59"]]
        else:
            filters["punch_time"] = ["<=", to_date + " 23:59:59"]
    if device:
        filters["device"] = device

    logs = frappe.get_all(
        "Biometric Attendance Log",
        filters=filters,
        fields=["name", "employee", "student", "punch_time", "punch_type", "device"],
        order_by="punch_time"
    )

    processed = 0
    errors = 0

    # Group by employee/student and date
    grouped = {}
    for log in logs:
        person = log.employee or log.student
        if not person:
            continue

        punch_date = get_datetime(log.punch_time).date()
        key = (person, punch_date, "employee" if log.employee else "student")

        if key not in grouped:
            grouped[key] = []
        grouped[key].append(log)

    for (person, date, person_type), person_logs in grouped.items():
        try:
            # Sort by time
            person_logs.sort(key=lambda x: get_datetime(x.punch_time))

            check_in = None
            check_out = None

            for log in person_logs:
                punch_time = get_datetime(log.punch_time)
                if log.punch_type == "Check In" and not check_in:
                    check_in = punch_time
                elif log.punch_type == "Check Out":
                    check_out = punch_time

            # Use first and last punch if types not set
            if not check_in:
                check_in = get_datetime(person_logs[0].punch_time)
            if not check_out and len(person_logs) > 1:
                check_out = get_datetime(person_logs[-1].punch_time)

            # Create/update attendance
            if person_type == "employee":
                create_employee_attendance(person, date, check_in, check_out, person_logs)
            else:
                create_student_attendance(person, date, check_in, check_out, person_logs)

            processed += len(person_logs)

        except Exception as e:
            errors += 1
            # Mark logs with error
            for log in person_logs:
                frappe.db.set_value(
                    "Biometric Attendance Log", log.name,
                    "processing_error", str(e)
                )

    frappe.db.commit()

    return {
        "processed": processed,
        "errors": errors
    }


def create_employee_attendance(employee, date, check_in, check_out, logs):
    """Create attendance record for employee"""
    device = frappe.get_doc("Biometric Device", logs[0].device)

    # Check existing
    existing = frappe.db.exists("Attendance", {
        "employee": employee,
        "attendance_date": date
    })

    if existing:
        attendance = frappe.get_doc("Attendance", existing)
    else:
        company = frappe.db.get_value("Employee", employee, "company")
        attendance = frappe.get_doc({
            "doctype": "Attendance",
            "employee": employee,
            "attendance_date": date,
            "company": company
        })

    # Calculate working hours
    if check_in and check_out:
        working_hours = (check_out - check_in).total_seconds() / 3600
        attendance.working_hours = round(working_hours, 2)

        # Determine status based on thresholds
        if working_hours >= device.working_hours_threshold:
            attendance.status = "Present"
        elif working_hours >= device.mark_half_day_after:
            attendance.status = "Half Day"
        else:
            attendance.status = "Present"  # Default to present with low hours
    elif check_in:
        attendance.status = "Half Day"
    else:
        attendance.status = "Absent"

    attendance.flags.ignore_permissions = True
    attendance.save()

    # Mark logs as processed
    for log in logs:
        frappe.db.set_value(
            "Biometric Attendance Log", log.name,
            {
                "processed": 1,
                "processing_date": now_datetime(),
                "attendance_doctype": "Attendance",
                "attendance_record": attendance.name
            }
        )


def create_student_attendance(student, date, check_in, check_out, logs):
    """Create attendance record for student (if Student Attendance doctype exists)"""
    # Mark logs as processed even if student attendance is not tracked
    for log in logs:
        frappe.db.set_value(
            "Biometric Attendance Log", log.name,
            {
                "processed": 1,
                "processing_date": now_datetime()
            }
        )


# Scheduled Tasks

def scheduled_sync_all_devices():
    """Sync all active biometric devices - called by scheduler"""
    devices = frappe.get_all(
        "Biometric Device",
        filters={"status": "Active", "auto_sync": 1},
        pluck="name"
    )

    for device in devices:
        try:
            sync_attendance(device)
        except Exception as e:
            frappe.log_error(
                f"Auto sync failed for {device}: {str(e)}",
                "Biometric Sync"
            )

            # Update device status
            frappe.db.set_value(
                "Biometric Device", device,
                {
                    "last_sync": now_datetime(),
                    "last_sync_status": "Failed"
                }
            )


def scheduled_process_attendance():
    """Process unprocessed attendance logs - called by scheduler"""
    today = getdate()
    yesterday = today - timedelta(days=1)

    process_attendance_logs(
        from_date=str(yesterday),
        to_date=str(today)
    )


# API Endpoints

@frappe.whitelist()
def get_device_users(device_name):
    """Get all users from a biometric device"""
    device_handler = get_biometric_device(device_name)
    return device_handler.get_all_users()


@frappe.whitelist()
def sync_users_to_device(device_name, users):
    """Sync users to biometric device"""
    if isinstance(users, str):
        users = frappe.parse_json(users)

    device_handler = get_biometric_device(device_name)
    result = device_handler.sync_users(users)

    return {"success": result}


@frappe.whitelist()
def clear_device_attendance(device_name):
    """Clear attendance logs from device"""
    device_handler = get_biometric_device(device_name)
    result = device_handler.clear_attendance()

    return {"success": result}


@frappe.whitelist()
def get_unprocessed_logs_count():
    """Get count of unprocessed logs"""
    return frappe.db.count("Biometric Attendance Log", {"processed": 0})


@frappe.whitelist()
def link_biometric_user(user_id, employee=None, student=None):
    """Link biometric user ID to employee or student"""
    if employee:
        frappe.db.set_value("Employee", employee, "custom_biometric_id", user_id)
    elif student:
        frappe.db.set_value("Student", student, "custom_biometric_id", user_id)
    else:
        frappe.throw(_("Please specify employee or student"))

    return {"success": True}
