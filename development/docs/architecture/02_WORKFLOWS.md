# University ERP - Workflows and Process Diagrams

## Table of Contents
1. [Student Admission Workflow](#1-student-admission-workflow)
2. [Student Registration & Enrollment Workflow](#2-student-registration--enrollment-workflow)
3. [Course Enrollment Workflow](#3-course-enrollment-workflow)
4. [Fee Payment Workflow](#4-fee-payment-workflow)
5. [Examination Workflow](#5-examination-workflow)
6. [Result Processing Workflow](#6-result-processing-workflow)
7. [Leave Application Workflow](#7-leave-application-workflow)
8. [Grievance Redressal Workflow](#8-grievance-redressal-workflow)
9. [Library Book Issue/Return Workflow](#9-library-book-issuereturn-workflow)
10. [Hostel Allocation Workflow](#10-hostel-allocation-workflow)
11. [Transport Allocation Workflow](#11-transport-allocation-workflow)
12. [Attendance Marking Workflow](#12-attendance-marking-workflow)
13. [Assignment Submission Workflow](#13-assignment-submission-workflow)
14. [Document Request Workflow](#14-document-request-workflow)
15. [Faculty Recruitment Workflow](#15-faculty-recruitment-workflow)

---

## 1. Student Admission Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Admission Cycle Opens]) --> CREATE_APP[Student Creates Application]
    CREATE_APP --> UPLOAD_DOC[Upload Required Documents]
    UPLOAD_DOC --> PAY_FEE[Pay Application Fee]
    PAY_FEE --> SUBMIT[Submit Application]

    SUBMIT --> VERIFY{Verification by<br/>Admission Office}
    VERIFY -->|Rejected| NOTIFY_REJECT[Notify Student - Rejection]
    VERIFY -->|Approved| ENTRANCE{Entrance Exam<br/>Required?}

    ENTRANCE -->|Yes| SCHEDULE_EXAM[Schedule Entrance Exam]
    ENTRANCE -->|No| MERIT_CALC[Calculate Merit]

    SCHEDULE_EXAM --> CONDUCT_EXAM[Conduct Exam]
    CONDUCT_EXAM --> PUBLISH_RESULT[Publish Exam Results]
    PUBLISH_RESULT --> MERIT_CALC

    MERIT_CALC --> GEN_MERIT[Generate Merit List]
    GEN_MERIT --> SEAT_ALLOT{Seat Available?}

    SEAT_ALLOT -->|No| WAITLIST[Add to Waitlist]
    SEAT_ALLOT -->|Yes| NOTIFY_SELECT[Notify Student - Selected]

    NOTIFY_SELECT --> VERIFY_DOC[Document Verification]
    VERIFY_DOC --> DOC_OK{Documents OK?}

    DOC_OK -->|No| REQUEST_RESUBMIT[Request Resubmission]
    REQUEST_RESUBMIT --> VERIFY_DOC
    DOC_OK -->|Yes| PAY_ADMISSION[Pay Admission Fee]

    PAY_ADMISSION --> CONFIRM_SEAT[Confirm Seat]
    CONFIRM_SEAT --> CREATE_STUDENT[Create Student Record]
    CREATE_STUDENT --> END([End: Admission Complete])

    NOTIFY_REJECT --> END
    WAITLIST --> END

    style START fill:#90EE90
    style END fill:#FFB6C1
    style VERIFY fill:#FFE4B5
    style ENTRANCE fill:#FFE4B5
    style SEAT_ALLOT fill:#FFE4B5
    style DOC_OK fill:#FFE4B5
```

### Workflow States

| State | Description | Allowed Transitions | Responsible Role |
|-------|-------------|---------------------|------------------|
| Draft | Application created but not submitted | Submit | Student |
| Submitted | Application submitted for review | Approve, Reject | Admission Officer |
| Under Review | Documents being verified | Approve, Request Resubmission | Admission Officer |
| Entrance Scheduled | Exam scheduled for candidate | Mark Attended | Exam Controller |
| Merit List Generated | Candidate in merit list | Allocate Seat, Waitlist | Admission Officer |
| Seat Allocated | Seat allocated to candidate | Confirm, Reject | Student |
| Document Verified | All documents verified | Proceed to Enrollment | Admission Officer |
| Fee Paid | Admission fee paid | Complete Enrollment | Accounts |
| Enrolled | Student enrolled successfully | - | Registrar |
| Rejected | Application rejected | - | Admission Officer |
| Waitlisted | Candidate in waitlist | Allocate Seat | Admission Officer |

### Notification Triggers

```mermaid
graph LR
    A[Application Submitted] --> N1[Email to Admission Office]
    B[Application Approved] --> N2[Email + SMS to Student]
    C[Entrance Exam Scheduled] --> N3[Email + SMS to Student]
    D[Merit List Published] --> N4[Email to All Applicants]
    E[Seat Allocated] --> N5[Email + SMS to Student]
    F[Document Verification] --> N6[Email to Student]
    G[Admission Confirmed] --> N7[Welcome Email + Login Credentials]

    style N1 fill:#E6F3FF
    style N2 fill:#E6F3FF
    style N3 fill:#E6F3FF
    style N4 fill:#E6F3FF
    style N5 fill:#E6F3FF
    style N6 fill:#E6F3FF
    style N7 fill:#E6F3FF
```

---

## 2. Student Registration & Enrollment Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Admission Confirmed]) --> SEND_CRED[Send Login Credentials]
    SEND_CRED --> FIRST_LOGIN[Student First Login]
    FIRST_LOGIN --> CHANGE_PWD[Change Password]
    CHANGE_PWD --> PROFILE[Complete Profile Details]

    PROFILE --> UPLOAD_PHOTO[Upload Photo]
    UPLOAD_PHOTO --> PARENT_INFO[Add Parent/Guardian Info]
    PARENT_INFO --> ADDRESS[Add Address Details]
    ADDRESS --> EMERGENCY[Add Emergency Contact]

    EMERGENCY --> REVIEW{HOD Review}
    REVIEW -->|Corrections Needed| NOTIFY_CORR[Notify Student]
    NOTIFY_CORR --> PROFILE

    REVIEW -->|Approved| ASSIGN_ROLL[Assign Roll Number]
    ASSIGN_ROLL --> ASSIGN_BATCH[Assign to Batch]
    ASSIGN_BATCH --> GEN_ID[Generate Student ID Card]

    GEN_ID --> CREATE_PORTAL[Activate Portal Access]
    CREATE_PORTAL --> SEND_WELCOME[Send Welcome Email]
    SEND_WELCOME --> ORIENT{Orientation<br/>Attendance}

    ORIENT --> COURSE_SELECT[Course Selection]
    COURSE_SELECT --> ADVISOR{Academic Advisor<br/>Approval}

    ADVISOR -->|Rejected| NOTIFY_REJECT[Notify Student]
    NOTIFY_REJECT --> COURSE_SELECT

    ADVISOR -->|Approved| ENROLL_COURSES[Enroll in Courses]
    ENROLL_COURSES --> GEN_TIMETABLE[Generate Personal Timetable]
    GEN_TIMETABLE --> END([End: Enrollment Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style REVIEW fill:#FFE4B5
    style ADVISOR fill:#FFE4B5
```

### Data Required at Each Stage

| Stage | Data Collection | Validation Rules |
|-------|----------------|------------------|
| Profile Completion | Name, DOB, Gender, Blood Group, Aadhar | All mandatory fields |
| Photo Upload | Passport size photo | Max 500KB, JPG/PNG |
| Parent Info | Father/Mother/Guardian name, occupation, phone, email | At least one parent mandatory |
| Address | Current & Permanent address, pincode | Valid pincode required |
| Emergency Contact | Name, relationship, phone | Valid phone number |
| Course Selection | Preferred courses list | Min credits, prerequisites |

---

## 3. Course Enrollment Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: New Semester]) --> OPEN_REG[Open Course Registration]
    OPEN_REG --> VIEW_COURSES[Student Views Available Courses]
    VIEW_COURSES --> CHECK_PREREQ{Check Prerequisites}

    CHECK_PREREQ -->|Not Met| SHOW_ERROR[Show Error Message]
    CHECK_PREREQ -->|Met| ADD_COURSE[Add Course to Cart]

    ADD_COURSE --> MORE{Add More<br/>Courses?}
    MORE -->|Yes| VIEW_COURSES
    MORE -->|No| CHECK_CREDITS{Total Credits<br/>Valid?}

    CHECK_CREDITS -->|Below Min| SHOW_MIN[Show Minimum Credits Error]
    SHOW_MIN --> VIEW_COURSES
    CHECK_CREDITS -->|Above Max| SHOW_MAX[Show Maximum Credits Error]
    SHOW_MAX --> VIEW_COURSES

    CHECK_CREDITS -->|Valid| SUBMIT_REQ[Submit Enrollment Request]
    SUBMIT_REQ --> ADVISOR_REV{Academic Advisor<br/>Review}

    ADVISOR_REV -->|Rejected| NOTIFY_REJ[Notify Student with Reason]
    NOTIFY_REJ --> VIEW_COURSES

    ADVISOR_REV -->|Approved| CHECK_SEATS{Seats Available<br/>in All Courses?}

    CHECK_SEATS -->|No| NOTIFY_WAIT[Add to Waitlist]
    CHECK_SEATS -->|Yes| RESERVE_SEATS[Reserve Seats]

    RESERVE_SEATS --> GEN_FEE[Generate Fee Invoice]
    GEN_FEE --> NOTIFY_PAY[Notify Student to Pay]

    NOTIFY_PAY --> PAYMENT{Payment within<br/>Deadline?}
    PAYMENT -->|No| CANCEL_SEATS[Cancel Seat Reservation]
    CANCEL_SEATS --> END_CANCEL([End: Enrollment Cancelled])

    PAYMENT -->|Yes| CONFIRM_ENROLL[Confirm Enrollment]
    CONFIRM_ENROLL --> ADD_TIMETABLE[Add to Student Timetable]
    ADD_TIMETABLE --> NOTIFY_SUCCESS[Notify Enrollment Success]
    NOTIFY_SUCCESS --> END([End: Enrollment Complete])

    NOTIFY_WAIT --> END_WAIT([End: Waitlisted])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_CANCEL fill:#FFB6C1
    style END_WAIT fill:#FFA07A
    style CHECK_PREREQ fill:#FFE4B5
    style CHECK_CREDITS fill:#FFE4B5
    style ADVISOR_REV fill:#FFE4B5
    style CHECK_SEATS fill:#FFE4B5
    style PAYMENT fill:#FFE4B5
```

### Business Rules

```mermaid
graph TD
    RULES[Course Enrollment Rules]

    RULES --> R1[Minimum Credits: 12]
    RULES --> R2[Maximum Credits: 24]
    RULES --> R3[Prerequisites Must Be Met]
    RULES --> R4[No Time Conflicts]
    RULES --> R5[Advisor Approval Required]
    RULES --> R6[Payment Within 7 Days]
    RULES --> R7[Add/Drop Period: 2 Weeks]

    style RULES fill:#FFE4B5
```

---

## 4. Fee Payment Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Fee Invoice Generated]) --> NOTIFY[Notify Student via Email/SMS]
    NOTIFY --> LOGIN[Student Logs into Portal]
    LOGIN --> VIEW_FEE[View Fee Structure]
    VIEW_FEE --> CHECK_DUE{Check Due Amount}

    CHECK_DUE --> SELECT_PAY[Select Payment Mode]
    SELECT_PAY --> MODE{Payment Mode}

    MODE -->|Online| GATEWAY[Redirect to Payment Gateway]
    MODE -->|Offline| BANK[Bank Challan/DD]

    GATEWAY --> SELECT_METHOD[Select Method: Card/UPI/Net Banking]
    SELECT_METHOD --> PROCESS_PAY[Process Payment]

    PROCESS_PAY --> PAY_STATUS{Payment Status}
    PAY_STATUS -->|Failed| RETRY{Retry?}
    RETRY -->|Yes| GATEWAY
    RETRY -->|No| END_FAIL([End: Payment Failed])

    PAY_STATUS -->|Success| CALLBACK[Payment Gateway Callback]
    CALLBACK --> VERIFY_SIG[Verify Signature]
    VERIFY_SIG --> SIG_OK{Signature Valid?}

    SIG_OK -->|No| LOG_FRAUD[Log Potential Fraud]
    LOG_FRAUD --> END_FAIL

    SIG_OK -->|Yes| UPDATE_INV[Update Invoice Status]
    UPDATE_INV --> CREATE_ENTRY[Create Payment Entry]
    CREATE_ENTRY --> GEN_RECEIPT[Generate Receipt]
    GEN_RECEIPT --> SEND_RECEIPT[Email Receipt to Student]

    BANK --> SUBMIT_BANK[Submit to Accounts Office]
    SUBMIT_BANK --> VERIFY_BANK{Verify with Bank}
    VERIFY_BANK -->|Invalid| REJECT_PAY[Reject Payment]
    REJECT_PAY --> NOTIFY_REJ[Notify Student]
    NOTIFY_REJ --> END_FAIL

    VERIFY_BANK -->|Valid| UPDATE_INV

    SEND_RECEIPT --> CHECK_FULL{Full Amount<br/>Paid?}
    CHECK_FULL -->|No| UPDATE_PART[Mark as Partial Payment]
    UPDATE_PART --> END([End: Partial Payment])

    CHECK_FULL -->|Yes| UPDATE_FULL[Mark as Fully Paid]
    UPDATE_FULL --> UNLOCK[Unlock Services]
    UNLOCK --> END_SUCCESS([End: Payment Complete])

    style START fill:#90EE90
    style END_SUCCESS fill:#FFB6C1
    style END_FAIL fill:#FF6B6B
    style END fill:#FFA07A
    style PAY_STATUS fill:#FFE4B5
    style SIG_OK fill:#FFE4B5
    style VERIFY_BANK fill:#FFE4B5
    style CHECK_FULL fill:#FFE4B5
```

### Payment Gateway Integration Flow

```mermaid
sequenceDiagram
    participant Student
    participant Portal
    participant ERP
    participant Gateway
    participant Bank

    Student->>Portal: Initiate Payment
    Portal->>ERP: Create Payment Order
    ERP->>Gateway: Create Order API
    Gateway-->>ERP: Order ID + Token
    ERP-->>Portal: Payment Details
    Portal->>Student: Redirect to Gateway

    Student->>Gateway: Enter Payment Details
    Gateway->>Bank: Process Transaction
    Bank-->>Gateway: Transaction Status
    Gateway-->>Student: Show Status Page
    Gateway->>ERP: Webhook Callback
    ERP->>Gateway: Verify Signature
    Gateway-->>ERP: Signature Valid
    ERP->>ERP: Update Payment Status
    ERP->>Portal: Notify Success
    Portal->>Student: Show Receipt
```

### Fee Components

```mermaid
graph TD
    FEE[Total Fee Structure]

    FEE --> TUITION[Tuition Fee]
    FEE --> EXAM[Examination Fee]
    FEE --> LIBRARY[Library Fee]
    FEE --> SPORTS[Sports Fee]
    FEE --> DEV[Development Fee]
    FEE --> LAB[Laboratory Fee]
    FEE --> CAUTION[Caution Deposit]

    TUITION --> DISCOUNT{Eligible for<br/>Discount?}
    DISCOUNT -->|Scholarship| REDUCE1[Apply Scholarship]
    DISCOUNT -->|Merit| REDUCE2[Apply Merit Discount]
    DISCOUNT -->|Category| REDUCE3[Apply Category Discount]

    style FEE fill:#FFE4B5
    style DISCOUNT fill:#E6F3FF
```

---

## 5. Examination Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Term End Approaching]) --> CREATE_SCHEDULE[Exam Controller Creates Exam Schedule]
    CREATE_SCHEDULE --> SELECT_COURSES[Select Courses for Examination]
    SELECT_COURSES --> SET_DATES[Set Exam Dates & Timings]
    SET_DATES --> ALLOC_HALLS[Allocate Exam Halls]

    ALLOC_HALLS --> GEN_SEATING[Generate Seating Plan]
    GEN_SEATING --> ASSIGN_INVIG[Assign Invigilators]
    ASSIGN_INVIG --> PUBLISH_SCHEDULE[Publish Exam Schedule]

    PUBLISH_SCHEDULE --> NOTIFY_STUDENTS[Notify Students]
    NOTIFY_STUDENTS --> PREP_QPAPER[Prepare Question Papers]

    PREP_QPAPER --> PAPER_MODE{Paper Type}
    PAPER_MODE -->|Online| CREATE_ONLINE[Create Online Exam]
    PAPER_MODE -->|Offline| PRINT_PAPER[Print Question Papers]

    CREATE_ONLINE --> ASSIGN_QUESTIONS[Assign Questions from Bank]
    ASSIGN_QUESTIONS --> SET_DURATION[Set Duration & Rules]
    SET_DURATION --> PUBLISH_ONLINE[Publish Online Exam]

    PRINT_PAPER --> SEAL[Seal in Envelopes]
    SEAL --> STORE[Store in Strong Room]

    PUBLISH_ONLINE --> WAIT_EXAM[Wait for Exam Date]
    STORE --> WAIT_EXAM

    WAIT_EXAM --> EXAM_DAY[Exam Day]

    EXAM_DAY --> MODE_CHECK{Exam Mode}
    MODE_CHECK -->|Online| ACTIVATE[Activate Online Exam]
    MODE_CHECK -->|Offline| DISTRIBUTE[Distribute Papers]

    ACTIVATE --> STUDENT_LOGIN[Students Login]
    STUDENT_LOGIN --> VERIFY_ID[Verify Student Identity]
    VERIFY_ID --> START_EXAM[Start Exam Timer]

    DISTRIBUTE --> VERIFY_SEAL[Verify Seal]
    VERIFY_SEAL --> HAND_PAPER[Hand Papers to Students]
    HAND_PAPER --> START_EXAM

    START_EXAM --> CONDUCT[Conduct Examination]
    CONDUCT --> MONITOR[Monitor for Malpractice]

    MONITOR --> MALPRACTICE{Malpractice<br/>Detected?}
    MALPRACTICE -->|Yes| REPORT_MALP[Report Malpractice]
    REPORT_MALP --> DISCIPLINARY[Disciplinary Action]
    DISCIPLINARY --> CONDUCT

    MALPRACTICE -->|No| CONTINUE[Continue Exam]
    CONTINUE --> TIME_UP{Time Up?}

    TIME_UP -->|No| CONDUCT
    TIME_UP -->|Yes| COLLECT[Collect Answer Sheets]

    COLLECT --> ONLINE_CHECK{Online Exam?}
    ONLINE_CHECK -->|Yes| AUTO_SAVE[Auto-Save Responses]
    ONLINE_CHECK -->|No| BUNDLE[Bundle Answer Sheets]

    AUTO_SAVE --> STORE_RESP[Store in Database]
    BUNDLE --> HAND_EVAL[Hand to Evaluators]

    STORE_RESP --> END([End: Exam Conducted])
    HAND_EVAL --> END

    style START fill:#90EE90
    style END fill:#FFB6C1
    style PAPER_MODE fill:#FFE4B5
    style MODE_CHECK fill:#FFE4B5
    style MALPRACTICE fill:#FFE4B5
    style TIME_UP fill:#FFE4B5
    style ONLINE_CHECK fill:#FFE4B5
```

### Exam Monitoring (Online Exams)

```mermaid
flowchart TD
    MONITOR[Online Exam Monitoring]

    MONITOR --> PROCTORING[Proctoring Features]
    PROCTORING --> WEBCAM[Webcam Monitoring]
    PROCTORING --> SCREEN[Screen Recording]
    PROCTORING --> TAB[Tab Switching Detection]
    PROCTORING --> BROWSER[Browser Lock]

    MONITOR --> ALERTS[Alert System]
    ALERTS --> FACE[Face Not Detected]
    ALERTS --> MULTI[Multiple Faces]
    ALERTS --> SWITCH[Tab Switched]
    ALERTS --> COPY[Copy-Paste Detected]

    MONITOR --> AI[AI-Based Detection]
    AI --> UNUSUAL[Unusual Eye Movement]
    AI --> AUDIO[Audio Detection]
    AI --> PATTERN[Behavior Pattern Analysis]

    style MONITOR fill:#FFE4B5
    style PROCTORING fill:#E6F3FF
    style ALERTS fill:#FFB6C1
    style AI fill:#90EE90
```

---

## 6. Result Processing Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Exams Completed]) --> COLLECT[Collect Answer Sheets]
    COLLECT --> MODE{Exam Mode}

    MODE -->|Online| AUTO_EVAL[Automatic Evaluation]
    MODE -->|Offline| DISTRIB[Distribute to Evaluators]

    AUTO_EVAL --> OBJECTIVE[Evaluate Objective Questions]
    OBJECTIVE --> CALC_MARKS[Calculate Marks]

    DISTRIB --> BLIND[Implement Blind Evaluation]
    BLIND --> EVALUATOR[Evaluator Reviews Answers]
    EVALUATOR --> AWARD_MARKS[Award Marks per Question]
    AWARD_MARKS --> SUBMIT_EVAL[Submit Evaluation]

    SUBMIT_EVAL --> DOUBLE_EVAL{Marks Difference<br/>> 10%?}
    DOUBLE_EVAL -->|Yes| THIRD_EVAL[Send to Third Evaluator]
    THIRD_EVAL --> FINAL_MARKS[Take Average/Final Decision]
    DOUBLE_EVAL -->|No| FINAL_MARKS

    FINAL_MARKS --> CALC_MARKS
    CALC_MARKS --> ENTER_MARKS[Enter Marks in System]

    ENTER_MARKS --> VERIFY{HOD Verification}
    VERIFY -->|Corrections Needed| NOTIFY_ERROR[Notify Evaluator]
    NOTIFY_ERROR --> EVALUATOR

    VERIFY -->|Approved| INTERNAL_DONE[Internal Marks Approved]
    INTERNAL_DONE --> EXTERNAL{External Exam?}

    EXTERNAL -->|Yes| EXTERNAL_EVAL[External Evaluation]
    EXTERNAL_EVAL --> COMBINE[Combine Internal + External]
    EXTERNAL -->|No| COMBINE

    COMBINE --> TOTAL_CALC[Calculate Total Marks]
    TOTAL_CALC --> GRADE_CALC[Calculate Grade]
    GRADE_CALC --> APPLY_RULES[Apply Grace Marks Rules]

    APPLY_RULES --> RESULT_STATUS{Pass/Fail<br/>Status}
    RESULT_STATUS --> GEN_RESULT[Generate Individual Results]

    GEN_RESULT --> CONTROLLER{Exam Controller<br/>Review}
    CONTROLLER -->|Corrections| BACK_REVIEW[Send for Re-review]
    BACK_REVIEW --> VERIFY

    CONTROLLER -->|Approved| PUBLISH_RESULT[Publish Results]
    PUBLISH_RESULT --> NOTIFY_ALL[Notify All Students]

    NOTIFY_ALL --> GEN_GRADE[Generate Grade Cards]
    GEN_GRADE --> REEVAL{Revaluation<br/>Requests?}

    REEVAL -->|Yes| PROCESS_REEVAL[Process Revaluation]
    PROCESS_REEVAL --> UPDATE_RESULT[Update Results if Changed]
    UPDATE_RESULT --> FINAL_PUBLISH[Final Publication]

    REEVAL -->|No| FINAL_PUBLISH
    FINAL_PUBLISH --> GEN_TRANSCRIPT[Generate Transcripts]
    GEN_TRANSCRIPT --> END([End: Result Processing Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style MODE fill:#FFE4B5
    style DOUBLE_EVAL fill:#FFE4B5
    style VERIFY fill:#FFE4B5
    style EXTERNAL fill:#FFE4B5
    style RESULT_STATUS fill:#FFE4B5
    style CONTROLLER fill:#FFE4B5
    style REEVAL fill:#FFE4B5
```

### Grade Calculation Logic

```mermaid
flowchart LR
    MARKS[Total Marks] --> PERCENT[Calculate Percentage]
    PERCENT --> GRADE_SCALE[Apply Grade Scale]

    GRADE_SCALE --> A[>= 90: A+]
    GRADE_SCALE --> B[80-89: A]
    GRADE_SCALE --> C[70-79: B+]
    GRADE_SCALE --> D[60-69: B]
    GRADE_SCALE --> E[50-59: C]
    GRADE_SCALE --> F[40-49: D]
    GRADE_SCALE --> G[< 40: F - Fail]

    A --> GPA[Calculate GPA]
    B --> GPA
    C --> GPA
    D --> GPA
    E --> GPA
    F --> GPA
    G --> GPA

    GPA --> CGPA[Calculate CGPA]

    style MARKS fill:#E6F3FF
    style CGPA fill:#90EE90
```

---

## 7. Leave Application Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Student Needs Leave]) --> LOGIN[Student Logs in Portal]
    LOGIN --> SELECT_TYPE[Select Leave Type]
    SELECT_TYPE --> TYPES{Leave Type}

    TYPES -->|Sick Leave| MEDICAL[Upload Medical Certificate]
    TYPES -->|Casual Leave| REASON[Enter Reason]
    TYPES -->|Emergency| EMERGENCY[Emergency Details]

    MEDICAL --> DATES[Select From/To Dates]
    REASON --> DATES
    EMERGENCY --> DATES

    DATES --> CONTACT[Provide Contact Details]
    CONTACT --> SUBMIT[Submit Application]

    SUBMIT --> CLASS_TEACHER{Class Teacher<br/>Review}
    CLASS_TEACHER -->|Rejected| NOTIFY_REJ[Notify Student - Rejected]
    NOTIFY_REJ --> END_REJ([End: Leave Rejected])

    CLASS_TEACHER -->|Approved| DURATION{Leave Duration}
    DURATION -->|> 3 Days| HOD_APPROVAL{HOD Approval}
    DURATION -->|<= 3 Days| APPROVED[Leave Approved]

    HOD_APPROVAL -->|Rejected| NOTIFY_REJ
    HOD_APPROVAL -->|Approved| DEAN_CHECK{> 7 Days?}

    DEAN_CHECK -->|Yes| DEAN_APPROVAL{Dean Approval}
    DEAN_CHECK -->|No| APPROVED

    DEAN_APPROVAL -->|Rejected| NOTIFY_REJ
    DEAN_APPROVAL -->|Approved| APPROVED

    APPROVED --> UPDATE_ATT[Mark Attendance as 'On Leave']
    UPDATE_ATT --> NOTIFY_FACULTY[Notify Course Instructors]
    NOTIFY_FACULTY --> NOTIFY_SUCCESS[Notify Student - Approved]
    NOTIFY_SUCCESS --> END([End: Leave Approved])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_REJ fill:#FF6B6B
    style CLASS_TEACHER fill:#FFE4B5
    style HOD_APPROVAL fill:#FFE4B5
    style DEAN_APPROVAL fill:#FFE4B5
```

### Leave Types & Approval Hierarchy

```mermaid
graph TD
    LEAVE[Leave Types]

    LEAVE --> SICK[Sick Leave]
    LEAVE --> CASUAL[Casual Leave]
    LEAVE --> EMERGENCY[Emergency Leave]
    LEAVE --> COMP[Compensatory Leave]

    SICK --> SICK_RULE[Max: 10 days/year<br/>Medical cert required]
    CASUAL --> CASUAL_RULE[Max: 5 days/year<br/>Prior approval needed]
    EMERGENCY --> EMERG_RULE[Max: 3 days/year<br/>Post-approval allowed]
    COMP --> COMP_RULE[For events/competitions<br/>HOD approval]

    APPROVAL[Approval Hierarchy]

    APPROVAL --> L1[<= 1 day: Class Teacher]
    APPROVAL --> L2[2-3 days: Class Teacher + HOD]
    APPROVAL --> L3[4-7 days: CT + HOD + Warden]
    APPROVAL --> L4[> 7 days: CT + HOD + Dean]

    style LEAVE fill:#E6F3FF
    style APPROVAL fill:#FFE4B5
```

---

## 8. Grievance Redressal Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Student Has Grievance]) --> LOGIN[Student Logs in Portal]
    LOGIN --> CATEGORY[Select Grievance Category]
    CATEGORY --> CATS{Category}

    CATS -->|Academic| ACAD[Academic Related]
    CATS -->|Fees| FEE[Fee Related]
    CATS -->|Infrastructure| INFRA[Infrastructure Related]
    CATS -->|Harassment| HARASS[Harassment/Ragging]
    CATS -->|Other| OTHER[Other Issues]

    ACAD --> DESC[Describe Issue in Detail]
    FEE --> DESC
    INFRA --> DESC
    HARASS --> URGENT[Mark as Urgent]
    OTHER --> DESC

    URGENT --> DESC
    DESC --> ATTACH[Attach Supporting Documents]
    ATTACH --> ANON{Submit<br/>Anonymously?}

    ANON -->|Yes| SUBMIT_ANON[Submit Anonymous]
    ANON -->|No| SUBMIT[Submit with Identity]

    SUBMIT_ANON --> ASSIGN
    SUBMIT --> ASSIGN[Auto-Assign to Officer]

    ASSIGN --> PRIORITY{Priority Level}
    PRIORITY -->|Critical| SLA_2[SLA: 2 Days]
    PRIORITY -->|High| SLA_5[SLA: 5 Days]
    PRIORITY -->|Medium| SLA_10[SLA: 10 Days]
    PRIORITY -->|Low| SLA_15[SLA: 15 Days]

    SLA_2 --> OFFICER{Officer<br/>Reviews}
    SLA_5 --> OFFICER
    SLA_10 --> OFFICER
    SLA_15 --> OFFICER

    OFFICER -->|Need More Info| REQUEST_INFO[Request Additional Info]
    REQUEST_INFO --> STUDENT_RESP[Student Responds]
    STUDENT_RESP --> OFFICER

    OFFICER -->|Cannot Resolve| ESCALATE{Escalate to<br/>Committee?}
    ESCALATE -->|Yes| COMMITTEE[Grievance Committee Review]
    ESCALATE -->|No| RESOLVE

    COMMITTEE --> HEARING[Conduct Hearing]
    HEARING --> DECISION[Committee Decision]
    DECISION --> RESOLVE[Resolve Grievance]

    OFFICER -->|Can Resolve| RESOLVE

    RESOLVE --> ACTION[Take Corrective Action]
    ACTION --> CLOSE[Close Grievance]
    CLOSE --> NOTIFY[Notify Student of Resolution]

    NOTIFY --> FEEDBACK{Student<br/>Satisfied?}
    FEEDBACK -->|No| REOPEN[Reopen Grievance]
    REOPEN --> ESCALATE

    FEEDBACK -->|Yes| SURVEY[Request Feedback Survey]
    SURVEY --> END([End: Grievance Resolved])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style PRIORITY fill:#FFE4B5
    style OFFICER fill:#FFE4B5
    style ESCALATE fill:#FFE4B5
    style FEEDBACK fill:#FFE4B5
```

### SLA Monitoring

```mermaid
flowchart LR
    TIMER[SLA Timer Starts]

    TIMER --> CHECK{Time Elapsed}
    CHECK -->|< 50% SLA| GREEN[Status: On Track]
    CHECK -->|50-80% SLA| YELLOW[Status: Warning]
    CHECK -->|80-100% SLA| ORANGE[Status: Alert]
    CHECK -->|> 100% SLA| RED[Status: Breached]

    YELLOW --> REMIND1[Remind Officer]
    ORANGE --> REMIND2[Alert Supervisor]
    RED --> ESCALATE[Auto-Escalate]

    style GREEN fill:#90EE90
    style YELLOW fill:#FFFF99
    style ORANGE fill:#FFA500
    style RED fill:#FF6B6B
```

---

## 9. Library Book Issue/Return Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Student Wants Book]) --> SEARCH[Search Book in Catalog]
    SEARCH --> FOUND{Book Found?}

    FOUND -->|No| SUGGEST[Show Similar Books]
    SUGGEST --> REQUEST_PUR[Request Purchase]
    REQUEST_PUR --> END_REQ([End: Purchase Request])

    FOUND -->|Yes| CHECK_AVAIL{Book Available?}
    CHECK_AVAIL -->|No| RESERVE[Reserve Book]
    RESERVE --> NOTIFY_AVAIL[Notify When Available]
    NOTIFY_AVAIL --> END_RESERVED([End: Book Reserved])

    CHECK_AVAIL -->|Yes| CHECK_QUOTA{Issue Quota<br/>Available?}
    CHECK_QUOTA -->|No| SHOW_QUOTA[Show Quota Exceeded Message]
    SHOW_QUOTA --> END_QUOTA([End: Quota Exceeded])

    CHECK_QUOTA -->|Yes| REQUEST_ISSUE[Request Book Issue]
    REQUEST_ISSUE --> VISIT_LIB[Visit Library]
    VISIT_LIB --> VERIFY_ID[Librarian Verifies ID Card]

    VERIFY_ID --> ID_OK{ID Valid?}
    ID_OK -->|No| REJECT[Reject Issue]
    REJECT --> END_REJECT([End: Issue Rejected])

    ID_OK -->|Yes| CHECK_DUES{Pending Dues?}
    CHECK_DUES -->|Yes| PAY_DUES[Pay Pending Dues]
    PAY_DUES --> ISSUE

    CHECK_DUES -->|No| ISSUE[Issue Book]
    ISSUE --> SCAN[Scan Book Barcode]
    SCAN --> UPDATE_RECORD[Update Issue Record]
    UPDATE_RECORD --> CALC_DUE[Calculate Due Date]
    CALC_DUE --> PRINT_SLIP[Print Issue Slip]
    PRINT_SLIP --> REMINDER[Set Return Reminder]

    REMINDER --> WAIT[Wait for Return]
    WAIT --> DUE_NEAR{Due Date<br/>Approaching?}
    DUE_NEAR -->|Yes| SEND_REMINDER[Send Return Reminder]
    SEND_REMINDER --> RETURNED{Book Returned?}

    DUE_NEAR -->|No| RETURNED
    RETURNED -->|No| OVERDUE{Due Date<br/>Passed?}

    OVERDUE -->|Yes| CALC_FINE[Calculate Fine]
    CALC_FINE --> BLOCK[Block Further Issues]
    BLOCK --> SEND_NOTICE[Send Overdue Notice]
    SEND_NOTICE --> RETURNED

    OVERDUE -->|No| WAIT

    RETURNED -->|Yes| VISIT_RETURN[Student Returns Book]
    VISIT_RETURN --> CHECK_DAMAGE{Book<br/>Damaged?}

    CHECK_DAMAGE -->|Yes| ASSESS_DAMAGE[Assess Damage]
    ASSESS_DAMAGE --> DAMAGE_FINE[Charge Damage Fine]
    DAMAGE_FINE --> COLLECT_FINE

    CHECK_DAMAGE -->|No| CHECK_LATE{Returned<br/>Late?}
    CHECK_LATE -->|Yes| COLLECT_FINE[Collect Late Fine]
    CHECK_LATE -->|No| COMPLETE

    COLLECT_FINE --> COMPLETE[Complete Return]
    COMPLETE --> UPDATE_REC[Update Return Record]
    UPDATE_REC --> UNBLOCK[Unblock Student]
    UNBLOCK --> NOTIFY_WAIT[Notify Reserved Students]
    NOTIFY_WAIT --> END([End: Book Returned])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_REQ fill:#E6F3FF
    style END_RESERVED fill:#FFA07A
    style END_QUOTA fill:#FF6B6B
    style END_REJECT fill:#FF6B6B
    style FOUND fill:#FFE4B5
    style CHECK_AVAIL fill:#FFE4B5
    style CHECK_QUOTA fill:#FFE4B5
    style ID_OK fill:#FFE4B5
    style CHECK_DUES fill:#FFE4B5
    style DUE_NEAR fill:#FFE4B5
    style RETURNED fill:#FFE4B5
    style OVERDUE fill:#FFE4B5
    style CHECK_DAMAGE fill:#FFE4B5
    style CHECK_LATE fill:#FFE4B5
```

### Library Rules & Fine Structure

```mermaid
graph TD
    RULES[Library Rules]

    RULES --> QUOTA[Issue Quota]
    QUOTA --> UG[UG Students: 3 books]
    QUOTA --> PG[PG Students: 5 books]
    QUOTA --> FACULTY[Faculty: 10 books]

    RULES --> DURATION[Issue Duration]
    DURATION --> UG_DUR[UG: 14 days]
    DURATION --> PG_DUR[PG: 21 days]
    DURATION --> FAC_DUR[Faculty: 30 days]

    RULES --> FINES[Fine Structure]
    FINES --> LATE[Late Return: ₹2/day]
    FINES --> LOST[Lost Book: Book Price + ₹100]
    FINES --> DAMAGE[Damaged: 50% Book Price]

    style RULES fill:#FFE4B5
    style QUOTA fill:#E6F3FF
    style DURATION fill:#E6F3FF
    style FINES fill:#FFB6C1
```

---

## 10. Hostel Allocation Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Hostel Application Opens]) --> LOGIN[Student Logs in Portal]
    LOGIN --> CHECK_ELIG{Eligible for<br/>Hostel?}

    CHECK_ELIG -->|No| SHOW_REASON[Show Ineligibility Reason]
    SHOW_REASON --> END_INELIG([End: Not Eligible])

    CHECK_ELIG -->|Yes| FILL_APP[Fill Application Form]
    FILL_APP --> PREFERENCE[Select Room Preferences]
    PREFERENCE --> UPLOAD_DOC[Upload Required Documents]
    UPLOAD_DOC --> PAY_APP_FEE[Pay Application Fee]

    PAY_APP_FEE --> SUBMIT[Submit Application]
    SUBMIT --> WARDEN_REV{Warden<br/>Review}

    WARDEN_REV -->|Rejected| NOTIFY_REJ[Notify Student - Rejected]
    NOTIFY_REJ --> END_REJ([End: Application Rejected])

    WARDEN_REV -->|Approved| PRIORITY_CALC[Calculate Priority Score]
    PRIORITY_CALC --> FACTORS{Priority Factors}

    FACTORS --> DISTANCE[Distance from Home]
    FACTORS --> CATEGORY[Category/Quota]
    FACTORS --> ACADEMIC[Academic Performance]
    FACTORS --> INCOME[Family Income]

    DISTANCE --> GEN_LIST[Generate Priority List]
    CATEGORY --> GEN_LIST
    ACADEMIC --> GEN_LIST
    INCOME --> GEN_LIST

    GEN_LIST --> ALLOC_ROUND[Allocation Round]
    ALLOC_ROUND --> CHECK_AVAIL{Rooms<br/>Available?}

    CHECK_AVAIL -->|No| WAITLIST[Add to Waitlist]
    WAITLIST --> END_WAIT([End: Waitlisted])

    CHECK_AVAIL -->|Yes| ALLOC[Allocate Room]
    ALLOC --> NOTIFY_ALLOC[Notify Student]

    NOTIFY_ALLOC --> ACCEPT{Student<br/>Accepts?}
    ACCEPT -->|No| RELEASE[Release Room]
    RELEASE --> END_DECLINED([End: Allocation Declined])

    ACCEPT -->|Yes| PAY_FEE[Pay Hostel Fee]
    PAY_FEE --> VERIFY_PAY{Payment<br/>Verified?}

    VERIFY_PAY -->|No| REMINDER[Send Payment Reminder]
    REMINDER --> DEADLINE{Within<br/>Deadline?}
    DEADLINE -->|No| CANCEL[Cancel Allocation]
    CANCEL --> RELEASE
    DEADLINE -->|Yes| PAY_FEE

    VERIFY_PAY -->|Yes| CONFIRM[Confirm Allocation]
    CONFIRM --> GEN_ALLOC_LETTER[Generate Allotment Letter]
    GEN_ALLOC_LETTER --> CHECKIN_DATE[Set Check-in Date]

    CHECKIN_DATE --> CHECKIN[Student Checks In]
    CHECKIN --> VERIFY_DOC[Verify Documents]
    VERIFY_DOC --> INSPECT[Inspect Room]
    INSPECT --> INVENTORY[Sign Inventory List]
    INVENTORY --> HANDOVER[Handover Keys]
    HANDOVER --> CREATE_RECORD[Create Occupancy Record]
    CREATE_RECORD --> END([End: Allocation Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_INELIG fill:#FF6B6B
    style END_REJ fill:#FF6B6B
    style END_WAIT fill:#FFA07A
    style END_DECLINED fill:#E6F3FF
    style CHECK_ELIG fill:#FFE4B5
    style WARDEN_REV fill:#FFE4B5
    style CHECK_AVAIL fill:#FFE4B5
    style ACCEPT fill:#FFE4B5
    style VERIFY_PAY fill:#FFE4B5
    style DEADLINE fill:#FFE4B5
```

### Priority Calculation

```mermaid
flowchart LR
    PRIORITY[Priority Score Calculation]

    PRIORITY --> DIST[Distance Points]
    DIST --> D1[> 100km: 40 points]
    DIST --> D2[50-100km: 30 points]
    DIST --> D3[< 50km: 10 points]

    PRIORITY --> CAT[Category Points]
    CAT --> C1[SC/ST: 20 points]
    CAT --> C2[OBC: 15 points]
    CAT --> C3[EWS: 10 points]

    PRIORITY --> ACAD[Academic Points]
    ACAD --> A1[CGPA > 8.5: 20 points]
    ACAD --> A2[CGPA 7-8.5: 15 points]
    ACAD --> A3[CGPA < 7: 10 points]

    PRIORITY --> INC[Income Points]
    INC --> I1[< 1 Lakh: 20 points]
    INC --> I2[1-3 Lakh: 15 points]
    INC --> I3[> 3 Lakh: 5 points]

    D1 --> TOTAL[Total Score]
    D2 --> TOTAL
    D3 --> TOTAL
    C1 --> TOTAL
    C2 --> TOTAL
    C3 --> TOTAL
    A1 --> TOTAL
    A2 --> TOTAL
    A3 --> TOTAL
    I1 --> TOTAL
    I2 --> TOTAL
    I3 --> TOTAL

    TOTAL --> RANK[Rank Students]

    style PRIORITY fill:#E6F3FF
    style TOTAL fill:#90EE90
```

---

## 11. Transport Allocation Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Transport Registration Opens]) --> LOGIN[Student Logs in Portal]
    LOGIN --> VIEW_ROUTES[View Available Routes]
    VIEW_ROUTES --> SELECT[Select Route]
    SELECT --> CHECK_STOPS{Pickup Stop<br/>Available?}

    CHECK_STOPS -->|No| REQ_STOP[Request New Stop]
    REQ_STOP --> TRANSPORT_OFF{Transport Officer<br/>Reviews}
    TRANSPORT_OFF -->|Rejected| NOTIFY_STOP_REJ[Notify Student]
    NOTIFY_STOP_REJ --> VIEW_ROUTES
    TRANSPORT_OFF -->|Approved| ADD_STOP[Add Stop to Route]
    ADD_STOP --> FILL_APP

    CHECK_STOPS -->|Yes| FILL_APP[Fill Application]
    FILL_APP --> UPLOAD[Upload Address Proof]
    UPLOAD --> SUBMIT_APP[Submit Application]

    SUBMIT_APP --> CHECK_SEATS{Seats<br/>Available?}
    CHECK_SEATS -->|No| WAITLIST[Add to Waitlist]
    WAITLIST --> END_WAIT([End: Waitlisted])

    CHECK_SEATS -->|Yes| CALC_FEE[Calculate Transport Fee]
    CALC_FEE --> NOTIFY_FEE[Notify Student]

    NOTIFY_FEE --> PAY_FEE[Pay Transport Fee]
    PAY_FEE --> VERIFY{Payment<br/>Verified?}

    VERIFY -->|No| REMINDER[Send Reminder]
    REMINDER --> DEADLINE{Within<br/>Deadline?}
    DEADLINE -->|No| CANCEL[Cancel Application]
    CANCEL --> END_CANCEL([End: Application Cancelled])
    DEADLINE -->|Yes| PAY_FEE

    VERIFY -->|Yes| ALLOC[Allocate Seat]
    ALLOC --> UPDATE[Update Vehicle Roster]
    UPDATE --> GEN_PASS[Generate Bus Pass]
    GEN_PASS --> NOTIFY_SUCCESS[Notify Student]
    NOTIFY_SUCCESS --> COLLECT[Collect Bus Pass from Office]
    COLLECT --> ACTIVE[Activate Transport Service]
    ACTIVE --> END([End: Transport Allocated])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_WAIT fill:#FFA07A
    style END_CANCEL fill:#FF6B6B
    style CHECK_STOPS fill:#FFE4B5
    style TRANSPORT_OFF fill:#FFE4B5
    style CHECK_SEATS fill:#FFE4B5
    style VERIFY fill:#FFE4B5
    style DEADLINE fill:#FFE4B5
```

### Route Optimization

```mermaid
graph TD
    OPTIMIZE[Route Optimization]

    OPTIMIZE --> FACTORS[Optimization Factors]
    FACTORS --> TIME[Minimize Travel Time]
    FACTORS --> DIST[Minimize Distance]
    FACTORS --> UTIL[Maximize Vehicle Utilization]
    FACTORS --> DEMAND[Balance Demand]

    OPTIMIZE --> SCHEDULE[Schedule Optimization]
    SCHEDULE --> MORNING[Morning Routes]
    SCHEDULE --> EVENING[Evening Routes]
    SCHEDULE --> TIMING[Timing based on Timetable]

    OPTIMIZE --> CAPACITY[Capacity Management]
    CAPACITY --> VEHICLE[Vehicle Capacity]
    CAPACITY --> STUDENT[Student Demand]
    CAPACITY --> PEAK[Peak Hour Management]

    style OPTIMIZE fill:#E6F3FF
```

---

## 12. Attendance Marking Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Class Begins]) --> METHOD{Attendance<br/>Method}

    METHOD -->|Manual| MANUAL[Manual Marking]
    METHOD -->|Biometric| BIOMETRIC[Biometric System]
    METHOD -->|App-Based| APP[Mobile App]
    METHOD -->|QR Code| QR[QR Code Scan]

    MANUAL --> FACULTY_LOGIN[Faculty Logs in]
    FACULTY_LOGIN --> SELECT_CLASS[Select Course Schedule]
    SELECT_CLASS --> LOAD_STUDENTS[Load Student List]
    LOAD_STUDENTS --> MARK[Mark Attendance]

    BIOMETRIC --> SCAN[Student Scans Fingerprint]
    SCAN --> VERIFY_BIO{Biometric<br/>Verified?}
    VERIFY_BIO -->|No| ERROR[Show Error]
    ERROR --> RETRY{Retry?}
    RETRY -->|Yes| SCAN
    RETRY -->|No| MANUAL_FALLBACK[Mark Manually]
    MANUAL_FALLBACK --> MARK

    VERIFY_BIO -->|Yes| LOCATION{Within Campus<br/>Location?}
    LOCATION -->|No| DENY[Deny Attendance]
    DENY --> ALERT_ADMIN[Alert Administrator]
    LOCATION -->|Yes| AUTO_MARK[Auto Mark Present]

    APP --> STUDENT_OPEN[Student Opens App]
    STUDENT_OPEN --> VERIFY_LOC{Location<br/>Verified?}
    VERIFY_LOC -->|No| DENY
    VERIFY_LOC -->|Yes| VERIFY_TIME{Within Time<br/>Window?}
    VERIFY_TIME -->|No| MARK_LATE[Mark Late]
    VERIFY_TIME -->|Yes| SELF_MARK[Self Mark Present]

    QR --> GENERATE_QR[Faculty Generates Dynamic QR]
    GENERATE_QR --> DISPLAY[Display QR Code]
    DISPLAY --> STUDENT_SCAN[Students Scan QR]
    STUDENT_SCAN --> QR_VERIFY{QR Valid &<br/>Not Expired?}
    QR_VERIFY -->|No| DENY
    QR_VERIFY -->|Yes| SELF_MARK

    MARK --> STATUS{Attendance<br/>Status}
    STATUS -->|Present| PRESENT
    STATUS -->|Absent| ABSENT
    STATUS -->|Late| LATE
    STATUS -->|Leave| ON_LEAVE

    AUTO_MARK --> PRESENT
    SELF_MARK --> PRESENT
    MARK_LATE --> LATE

    PRESENT --> RECORD[Record Attendance]
    ABSENT --> RECORD
    LATE --> RECORD
    ON_LEAVE --> RECORD

    RECORD --> SYNC[Sync to Database]
    SYNC --> CALC_PERCENT[Calculate Attendance %]
    CALC_PERCENT --> CHECK_LOW{Attendance<br/>< 75%?}

    CHECK_LOW -->|Yes| ALERT[Alert Student & Parent]
    CHECK_LOW -->|No| UPDATE

    ALERT --> UPDATE[Update Dashboard]
    UPDATE --> NOTIFY_STUDENT[Notify Student]
    NOTIFY_STUDENT --> END([End: Attendance Recorded])

    ALERT_ADMIN --> END

    style START fill:#90EE90
    style END fill:#FFB6C1
    style METHOD fill:#FFE4B5
    style VERIFY_BIO fill:#FFE4B5
    style LOCATION fill:#FFE4B5
    style VERIFY_LOC fill:#FFE4B5
    style VERIFY_TIME fill:#FFE4B5
    style QR_VERIFY fill:#FFE4B5
    style STATUS fill:#FFE4B5
    style CHECK_LOW fill:#FFE4B5
```

### Attendance Methods Comparison

```mermaid
graph TD
    METHODS[Attendance Methods]

    METHODS --> M1[Manual Marking]
    M1 --> M1_PRO[Pros: Simple, Flexible]
    M1 --> M1_CON[Cons: Time-consuming, Proxy risk]

    METHODS --> M2[Biometric]
    M2 --> M2_PRO[Pros: Secure, Automated]
    M2 --> M2_CON[Cons: Hardware cost, Queues]

    METHODS --> M3[Mobile App]
    M3 --> M3_PRO[Pros: Quick, Location-based]
    M3 --> M3_CON[Cons: GPS spoofing risk]

    METHODS --> M4[QR Code]
    M4 --> M4_PRO[Pros: Fast, Dynamic]
    M4 --> M4_CON[Cons: Screenshot sharing risk]

    style METHODS fill:#E6F3FF
```

---

## 13. Assignment Submission Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Assignment Created]) --> FACULTY[Faculty Creates Assignment]
    FACULTY --> SET_DETAILS[Set Title, Description, Marks]
    SET_DETAILS --> SET_DEADLINE[Set Submission Deadline]
    SET_DEADLINE --> ATTACH[Attach Reference Files]
    ATTACH --> PUBLISH[Publish Assignment]

    PUBLISH --> NOTIFY[Notify Students]
    NOTIFY --> STUDENT_VIEW[Student Views Assignment]
    STUDENT_VIEW --> DOWNLOAD[Download Reference Materials]
    DOWNLOAD --> WORK[Student Works on Assignment]

    WORK --> PREPARE[Prepare Submission File]
    PREPARE --> UPLOAD[Upload File]
    UPLOAD --> CHECK_SIZE{File Size<br/>Valid?}

    CHECK_SIZE -->|No| SIZE_ERROR[Show Size Error]
    SIZE_ERROR --> UPLOAD

    CHECK_SIZE -->|Yes| CHECK_FORMAT{File Format<br/>Allowed?}
    CHECK_FORMAT -->|No| FORMAT_ERROR[Show Format Error]
    FORMAT_ERROR --> UPLOAD

    CHECK_FORMAT -->|Yes| CHECK_DEADLINE{Before<br/>Deadline?}
    CHECK_DEADLINE -->|No| LATE{Allow Late<br/>Submission?}

    LATE -->|No| REJECT[Reject Submission]
    REJECT --> END_REJ([End: Submission Rejected])

    LATE -->|Yes| PENALTY[Apply Late Penalty]
    PENALTY --> SUBMIT

    CHECK_DEADLINE -->|Yes| SUBMIT[Submit Assignment]
    SUBMIT --> PLAGIARISM[Run Plagiarism Check]

    PLAGIARISM --> PLAG_SCORE{Plagiarism<br/>> Threshold?}
    PLAG_SCORE -->|Yes| FLAG[Flag Submission]
    FLAG --> NOTIFY_FAC[Notify Faculty]
    NOTIFY_FAC --> MANUAL_REV

    PLAG_SCORE -->|No| CONFIRM[Confirm Submission]
    CONFIRM --> RECEIPT[Generate Receipt]
    RECEIPT --> NOTIFY_STUDENT[Notify Student]
    NOTIFY_STUDENT --> QUEUE[Add to Evaluation Queue]

    QUEUE --> MANUAL_REV[Faculty Reviews Submission]
    MANUAL_REV --> EVALUATE[Evaluate & Award Marks]
    EVALUATE --> FEEDBACK[Provide Feedback]
    FEEDBACK --> PLAG_ACTION{Plagiarism<br/>Flagged?}

    PLAG_ACTION -->|Yes| DISCIPLINARY[Disciplinary Action]
    DISCIPLINARY --> ZERO_MARKS[Award Zero Marks]
    ZERO_MARKS --> PUBLISH_GRADE

    PLAG_ACTION -->|No| PUBLISH_GRADE[Publish Grade]
    PUBLISH_GRADE --> NOTIFY_RESULT[Notify Student]
    NOTIFY_RESULT --> VIEW_RESULT{Student Views<br/>Result}

    VIEW_RESULT --> SATISFIED{Satisfied with<br/>Evaluation?}
    SATISFIED -->|No| REEVAL_REQ[Request Re-evaluation]
    REEVAL_REQ --> HOD_REV{HOD Reviews<br/>Request}
    HOD_REV -->|Approved| MANUAL_REV
    HOD_REV -->|Rejected| FINAL

    SATISFIED -->|Yes| FINAL[Finalize Marks]
    FINAL --> UPDATE_RECORD[Update Academic Record]
    UPDATE_RECORD --> END([End: Assignment Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_REJ fill:#FF6B6B
    style CHECK_SIZE fill:#FFE4B5
    style CHECK_FORMAT fill:#FFE4B5
    style CHECK_DEADLINE fill:#FFE4B5
    style LATE fill:#FFE4B5
    style PLAG_SCORE fill:#FFE4B5
    style PLAG_ACTION fill:#FFE4B5
    style VIEW_RESULT fill:#FFE4B5
    style SATISFIED fill:#FFE4B5
    style HOD_REV fill:#FFE4B5
```

### Plagiarism Detection

```mermaid
flowchart LR
    SUBMIT[Submitted Assignment]

    SUBMIT --> EXTRACT[Extract Text Content]
    EXTRACT --> COMPARE[Compare with Sources]

    COMPARE --> DB[Internal Database]
    COMPARE --> WEB[Web Search]
    COMPARE --> PREV[Previous Submissions]

    DB --> SCORE[Calculate Similarity Score]
    WEB --> SCORE
    PREV --> SCORE

    SCORE --> THRESHOLD{Score > 30%?}
    THRESHOLD -->|No| PASS[Mark as Original]
    THRESHOLD -->|Yes| FLAG[Flag for Review]

    FLAG --> REPORT[Generate Detailed Report]
    REPORT --> FACULTY[Send to Faculty]

    style SUBMIT fill:#E6F3FF
    style PASS fill:#90EE90
    style FLAG fill:#FFB6C1
```

---

## 14. Document Request Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Student Needs Document]) --> LOGIN[Student Logs in Portal]
    LOGIN --> SELECT[Select Document Type]
    SELECT --> TYPES{Document Type}

    TYPES -->|Bonafide| BONAFIDE[Bonafide Certificate]
    TYPES -->|TC| TC[Transfer Certificate]
    TYPES -->|Transcript| TRANSCRIPT[Academic Transcript]
    TYPES -->|ID Card| ID_CARD[ID Card Duplicate]
    TYPES -->|NOC| NOC[No Objection Certificate]

    BONAFIDE --> PURPOSE[Specify Purpose]
    TC --> TC_REASON[Specify Reason]
    TRANSCRIPT --> DELIVERY[Select Delivery Address]
    ID_CARD --> POLICE[Upload Police FIR]
    NOC --> NOC_PURPOSE[Specify Purpose]

    PURPOSE --> FILL
    TC_REASON --> FILL
    DELIVERY --> FILL
    POLICE --> FILL
    NOC_PURPOSE --> FILL

    FILL[Fill Request Form] --> PAY{Fee<br/>Required?}
    PAY -->|Yes| PAY_FEE[Pay Processing Fee]
    PAY -->|No| SUBMIT

    PAY_FEE --> SUBMIT[Submit Request]
    SUBMIT --> REGISTRAR{Registrar<br/>Review}

    REGISTRAR -->|Rejected| NOTIFY_REJ[Notify Student - Rejected]
    NOTIFY_REJ --> END_REJ([End: Request Rejected])

    REGISTRAR -->|Approved| CHECK{Document Type<br/>Check}

    CHECK -->|Auto-Generate| GENERATE[Auto-Generate Document]
    CHECK -->|Manual| PREPARE[Manually Prepare Document]

    GENERATE --> SIGN[Digital Signature]
    PREPARE --> PRINT[Print Document]
    PRINT --> MANUAL_SIGN[Physical Signature & Seal]

    SIGN --> READY
    MANUAL_SIGN --> READY[Document Ready]

    READY --> MODE{Delivery Mode}
    MODE -->|Collect| NOTIFY_COLLECT[Notify to Collect]
    MODE -->|Post| COURIER[Send via Courier]
    MODE -->|Email| EMAIL[Send via Email]

    NOTIFY_COLLECT --> COLLECT_OFFICE[Student Collects from Office]
    COLLECT_OFFICE --> VERIFY_ID[Verify Identity]
    VERIFY_ID --> HANDOVER[Handover Document]

    COURIER --> TRACK[Provide Tracking Number]
    TRACK --> DELIVERED

    EMAIL --> SEND_EMAIL[Send Email with PDF]
    SEND_EMAIL --> DELIVERED

    HANDOVER --> DELIVERED[Document Delivered]
    DELIVERED --> UPDATE[Update Request Status]
    UPDATE --> NOTIFY_SUCCESS[Notify Student - Completed]
    NOTIFY_SUCCESS --> END([End: Request Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_REJ fill:#FF6B6B
    style TYPES fill:#FFE4B5
    style PAY fill:#FFE4B5
    style REGISTRAR fill:#FFE4B5
    style CHECK fill:#FFE4B5
    style MODE fill:#FFE4B5
```

### Document Types & Processing Time

```mermaid
graph TD
    DOCS[Document Types]

    DOCS --> D1[Bonafide Certificate]
    D1 --> T1[Processing: 2 days<br/>Fee: ₹50]

    DOCS --> D2[Transfer Certificate]
    D2 --> T2[Processing: 7 days<br/>Fee: ₹200]

    DOCS --> D3[Academic Transcript]
    D3 --> T3[Processing: 5 days<br/>Fee: ₹500]

    DOCS --> D4[Provisional Certificate]
    D4 --> T4[Processing: 3 days<br/>Fee: ₹100]

    DOCS --> D5[Degree Certificate]
    D5 --> T5[Processing: 30 days<br/>Fee: ₹1000]

    style DOCS fill:#E6F3FF
```

---

## 15. Faculty Recruitment Workflow

### Process Flow Diagram

```mermaid
flowchart TD
    START([Start: Recruitment Need Identified]) --> HOD[HOD Creates Job Requisition]
    HOD --> JUSTIFICATION[Provide Justification]
    JUSTIFICATION --> POSITION[Define Position Details]
    POSITION --> BUDGET{Budget<br/>Available?}

    BUDGET -->|No| REQ_BUDGET[Request Budget Approval]
    REQ_BUDGET --> ADMIN{Admin<br/>Approval}
    ADMIN -->|Rejected| END_REJ([End: Budget Not Approved])
    ADMIN -->|Approved| ALLOC_BUDGET[Allocate Budget]
    ALLOC_BUDGET --> POST

    BUDGET -->|Yes| POST[Post Job Opening]
    POST --> ADVERTISE[Advertise on Portals]
    ADVERTISE --> COLLECT_APP[Collect Applications]

    COLLECT_APP --> DEADLINE{Application<br/>Deadline Reached?}
    DEADLINE -->|No| COLLECT_APP
    DEADLINE -->|Yes| SCREEN[Initial Screening]

    SCREEN --> SHORTLIST[Shortlist Candidates]
    SHORTLIST --> NOTIFY_SHORT[Notify Shortlisted Candidates]
    NOTIFY_SHORT --> SCHEDULE_DEMO[Schedule Demo Lecture]

    SCHEDULE_DEMO --> CONDUCT_DEMO[Conduct Demo Lecture]
    CONDUCT_DEMO --> EVAL_DEMO[Evaluate Demo]
    EVAL_DEMO --> DEMO_PASS{Demo<br/>Satisfactory?}

    DEMO_PASS -->|No| REJECT1[Reject Candidate]
    REJECT1 --> MORE_CAND{More<br/>Candidates?}
    MORE_CAND -->|Yes| CONDUCT_DEMO
    MORE_CAND -->|No| RE_ADVERTISE[Re-advertise Position]
    RE_ADVERTISE --> ADVERTISE

    DEMO_PASS -->|Yes| SCHEDULE_INTERVIEW[Schedule Interview]
    SCHEDULE_INTERVIEW --> PANEL[Form Interview Panel]
    PANEL --> CONDUCT_INT[Conduct Interview]

    CONDUCT_INT --> TECHNICAL[Technical Round]
    TECHNICAL --> HR[HR Round]
    HR --> PANEL_DISCUSSION[Panel Discussion]
    PANEL_DISCUSSION --> DECISION{Selection<br/>Decision}

    DECISION -->|Rejected| REJECT2[Reject Candidate]
    REJECT2 --> MORE_CAND

    DECISION -->|Selected| SEND_OFFER[Send Offer Letter]
    SEND_OFFER --> NEGOTIATE{Candidate<br/>Accepts?}

    NEGOTIATE -->|No| COUNTER{Counter<br/>Offer?}
    COUNTER -->|Yes| ADMIN_APPR{Admin<br/>Approves?}
    ADMIN_APPR -->|Yes| REVISE[Revise Offer]
    REVISE --> SEND_OFFER
    ADMIN_APPR -->|No| REJECT3[Reject Counter]
    REJECT3 --> MORE_CAND

    COUNTER -->|No| MORE_CAND

    NEGOTIATE -->|Yes| ACCEPT_OFFER[Offer Accepted]
    ACCEPT_OFFER --> DOC_VERIFY[Document Verification]
    DOC_VERIFY --> BG_CHECK[Background Check]
    BG_CHECK --> BG_OK{Background<br/>Clear?}

    BG_OK -->|No| REJECT4[Withdraw Offer]
    REJECT4 --> MORE_CAND

    BG_OK -->|Yes| JOINING[Set Joining Date]
    JOINING --> ONBOARD[Onboarding Process]
    ONBOARD --> CREATE_EMP[Create Employee Record]
    CREATE_EMP --> ORIENTATION[Conduct Orientation]
    ORIENTATION --> ASSIGN[Assign Courses & Timetable]
    ASSIGN --> PROBATION[Start Probation Period]
    PROBATION --> END([End: Recruitment Complete])

    style START fill:#90EE90
    style END fill:#FFB6C1
    style END_REJ fill:#FF6B6B
    style BUDGET fill:#FFE4B5
    style ADMIN fill:#FFE4B5
    style DEADLINE fill:#FFE4B5
    style DEMO_PASS fill:#FFE4B5
    style MORE_CAND fill:#FFE4B5
    style DECISION fill:#FFE4B5
    style NEGOTIATE fill:#FFE4B5
    style COUNTER fill:#FFE4B5
    style ADMIN_APPR fill:#FFE4B5
    style BG_OK fill:#FFE4B5
```

### Interview Evaluation Criteria

```mermaid
graph TD
    EVAL[Evaluation Criteria]

    EVAL --> TECH[Technical Knowledge - 30%]
    TECH --> T1[Subject Expertise]
    TECH --> T2[Research Publications]
    TECH --> T3[Industry Experience]

    EVAL --> TEACH[Teaching Skills - 30%]
    TEACH --> TE1[Demo Lecture Quality]
    TEACH --> TE2[Communication Skills]
    TEACH --> TE3[Student Engagement]

    EVAL --> RESEARCH[Research Aptitude - 20%]
    RESEARCH --> R1[Publications Count]
    RESEARCH --> R2[Research Proposals]
    RESEARCH --> R3[Patents/Awards]

    EVAL --> PERSON[Personality - 20%]
    PERSON --> P1[Leadership Qualities]
    PERSON --> P2[Team Player]
    PERSON --> P3[Cultural Fit]

    style EVAL fill:#E6F3FF
```

---

## Summary

This workflow documentation provides:

1. **15 Comprehensive Workflows** covering all major university operations
2. **Detailed Process Flow Diagrams** with decision points and alternate paths
3. **State Transitions** with responsible roles at each stage
4. **Business Rules** and validation logic
5. **Notification Triggers** and communication flows
6. **Integration Points** with external systems
7. **Exception Handling** and error scenarios

All diagrams use Mermaid syntax and can be rendered in any Mermaid-compatible viewer or documentation platform.
