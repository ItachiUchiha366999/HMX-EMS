# University Research Module

## Overview

The University Research module manages faculty research activities including publications, research projects, grants, and collaborations. It tracks research output for performance evaluation and accreditation purposes.

## Module Location
```
university_erp/university_research/
```

## DocTypes (7 Total)

| DocType | Type | Purpose |
|---------|------|---------|
| Research Publication | Main | Published research papers |
| Publication Author | Child | Paper authors |
| Research Project | Main | Research project records |
| Research Team Member | Child | Project team |
| Project Publication Link | Child | Project-publication mapping |
| Research Grant | Main | Grant/funding records |
| Grant Utilization | Child | Fund usage tracking |

## Architecture Diagram

```
+------------------------------------------------------------------+
|                   UNIVERSITY RESEARCH MODULE                      |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+       +-------------------+                |
|  |RESEARCH PUBLICATION|     |  RESEARCH PROJECT  |                |
|  +-------------------+       +-------------------+                |
|  | - Title           |       | - Title           |                |
|  | - Journal         |       | - Objectives      |                |
|  | - DOI             |       | - Team            |                |
|  | - Authors         |       | - Publications    |                |
|  +-------------------+       +-------------------+                |
|           |                           |                           |
|           v                           v                           |
|  +-------------------+       +-------------------+                |
|  |Publication Author |       |Research Team Member|               |
|  | (Child Table)     |       | (Child Table)     |                |
|  +-------------------+       +-------------------+                |
|                                       |                           |
|                                       v                           |
|                              +-------------------+                |
|                              |  RESEARCH GRANT   |                |
|                              +-------------------+                |
|                              | - Funding Agency  |                |
|                              | - Amount          |                |
|                              | - Utilization     |                |
|                              +-------------------+                |
|                                       |                           |
|                                       v                           |
|                              +-------------------+                |
|                              | Grant Utilization |                |
|                              | (Child Table)     |                |
|                              +-------------------+                |
|                                                                   |
+------------------------------------------------------------------+
```

## Connections to Other Modules/Apps

### HR Module Integration
```
+--------------------+       +--------------------+
|     RESEARCH       |       |   UNIVERSITY HR    |
|     (Custom)       |------>|                    |
+--------------------+       +--------------------+
|                    |       |                    |
| Publication -------|------>| Faculty Profile    |
| Project ----------|------>| (Publications table)|
|                    |       |                    |
| Performance -------|------>| Faculty Evaluation |
|   metrics          |       | (research score)   |
+--------------------+       +--------------------+
```

### Cross-Module Relationships
```
                    +--------------------+
                    |     RESEARCH       |
                    +--------------------+
                            /|\
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
+----------------+  +----------------+  +----------------+
| UNIVERSITY HR  |  |     OBE        |  |   FINANCE      |
+----------------+  +----------------+  +----------------+
| Faculty ->     |  | Research ->    |  | Grant ->       |
| Publications   |  | PO Attainment  |  | Fund tracking  |
| Projects       |  | (research PO)  |  |                |
+----------------+  +----------------+  +----------------+
```

## DocType Details

### 1. Research Publication
**Purpose**: Track published research papers

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| title | Data | Paper title |
| publication_type | Select | Journal/Conference/Book Chapter |
| authors | Table | Author list |
| primary_author | Link (Faculty Profile) | Lead author |
| journal_name | Data | Journal/Conference name |
| publisher | Data | Publisher name |
| publication_date | Date | Published date |
| volume | Data | Volume number |
| issue | Data | Issue number |
| pages | Data | Page range |
| doi | Data | Digital Object Identifier |
| isbn_issn | Data | ISBN/ISSN |
| abstract | Text | Paper abstract |
| keywords | Small Text | Keywords |
| impact_factor | Float | Journal impact factor |
| citation_count | Int | Citations received |
| indexing | Multi Select | SCI/Scopus/Web of Science |
| research_project | Link (Research Project) | Related project |
| file_attachment | Attach | Paper PDF |
| status | Select | Published/Accepted/Under Review |

**Publication Types**:
- Journal Article (Peer-reviewed)
- Conference Paper
- Book Chapter
- Book
- Patent
- Technical Report

### 2. Publication Author (Child Table)
**Purpose**: Author details and order

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| author_name | Data | Full name |
| author_type | Select | Internal/External |
| faculty | Link (Faculty Profile) | If internal |
| affiliation | Data | Institution |
| author_order | Int | Authorship position |
| is_corresponding | Check | Corresponding author |
| email | Data | Author email |

### 3. Research Project
**Purpose**: Research project records

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| project_title | Data | Project title |
| principal_investigator | Link (Faculty Profile) | PI |
| department | Link (Department) | Lead department |
| project_type | Select | Sponsored/Consultancy/Internal |
| start_date | Date | Project start |
| end_date | Date | Expected completion |
| actual_end_date | Date | Actual completion |
| objectives | Text Editor | Project objectives |
| methodology | Text Editor | Research methodology |
| team_members | Table | Project team |
| publications | Table | Related publications |
| deliverables | Text | Expected outcomes |
| funding_source | Data | Funding agency |
| sanctioned_amount | Currency | Total funding |
| utilized_amount | Currency | Amount spent |
| status | Select | Proposed/Ongoing/Completed/Terminated |

**Project Types**:
- Sponsored Research (Government/Industry funded)
- Consultancy Project
- Internal Research
- Collaborative Research
- PhD Thesis Research

### 4. Research Team Member (Child Table)
**Purpose**: Project team composition

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| member | Link (Faculty Profile) | Team member |
| member_name | Data | Name |
| role | Select | PI/Co-PI/Researcher/PhD Scholar |
| department | Link (Department) | Department |
| from_date | Date | Joined project |
| to_date | Date | Left project |
| time_commitment | Percent | % time on project |

### 5. Project Publication Link (Child Table)
**Purpose**: Link projects to publications

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| publication | Link (Research Publication) | Publication |
| publication_title | Data | Title |
| publication_type | Data | Type |
| publication_date | Date | Date |

### 6. Research Grant
**Purpose**: Track research funding

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| grant_title | Data | Grant title |
| research_project | Link (Research Project) | Related project |
| principal_investigator | Link (Faculty Profile) | PI |
| funding_agency | Data | Funder name |
| agency_type | Select | Government/Industry/International |
| scheme_name | Data | Funding scheme |
| grant_number | Data | Grant reference |
| sanctioned_date | Date | Approval date |
| start_date | Date | Grant period start |
| end_date | Date | Grant period end |
| sanctioned_amount | Currency | Total amount |
| released_amount | Currency | Amount received |
| utilized_amount | Currency | Amount spent |
| balance_amount | Currency | Remaining |
| utilization | Table | Expense breakdown |
| status | Select | Applied/Sanctioned/Active/Closed |

**Major Funding Agencies**:
- SERB (Science & Engineering Research Board)
- DST (Department of Science & Technology)
- DBT (Department of Biotechnology)
- UGC (University Grants Commission)
- CSIR (Council of Scientific & Industrial Research)
- AICTE
- Industry Partners

### 7. Grant Utilization (Child Table)
**Purpose**: Track fund usage

**Key Fields**:
| Field | Type | Description |
|-------|------|-------------|
| expense_head | Select | Equipment/Travel/Consumables/Manpower |
| sanctioned_amount | Currency | Allocated |
| spent_amount | Currency | Utilized |
| balance | Currency | Remaining |
| remarks | Data | Notes |

**Expense Heads**:
- Equipment
- Consumables
- Travel & Contingency
- Manpower (JRF/SRF/RA)
- Overhead
- Miscellaneous

## Data Flow Diagrams

### Research Publication Flow
```
+----------------+     +------------------+     +------------------+
| Faculty        |---->| Draft            |---->| Submit to        |
| Conducts       |     | Paper            |     | Journal          |
| Research       |     |                  |     |                  |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+            |
| Record in      |<----|   Published      |<-----------+
| System         |     |   (Accepted)     |
+----------------+     +------------------+
        |
        v
+----------------+
| Update Faculty |
| Profile        |
+----------------+
```

### Grant Lifecycle Flow
```
+----------------+     +------------------+     +------------------+
| Identify       |---->| Submit           |---->| Agency           |
| Funding        |     | Proposal         |     | Review           |
| Opportunity    |     |                  |     |                  |
+----------------+     +------------------+     +------------------+
                                                        |
+----------------+     +------------------+            |
| Project        |<----|   Grant          |<-----------+
| Execution      |     |   Sanctioned     |
+----------------+     +------------------+
        |
        v
+----------------+     +------------------+
| Utilization    |---->|   Project        |
| Reporting      |     |   Closure        |
+----------------+     +------------------+
```

### Research Metrics
```
+------------------------------------------------------------------+
|                    FACULTY RESEARCH METRICS                       |
+------------------------------------------------------------------+
|                                                                   |
|  Faculty: Dr. John Smith                                          |
|  Department: Computer Science                                     |
|                                                                   |
|  +------------------+  +------------------+  +------------------+ |
|  |  PUBLICATIONS    |  |     PROJECTS     |  |     GRANTS       | |
|  +------------------+  +------------------+  +------------------+ |
|  | Total: 25        |  | Completed: 5     |  | Active: 2        | |
|  | SCI: 15          |  | Ongoing: 2       |  | Total: Rs. 50L   | |
|  | Scopus: 20       |  | PhD Guided: 8    |  | Utilized: Rs. 30L| |
|  | h-index: 12      |  |                  |  |                  | |
|  +------------------+  +------------------+  +------------------+ |
|                                                                   |
+------------------------------------------------------------------+
```

## Integration Points

### With Faculty Profile
```python
# Sync publications to faculty profile
def sync_publications_to_faculty(faculty):
    """Update faculty profile with publication stats"""
    publications = frappe.get_all("Research Publication", {
        "primary_author": faculty
    })

    faculty_doc = frappe.get_doc("Faculty Profile", faculty)
    faculty_doc.total_publications = len(publications)
    faculty_doc.sci_publications = count_indexed(publications, "SCI")
    faculty_doc.scopus_publications = count_indexed(publications, "Scopus")
    faculty_doc.save()

# Publications also stored in faculty profile child table
def add_publication_to_faculty(publication):
    """Add publication to faculty profile"""
    pub = frappe.get_doc("Research Publication", publication)

    for author in pub.authors:
        if author.faculty:
            faculty = frappe.get_doc("Faculty Profile", author.faculty)
            faculty.append("publications", {
                "title": pub.title,
                "publication_type": pub.publication_type,
                "journal_name": pub.journal_name,
                "year": pub.publication_date.year,
                "doi": pub.doi
            })
            faculty.save()
```

### With Performance Evaluation
```python
# Research metrics for faculty appraisal
def get_research_score(faculty, academic_year):
    """Calculate research score for evaluation"""
    start_date, end_date = get_year_dates(academic_year)

    # Publications
    publications = frappe.get_all("Research Publication", {
        "primary_author": faculty,
        "publication_date": ["between", [start_date, end_date]]
    })

    publication_score = 0
    for pub in publications:
        if "SCI" in pub.indexing:
            publication_score += 10
        elif "Scopus" in pub.indexing:
            publication_score += 7
        else:
            publication_score += 3

    # Projects
    projects = frappe.get_all("Research Project", {
        "principal_investigator": faculty,
        "status": "Ongoing"
    })
    project_score = len(projects) * 5

    # Grants
    grants = frappe.get_all("Research Grant", {
        "principal_investigator": faculty,
        "status": "Active"
    })
    grant_score = sum(g.sanctioned_amount for g in grants) / 100000  # Per lakh

    return {
        "publication_score": publication_score,
        "project_score": project_score,
        "grant_score": grant_score,
        "total": publication_score + project_score + grant_score
    }
```

### With Finance Module
```python
# Grant fund tracking integration
def track_grant_expenditure(grant, expense_type, amount, description):
    """Record grant expenditure"""
    grant_doc = frappe.get_doc("Research Grant", grant)

    # Update utilization
    for item in grant_doc.utilization:
        if item.expense_head == expense_type:
            item.spent_amount += amount
            item.balance = item.sanctioned_amount - item.spent_amount
            break

    grant_doc.utilized_amount = sum(u.spent_amount for u in grant_doc.utilization)
    grant_doc.balance_amount = grant_doc.released_amount - grant_doc.utilized_amount
    grant_doc.save()

    # Create expense record (can integrate with ERPNext)
    create_expense_record(grant, expense_type, amount, description)
```

## API Endpoints

### Publications
```python
@frappe.whitelist()
def get_faculty_publications(faculty, year=None, indexing=None):
    """Get publications for faculty"""
    filters = {"primary_author": faculty}
    if year:
        filters["publication_date"] = ["like", f"{year}%"]

    publications = frappe.get_all("Research Publication",
        filters=filters,
        fields=["*"]
    )

    if indexing:
        publications = [p for p in publications if indexing in p.indexing]

    return publications

@frappe.whitelist()
def add_publication(data):
    """Add new publication record"""
    pub = frappe.new_doc("Research Publication")
    pub.update(data)
    pub.insert()

    # Sync to faculty profile
    add_publication_to_faculty(pub.name)

    return pub
```

### Projects & Grants
```python
@frappe.whitelist()
def get_department_research(department):
    """Get research activity for department"""
    faculty_list = frappe.get_all("Faculty Profile", {"department": department})

    projects = frappe.get_all("Research Project", {
        "principal_investigator": ["in", [f.name for f in faculty_list]]
    })

    grants = frappe.get_all("Research Grant", {
        "principal_investigator": ["in", [f.name for f in faculty_list]]
    }, ["sanctioned_amount", "status"])

    return {
        "projects": len(projects),
        "active_grants": len([g for g in grants if g.status == "Active"]),
        "total_funding": sum(g.sanctioned_amount for g in grants)
    }

@frappe.whitelist()
def get_grant_utilization_status(grant):
    """Get grant fund utilization status"""
    grant_doc = frappe.get_doc("Research Grant", grant)

    return {
        "sanctioned": grant_doc.sanctioned_amount,
        "released": grant_doc.released_amount,
        "utilized": grant_doc.utilized_amount,
        "balance": grant_doc.balance_amount,
        "utilization_percentage": (grant_doc.utilized_amount / grant_doc.sanctioned_amount) * 100,
        "breakdown": [u.as_dict() for u in grant_doc.utilization]
    }
```

## Reports

1. **Publication Report** - Faculty/department-wise publications
2. **Citation Analysis** - Citation metrics and h-index
3. **Research Project Status** - Ongoing/completed projects
4. **Grant Utilization Report** - Fund usage tracking
5. **Research Dashboard** - Institutional research overview
6. **Department Research Summary** - Department-wise metrics

## Related Files

```
university_erp/
+-- university_research/
    +-- doctype/
    |   +-- research_publication/
    |   +-- publication_author/
    |   +-- research_project/
    |   +-- research_team_member/
    |   +-- project_publication_link/
    |   +-- research_grant/
    |   +-- grant_utilization/
    +-- api.py
```

## See Also

- [University HR Module](06_UNIVERSITY_HR.md)
- [University OBE Module](13_UNIVERSITY_OBE.md)
- [University Finance Module](05_UNIVERSITY_FINANCE.md)
