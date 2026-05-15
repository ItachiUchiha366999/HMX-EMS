# Creating Sample Data for Student Portal

## Student Information
- **Student Name:** Test Student
- **Student ID:** EDU-STU-2026-00002
- **Email:** student@test.edu
- **Program:** B.Tech Computer Science
- **Academic Year:** 2025-26

---

## Step-by-Step Data Creation

### Step 1: Create Student Group

1. **Login as Administrator**
2. **Search for:** "Student Group"
3. **Click:** New Student Group
4. **Fill in:**
   ```
   Student Group Name: BCS-2024-Batch-A
   Group Based On: Batch
   Academic Year: 2025-26
   Program: B.Tech Computer Science
   ```
5. **In "Students" table, add:**
   - Click "Add Row"
   - Student: EDU-STU-2026-00002 (Test Student)
   - Active: ✓ (checked)
6. **Click:** Save

---

### Step 2: Create Exam Schedules (Upcoming Exams)

#### Exam 1: Data Structures - Tomorrow
1. **Search for:** "Exam"
2. **Select:** "Exam" doctype (not Exam Schedule)
3. **Click:** New
4. **Fill in:**
   ```
   Exam Name: Mid Semester Examination - October 2025
   ```
5. **Save**

6. **Now create Exam Schedule:**
   - Search for: "Course Schedule"
   - Click: New
   - Fill in:
     ```
     Student Group: BCS-2024-Batch-A
     Course: Data Structures and Algorithms (or any available course)
     Instructor: (Select any faculty)
     From Time: 10:00:00
     To Time: 13:00:00
     Room: Room 101
     Schedule Date: [Tomorrow's date - e.g., 2026-01-05]
     ```
   - Save

#### Exam 2: Database Systems - In 3 Days
Repeat above steps with:
```
Course: Database Management Systems
Schedule Date: [Date 3 days from now]
From Time: 14:00:00
To Time: 17:00:00
Room: Room 102
```

#### Exam 3: Operating Systems - In 7 Days
```
Course: Operating Systems
Schedule Date: [Date 7 days from now]
From Time: 10:00:00
To Time: 13:00:00
Room: Room 103
```

---

### Step 3: Create Past Exams (Completed Exams)

Repeat Exam Schedule creation with past dates:

#### Past Exam 1
```
Course: Computer Networks
Schedule Date: 2025-12-15
From Time: 10:00:00
To Time: 13:00:00
Room: Room 104
```

#### Past Exam 2
```
Course: Software Engineering
Schedule Date: 2025-12-10
From Time: 14:00:00
To Time: 17:00:00
Room: Room 105
```

---

### Step 4: Create Assessment Results (Grades)

1. **Search for:** "Assessment Result"
2. **Click:** New
3. **Fill in:**
   ```
   Student: EDU-STU-2026-00002 (Test Student)
   Assessment Plan: (Select or create one for a course)
   Course: Computer Networks
   Total Score: 85
   Maximum Score: 100
   Grade: A
   ```
4. **Save and Submit**

Create 4-5 more assessment results with different grades to populate the CGPA calculation.

---

### Step 5: Update Student CGPA

1. **Search for:** "Student" → Open EDU-STU-2026-00002
2. **Scroll to:** Custom CGPA field (if available)
3. **Set:** `8.5` (or it will be calculated from assessment results)
4. **Save**

---

### Step 6: Verify Data in Portal

1. **Logout from Administrator**
2. **Clear browser cookies** (important!)
3. **Go to:** `http://localhost:18000/login`
4. **Login as:** `student@test.edu`
5. **You should be redirected to:** `/student_portal`

**Expected Dashboard Display:**
- Student name: Test Student
- Program: B.Tech Computer Science
- CGPA: 8.5 (or calculated value)
- Quick stats with real numbers

**Navigate to Examinations:**
- Click "Examinations" in sidebar
- **Upcoming Exams tab:** Should show 3 upcoming exams with countdown
- **Completed Exams tab:** Should show 2 past exams
- **Hall Tickets tab:** Empty (we'll create these next)

---

## Quick Data Summary

After completing these steps, you'll have:

✅ **Student Group:** 1 group with Test Student enrolled
✅ **Upcoming Exams:** 3 exams (tomorrow, 3 days, 7 days)
✅ **Past Exams:** 2 completed exams
✅ **Grades:** 4-5 assessment results for CGPA
✅ **Program Enrollment:** Already exists

---

## Troubleshooting

### Issue: Can't find Course Schedule
- **Solution:** The Education app might use "Exam Schedule" instead
- Check: Setup → Education → Exam Schedule

### Issue: Courses don't exist
- **Create courses first:**
  1. Search: "Course"
  2. Create: Data Structures and Algorithms, Database Systems, etc.

### Issue: No instructor available
- **Create a dummy instructor:**
  1. Search: "Instructor"
  2. Create new with any name

### Issue: Dashboard still shows 0 exams
- **Clear cache:**
  ```bash
  bench clear-cache
  bench restart
  ```
- **Clear browser cache:** Ctrl+Shift+R

---

## Alternative: Use Frappe Desk UI

Instead of console commands, **use the Frappe desk interface** to create all data:

1. Login as Administrator
2. Use the awesome bar (Ctrl+K) to search for doctypes
3. Click "New" to create records
4. Fill in forms visually
5. This is **much easier** and shows all available fields

---

*Last Updated: January 4, 2026*
