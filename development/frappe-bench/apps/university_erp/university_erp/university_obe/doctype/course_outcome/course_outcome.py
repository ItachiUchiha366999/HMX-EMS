# Copyright (c) 2026, University and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CourseOutcome(Document):
    def validate(self):
        self.set_co_code()
        self.set_bloom_level_number()
        self.validate_unique_co_number()

    def set_co_code(self):
        """Generate CO code based on course"""
        course_code = frappe.db.get_value("Course", self.course, "course_code") or self.course[:8]
        self.co_code = f"{course_code}.CO{self.co_number}"

    def set_bloom_level_number(self):
        """Set numeric Bloom's level (1-6)"""
        levels = {
            "Remember": 1,
            "Understand": 2,
            "Apply": 3,
            "Analyze": 4,
            "Evaluate": 5,
            "Create": 6
        }
        self.bloom_level_number = levels.get(self.bloom_level, 0)

    def validate_unique_co_number(self):
        """Ensure CO number is unique within the course"""
        existing = frappe.db.exists(
            "Course Outcome",
            {
                "course": self.course,
                "co_number": self.co_number,
                "name": ("!=", self.name),
                "status": ("!=", "Archived")
            }
        )
        if existing:
            frappe.throw(f"CO {self.co_number} already exists for course {self.course}")


@frappe.whitelist()
def get_course_outcomes(course):
    """Get all COs for a course"""
    return frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=[
            "name", "co_number", "co_code", "co_statement",
            "bloom_level", "bloom_level_number", "target_attainment",
            "current_attainment", "assessment_methods", "weightage"
        ],
        order_by="co_number"
    )


@frappe.whitelist()
def get_bloom_taxonomy():
    """Get Bloom's taxonomy levels with action verbs"""
    return {
        "Remember": {
            "level": 1,
            "description": "Retrieve relevant knowledge from long-term memory",
            "action_verbs": ["Define", "List", "Name", "Recall", "Recognize", "State", "Identify"]
        },
        "Understand": {
            "level": 2,
            "description": "Construct meaning from instructional messages",
            "action_verbs": ["Describe", "Explain", "Interpret", "Summarize", "Classify", "Compare"]
        },
        "Apply": {
            "level": 3,
            "description": "Carry out or use a procedure in a given situation",
            "action_verbs": ["Apply", "Demonstrate", "Execute", "Implement", "Solve", "Use"]
        },
        "Analyze": {
            "level": 4,
            "description": "Break material into parts and determine relationships",
            "action_verbs": ["Analyze", "Differentiate", "Distinguish", "Examine", "Organize", "Compare"]
        },
        "Evaluate": {
            "level": 5,
            "description": "Make judgments based on criteria and standards",
            "action_verbs": ["Assess", "Critique", "Evaluate", "Judge", "Justify", "Recommend"]
        },
        "Create": {
            "level": 6,
            "description": "Put elements together to form a novel, coherent whole",
            "action_verbs": ["Create", "Design", "Develop", "Formulate", "Generate", "Produce"]
        }
    }


@frappe.whitelist()
def get_co_statistics(course):
    """Get CO statistics for a course"""
    cos = frappe.get_all(
        "Course Outcome",
        filters={"course": course, "status": "Active"},
        fields=["name", "bloom_level", "bloom_level_number", "target_attainment", "current_attainment"]
    )

    if not cos:
        return {"total_cos": 0, "bloom_distribution": {}, "avg_attainment": 0}

    # Bloom's distribution
    bloom_dist = {}
    for co in cos:
        level = co.bloom_level or "Not Set"
        bloom_dist[level] = bloom_dist.get(level, 0) + 1

    # Average attainment
    attainments = [co.current_attainment for co in cos if co.current_attainment]
    avg_attainment = sum(attainments) / len(attainments) if attainments else 0

    return {
        "total_cos": len(cos),
        "bloom_distribution": bloom_dist,
        "avg_attainment": round(avg_attainment, 2),
        "cos_with_attainment": len(attainments)
    }
