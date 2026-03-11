"""
AI-Powered Project Management Dashboard
Interactive Streamlit application for 15km Metro Rail Project
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from datetime import datetime

# Import custom modules
from data_processor import DataProcessor
from wbs_hierarchy import WBSHierarchy
from dependency_analyzer import DependencyAnalyzer
from resource_analyzer import ResourceAnalyzer
from transcript_analyzer import TranscriptAnalyzer
from conflict_detector import ConflictDetector
from risk_predictor import RiskPredictor


# Page configuration
st.set_page_config(
    page_title="AI-PMS: Metro Rail Project",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical-alert {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4d4d;
    }
    .success-card {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00cc00;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_data():
    """Load and process all project data"""
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        date_anomalies = processor.detect_date_anomalies()
        return df, date_anomalies, None
    else:
        return None, None, processor.get_errors()


@st.cache_data
def analyze_transcripts():
    """Analyze meeting transcripts"""
    transcript_files = [
        "progress_review_meeting_transcript.md",
        "design_coordination_meeting_transcript.md",
        "safety_readiness_briefing_transcript.md"
    ]
    
    analyzer = TranscriptAnalyzer(transcript_files)
    analyses = analyzer.analyze_all()
    insights = analyzer.get_consolidated_insights(analyses)
    
    return insights


@st.cache_data
def analyze_dependencies(_df):
    """Analyze task dependencies"""
    analyzer = DependencyAnalyzer(_df)
    analyzer.build_dependency_graph()
    validation = analyzer.validate_all()
    stats = analyzer.get_dependency_stats()
    
    return analyzer, validation, stats


@st.cache_data
def analyze_resources(_df):
    """Analyze resource allocation"""
    analyzer = ResourceAnalyzer(_df)
    utilization = analyzer.get_resource_utilization_summary()
    overload = analyzer.detect_overallocation()
    conflicts = analyzer.get_conflict_periods()
    
    return analyzer, utilization, overload, conflicts


@st.cache_data
def predict_risks(_df, _dep_analyzer, _res_analyzer):
    """Generate risk predictions"""
    predictor = RiskPredictor(_df, _dep_analyzer, _res_analyzer)
    predictions = predictor.predict_delays()
    high_risk = predictor.get_high_risk_tasks(predictions, min_risk_score=60)
    distribution = predictor.get_risk_distribution(predictions)
    
    return predictor, predictions, high_risk, distribution


def main():
    # Header
    st.markdown('<h1 class="main-header">🚇 AI-PMS: Construction Control Tower</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">15km Metro Rail Project - Intelligent Dashboard</p>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading project data..."):
        df, date_anomalies, errors = load_and_process_data()
    
    if df is None:
        st.error("❌ Failed to load project data!")
        if errors:
            for error in errors:
                st.error(f"  • {error}")
        return
    
    # Analyze data
    with st.spinner("Analyzing project intelligence..."):
        insights = analyze_transcripts()
        dep_analyzer, dep_validation, dep_stats = analyze_dependencies(df)
        res_analyzer, res_utilization, res_overload, res_conflicts = analyze_resources(df)
        predictor, predictions, high_risk, risk_dist = predict_risks(df, dep_analyzer, res_analyzer)
        
        # Conflict detection
        detector = ConflictDetector(df, insights)
        conflicts = detector.detect_all_conflicts()
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.radio(
        "Select View:",
        ["🏠 Project Overview", "📊 Schedule Validation", "👥 Resource Analysis", 
         "⚠️ Risk Prediction", "📝 Meeting Insights", "⚡ Conflict Detection"]
    )
    
    # ===== PAGE 1: PROJECT OVERVIEW =====
    if page == "🏠 Project Overview":
        st.header("📊 Project Health Dashboard")
        
        # Key metrics row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        status_counts = df['Status'].value_counts()
        
        with col1:
            st.metric("Total Tasks", len(df))
        with col2:
            st.metric("Completed", status_counts.get('Completed', 0), 
                     delta=f"{(status_counts.get('Completed', 0)/len(df)*100):.1f}%")
        with col3:
            st.metric("In Progress", status_counts.get('In Progress', 0))
        with col4:
            st.metric("Not Started", status_counts.get('Not Started', 0))
        with col5:
            critical_issues = (len(dep_validation['missing_references']) + 
                             len(dep_validation['circular_dependencies']) +
                             len(high_risk))
            st.metric("Critical Issues", critical_issues, delta_color="inverse")
        
        st.divider()
        
        # Project timeline
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Project Timeline Status")
            
            # Status distribution pie chart
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Task Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Project Milestones")
            
            milestones = df[df['Milestone'] == 'Yes'].sort_values('Finish_Date')
            if not milestones.empty:
                for idx, milestone in milestones.head(8).iterrows():
                    status_icon = "✅" if milestone['Status'] == 'Completed' else "🔄" if milestone['Status'] == 'In Progress' else "⏳"
                    st.write(f"{status_icon} **{milestone['Task_Name']}**")
                    st.write(f"   Target: {milestone['Finish_Date'].strftime('%Y-%m-%d') if pd.notna(milestone['Finish_Date']) else 'TBD'}")
            else:
                st.info("No milestones defined")
        
        st.divider()
        
        # Risk overview
        st.subheader("⚠️ Risk Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("High-Risk Tasks", len(high_risk))
            st.write("Tasks requiring immediate attention")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Resource Conflicts", len(res_conflicts))
            st.write("Resource over-allocation instances")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Schedule Errors", dep_validation['total_issues'])
            st.write("Dependency and date logic issues")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Risk distribution chart
        st.subheader("📈 Risk Distribution")
        risk_df = pd.DataFrame(list(risk_dist.items()), columns=['Risk Level', 'Count'])
        risk_df = risk_df.sort_values('Count', ascending=False)
        
        fig_risk = px.bar(
            risk_df,
            x='Risk Level',
            y='Count',
            title="Tasks by Risk Level",
            color='Risk Level',
            color_discrete_map={
                'Critical': '#dc3545',
                'High': '#fd7e14',
                'Medium': '#ffc107',
                'Low': '#20c997',
                'Very Low': '#28a745'
            }
        )
        st.plotly_chart(fig_risk, use_container_width=True)
    
    # ===== PAGE 2: SCHEDULE VALIDATION =====
    elif page == "📊 Schedule Validation":
        st.header("📊 Schedule Validation & Dependency Analysis")
        
        # Dependency statistics
        st.subheader("🔗 Dependency Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Dependencies", dep_stats['total_dependencies'])
        with col2:
            st.metric("Is Valid DAG", "✅ Yes" if dep_stats['is_dag'] else "❌ No")
        with col3:
            st.metric("Root Tasks", dep_stats['tasks_with_no_predecessors'])
        with col4:
            st.metric("Leaf Tasks", dep_stats['tasks_with_no_successors'])
        
        st.divider()
        
        # Validation issues
        st.subheader("⚠️ Detected Issues")
        
        # Missing references
        if dep_validation['missing_references']:
            st.markdown('<div class="critical-alert">', unsafe_allow_html=True)
            st.error(f"❌ **Missing Predecessor References: {len(dep_validation['missing_references'])}**")
            
            missing_df = pd.DataFrame(dep_validation['missing_references'])
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No missing predecessor references found")
        
        st.divider()
        
        # Circular dependencies
        if dep_validation['circular_dependencies']:
            st.markdown('<div class="critical-alert">', unsafe_allow_html=True)
            st.error(f"❌ **Circular Dependencies: {len(dep_validation['circular_dependencies'])}**")
            
            for cycle in dep_validation['circular_dependencies']:
                st.write(f"🔄 **Cycle:** {cycle['Cycle']}")
                st.write(f"   Tasks involved: {cycle['Tasks_Involved']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No circular dependencies detected")
        
        st.divider()
        
        # Date logic violations
        if dep_validation['date_logic_violations']:
            st.warning(f"⚠️ **Date Logic Violations: {len(dep_validation['date_logic_violations'])}**")
            
            date_violations_df = pd.DataFrame(dep_validation['date_logic_violations'])
            st.dataframe(date_violations_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No date logic violations")
        
        st.divider()
        
        # Date anomalies from data processor
        if not date_anomalies.empty:
            st.warning(f"⚠️ **Date Anomalies: {len(date_anomalies)}**")
            st.dataframe(date_anomalies, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No date anomalies detected")
    
    # ===== PAGE 3: RESOURCE ANALYSIS =====
    elif page == "👥 Resource Analysis":
        st.header("👥 Resource Allocation Analysis")
        
        # Resource utilization summary
        st.subheader("📊 Resource Utilization Summary")
        st.dataframe(res_utilization, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Over-allocation instances
        st.subheader("⚠️ Resource Over-Allocation Instances")
        
        if not res_overload.empty:
            st.error(f"Found {len(res_overload)} instances of resource over-allocation")
            
            # Show top cases
            top_overload = res_overload.head(20)[['Date', 'Resource', 'Task_Count', 'Severity']]
            st.dataframe(top_overload, use_container_width=True, hide_index=True)
            
            # Visualize resource workload over time
            st.subheader("📈 Resource Workload Timeline")
            
            # Sample data for visualization
            sample_resources = res_overload['Resource'].unique()[:3]  # Top 3 most overloaded
            
            for resource in sample_resources:
                resource_data = res_overload[res_overload['Resource'] == resource].sort_values('Date')
                if not resource_data.empty:
                    fig = px.line(
                        resource_data,
                        x='Date',
                        y='Task_Count',
                        title=f"{resource} - Daily Workload",
                        markers=True
                    )
                    fig.add_hline(y=4, line_dash="dash", line_color="red", 
                                 annotation_text="Threshold (4 tasks/day)")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No resource over-allocation detected!")
        
        st.divider()
        
        # Conflict periods
        st.subheader("🔥 Critical Conflict Periods")
        
        if not res_conflicts.empty:
            top_conflicts = res_conflicts.head(10)
            
            for idx, conflict in top_conflicts.iterrows():
                severity_color = "🔴" if conflict['Severity'] == 'Critical' else "🟡"
                st.write(f"{severity_color} **{conflict['Resource']}** on {conflict['Date']}")
                st.write(f"   Concurrent tasks: **{conflict['Concurrent_Tasks']}**")
                st.write(f"   Sample tasks: {', '.join(conflict['Sample_Tasks'][:3])}")
                st.divider()
        else:
            st.success("✅ No critical conflict periods identified")
    
    # ===== PAGE 4: RISK PREDICTION =====
    elif page == "⚠️ Risk Prediction":
        st.header("⚠️ AI Risk Prediction & Early Warning")
        
        # Risk distribution
        st.subheader("📊 Risk Distribution Overview")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.metric("Critical Risk", risk_dist['Critical'], delta_color="inverse")
            st.metric("High Risk", risk_dist['High'], delta_color="inverse")
        
        with col2:
            # Risk gauge chart
            risk_df_viz = pd.DataFrame(list(risk_dist.items()), columns=['Level', 'Count'])
            fig_risk_dist = px.bar(
                risk_df_viz,
                x='Level',
                y='Count',
                title="Tasks by Risk Level",
                color='Level',
                color_discrete_map={
                    'Critical': '#dc3545',
                    'High': '#fd7e14',
                    'Medium': '#ffc107',
                    'Low': '#20c997',
                    'Very Low': '#28a745'
                }
            )
            st.plotly_chart(fig_risk_dist, use_container_width=True)
        
        with col3:
            st.metric("Medium Risk", risk_dist['Medium'])
            st.metric("Low Risk", risk_dist['Low'])
        
        st.divider()
        
        # High-risk tasks
        st.subheader("🔥 High-Risk Tasks Requiring Attention")
        
        if not high_risk.empty:
            st.error(f"⚠️ {len(high_risk)} tasks identified as high risk")
            
            # Display table
            display_cols = ['Task_ID', 'Task_Name', 'Risk_Score', 'Risk_Level', 
                           'Current_Status', 'Duration', 'Is_Milestone']
            st.dataframe(high_risk[display_cols].head(20), use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Recommendations
            st.subheader("💡 Recommended Actions")
            
            recommendations = predictor.recommend_actions(high_risk.head(10))
            
            for rec in recommendations:
                with st.expander(f"Task {rec['Task_ID']}: {rec['Task_Name']} ({rec['Risk_Level']})"):
                    st.write("**Priority Actions:**")
                    for action in rec['Priority_Actions']:
                        st.write(f"  • {action}")
        else:
            st.success("✅ No high-risk tasks detected!")
        
        st.divider()
        
        # Risk by phase
        st.subheader("📋 Risk Analysis by Project Phase")
        
        phase_risk = predictor.analyze_risk_by_phase(predictions)
        st.dataframe(phase_risk, use_container_width=True)
    
    # ===== PAGE 5: MEETING INSIGHTS =====
    elif page == "📝 Meeting Insights":
        st.header("📝 Meeting Transcript Intelligence")
        
        st.subheader("📊 Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Transcripts Analyzed", insights['total_transcripts'])
        with col2:
            st.metric("Tasks Mentioned", len(insights['unique_tasks_mentioned']))
        with col3:
            st.metric("Delay Mentions", len(insights['delay_mentions']))
        with col4:
            st.metric("Resource Conflicts", len(insights['resource_conflicts']))
        
        st.divider()
        
        # Delay mentions
        if insights['delay_mentions']:
            st.subheader("⏱️ Delay Mentions from Meetings")
            
            for mention in insights['delay_mentions']:
                st.warning(f"**{mention['meeting']}** ({mention['date']})")
                st.write(f"   {mention['description']}")
                if mention['task_ids']:
                    st.write(f"   Related tasks: {mention['task_ids']}")
                st.divider()
        
        # Resource conflicts
        if insights['resource_conflicts']:
            st.subheader("👥 Resource Conflicts Mentioned")
            
            for conflict in insights['resource_conflicts']:
                st.error(f"**{conflict['meeting']}** ({conflict['date']})")
                st.write(f"   {conflict['description']}")
                if conflict['task_ids']:
                    st.write(f"   Related tasks: {conflict['task_ids']}")
                st.divider()
        
        # Data errors
        st.subheader("📋 Data Quality Issues Identified")
        
        if insights['data_errors']['date_errors']:
            st.error("**Date Errors:**")
            for error in insights['data_errors']['date_errors']:
                st.write(f"  • {error['description']}")
        
        if insights['data_errors']['reference_errors']:
            st.error("**Reference Errors:**")
            for error in insights['data_errors']['reference_errors']:
                st.write(f"  • {error['description']}")
        
        if not insights['data_errors']['date_errors'] and not insights['data_errors']['reference_errors']:
            st.success("✅ No data quality issues mentioned in meetings")
    
    # ===== PAGE 6: CONFLICT DETECTION =====
    elif page == "⚡ Conflict Detection":
        st.header("⚡ Intelligent Conflict Detection")
        
        st.info("Comparing schedule data with meeting insights to identify discrepancies...")
        
        # Summary
        st.subheader("📊 Conflict Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status Conflicts", conflicts['summary']['status_conflicts_count'])
        with col2:
            st.metric("Resource Conflicts", conflicts['summary']['resource_conflicts_count'])
        with col3:
            st.metric("Data Errors", conflicts['summary']['data_errors_count'])
        
        st.divider()
        
        # Status conflicts
        if conflicts['status_conflicts']:
            st.subheader("⚠️ Status Conflicts")
            st.error(f"Found {len(conflicts['status_conflicts'])} conflicts between schedule and meeting reports")
            
            status_conflicts_df = pd.DataFrame(conflicts['status_conflicts'])
            st.dataframe(status_conflicts_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No status conflicts detected")
        
        st.divider()
        
        # Resource conflicts
        if conflicts['resource_conflicts']:
            st.subheader("👥 Resource Allocation Conflicts")
            
            resource_conflicts_df = pd.DataFrame(conflicts['resource_conflicts'])
            st.dataframe(resource_conflicts_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No resource conflicts detected")
        
        st.divider()
        
        # Data errors
        if conflicts['data_errors']:
            st.subheader("📋 Data Quality Errors")
            st.error(f"Found {len(conflicts['data_errors'])} data quality issues validated by meetings")
            
            data_errors_df = pd.DataFrame(conflicts['data_errors'])
            st.dataframe(data_errors_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No data quality errors detected")
        
        st.divider()
        
        # Generate full report
        with st.expander("📄 View Full Conflict Report"):
            report = detector.generate_conflict_report(conflicts)
            st.code(report, language='text')
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>AI-Powered Project Management System (AI-PMS)</p>
        <p>15km Metro Rail Project Construction Control Tower</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
