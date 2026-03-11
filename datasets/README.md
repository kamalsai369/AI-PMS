# Project Dataset Overview: 15km Metro Rail Project

Welcome to the AI-PMS development test. You have been provided with a baseline project schedule and supplemental meeting transcripts. Your task is to process this data into a structured dashboard that highlights conflicts, status, and logic errors.

## Data Files
- `metro_rail_wbs_data.csv`: The master work breakdown structure.
- `progress_review_meeting_transcript.md`: Supplemental narrative data.
- `design_coordination_meeting_transcript.md`: Supplemental narrative data.
- `safety_readiness_briefing_transcript.md`: Supplemental narrative data.

## WBS CSV Structure
The master CSV uses the following schema:

| Column | Description |
| :--- | :--- |
| `ID` | Unique 4-digit numeric identifier for the task. |
| `WBS_Code` | Hierarchical code representing the project levels (e.g., 1.1.2.1). |
| `Task_Name` | Descriptive name of the project activity. |
| `Start_Date` | Planned start date in `YYYY-MM-DD` format. |
| `Finish_Date` | Planned finish date in `YYYY-MM-DD` format. |
| `Duration_Days` | Total work days for the activity. |
| `Predecessors` | Comma-separated list of Task `ID`s that must complete before this task starts. |
| `Resources` | Professional role(s) assigned to the task. |
| `Status` | Current state: `Not Started`, `In Progress`, `On Hold`, `Completed`, `Delayed`, `Under Review`. |
| `Milestone` | `Yes` if the task is a major project milestone, otherwise `No`. |
| `Deadline` | Optional constraint date for major deliverables. |

## Key Technical Constraints
1. **Hierarchy**: Your system must respect the `WBS_Code` hierarchy. Level 4 tasks represent over 30% of the dataset.
2. **Logic Validation**: Identify missing references, circular dependencies, and date anomalies.
3. **Resource Analysis**: Track the daily workload for the 10 core resources to identify over-allocations.
4. **Narrative Correlation**: The provided markdown transcripts contain critical information that may contradict or explain anomalies in the CSV data.

## Resource List
The following roles are used throughout the project:
`Lead Architect`, `Safety Engineer`, `TBM Operator`, `Project Manager`, `Civil Engineer`, `Signaling Specialist`, `Quality Auditor`, `Land Surveyor`, `Legal Consultant`, `Rolling Stock Engineer`.
