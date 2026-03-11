# AI-Powered Project Management System (AI-PMS)
## Intelligent Dashboard for 15km Metro Rail Project

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red)

## 🏗️ Project Overview

An intelligent project management system that analyzes WBS schedules and meeting transcripts to provide comprehensive project intelligence for a 15km Metro Rail construction project.

## ✨ Key Features

### 1. **Schedule Validation Engine**
- Detects missing predecessor references
- Identifies circular dependencies
- Validates date logic (start/finish consistency)
- Checks for impossible dates (e.g., June 31st)

### 2. **Dependency Graph Analyzer**
- Builds directed graph of task relationships
- Computes critical path analysis
- Validates task sequencing logic
- Provides dependency statistics

### 3. **Resource Allocation Analyzer**
- Tracks workload per resource per day
- Detects over-allocation (>4 tasks/day threshold)
- Identifies resource conflicts across timeline
- Generates utilization heatmaps

### 4. **NLP Meeting Transcript Analyzer**
- Extracts task mentions from meeting notes
- Identifies delay indicators
- Detects resource conflict discussions
- Flags data quality issues

### 5. **Intelligent Conflict Detection**
- Compares schedule data with meeting insights
- Identifies status discrepancies
- Validates resource assignments
- Cross-references task mentions

### 6. **AI Risk Prediction Model**
- Predicts task delay probability
- Scores risks based on multiple factors:
  - Task duration and complexity
  - Dependency count
  - Resource allocation
  - Current status
  - Deadline pressure
- Provides actionable recommendations

### 7. **Interactive Dashboard**
- Real-time project health monitoring
- Multi-page navigation interface
- Interactive visualizations (Plotly)
- Comprehensive reporting

## 📁 Project Structure

```
dataset/
├── metro_rail_wbs_data.csv                    # Project WBS schedule
├── progress_review_meeting_transcript.md      # Meeting notes
├── design_coordination_meeting_transcript.md  # Meeting notes
├── safety_readiness_briefing_transcript.md    # Meeting notes
├── data_processor.py                          # Data loading & cleaning
├── wbs_hierarchy.py                           # WBS hierarchy engine
├── dependency_analyzer.py                     # Dependency validation
├── resource_analyzer.py                       # Resource allocation analysis
├── transcript_analyzer.py                     # NLP meeting analysis
├── conflict_detector.py                       # Conflict detection system
├── risk_predictor.py                          # Risk prediction model
├── dashboard.py                               # Main Streamlit dashboard
├── requirements.txt                           # Python dependencies
└── README.md                                  # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or navigate to the project directory:**
```bash
cd "C:\Users\tilla\OneDrive\Documents\Interviewprep\dataset"
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify data files exist:**
- `metro_rail_wbs_data.csv`
- Meeting transcript files (.md)

## 🎯 Usage

### Launch the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your default browser at `http://localhost:8501`

### Run Individual Modules

**Test Data Processing:**
```bash
python data_processor.py
```

**Test Dependency Analysis:**
```bash
python dependency_analyzer.py
```

**Test Resource Analysis:**
```bash
python resource_analyzer.py
```

**Test Transcript Analysis:**
```bash
python transcript_analyzer.py
```

**Test Conflict Detection:**
```bash
python conflict_detector.py
```

**Test Risk Prediction:**
```bash
python risk_predictor.py
```

## 📊 Dashboard Pages

### 1. 🏠 Project Overview
- Project health metrics
- Task status distribution
- Milestone tracking
- Risk overview

### 2. 📊 Schedule Validation
- Dependency statistics
- Missing references
- Circular dependencies
- Date logic violations
- Date anomalies

### 3. 👥 Resource Analysis
- Resource utilization summary
- Over-allocation detection
- Workload timeline visualization
- Critical conflict periods

### 4. ⚠️ Risk Prediction
- Risk distribution overview
- High-risk task identification
- Recommended actions
- Risk analysis by project phase

### 5. 📝 Meeting Insights
- Transcript analysis summary
- Delay mentions from meetings
- Resource conflicts mentioned
- Data quality issues identified

### 6. ⚡ Conflict Detection
- Status conflicts (schedule vs meetings)
- Resource allocation conflicts
- Data quality errors
- Full conflict report

## 🔍 Key Insights Detected

### From Analysis
1. **Task 1096** depends on non-existent task **1315** (Ghost reference)
2. **Task 1157** has invalid deadline: **June 31st, 2026**
3. **Lead Architect** over-allocated to **10 stations simultaneously**
4. **TBM Operator** assigned to **5 tunnel segments in parallel**
5. **Safety Engineer** assigned to **6 functional tests concurrently**

### Schedule Errors
- Missing predecessor references
- Date logic violations
- Invalid calendar dates

### Resource Conflicts
- Multiple instances of >7 concurrent tasks per resource
- Critical conflict periods identified
- Over-allocation rate calculated per resource

## 📈 Sample Outputs

### Risk Prediction Example
```
Task 1087: TBM Breakout at Retrieval Shaft
Risk Score: 78%
Risk Level: Critical
Recommendations:
  • Critical path task - prioritize resources
  • URGENT: Task not started but high risk
  • Milestone task - ensure executive visibility
```

### Conflict Detection Example
```
⚠️ Conflict Detected
Task: 1096 (Substation Foundation & Earthwork)
Schedule Status: Completed
Meeting Evidence: "Task 1096 is waiting on non-existent task 1315"
Severity: Critical
Recommendation: Remove ghost reference
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| Data Processing | Pandas, NumPy |
| Graph Analysis | NetworkX |
| NLP | Regular Expressions, Pattern Matching |
| Visualization | Plotly, Plotly Express |
| Dashboard | Streamlit |
| Date Handling | datetime |

## 📊 Data Sources

### WBS Dataset (`metro_rail_wbs_data.csv`)
- 162 tasks across entire project lifecycle
- Columns: ID, WBS_Code, Task_Name, Start_Date, Finish_Date, Duration_Days, Predecessors, Resources, Status, Milestone, Deadline

### Meeting Transcripts
1. **Progress Review Meeting** (2025-05-10)
   - Ghost reference issue (Task 1315)
   
2. **Design Coordination Meeting** (2024-02-05)
   - Resource overallocation issues
   
3. **Safety Readiness Briefing** (2026-12-20)
   - Invalid date error (June 31st)
   - Safety Engineer over-allocation

## 🎓 Advanced Features

### WBS Hierarchy Analysis
- Multi-level project decomposition
- Parent-child relationship tracking
- Delay propagation analysis
- Phase-level aggregation

### Dependency Graph Algorithms
- Cycle detection using DFS
- Critical path computation
- Topological sorting
- Predecessor/successor traversal

### Resource Workload Modeling
- Daily timeline construction
- Concurrent task counting
- Threshold-based alerting
- Heatmap visualization

### NLP Pattern Matching
- Task ID extraction (multiple patterns)
- Delay keyword detection
- Resource issue identification
- Data error recognition

## 🔧 Customization

### Adjust Resource Threshold
Edit `resource_analyzer.py`:
```python
self.workload_threshold = 4  # Change to desired max tasks/day
```

### Modify Risk Scoring Weights
Edit `risk_predictor.py` in the `compute_score()` method to adjust weights for:
- Duration risk
- Dependency complexity
- Status-based risk
- Critical path bonus
- Milestone importance
- Deadline pressure

### Add New NLP Keywords
Edit `transcript_analyzer.py` to add keywords for:
- Delays
- Resource issues
- Data quality problems

## 📝 Known Issues & Limitations

1. **Risk Prediction**: Currently uses rule-based scoring. Could be enhanced with ML models (Random Forest, XGBoost) if historical delay data available.

2. **NLP Analysis**: Uses pattern matching. Could be improved with SpaCy or LLM-based entity recognition.

3. **Critical Path**: Requires DAG (no cycles). System detects and reports cycles but cannot compute critical path if they exist.

4. **Scale**: Dashboard caches data for performance. For very large projects (>10,000 tasks), may need optimization.

## 🚀 Future Enhancements

- [ ] Real-time data integration (API endpoints)
- [ ] Automated email alerts for critical issues
- [ ] Machine learning delay prediction (requires historical data)
- [ ] Advanced NLP with SpaCy/transformers
- [ ] Monte Carlo schedule simulation
- [ ] Earned Value Management (EVM) metrics
- [ ] Mobile responsive dashboard
- [ ] Export reports to PDF/Excel
- [ ] User authentication & role-based access
- [ ] Integration with MS Project/Primavera

## 📄 License

This is a demonstration project for portfolio and educational purposes.

## 👨‍💻 Author

**Your Name**
- AI-Powered Project Management System
- Metro Rail Project Intelligence Dashboard

## 🙏 Acknowledgments

- Project management best practices from PMI
- Construction scheduling methodologies
- Network analysis algorithms
- Data visualization libraries

---

**Last Updated:** March 2026
**Version:** 1.0.0
**Status:** Production Ready ✅
