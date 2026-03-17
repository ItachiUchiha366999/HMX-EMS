# University ERP Development Prompt for Claude Code

Use this prompt to instruct Claude Code to systematically develop the University ERP project following the phase-wise blueprint documents.

---

## Master Development Prompt

```
You are tasked with developing a complete University ERP system as a custom Frappe/ERPNext application. The project uses a **Hybrid Architecture** that extends the Frappe Education module with custom functionality.

## Project Documentation Location
All development documentation is located at:
`/workspace/development/docs/university_erp_blueprint/`

Key files:
- `phases/README.md` - Phase overview and index
- `phases/phase_01_foundation.md` through `phase_08_integrations_deployment.md` - Detailed phase documents
- `01_architecture_overview.md` - System architecture
- `03_modules_doctypes.md` - DocType specifications
- `04_education_deep_dive.md` - Education module integration

## Development Methodology

### Before Starting Any Phase:
1. **Read the phase document thoroughly** from `/workspace/development/docs/university_erp_blueprint/phases/phase_XX_*.md`
2. **Create a detailed task checklist** by breaking down the phase into atomic tasks
3. **Use the TodoWrite tool** to create and track all tasks
4. **Get confirmation** before proceeding with implementation

### Task Breakdown Rules:
- Each task should be completable in 15-30 minutes
- Tasks should be atomic (single responsibility)
- Include validation/testing tasks after implementation tasks
- Group related tasks together
- Mark dependencies between tasks

### For Each Task:
1. Mark task as `in_progress` before starting
2. Implement the task following code examples in the documentation
3. Test the implementation
4. Mark task as `completed` only after successful testing
5. Move to next task

### Code Standards:
- Follow Frappe framework conventions
- Use `custom_` prefix for all custom fields on Education DocTypes
- Implement override classes in `university_erp/overrides/` directory
- Store fixtures in `university_erp/fixtures/` directory
- Write docstrings for all classes and methods
- Include proper error handling

## Phase Execution Order

Execute phases in order:
1. Phase 1: Foundation & Core Setup
2. Phase 2: Admissions & SIS
3. Phase 3: Academics
4. Phase 4: Examinations
5. Phase 5: Fees & Finance
6. Phase 6: HR & Faculty
7. Phase 7: Extended Modules
8. Phase 8: Integrations & Deployment

## Current Status
[UPDATE THIS SECTION AS YOU PROGRESS]
- Current Phase: Phase 1
- Tasks Completed: 0
- Tasks Remaining: All

## Commands

Start development:
"Begin Phase 1 development by reading the phase document and creating a detailed task checklist"

Continue development:
"Continue with the next pending task in the current phase"

Phase status:
"Show current phase progress and remaining tasks"

Move to next phase:
"Complete current phase and begin next phase"
```

---

## Phase-Specific Prompts

### Phase 1: Foundation & Core Setup

```
## Phase 1: Foundation & Core Setup

Read `/workspace/development/docs/university_erp_blueprint/phases/phase_01_foundation.md` and create a detailed task checklist.

### Expected Task Breakdown:

**Week 1: App Scaffold & Structure**
- [ ] Task 1.1: Create Frappe app using `bench new-app university_erp`
- [ ] Task 1.2: Configure app metadata in `hooks.py` (app_name, app_title, app_publisher)
- [ ] Task 1.3: Create directory structure (`overrides/`, `fixtures/`, `api/`)
- [ ] Task 1.4: Add Education and ERPNext as app dependencies
- [ ] Task 1.5: Install app on development site
- [ ] Task 1.6: Verify app installation and basic functionality

**Week 2: Override Classes**
- [ ] Task 2.1: Create `university_erp/overrides/__init__.py`
- [ ] Task 2.2: Create `UniversityStudent` override class in `overrides/student.py`
- [ ] Task 2.3: Create `UniversityProgram` override class in `overrides/program.py`
- [ ] Task 2.4: Create `UniversityCourse` override class in `overrides/course.py`
- [ ] Task 2.5: Create `UniversityFees` override class in `overrides/fees.py`
- [ ] Task 2.6: Create `UniversityAssessmentResult` override class
- [ ] Task 2.7: Configure `override_doctype_class` in hooks.py
- [ ] Task 2.8: Test all override classes load correctly

**Week 3: Custom Fields**
- [ ] Task 3.1: Create `fixtures/custom_field/` directory
- [ ] Task 3.2: Create Student custom fields JSON fixture
- [ ] Task 3.3: Create Program custom fields JSON fixture
- [ ] Task 3.4: Create Course custom fields JSON fixture (L-T-P-S credits)
- [ ] Task 3.5: Create Fees custom fields JSON fixture
- [ ] Task 3.6: Add fixtures to hooks.py
- [ ] Task 3.7: Import fixtures and verify custom fields appear
- [ ] Task 3.8: Test custom field data entry and retrieval

**Week 4: Roles & Permissions**
- [ ] Task 4.1: Create Role JSON fixtures for university-specific roles
- [ ] Task 4.2: Create University Administrator role
- [ ] Task 4.3: Create Admissions Officer role
- [ ] Task 4.4: Create Examination Controller role
- [ ] Task 4.5: Create Accounts Officer role
- [ ] Task 4.6: Create Hostel Warden role
- [ ] Task 4.7: Configure module visibility in hooks.py
- [ ] Task 4.8: Test role-based access for each role
- [ ] Task 4.9: Create University ERP Settings DocType
- [ ] Task 4.10: Configure default values in settings

**Validation Tasks**
- [ ] Task V1: Verify all override classes are loaded (check logs)
- [ ] Task V2: Verify all custom fields are visible on forms
- [ ] Task V3: Verify roles have correct permissions
- [ ] Task V4: Run `bench migrate` without errors
- [ ] Task V5: Document any deviations from blueprint

After creating this checklist, begin executing tasks in order, marking each as in_progress before starting and completed after testing.
```

---

### Phase 2: Admissions & SIS

```
## Phase 2: Admissions & Student Information System

Read `/workspace/development/docs/university_erp_blueprint/phases/phase_02_admissions_sis.md` and create a detailed task checklist.

### Expected Task Breakdown:

**Week 1: Student Applicant Extensions**
- [ ] Task 1.1: Create Student Applicant custom fields fixture
- [ ] Task 1.2: Create `UniversityApplicant` override class
- [ ] Task 1.3: Implement entrance exam score tracking
- [ ] Task 1.4: Implement category-based fields (General, SC/ST, OBC, EWS)
- [ ] Task 1.5: Create Admission Cycle DocType
- [ ] Task 1.6: Create Seat Matrix DocType
- [ ] Task 1.7: Create Seat Matrix Item child table
- [ ] Task 1.8: Test Admission Cycle and Seat Matrix creation

**Week 2: Merit List & Selection**
- [ ] Task 2.1: Create Merit List DocType
- [ ] Task 2.2: Create Merit List Entry child table
- [ ] Task 2.3: Implement `MeritListGenerator` class
- [ ] Task 2.4: Implement merit calculation logic (entrance + academics)
- [ ] Task 2.5: Implement category-wise ranking
- [ ] Task 2.6: Implement cutoff-based filtering
- [ ] Task 2.7: Create Merit List Report
- [ ] Task 2.8: Test merit list generation with sample data

**Week 3: Admission Workflow**
- [ ] Task 3.1: Create Student Applicant workflow JSON fixture
- [ ] Task 3.2: Configure workflow states (Applied → Verified → Selected → Admitted)
- [ ] Task 3.3: Configure workflow transitions and permissions
- [ ] Task 3.4: Implement `StudentCreator` class for applicant conversion
- [ ] Task 3.5: Implement auto-generation of enrollment number
- [ ] Task 3.6: Create Program Enrollment on admission
- [ ] Task 3.7: Test complete admission workflow
- [ ] Task 3.8: Create Admission Dashboard page

**Week 4: Student Portal**
- [ ] Task 4.1: Create Student Portal web template
- [ ] Task 4.2: Create student profile view page
- [ ] Task 4.3: Create application status tracking page
- [ ] Task 4.4: Implement document upload functionality
- [ ] Task 4.5: Create admission letter download feature
- [ ] Task 4.6: Style portal with responsive CSS
- [ ] Task 4.7: Test portal authentication and access control
- [ ] Task 4.8: Create Admission Reports (program-wise, category-wise)

**Validation Tasks**
- [ ] Task V1: Test complete admission flow from application to enrollment
- [ ] Task V2: Verify merit list ranking is correct
- [ ] Task V3: Verify workflow transitions work correctly
- [ ] Task V4: Verify student portal is accessible and secure
- [ ] Task V5: Verify all reports generate correct data

Begin execution after creating the complete checklist.
```

---

### Phase 3-8 Prompts

Follow the same pattern for remaining phases. Each prompt should:

1. Reference the specific phase document
2. Break down into weekly task groups
3. Include atomic tasks (15-30 min each)
4. Include validation tasks at the end
5. Request checklist creation before execution

---

## Execution Commands

### Start Fresh Development

```
I want to develop the University ERP project using the blueprint documents in `/workspace/development/docs/university_erp_blueprint/`.

Start with Phase 1: Foundation & Core Setup.

1. Read the phase document at `phases/phase_01_foundation.md`
2. Create a detailed task checklist breaking down all deliverables into atomic tasks
3. Use TodoWrite to track all tasks
4. Wait for my confirmation before starting implementation
5. Execute tasks one by one, marking progress as you go
```

### Continue Development

```
Continue development of University ERP.

Current status:
- Phase: [CURRENT_PHASE]
- Last completed task: [LAST_TASK]

Review the task checklist and continue with the next pending task.
Mark the task as in_progress, implement it, test it, then mark as completed.
```

### Phase Completion

```
Complete the current phase and prepare for next phase.

1. Review all completed tasks in the checklist
2. Verify all deliverables from the phase document are complete
3. Run validation tasks
4. Document any deviations or issues
5. Create summary of what was implemented
6. Read the next phase document and create its task checklist
```

### Status Check

```
Show University ERP development status.

1. Current phase and progress percentage
2. Completed tasks
3. Pending tasks
4. Any blockers or issues
5. Estimated completion for current phase
```

---

## Task Template

When Claude creates tasks, use this format:

```
- [ ] Task X.Y: [Brief description]
  - File: [file path to create/modify]
  - Type: [create/modify/configure/test]
  - Depends on: [task dependencies if any]
  - Validation: [how to verify completion]
```

---

## Code Implementation Guidelines

### Creating Override Classes

```python
# university_erp/overrides/[doctype].py

from frappe_education.education.doctype.[doctype].[doctype] import [OriginalClass]
import frappe

class University[DocType]([OriginalClass]):
    """
    Extended [DocType] with university-specific features.

    Custom Features:
    - [Feature 1]
    - [Feature 2]
    """

    def validate(self):
        """Run validations before save"""
        super().validate()
        self.custom_validation_1()
        self.custom_validation_2()

    def custom_validation_1(self):
        """[Description of validation]"""
        pass

    # Add custom methods...
```

### Creating Custom Fields Fixture

```json
// university_erp/fixtures/custom_field/[doctype]_custom_fields.json
[
    {
        "dt": "[Parent DocType]",
        "fieldname": "custom_[field_name]",
        "fieldtype": "[Field Type]",
        "label": "[Label]",
        "insert_after": "[existing_field]",
        "reqd": 0,
        "description": "[Help text]"
    }
]
```

### Creating New DocType

```python
# university_erp/university_erp/doctype/[doctype]/[doctype].py

import frappe
from frappe.model.document import Document

class [DocTypeName](Document):
    """
    [DocType Description]

    Attributes:
        [field1]: [description]
        [field2]: [description]
    """

    def validate(self):
        """Validate document before save"""
        self.validate_[something]()

    def on_submit(self):
        """Actions on document submission"""
        pass

    def on_cancel(self):
        """Actions on document cancellation"""
        pass
```

---

## Testing Guidelines

After implementing each task:

1. **Syntax Check**: Ensure no Python syntax errors
2. **Import Check**: Verify all imports work
3. **Migrate Check**: Run `bench migrate` without errors
4. **Functional Test**: Manually test the feature
5. **Permission Test**: Verify role-based access

```bash
# Useful commands for testing
bench --site [site] migrate
bench --site [site] clear-cache
bench --site [site] run-tests --app university_erp
bench restart
```

---

## Error Recovery

If a task fails:

```
The task [TASK_NAME] failed with error:
[ERROR_MESSAGE]

1. Do NOT mark the task as completed
2. Analyze the error
3. Propose a fix
4. Implement the fix
5. Re-test
6. Only mark completed after successful test
```

---

## Progress Tracking

Claude should maintain a progress file:

```
# /workspace/development/docs/university_erp_blueprint/PROGRESS.md

## Development Progress

### Current Phase: Phase 1 - Foundation
### Started: [DATE]
### Status: In Progress

## Completed Tasks
- [x] Task 1.1: Created app scaffold - 2024-01-15
- [x] Task 1.2: Configured hooks.py - 2024-01-15

## Current Task
- [ ] Task 1.3: Creating directory structure

## Pending Tasks
- [ ] Task 1.4: Add app dependencies
- [ ] Task 1.5: Install app on site
...

## Issues Encountered
1. [Issue description] - [Resolution]

## Deviations from Blueprint
1. [Deviation description] - [Reason]
```

---

## Final Notes

1. **Always read documentation first** before implementing
2. **Create complete checklist** before starting any phase
3. **One task at a time** - don't parallelize unnecessarily
4. **Test thoroughly** before marking complete
5. **Document deviations** from the blueprint
6. **Ask for clarification** if requirements are unclear
7. **Commit frequently** with meaningful messages

Start by saying: "I'm ready to begin University ERP development. Please confirm to start with Phase 1, and I'll create a detailed task checklist."
```
