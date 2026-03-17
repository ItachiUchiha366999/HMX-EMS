# University ERP - Activity Diagrams

## Table of Contents
1. [Student Onboarding Process](#1-student-onboarding-process)
2. [Course Registration Process](#2-course-registration-process)
3. [Examination Process](#3-examination-process)
4. [Fee Collection Process](#4-fee-collection-process)
5. [Library Management Process](#5-library-management-process)
6. [Hostel Management Process](#6-hostel-management-process)
7. [Attendance Management Process](#7-attendance-management-process)
8. [Result Declaration Process](#8-result-declaration-process)
9. [Grievance Resolution Process](#9-grievance-resolution-process)
10. [Document Issuance Process](#10-document-issuance-process)

---

## 1. Student Onboarding Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Student Admission Confirmed]) --> SendCreds[Send Login Credentials]
    SendCreds --> StudentLogin[Student First Login]
    StudentLogin --> ChangePwd[Change Password]
    ChangePwd --> CompleteProfile[Complete Profile Information]

    CompleteProfile --> UploadPhoto[Upload Photograph]
    UploadPhoto --> AddParent[Add Parent/Guardian Details]
    AddParent --> AddAddress[Add Address Information]
    AddAddress --> AddEmergency[Add Emergency Contact]

    AddEmergency --> SubmitProfile[Submit Profile for Review]
    SubmitProfile --> HODReview{HOD Reviews Profile}

    HODReview -->|Corrections Needed| NotifyCorrections[Notify Student of Corrections]
    NotifyCorrections --> CompleteProfile

    HODReview -->|Approved| AssignRoll[Assign Roll Number]
    AssignRoll --> AssignBatch[Assign to Student Batch]
    AssignBatch --> GenID[Generate ID Card]
    GenID --> ActivatePortal[Activate Portal Access]

    ActivatePortal --> SendWelcome[Send Welcome Email]
    SendWelcome --> ScheduleOrientation[Schedule Orientation]

    ScheduleOrientation --> AttendOrientation{Attend Orientation?}
    AttendOrientation -->|No| MarkAbsent[Mark as Absent]
    MarkAbsent --> FollowUp[Follow Up with Student]

    AttendOrientation -->|Yes| MarkPresent[Mark Attendance]
    MarkPresent --> CourseSelection[Open Course Selection]

    CourseSelection --> SelectCourses[Student Selects Courses]
    SelectCourses --> CheckPrereq{Check Prerequisites}
    CheckPrereq -->|Not Met| ShowError[Show Error]
    ShowError --> SelectCourses

    CheckPrereq -->|Met| CheckCredits{Check Credit Limits}
    CheckCredits -->|Invalid| ShowCreditError[Show Credit Error]
    ShowCreditError --> SelectCourses

    CheckCredits -->|Valid| SubmitSelection[Submit Course Selection]
    SubmitSelection --> AdvisorApproval{Academic Advisor Approval}

    AdvisorApproval -->|Rejected| NotifyRejection[Notify Student]
    NotifyRejection --> SelectCourses

    AdvisorApproval -->|Approved| EnrollCourses[Enroll in Courses]
    EnrollCourses --> GenTimetable[Generate Personal Timetable]
    GenTimetable --> ProvideResources[Provide Learning Resources]
    ProvideResources --> End([Onboarding Complete])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style HODReview fill:#FFE4B5
    style AttendOrientation fill:#FFE4B5
    style CheckPrereq fill:#FFE4B5
    style CheckCredits fill:#FFE4B5
    style AdvisorApproval fill:#FFE4B5
```

### Process Details

| Activity | Responsible | Duration | Notes |
|----------|-------------|----------|-------|
| Send Login Credentials | System | Automated | Email + SMS |
| Profile Completion | Student | 1-2 days | All fields mandatory |
| HOD Review | HOD | 1-2 days | Verify documents |
| ID Card Generation | Admin Office | 3-5 days | Physical card |
| Orientation | Student + Faculty | 1 day | Mandatory attendance |
| Course Selection | Student + Advisor | 3-5 days | During registration period |

---

## 2. Course Registration Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Registration Period Opens]) --> Announce[Announce Registration Dates]
    Announce --> StudentLogin[Student Logs In]
    StudentLogin --> ViewCourses[View Available Courses]

    ViewCourses --> FilterCourses{Filter by Program/Semester}
    FilterCourses --> ShowCourseList[Display Course List]

    ShowCourseList --> SelectCourse[Select Course]
    SelectCourse --> CheckEligibility{Check Eligibility}

    CheckEligibility -->|Not Eligible| ShowReason[Show Reason]
    ShowReason --> ShowCourseList

    CheckEligibility -->|Eligible| CheckSeats{Seats Available?}
    CheckSeats -->|No| AddWaitlist[Add to Waitlist]
    AddWaitlist --> ShowCourseList

    CheckSeats -->|Yes| AddCart[Add to Cart]
    AddCart --> MoreCourses{Add More Courses?}
    MoreCourses -->|Yes| ShowCourseList

    MoreCourses -->|No| ReviewCart[Review Cart]
    ReviewCart --> ValidateCredits{Validate Total Credits}

    ValidateCredits -->|Invalid| ShowError[Show Validation Error]
    ShowError --> ShowCourseList

    ValidateCredits -->|Valid| SubmitRequest[Submit Enrollment Request]
    SubmitRequest --> NotifyAdvisor[Notify Academic Advisor]

    NotifyAdvisor --> AdvisorReview[Advisor Reviews Request]
    AdvisorReview --> AdvisorDecision{Advisor Decision}

    AdvisorDecision -->|Rejected| NotifyStudent[Notify Student]
    NotifyStudent --> ViewCourses

    AdvisorDecision -->|Approved| ReservSeats[Reserve Seats]
    ReservSeats --> GenFeeInvoice[Generate Fee Invoice]
    GenFeeInvoice --> NotifyPayment[Notify to Pay Fee]

    NotifyPayment --> WaitPayment{Payment Within Deadline?}
    WaitPayment -->|No| CancelSeats[Cancel Seat Reservation]
    CancelSeats --> EndCancel([Registration Cancelled])

    WaitPayment -->|Yes| ProcessPayment[Process Payment]
    ProcessPayment --> ConfirmEnroll[Confirm Enrollment]
    ConfirmEnroll --> UpdateTimetable[Update Student Timetable]
    UpdateTimetable --> SendConfirm[Send Confirmation]
    SendConfirm --> ProvideAccess[Provide Course Materials Access]
    ProvideAccess --> End([Registration Complete])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndCancel fill:#FF6B6B
    style CheckEligibility fill:#FFE4B5
    style CheckSeats fill:#FFE4B5
    style ValidateCredits fill:#FFE4B5
    style AdvisorDecision fill:#FFE4B5
    style WaitPayment fill:#FFE4B5
```

---

## 3. Examination Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Examination Planning]) --> CreateSchedule[Create Exam Schedule]
    CreateSchedule --> SelectCourses[Select Courses]
    SelectCourses --> SetDates[Set Exam Dates]
    SetDates --> AllocHalls[Allocate Exam Halls]
    AllocHalls --> GenSeating[Generate Seating Arrangement]
    GenSeating --> AssignInvig[Assign Invigilators]

    AssignInvig --> PrepQuestions[Prepare Question Papers]
    PrepQuestions --> ExamType{Exam Type}

    ExamType -->|Online| CreateOnline[Create Online Exam]
    ExamType -->|Offline| PrintPapers[Print Question Papers]

    CreateOnline --> SelectQuestions[Select Questions from Bank]
    SelectQuestions --> ConfigExam[Configure Exam Settings]
    ConfigExam --> PublishOnline[Publish Online Exam]

    PrintPapers --> SealPapers[Seal in Envelopes]
    SealPapers --> StoreSecure[Store in Strong Room]

    PublishOnline --> PublishSchedule[Publish Exam Schedule]
    StoreSecure --> PublishSchedule

    PublishSchedule --> NotifyAll[Notify All Stakeholders]
    NotifyAll --> WaitExam[Wait for Exam Day]

    WaitExam --> ExamDay[Exam Day Arrives]
    ExamDay --> ModeCheck{Exam Mode}

    ModeCheck -->|Online| ActivateOnline[Activate Online Exam]
    ModeCheck -->|Offline| DistributePapers[Distribute Papers to Halls]

    ActivateOnline --> StudentLogin[Students Login]
    StudentLogin --> VerifyIdentity[Verify Student Identity]
    VerifyIdentity --> StartProctoring[Start Proctoring]
    StartProctoring --> StartTimer[Start Exam Timer]

    DistributePapers --> VerifySeal[Verify Seals]
    VerifySeal --> HandPapers[Hand Papers to Students]
    HandPapers --> StartTimer

    StartTimer --> ConductExam[Conduct Examination]
    ConductExam --> MonitorExam[Monitor for Malpractice]

    MonitorExam --> DetectIssue{Issue Detected?}
    DetectIssue -->|Yes| ReportIssue[Report Malpractice]
    ReportIssue --> TakeAction[Take Disciplinary Action]
    TakeAction --> ConductExam

    DetectIssue -->|No| CheckTime{Time Remaining?}
    CheckTime -->|Yes| ConductExam
    CheckTime -->|No| CollectAnswers[Collect Answer Sheets]

    CollectAnswers --> OnlineCheck{Online Exam?}
    OnlineCheck -->|Yes| AutoSave[Auto-Save Responses]
    OnlineCheck -->|No| BundleSheets[Bundle Answer Sheets]

    AutoSave --> StoreDB[Store in Database]
    BundleSheets --> HandEvaluators[Hand to Evaluators]

    StoreDB --> PrepEval[Prepare for Evaluation]
    HandEvaluators --> PrepEval

    PrepEval --> End([Examination Conducted])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style ExamType fill:#FFE4B5
    style ModeCheck fill:#FFE4B5
    style DetectIssue fill:#FFE4B5
    style CheckTime fill:#FFE4B5
    style OnlineCheck fill:#FFE4B5
```

---

## 4. Fee Collection Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Fee Structure Defined]) --> CreateFeeStruct[Create Fee Structure]
    CreateFeeStruct --> DefineComponents[Define Fee Components]
    DefineComponents --> SetAmounts[Set Amounts]
    SetAmounts --> ApplyDiscounts{Apply Discounts?}

    ApplyDiscounts -->|Yes| CalcDiscount[Calculate Discounts]
    ApplyDiscounts -->|No| GenInvoices[Generate Fee Invoices]
    CalcDiscount --> GenInvoices

    GenInvoices --> AssignStudents[Assign to Students]
    AssignStudents --> SetDueDate[Set Due Dates]
    SetDueDate --> PublishFee[Publish Fee Structure]

    PublishFee --> NotifyStudents[Notify Students]
    NotifyStudents --> StudentView[Student Views Invoice]

    StudentView --> SelectMode{Select Payment Mode}
    SelectMode -->|Online| InitiateOnline[Initiate Online Payment]
    SelectMode -->|Offline| GenChallan[Generate Bank Challan]

    InitiateOnline --> SelectMethod[Select Payment Method]
    SelectMethod --> Gateway[Redirect to Gateway]
    Gateway --> EnterDetails[Enter Payment Details]
    EnterDetails --> ProcessTxn[Process Transaction]

    ProcessTxn --> TxnStatus{Transaction Status}
    TxnStatus -->|Failed| ShowError[Show Error]
    ShowError --> Retry{Retry Payment?}
    Retry -->|Yes| Gateway
    Retry -->|No| EndFail([Payment Failed])

    TxnStatus -->|Success| Callback[Gateway Callback]

    GenChallan --> PrintChallan[Print Challan]
    PrintChallan --> VisitBank[Visit Bank]
    VisitBank --> MakePayment[Make Payment]
    MakePayment --> BankReceipt[Get Bank Receipt]
    BankReceipt --> SubmitAccounts[Submit to Accounts]

    SubmitAccounts --> VerifyBank{Verify with Bank}
    VerifyBank -->|Invalid| RejectPayment[Reject Payment]
    RejectPayment --> NotifyInvalid[Notify Student]
    NotifyInvalid --> EndFail

    VerifyBank -->|Valid| UpdateInvoice[Update Invoice]

    Callback --> VerifySign{Verify Signature}
    VerifySign -->|Invalid| LogFraud[Log Fraud Attempt]
    LogFraud --> EndFail

    VerifySign -->|Valid| UpdateInvoice
    UpdateInvoice --> CreatePayEntry[Create Payment Entry]
    CreatePayEntry --> CreateJE[Create Journal Entry]
    CreateJE --> GenReceipt[Generate Receipt]
    GenReceipt --> EmailReceipt[Email Receipt]

    EmailReceipt --> CheckFull{Full Amount Paid?}
    CheckFull -->|No| MarkPartial[Mark as Partial Payment]
    MarkPartial --> EndPartial([Partial Payment])

    CheckFull -->|Yes| MarkPaid[Mark as Fully Paid]
    MarkPaid --> UnlockServices[Unlock Services]
    UnlockServices --> UpdateLedger[Update Accounting Ledger]
    UpdateLedger --> End([Payment Complete])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndFail fill:#FF6B6B
    style EndPartial fill:#FFA07A
    style ApplyDiscounts fill:#FFE4B5
    style SelectMode fill:#FFE4B5
    style TxnStatus fill:#FFE4B5
    style Retry fill:#FFE4B5
    style VerifyBank fill:#FFE4B5
    style VerifySign fill:#FFE4B5
    style CheckFull fill:#FFE4B5
```

---

## 5. Library Management Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Student Needs Book]) --> SearchBook[Search Book Catalog]
    SearchBook --> BookFound{Book Found?}

    BookFound -->|No| SuggestBooks[Show Similar Books]
    SuggestBooks --> RequestPurchase{Request Purchase?}
    RequestPurchase -->|Yes| SubmitRequest[Submit Purchase Request]
    SubmitRequest --> EndRequest([Request Submitted])
    RequestPurchase -->|No| EndSearch([End Search])

    BookFound -->|Yes| CheckAvail{Check Availability}
    CheckAvail -->|Not Available| ReserveBook[Reserve Book]
    ReserveBook --> AddQueue[Add to Queue]
    AddQueue --> NotifyWait[Will Notify When Available]
    NotifyWait --> EndReserved([Book Reserved])

    CheckAvail -->|Available| CheckQuota{Check Issue Quota}
    CheckQuota -->|Exceeded| ShowQuotaMsg[Show Quota Exceeded]
    ShowQuotaMsg --> EndQuota([Cannot Issue])

    CheckQuota -->|Available| RequestIssue[Request Book Issue]
    RequestIssue --> VisitLibrary[Visit Library]
    VisitLibrary --> ShowID[Show ID Card to Librarian]

    ShowID --> VerifyID{Verify ID}
    VerifyID -->|Invalid| RejectIssue[Reject Issue Request]
    RejectIssue --> EndReject([Issue Rejected])

    VerifyID -->|Valid| CheckDues{Check Pending Dues}
    CheckDues -->|Has Dues| PayDues[Pay Pending Dues]
    PayDues --> ClearDues[Clear Dues]
    ClearDues --> ProceedIssue[Proceed to Issue]

    CheckDues -->|No Dues| ProceedIssue
    ProceedIssue --> FetchBook[Librarian Fetches Book]
    FetchBook --> ScanBarcode[Scan Book Barcode]
    ScanBarcode --> CreateTxn[Create Library Transaction]
    CreateTxn --> CalcDue[Calculate Due Date]
    CalcDue --> UpdateStatus[Update Book Status to Issued]
    UpdateStatus --> PrintSlip[Print Issue Slip]
    PrintSlip --> HandBook[Hand Book to Student]

    HandBook --> SendConfirm[Send Confirmation Email/SMS]
    SendConfirm --> SetReminder[Set Return Reminder]
    SetReminder --> WaitReturn[Wait for Return]

    WaitReturn --> DueNear{Due Date Near?}
    DueNear -->|Yes| SendReminder[Send Return Reminder]
    SendReminder --> CheckReturn{Book Returned?}

    DueNear -->|No| CheckReturn
    CheckReturn -->|No| DuePassed{Due Date Passed?}
    DuePassed -->|No| WaitReturn

    DuePassed -->|Yes| CalcFine[Calculate Late Fine]
    CalcFine --> BlockIssue[Block Further Issues]
    BlockIssue --> SendNotice[Send Overdue Notice]
    SendNotice --> WaitReturn

    CheckReturn -->|Yes| ReturnBook[Student Returns Book]
    ReturnBook --> InspectBook{Inspect Book Condition}

    InspectBook -->|Damaged| AssessDamage[Assess Damage]
    AssessDamage --> CalcDamageFine[Calculate Damage Fine]
    CalcDamageFine --> TotalFine[Add to Late Fine]
    TotalFine --> CollectFine[Collect Fine]

    InspectBook -->|Good Condition| CheckLate{Returned Late?}
    CheckLate -->|Yes| CollectFine
    CheckLate -->|No| CompleteReturn[Complete Return]

    CollectFine --> PayFine[Student Pays Fine]
    PayFine --> RecordPayment[Record Fine Payment]
    RecordPayment --> CompleteReturn

    CompleteReturn --> UpdateReturn[Update Transaction]
    UpdateReturn --> MarkAvailable[Mark Book as Available]
    MarkAvailable --> UnblockStudent[Unblock Student]
    UnblockStudent --> NotifyQueued[Notify Next in Queue]
    NotifyQueued --> End([Book Returned])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndRequest fill:#E6F3FF
    style EndSearch fill:#E6F3FF
    style EndReserved fill:#FFA07A
    style EndQuota fill:#FF6B6B
    style EndReject fill:#FF6B6B
    style BookFound fill:#FFE4B5
    style CheckAvail fill:#FFE4B5
    style CheckQuota fill:#FFE4B5
    style VerifyID fill:#FFE4B5
    style CheckDues fill:#FFE4B5
    style DueNear fill:#FFE4B5
    style CheckReturn fill:#FFE4B5
    style DuePassed fill:#FFE4B5
    style InspectBook fill:#FFE4B5
    style CheckLate fill:#FFE4B5
```

---

## 6. Hostel Management Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Hostel Application Opens]) --> OpenReg[Open Registration]
    OpenReg --> StudentLogin[Student Logs In]
    StudentLogin --> CheckElig{Check Eligibility}

    CheckElig -->|Not Eligible| ShowReason[Show Ineligibility Reason]
    ShowReason --> EndInelig([Not Eligible])

    CheckElig -->|Eligible| FillApp[Fill Application Form]
    FillApp --> SelectPref[Select Room Preferences]
    SelectPref --> UploadDocs[Upload Required Documents]
    UploadDocs --> PayAppFee[Pay Application Fee]
    PayAppFee --> SubmitApp[Submit Application]

    SubmitApp --> WardenReview[Warden Reviews Application]
    WardenReview --> WardenDecision{Warden Decision}

    WardenDecision -->|Rejected| NotifyRej[Notify Student]
    NotifyRej --> EndRej([Application Rejected])

    WardenDecision -->|Approved| CalcPriority[Calculate Priority Score]
    CalcPriority --> AddList[Add to Priority List]
    AddList --> WaitAlloc[Wait for Allocation Round]

    WaitAlloc --> AllocRound[Allocation Round Begins]
    AllocRound --> SortList[Sort by Priority Score]
    SortList --> GetAvailRooms[Get Available Rooms]
    GetAvailRooms --> ProcessList[Process Applicants in Order]

    ProcessList --> NextApplicant{Next Applicant}
    NextApplicant -->|No More| EndAlloc([Allocation Complete])

    NextApplicant -->|Yes| MatchPref[Match Preferences]
    MatchPref --> RoomAvail{Room Available?}

    RoomAvail -->|No| AddWaitlist[Add to Waitlist]
    AddWaitlist --> NotifyWait[Notify Waitlist Status]
    NotifyWait --> ProcessList

    RoomAvail -->|Yes| AllocRoom[Allocate Room]
    AllocRoom --> MarkOccupied[Mark Room as Occupied]
    MarkOccupied --> NotifyAlloc[Notify Student]

    NotifyAlloc --> StudentAccept{Student Accepts?}
    StudentAccept -->|No| ReleaseRoom[Release Room]
    ReleaseRoom --> ProcessList

    StudentAccept -->|Yes| GenHostelFee[Generate Hostel Fee Invoice]
    GenHostelFee --> NotifyPay[Notify to Pay]

    NotifyPay --> WaitPay{Payment Within Deadline?}
    WaitPay -->|No| CancelAlloc[Cancel Allocation]
    CancelAlloc --> ReleaseRoom

    WaitPay -->|Yes| PayFee[Pay Hostel Fee]
    PayFee --> VerifyPay[Verify Payment]
    VerifyPay --> ConfirmAlloc[Confirm Allocation]
    ConfirmAlloc --> GenLetter[Generate Allotment Letter]
    GenLetter --> SetCheckin[Set Check-in Date]
    SetCheckin --> EmailLetter[Email Allotment Letter]

    EmailLetter --> CheckinDay[Check-in Day Arrives]
    CheckinDay --> VisitHostel[Student Visits Hostel]
    VisitHostel --> VerifyDocs[Verify Documents]
    VerifyDocs --> InspectRoom[Inspect Room]
    InspectRoom --> SignInventory[Sign Inventory Checklist]
    SignInventory --> CreateOccupancy[Create Occupancy Record]
    CreateOccupancy --> ActivateServices[Activate Hostel Services]
    ActivateServices --> HandoverKeys[Handover Room Keys]
    HandoverKeys --> SendWelcome[Send Welcome Message]
    SendWelcome --> End([Allocation Complete])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndAlloc fill:#E6F3FF
    style EndInelig fill:#FF6B6B
    style EndRej fill:#FF6B6B
    style CheckElig fill:#FFE4B5
    style WardenDecision fill:#FFE4B5
    style NextApplicant fill:#FFE4B5
    style RoomAvail fill:#FFE4B5
    style StudentAccept fill:#FFE4B5
    style WaitPay fill:#FFE4B5
```

---

## 7. Attendance Management Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Class Begins]) --> CheckMethod{Attendance Method}

    CheckMethod -->|Manual| FacultyLogin[Faculty Logs In]
    CheckMethod -->|Biometric| BiometricScan[Student Scans Fingerprint]
    CheckMethod -->|Mobile App| AppOpen[Student Opens App]
    CheckMethod -->|QR Code| GenQR[Faculty Generates QR]

    FacultyLogin --> SelectSchedule[Select Course Schedule]
    SelectSchedule --> LoadStudents[Load Student List]
    LoadStudents --> MarkAttendance[Mark Attendance]

    BiometricScan --> VerifyBio{Verify Biometric}
    VerifyBio -->|Failed| ShowError[Show Error Message]
    ShowError --> RetryBio{Retry?}
    RetryBio -->|Yes| BiometricScan
    RetryBio -->|No| ManualMark[Mark Manually]
    ManualMark --> MarkAttendance

    VerifyBio -->|Success| CheckLocation{Location Valid?}
    CheckLocation -->|No| DenyAtt[Deny Attendance]
    DenyAtt --> AlertAdmin[Alert Administrator]
    AlertAdmin --> EndDeny([Attendance Denied])

    CheckLocation -->|Yes| AutoMark[Auto Mark Present]
    AutoMark --> RecordAtt[Record Attendance]

    AppOpen --> VerifyLoc{Verify Location}
    VerifyLoc -->|Invalid| DenyAtt
    VerifyLoc -->|Valid| CheckTime{Within Time Window?}
    CheckTime -->|No| MarkLate[Mark as Late]
    CheckTime -->|Yes| SelfMark[Self Mark Present]

    GenQR --> DisplayQR[Display QR Code]
    DisplayQR --> StudentScan[Students Scan QR]
    StudentScan --> ValidateQR{QR Valid?}
    ValidateQR -->|No| DenyAtt
    ValidateQR -->|Yes| SelfMark

    MarkAttendance --> SelectStatus{Attendance Status}
    SelectStatus -->|Present| MarkPresent[Mark Present]
    SelectStatus -->|Absent| MarkAbsent[Mark Absent]
    SelectStatus -->|Late| MarkLate
    SelectStatus -->|Leave| MarkLeave[Mark on Leave]

    MarkPresent --> RecordAtt
    MarkAbsent --> RecordAtt
    MarkLate --> RecordAtt
    MarkLeave --> RecordAtt
    SelfMark --> RecordAtt

    RecordAtt --> SyncDB[Sync to Database]
    SyncDB --> CalcPercent[Calculate Attendance %]
    CalcPercent --> CheckLow{Attendance < 75%?}

    CheckLow -->|Yes| SendAlert[Alert Student & Parent]
    SendAlert --> UpdateDash[Update Dashboard]

    CheckLow -->|No| UpdateDash
    UpdateDash --> NotifyStudent[Notify Student]
    NotifyStudent --> End([Attendance Recorded])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndDeny fill:#FF6B6B
    style CheckMethod fill:#FFE4B5
    style VerifyBio fill:#FFE4B5
    style CheckLocation fill:#FFE4B5
    style VerifyLoc fill:#FFE4B5
    style CheckTime fill:#FFE4B5
    style ValidateQR fill:#FFE4B5
    style SelectStatus fill:#FFE4B5
    style CheckLow fill:#FFE4B5
```

---

## 8. Result Declaration Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Exams Completed]) --> CollectSheets[Collect Answer Sheets]
    CollectSheets --> ExamMode{Exam Mode}

    ExamMode -->|Online| AutoEval[Automatic Evaluation]
    ExamMode -->|Offline| Distribute[Distribute to Evaluators]

    AutoEval --> EvalObjective[Evaluate Objective Questions]
    EvalObjective --> CalcMarks[Calculate Marks]

    Distribute --> BlindEval[Implement Blind Evaluation]
    BlindEval --> EvaluatorReview[Evaluator Reviews Answers]
    EvaluatorReview --> AwardMarks[Award Marks]
    AwardMarks --> SubmitEval[Submit Evaluation]

    SubmitEval --> CheckDiff{Marks Difference > 10%?}
    CheckDiff -->|Yes| ThirdEval[Send to Third Evaluator]
    ThirdEval --> FinalMarks[Take Final Decision]
    CheckDiff -->|No| FinalMarks

    FinalMarks --> CalcMarks
    CalcMarks --> EnterMarks[Enter Marks in System]
    EnterMarks --> HODVerify{HOD Verification}

    HODVerify -->|Corrections| NotifyError[Notify Evaluator]
    NotifyError --> EvaluatorReview

    HODVerify -->|Approved| InternalDone[Internal Marks Approved]
    InternalDone --> ExternalExam{External Exam?}

    ExternalExam -->|Yes| ExternalEval[External Evaluation]
    ExternalEval --> CombineMarks[Combine Internal + External]
    ExternalExam -->|No| CombineMarks

    CombineMarks --> TotalCalc[Calculate Total Marks]
    TotalCalc --> GradeCalc[Calculate Grade]
    GradeCalc --> ApplyRules[Apply Grace Marks Rules]
    ApplyRules --> ResultStatus{Determine Pass/Fail}

    ResultStatus --> GenResults[Generate Individual Results]
    GenResults --> ControllerReview{Controller Review}

    ControllerReview -->|Corrections| BackReview[Send for Re-review]
    BackReview --> HODVerify

    ControllerReview -->|Approved| PublishResults[Publish Results]
    PublishResults --> NotifyAll[Notify All Students]
    NotifyAll --> GenGradeCards[Generate Grade Cards]
    GenGradeCards --> RevalReq{Revaluation Requests?}

    RevalReq -->|Yes| ProcessReval[Process Revaluation]
    ProcessReval --> UpdateResults[Update Results if Changed]
    UpdateResults --> FinalPub[Final Publication]

    RevalReq -->|No| FinalPub
    FinalPub --> GenTranscript[Generate Transcripts]
    GenTranscript --> ArchiveResults[Archive Results]
    ArchiveResults --> End([Result Declared])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style ExamMode fill:#FFE4B5
    style CheckDiff fill:#FFE4B5
    style HODVerify fill:#FFE4B5
    style ExternalExam fill:#FFE4B5
    style ResultStatus fill:#FFE4B5
    style ControllerReview fill:#FFE4B5
    style RevalReq fill:#FFE4B5
```

---

## 9. Grievance Resolution Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Student Has Grievance]) --> Login[Student Logs In]
    Login --> SelectCategory[Select Category]
    SelectCategory --> DescribeIssue[Describe Issue]
    DescribeIssue --> AttachDocs[Attach Supporting Documents]
    AttachDocs --> Anonymous{Submit Anonymously?}

    Anonymous -->|Yes| SubmitAnon[Submit Anonymous]
    Anonymous -->|No| SubmitID[Submit with Identity]

    SubmitAnon --> AutoAssign[Auto-Assign to Officer]
    SubmitID --> AutoAssign

    AutoAssign --> DeterminePriority{Determine Priority}
    DeterminePriority -->|Critical| SLA2[SLA: 2 Days]
    DeterminePriority -->|High| SLA5[SLA: 5 Days]
    DeterminePriority -->|Medium| SLA10[SLA: 10 Days]
    DeterminePriority -->|Low| SLA15[SLA: 15 Days]

    SLA2 --> NotifyOfficer[Notify Assigned Officer]
    SLA5 --> NotifyOfficer
    SLA10 --> NotifyOfficer
    SLA15 --> NotifyOfficer

    NotifyOfficer --> OfficerReview[Officer Reviews Grievance]
    OfficerReview --> NeedInfo{Need More Info?}

    NeedInfo -->|Yes| RequestInfo[Request Additional Info]
    RequestInfo --> AnonymousCheck{Anonymous Submission?}
    AnonymousCheck -->|Yes| CannotRequest[Cannot Request Info]
    CannotRequest --> OfficerDecide[Officer Decides]

    AnonymousCheck -->|No| NotifyStudent[Notify Student]
    NotifyStudent --> StudentResponds[Student Provides Info]
    StudentResponds --> OfficerReview

    NeedInfo -->|No| CanResolve{Can Resolve?}

    CanResolve -->|No| EscalateCommittee[Escalate to Committee]
    EscalateCommittee --> NotifyCommittee[Notify Committee Members]
    NotifyCommittee --> ScheduleHearing[Schedule Hearing]
    ScheduleHearing --> ConductHearing[Conduct Hearing]
    ConductHearing --> CommitteeDecision[Committee Decision]
    CommitteeDecision --> DocumentResolution[Document Resolution]

    CanResolve -->|Yes| OfficerDecide
    OfficerDecide --> TakeAction[Take Corrective Action]
    TakeAction --> DocumentResolution

    DocumentResolution --> CloseGrievance[Close Grievance]
    CloseGrievance --> NotifyResolution[Notify Resolution]
    NotifyResolution --> AnonymousFeedback{Anonymous?}

    AnonymousFeedback -->|Yes| EndAnon([Grievance Resolved])
    AnonymousFeedback -->|No| RequestFeedback[Request Feedback]

    RequestFeedback --> StudentFeedback[Student Provides Feedback]
    StudentFeedback --> CheckSat{Satisfied?}

    CheckSat -->|No| ReopenGrievance[Reopen Grievance]
    ReopenGrievance --> EscalateCommittee

    CheckSat -->|Yes| ThankStudent[Send Thank You]
    ThankStudent --> UpdateAnalytics[Update Analytics]
    UpdateAnalytics --> End([Grievance Closed])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndAnon fill:#E6F3FF
    style Anonymous fill:#FFE4B5
    style DeterminePriority fill:#FFE4B5
    style NeedInfo fill:#FFE4B5
    style AnonymousCheck fill:#FFE4B5
    style CanResolve fill:#FFE4B5
    style AnonymousFeedback fill:#FFE4B5
    style CheckSat fill:#FFE4B5
```

---

## 10. Document Issuance Process

### Activity Diagram

```mermaid
flowchart TD
    Start([Student Needs Document]) --> Login[Student Logs In]
    Login --> SelectType[Select Document Type]
    SelectType --> FillForm[Fill Request Form]
    FillForm --> FeeRequired{Fee Required?}

    FeeRequired -->|Yes| PayFee[Pay Processing Fee]
    FeeRequired -->|No| SubmitReq[Submit Request]
    PayFee --> SubmitReq

    SubmitReq --> RegistrarReview[Registrar Reviews Request]
    RegistrarReview --> RegistrarDecision{Registrar Decision}

    RegistrarDecision -->|Rejected| NotifyRej[Notify Student]
    NotifyRej --> EndRej([Request Rejected])

    RegistrarDecision -->|Approved| DocType{Document Type}

    DocType -->|Auto-Generate| GetData[Get Student Data]
    DocType -->|Manual Prepare| NotifyCell[Notify Document Cell]

    GetData --> LoadTemplate[Load Template]
    LoadTemplate --> PopulateData[Populate Data]
    PopulateData --> GenPDF[Generate PDF]
    GenPDF --> DigitalSign[Apply Digital Signature]
    DigitalSign --> AddQR[Add Verification QR]
    AddQR --> StoreDoc[Store Document]
    StoreDoc --> MarkReady[Mark as Ready]

    NotifyCell --> PrepareDoc[Prepare Document]
    PrepareDoc --> PrintDoc[Print Document]
    PrintDoc --> PhysicalSign[Physical Signature & Seal]
    PhysicalSign --> MarkReady

    MarkReady --> NotifyReady[Notify Student]
    NotifyReady --> SelectDelivery{Select Delivery Mode}

    SelectDelivery -->|Collect| NotifyCollect[Notify to Collect]
    SelectDelivery -->|Post| CreateShipment[Create Courier Shipment]
    SelectDelivery -->|Email| PrepareEmail[Prepare Email]

    NotifyCollect --> StudentVisit[Student Visits Office]
    StudentVisit --> VerifyID[Verify Identity]
    VerifyID --> HandoverDoc[Handover Document]
    HandoverDoc --> SignReceipt[Sign Receipt]
    SignReceipt --> MarkDelivered[Mark as Delivered]

    CreateShipment --> GenAWB[Generate AWB Number]
    GenAWB --> SchedulePickup[Schedule Pickup]
    SchedulePickup --> TrackShipment[Track Shipment]
    TrackShipment --> DeliverCourier[Courier Delivers]
    DeliverCourier --> POD[Proof of Delivery]
    POD --> MarkDelivered

    PrepareEmail --> AttachPDF[Attach PDF]
    AttachPDF --> AddVerifyLink[Add Verification Link]
    AddVerifyLink --> SendEmail[Send Email]
    SendEmail --> MarkDelivered

    MarkDelivered --> CloseRequest[Close Request]
    CloseRequest --> ConfirmDelivery[Confirm Delivery]
    ConfirmDelivery --> UpdateRecords[Update Records]
    UpdateRecords --> End([Document Issued])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style EndRej fill:#FF6B6B
    style FeeRequired fill:#FFE4B5
    style RegistrarDecision fill:#FFE4B5
    style DocType fill:#FFE4B5
    style SelectDelivery fill:#FFE4B5
```

---

## Summary

This document provides comprehensive activity diagrams for:

1. **Student Onboarding** - From admission to course enrollment
2. **Course Registration** - Course selection and enrollment confirmation
3. **Examination** - Planning, conduct, and monitoring
4. **Fee Collection** - Online and offline payment processing
5. **Library Management** - Book issue, return, and fine collection
6. **Hostel Management** - Application, allocation, and check-in
7. **Attendance Management** - Multiple marking methods
8. **Result Declaration** - Evaluation to publication
9. **Grievance Resolution** - Filing, escalation, and closure
10. **Document Issuance** - Request to delivery

All diagrams show:
- Complete process flows with decision points
- Parallel and sequential activities
- Error handling and exception paths
- Multiple actors and their interactions
- Alternative paths based on conditions

The diagrams use Mermaid syntax and can be rendered in Mermaid-compatible viewers or documentation platforms.
