"""
Conflict Detection System
Compares schedule data with meeting insights to identify conflicts
"""

import pandas as pd
from datetime import datetime


class ConflictDetector:
    """Detects conflicts between schedule data and meeting insights"""
    
    def __init__(self, df, transcript_insights):
        self.df = df
        self.insights = transcript_insights
        self.conflicts = []
        
    def detect_status_conflicts(self):
        """Detect conflicts between transcript mentions and task status"""
        status_conflicts = []
        
        # Check delay mentions against task status
        for delay_mention in self.insights.get('delay_mentions', []):
            for task_id in delay_mention['task_ids']:
                task_row = self.df[self.df['ID'] == task_id]
                
                if not task_row.empty:
                    task_status = task_row.iloc[0]['Status']
                    task_name = task_row.iloc[0]['Task_Name']
                    
                    # If transcript says delayed but status is "In Progress" or "Completed"
                    if task_status in ['In Progress', 'Completed']:
                        status_conflicts.append({
                            'Type': 'Status Conflict',
                            'Task_ID': task_id,
                            'Task_Name': task_name,
                            'Schedule_Status': task_status,
                            'Meeting_Evidence': delay_mention['description'][:100],
                            'Meeting_Type': delay_mention['meeting'],
                            'Meeting_Date': delay_mention['date'],
                            'Severity': 'High',
                            'Recommendation': 'Update task status to reflect actual delay'
                        })
        
        return status_conflicts
    
    def validate_resource_allocations(self):
        """Cross-check resource issues mentioned in meetings with schedule"""
        resource_conflicts = []
        
        for resource_issue in self.insights.get('resource_conflicts', []):
            for task_id in resource_issue['task_ids']:
                task_row = self.df[self.df['ID'] == task_id]
                
                if not task_row.empty:
                    task_name = task_row.iloc[0]['Task_Name']
                    resource = task_row.iloc[0]['Resources']
                    start_date = task_row.iloc[0]['Start_Date']
                    
                    resource_conflicts.append({
                        'Type': 'Resource Overallocation',
                        'Task_ID': task_id,
                        'Task_Name': task_name,
                        'Resource': resource,
                        'Start_Date': start_date.strftime('%Y-%m-%d') if pd.notna(start_date) else 'Unknown',
                        'Meeting_Evidence': resource_issue['description'][:100],
                        'Meeting_Type': resource_issue['meeting'],
                        'Severity': 'Critical',
                        'Recommendation': 'Review and adjust resource assignments'
                    })
        
        return resource_conflicts
    
    def validate_data_errors(self):
        """Validate data quality issues mentioned in meetings"""
        data_errors = []
        
        # Check date errors
        for date_error in self.insights['data_errors']['date_errors']:
            for task_id in date_error['task_ids']:
                task_row = self.df[self.df['ID'] == task_id]
                
                if not task_row.empty:
                    task_name = task_row.iloc[0]['Task_Name']
                    deadline = task_row.iloc[0]['Deadline']
                    
                    data_errors.append({
                        'Type': 'Invalid Date',
                        'Task_ID': task_id,
                        'Task_Name': task_name,
                        'Field': 'Deadline',
                        'Value': str(deadline),
                        'Meeting_Evidence': date_error['description'][:100],
                        'Severity': 'Critical',
                        'Recommendation': 'Correct date to valid calendar date'
                    })
        
        # Check reference errors
        for ref_error in self.insights['data_errors']['reference_errors']:
            for task_id in ref_error['task_ids']:
                task_row = self.df[self.df['ID'] == task_id]
                
                if not task_row.empty:
                    task_name = task_row.iloc[0]['Task_Name']
                    predecessors = task_row.iloc[0]['Predecessor_List']
                    
                    data_errors.append({
                        'Type': 'Missing Predecessor Reference',
                        'Task_ID': task_id,
                        'Task_Name': task_name,
                        'Field': 'Predecessors',
                        'Value': str(predecessors),
                        'Meeting_Evidence': ref_error['description'][:100],
                        'Severity': 'Critical',
                        'Recommendation': 'Remove ghost reference or add missing task'
                    })
        
        return data_errors
    
    def cross_reference_tasks(self):
        """Cross-reference tasks mentioned in meetings with schedule"""
        mentioned_tasks = set(self.insights.get('unique_tasks_mentioned', []))
        scheduled_tasks = set(self.df['ID'].values)
        
        # Tasks mentioned but not in schedule
        orphan_mentions = mentioned_tasks - scheduled_tasks
        
        # Tasks in schedule but never mentioned (might be less important)
        unmentioned_tasks = scheduled_tasks - mentioned_tasks
        
        return {
            'tasks_mentioned_in_meetings': len(mentioned_tasks),
            'tasks_in_schedule': len(scheduled_tasks),
            'orphan_task_mentions': list(orphan_mentions),
            'unmentioned_tasks_count': len(unmentioned_tasks)
        }
    
    def detect_all_conflicts(self):
        """Run all conflict detection checks"""
        conflicts = {
            'status_conflicts': self.detect_status_conflicts(),
            'resource_conflicts': self.validate_resource_allocations(),
            'data_errors': self.validate_data_errors(),
            'cross_reference': self.cross_reference_tasks()
        }
        
        # Calculate totals
        total_issues = (
            len(conflicts['status_conflicts']) +
            len(conflicts['resource_conflicts']) +
            len(conflicts['data_errors'])
        )
        
        conflicts['summary'] = {
            'total_conflicts': total_issues,
            'status_conflicts_count': len(conflicts['status_conflicts']),
            'resource_conflicts_count': len(conflicts['resource_conflicts']),
            'data_errors_count': len(conflicts['data_errors'])
        }
        
        return conflicts
    
    def get_critical_issues(self, conflicts):
        """Extract only critical severity issues"""
        critical = []
        
        for conflict in conflicts.get('status_conflicts', []):
            if conflict['Severity'] == 'Critical' or conflict['Severity'] == 'High':
                critical.append(conflict)
        
        for conflict in conflicts.get('resource_conflicts', []):
            if conflict['Severity'] == 'Critical':
                critical.append(conflict)
        
        for error in conflicts.get('data_errors', []):
            if error['Severity'] == 'Critical':
                critical.append(error)
        
        return critical
    
    def generate_conflict_report(self, conflicts):
        """Generate human-readable conflict report"""
        report = []
        
        report.append("="*80)
        report.append("CONFLICT DETECTION REPORT")
        report.append("="*80)
        
        summary = conflicts['summary']
        report.append(f"\nTotal Conflicts Found: {summary['total_conflicts']}")
        report.append(f"  - Status Conflicts: {summary['status_conflicts_count']}")
        report.append(f"  - Resource Conflicts: {summary['resource_conflicts_count']}")
        report.append(f"  - Data Errors: {summary['data_errors_count']}")
        
        # Status conflicts
        if conflicts['status_conflicts']:
            report.append("\n" + "-"*80)
            report.append("STATUS CONFLICTS")
            report.append("-"*80)
            for conflict in conflicts['status_conflicts'][:5]:
                report.append(f"\nTask {conflict['Task_ID']}: {conflict['Task_Name']}")
                report.append(f"  Schedule shows: {conflict['Schedule_Status']}")
                report.append(f"  Meeting evidence: {conflict['Meeting_Evidence']}")
                report.append(f"  Source: {conflict['Meeting_Type']} ({conflict['Meeting_Date']})")
        
        # Resource conflicts
        if conflicts['resource_conflicts']:
            report.append("\n" + "-"*80)
            report.append("RESOURCE CONFLICTS")
            report.append("-"*80)
            for conflict in conflicts['resource_conflicts'][:5]:
                report.append(f"\nTask {conflict['Task_ID']}: {conflict['Task_Name']}")
                report.append(f"  Resource: {conflict['Resource']}")
                report.append(f"  Evidence: {conflict['Meeting_Evidence']}")
        
        # Data errors
        if conflicts['data_errors']:
            report.append("\n" + "-"*80)
            report.append("DATA QUALITY ERRORS")
            report.append("-"*80)
            for error in conflicts['data_errors'][:5]:
                report.append(f"\nTask {error['Task_ID']}: {error['Task_Name']}")
                report.append(f"  Issue: {error['Type']}")
                report.append(f"  Evidence: {error['Meeting_Evidence']}")
        
        report.append("\n" + "="*80)
        
        return "\n".join(report)


if __name__ == "__main__":
    from data_processor import DataProcessor
    from transcript_analyzer import TranscriptAnalyzer
    
    # Load data
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        
        # Analyze transcripts
        transcript_files = [
            "progress_review_meeting_transcript.md",
            "design_coordination_meeting_transcript.md",
            "safety_readiness_briefing_transcript.md"
        ]
        
        t_analyzer = TranscriptAnalyzer(transcript_files)
        analyses = t_analyzer.analyze_all()
        insights = t_analyzer.get_consolidated_insights(analyses)
        
        # Detect conflicts
        detector = ConflictDetector(df, insights)
        conflicts = detector.detect_all_conflicts()
        
        print("✅ Conflict detection complete")
        print(f"\n📊 Conflict Summary:")
        print(f"  Total Conflicts: {conflicts['summary']['total_conflicts']}")
        print(f"  Status Conflicts: {conflicts['summary']['status_conflicts_count']}")
        print(f"  Resource Conflicts: {conflicts['summary']['resource_conflicts_count']}")
        print(f"  Data Errors: {conflicts['summary']['data_errors_count']}")
        
        # Generate report
        report = detector.generate_conflict_report(conflicts)
        print("\n" + report)
