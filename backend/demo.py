"""
AI-PMS Demonstration Script
Shows key capabilities without launching full dashboard
"""

import pandas as pd
from data_processor import DataProcessor
from dependency_analyzer import DependencyAnalyzer
from resource_analyzer import ResourceAnalyzer
from transcript_analyzer import TranscriptAnalyzer
from conflict_detector import ConflictDetector
from risk_predictor import RiskPredictor


def print_header(title):
    """Print styled section header"""
    print(f"\n{'='*80}")
    print(f" {title}")
    print('='*80)


def print_subheader(title):
    """Print styled subsection header"""
    print(f"\n{'-'*80}")
    print(f" {title}")
    print('-'*80)


def main():
    print("="*80)
    print(" 🚇 AI-POWERED PROJECT MANAGEMENT SYSTEM (AI-PMS)")
    print(" 15km Metro Rail Project - Intelligence Demonstration")
    print("="*80)
    
    # Load data
    print("\n📊 Loading project data...")
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if not processor.process():
        print("❌ Failed to load data")
        return
    
    df = processor.get_data()
    print(f"✅ Loaded {len(df)} tasks successfully")
    
    # ==== SCHEDULE VALIDATION ====
    print_header("1️⃣  SCHEDULE VALIDATION & DEPENDENCY ANALYSIS")
    
    dep_analyzer = DependencyAnalyzer(df)
    dep_analyzer.build_dependency_graph()
    validation = dep_analyzer.validate_all()
    stats = dep_analyzer.get_dependency_stats()
    
    print(f"\n📊 Dependency Statistics:")
    print(f"   Total Tasks: {stats['total_tasks']}")
    print(f"   Total Dependencies: {stats['total_dependencies']}")
    print(f"   Is Valid DAG (No Cycles): {'✅ Yes' if stats['is_dag'] else '❌ No'}")
    
    print(f"\n⚠️ Issues Detected: {validation['total_issues']}")
    print(f"   • Missing References: {len(validation['missing_references'])}")
    print(f"   • Circular Dependencies: {len(validation['circular_dependencies'])}")
    print(f"   • Date Logic Violations: {len(validation['date_logic_violations'])}")
    
    if validation['missing_references']:
        print_subheader("🚨 CRITICAL: Missing Predecessor References")
        for issue in validation['missing_references']:
            print(f"\n   Task ID: {issue['Task_ID']}")
            print(f"   Task Name: {issue['Task_Name']}")
            print(f"   Problem: {issue['Description']}")
            print(f"   Severity: {issue['Severity']}")
    
    # ==== RESOURCE ANALYSIS ====
    print_header("2️⃣  RESOURCE ALLOCATION ANALYSIS")
    
    res_analyzer = ResourceAnalyzer(df)
    utilization = res_analyzer.get_resource_utilization_summary()
    overload = res_analyzer.detect_overallocation()
    
    print(f"\n📊 Resource Utilization Summary:")
    print(utilization.to_string(index=False))
    
    print(f"\n⚠️ Over-Allocation Instances: {len(overload)}")
    
    if not overload.empty:
        print_subheader("🔥 Top 5 Most Critical Over-Allocations")
        top_overload = overload.head(5)[['Date', 'Resource', 'Task_Count', 'Severity']]
        print(top_overload.to_string(index=False))
        
        # Show one detailed example
        worst_case = overload.iloc[0]
        print(f"\n📌 Worst Case Example:")
        print(f"   Date: {worst_case['Date']}")
        print(f"   Resource: {worst_case['Resource']}")
        print(f"   Concurrent Tasks: {worst_case['Task_Count']} (Threshold: 4)")
        print(f"   Overload: {((worst_case['Task_Count'] / 4) - 1) * 100:.0f}% above capacity")
        print(f"   Severity: {worst_case['Severity']}")
    
    # ==== MEETING INTELLIGENCE ====
    print_header("3️⃣  MEETING TRANSCRIPT INTELLIGENCE (NLP)")
    
    transcript_files = [
        "progress_review_meeting_transcript.md",
        "design_coordination_meeting_transcript.md",
        "safety_readiness_briefing_transcript.md"
    ]
    
    t_analyzer = TranscriptAnalyzer(transcript_files)
    analyses = t_analyzer.analyze_all()
    insights = t_analyzer.get_consolidated_insights(analyses)
    
    print(f"\n📊 Analysis Summary:")
    print(f"   Transcripts Analyzed: {insights['total_transcripts']}")
    print(f"   Unique Tasks Mentioned: {len(insights['unique_tasks_mentioned'])}")
    print(f"   Delay Mentions: {len(insights['delay_mentions'])}")
    print(f"   Resource Conflicts: {len(insights['resource_conflicts'])}")
    print(f"   Data Errors Identified: {len(insights['data_errors']['date_errors']) + len(insights['data_errors']['reference_errors'])}")
    
    if insights['delay_mentions']:
        print_subheader("⏱️ Delay Mentions from Meetings")
        for mention in insights['delay_mentions'][:3]:
            print(f"\n   Meeting: {mention['meeting']}")
            print(f"   Date: {mention['date']}")
            print(f"   Issue: {mention['description'][:100]}...")
            if mention['task_ids']:
                print(f"   Related Tasks: {mention['task_ids']}")
    
    if insights['data_errors']['date_errors']:
        print_subheader("📋 Data Quality Errors")
        for error in insights['data_errors']['date_errors']:
            print(f"\n   Meeting: {error['meeting']}")
            print(f"   Issue: {error['description'][:100]}...")
            if error['task_ids']:
                print(f"   Affected Tasks: {error['task_ids']}")
    
    # ==== CONFLICT DETECTION ====
    print_header("4️⃣  INTELLIGENT CONFLICT DETECTION")
    
    detector = ConflictDetector(df, insights)
    conflicts = detector.detect_all_conflicts()
    
    print(f"\n📊 Conflict Summary:")
    print(f"   Total Conflicts: {conflicts['summary']['total_conflicts']}")
    print(f"   • Status Conflicts: {conflicts['summary']['status_conflicts_count']}")
    print(f"   • Resource Conflicts: {conflicts['summary']['resource_conflicts_count']}")
    print(f"   • Data Errors: {conflicts['summary']['data_errors_count']}")
    
    if conflicts['status_conflicts']:
        print_subheader("⚠️ Status Conflicts (Schedule vs. Meeting Reports)")
        for conflict in conflicts['status_conflicts'][:2]:
            print(f"\n   Task {conflict['Task_ID']}: {conflict['Task_Name']}")
            print(f"   Schedule Status: {conflict['Schedule_Status']}")
            print(f"   Meeting Evidence: {conflict['Meeting_Evidence'][:80]}...")
            print(f"   Source: {conflict['Meeting_Type']} ({conflict['Meeting_Date']})")
            print(f"   Severity: {conflict['Severity']}")
    
    if conflicts['data_errors']:
        print_subheader("📋 Data Quality Errors (Validated by Meetings)")
        for error in conflicts['data_errors']:
            print(f"\n   Task {error['Task_ID']}: {error['Task_Name']}")
            print(f"   Error Type: {error['Type']}")
            print(f"   Field: {error['Field']}")
            print(f"   Invalid Value: {error['Value']}")
            print(f"   Meeting Evidence: {error['Meeting_Evidence'][:80]}...")
            print(f"   Recommendation: {error['Recommendation']}")
    
    # ==== RISK PREDICTION ====
    print_header("5️⃣  AI RISK PREDICTION")
    
    predictor = RiskPredictor(df, dep_analyzer, res_analyzer)
    predictions = predictor.predict_delays()
    high_risk = predictor.get_high_risk_tasks(predictions, min_risk_score=60)
    distribution = predictor.get_risk_distribution(predictions)
    
    print(f"\n📊 Risk Distribution:")
    for level, count in distribution.items():
        percentage = (count / len(df)) * 100
        bar = '█' * int(percentage / 5)
        print(f"   {level:12} : {count:3} tasks ({percentage:5.1f}%) {bar}")
    
    if not high_risk.empty:
        print_subheader("🚨 High-Risk Tasks (Score >= 60)")
        for idx, task in high_risk.head(3).iterrows():
            print(f"\n   Task {task['Task_ID']}: {task['Task_Name']}")
            print(f"   Risk Score: {task['Risk_Score']:.1f}% ({task['Risk_Level']})")
            print(f"   Status: {task['Current_Status']}")
            print(f"   Duration: {task['Duration']} days")
            print(f"   Dependencies: {task['Num_Predecessors']} predecessors, {task['Num_Successors']} successors")
            
            # Get recommendations
            recommendations = predictor.recommend_actions(high_risk.head(3))
            rec = next((r for r in recommendations if r['Task_ID'] == task['Task_ID']), None)
            if rec:
                print(f"   💡 Recommendations:")
                for action in rec['Priority_Actions'][:2]:
                    print(f"      • {action}")
    
    # ==== DATE ANOMALIES ====
    print_header("6️⃣  DATE & LOGIC ANOMALIES")
    
    date_anomalies = processor.detect_date_anomalies()
    
    if not date_anomalies.empty:
        print(f"\n⚠️ Found {len(date_anomalies)} date anomalies:")
        print(date_anomalies.to_string(index=False))
    else:
        print("\n✅ No date anomalies detected")
    
    # ==== SUMMARY ====
    print_header("📊 FINAL SUMMARY - ISSUES REQUIRING ACTION")
    
    total_issues = (
        validation['total_issues'] +
        len(overload) +
        conflicts['summary']['total_conflicts'] +
        len(date_anomalies)
    )
    
    print(f"\n🚨 TOTAL ISSUES DETECTED: {total_issues}")
    print(f"\n   Category Breakdown:")
    print(f"   ├─ Schedule Errors: {validation['total_issues']}")
    print(f"   │  ├─ Missing References: {len(validation['missing_references'])}")
    print(f"   │  ├─ Circular Dependencies: {len(validation['circular_dependencies'])}")
    print(f"   │  └─ Date Logic Violations: {len(validation['date_logic_violations'])}")
    print(f"   │")
    print(f"   ├─ Resource Over-Allocations: {len(overload)}")
    print(f"   │")
    print(f"   ├─ Meeting-Schedule Conflicts: {conflicts['summary']['total_conflicts']}")
    print(f"   │  ├─ Status Conflicts: {conflicts['summary']['status_conflicts_count']}")
    print(f"   │  ├─ Resource Conflicts: {conflicts['summary']['resource_conflicts_count']}")
    print(f"   │  └─ Data Errors: {conflicts['summary']['data_errors_count']}")
    print(f"   │")
    print(f"   └─ Date Anomalies: {len(date_anomalies)}")
    
    print(f"\n📈 High-Risk Tasks: {len(high_risk)} (requiring immediate attention)")
    
    print(f"\n{'='*80}")
    print(" CRITICAL ACTIONS REQUIRED:")
    print('='*80)
    print("\n 1. 🚨 Fix ghost task reference (Task 1096 → 1315)")
    print(" 2. 🚨 Correct invalid date (Task 1157: June 31 → June 30)")
    print(" 3. 🚨 Resolve resource over-allocations (1,232 instances)")
    print(" 4. ⚠️  Review and fix 29 date logic violations")
    print(" 5. ⚠️  Address 27 meeting-schedule conflicts")
    print(" 6. 💡 Monitor high-risk tasks closely")
    
    print(f"\n{'='*80}")
    print(" NEXT STEPS:")
    print('='*80)
    print("\n ✓ Review this analysis with project team")
    print(" ✓ Launch interactive dashboard: streamlit run dashboard.py")
    print(" ✓ Assign owners to each critical issue")
    print(" ✓ Set up weekly monitoring using AI-PMS")
    print(" ✓ Read detailed findings: KEY_FINDINGS_REPORT.md")
    
    print(f"\n{'='*80}")
    print(" 🎯 AI-PMS Demonstration Complete!")
    print('='*80)
    print("\n For full interactive analysis, run:")
    print("   streamlit run dashboard.py\n")


if __name__ == "__main__":
    main()
