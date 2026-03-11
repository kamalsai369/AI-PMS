"""
Resource Allocation Analyzer
Detects resource over-allocation and workload conflicts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict


class ResourceAnalyzer:
    """Analyzes resource allocation and detects overload"""
    
    def __init__(self, df):
        self.df = df
        self.resource_types = [
            'Lead Architect',
            'Safety Engineer',
            'TBM Operator',
            'Project Manager',
            'Civil Engineer',
            'Signaling Specialist',
            'Quality Auditor',
            'Land Surveyor',
            'Legal Consultant',
            'Rolling Stock Engineer'
        ]
        self.workload_threshold = 4  # Max tasks per resource per day
        
    def get_active_tasks_by_date(self):
        """Build timeline of active tasks for each date"""
        timeline = defaultdict(list)
        
        for idx, row in self.df.iterrows():
            start = row['Start_Date']
            finish = row['Finish_Date']
            
            if pd.notna(start) and pd.notna(finish):
                task_info = {
                    'id': row['ID'],
                    'name': row['Task_Name'],
                    'resource': row['Resources'],
                    'status': row['Status']
                }
                
                # Add task to each day in its duration
                current_date = start
                while current_date <= finish:
                    date_key = current_date.strftime('%Y-%m-%d')
                    timeline[date_key].append(task_info)
                    current_date += timedelta(days=1)
        
        return timeline
    
    def calculate_daily_workload(self):
        """Calculate workload per resource per day"""
        timeline = self.get_active_tasks_by_date()
        workload_data = []
        
        for date_str, tasks in timeline.items():
            # Count tasks per resource
            resource_counts = defaultdict(int)
            resource_tasks = defaultdict(list)
            
            for task in tasks:
                resource = task['resource']
                if resource in self.resource_types:
                    resource_counts[resource] += 1
                    resource_tasks[resource].append(task)
            
            # Record workload
            for resource, count in resource_counts.items():
                workload_data.append({
                    'Date': date_str,
                    'Resource': resource,
                    'Task_Count': count,
                    'Tasks': resource_tasks[resource],
                    'Overloaded': count > self.workload_threshold
                })
        
        return pd.DataFrame(workload_data)
    
    def detect_overallocation(self):
        """Identify specific instances of resource over-allocation"""
        workload_df = self.calculate_daily_workload()
        
        # Filter to overloaded instances
        overloaded = workload_df[workload_df['Overloaded'] == True].copy()
        
        if overloaded.empty:
            return pd.DataFrame()
        
        # Add severity
        overloaded['Severity'] = overloaded['Task_Count'].apply(
            lambda x: 'Critical' if x >= 7 else 'High' if x >= 5 else 'Medium'
        )
        
        # Sort by severity and count
        overloaded = overloaded.sort_values(['Task_Count', 'Date'], ascending=[False, True])
        
        return overloaded
    
    def get_resource_utilization_summary(self):
        """Get summary statistics for each resource"""
        workload_df = self.calculate_daily_workload()
        
        summary = []
        for resource in self.resource_types:
            resource_data = workload_df[workload_df['Resource'] == resource]
            
            if not resource_data.empty:
                total_days = len(resource_data)
                overloaded_days = len(resource_data[resource_data['Overloaded']])
                avg_workload = resource_data['Task_Count'].mean()
                max_workload = resource_data['Task_Count'].max()
                max_date = resource_data.loc[resource_data['Task_Count'].idxmax(), 'Date']
                
                summary.append({
                    'Resource': resource,
                    'Total_Working_Days': total_days,
                    'Overloaded_Days': overloaded_days,
                    'Overload_Rate_%': round((overloaded_days / total_days) * 100, 1) if total_days > 0 else 0,
                    'Avg_Daily_Tasks': round(avg_workload, 2),
                    'Peak_Workload': int(max_workload),
                    'Peak_Date': max_date
                })
        
        return pd.DataFrame(summary).sort_values('Overload_Rate_%', ascending=False)
    
    def get_conflict_periods(self):
        """Identify specific date ranges with conflicts"""
        workload_df = self.calculate_daily_workload()
        overloaded = workload_df[workload_df['Overloaded'] == True]
        
        conflicts = []
        for resource in self.resource_types:
            resource_overload = overloaded[overloaded['Resource'] == resource]
            
            if not resource_overload.empty:
                # Group consecutive dates
                dates = sorted(resource_overload['Date'].unique())
                
                for date in dates[:10]:  # Show top 10 dates
                    day_data = resource_overload[resource_overload['Date'] == date].iloc[0]
                    task_names = [t['name'] for t in day_data['Tasks'][:5]]  # First 5 tasks
                    
                    conflicts.append({
                        'Resource': resource,
                        'Date': date,
                        'Concurrent_Tasks': day_data['Task_Count'],
                        'Sample_Tasks': task_names,
                        'Severity': 'Critical' if day_data['Task_Count'] >= 7 else 'High'
                    })
        
        return pd.DataFrame(conflicts).sort_values('Concurrent_Tasks', ascending=False)
    
    def analyze_specific_date_range(self, start_date_str, end_date_str):
        """Analyze resource allocation for a specific date range"""
        workload_df = self.calculate_daily_workload()
        
        # Filter to date range
        range_data = workload_df[
            (workload_df['Date'] >= start_date_str) & 
            (workload_df['Date'] <= end_date_str)
        ]
        
        summary = range_data.groupby('Resource').agg({
            'Task_Count': ['mean', 'max', 'sum'],
            'Overloaded': 'sum'
        }).round(2)
        
        return summary
    
    def get_resource_heatmap_data(self, start_date=None, end_date=None, sample_days=100):
        """Prepare data for resource workload heatmap visualization"""
        workload_df = self.calculate_daily_workload()
        
        # Filter date range if specified
        if start_date:
            workload_df = workload_df[workload_df['Date'] >= start_date]
        if end_date:
            workload_df = workload_df[workload_df['Date'] <= end_date]
        
        # Sample dates for visualization (to avoid too many columns)
        unique_dates = sorted(workload_df['Date'].unique())
        if len(unique_dates) > sample_days:
            step = len(unique_dates) // sample_days
            sampled_dates = unique_dates[::step]
        else:
            sampled_dates = unique_dates
        
        # Pivot for heatmap
        heatmap_data = workload_df[workload_df['Date'].isin(sampled_dates)].pivot_table(
            index='Resource',
            columns='Date',
            values='Task_Count',
            fill_value=0
        )
        
        return heatmap_data
    
    def identify_conflicting_tasks(self, resource_name, date_str):
        """Get list of conflicting tasks for a specific resource on a specific date"""
        workload_df = self.calculate_daily_workload()
        
        match = workload_df[
            (workload_df['Resource'] == resource_name) & 
            (workload_df['Date'] == date_str)
        ]
        
        if match.empty:
            return []
        
        tasks = match.iloc[0]['Tasks']
        return tasks


if __name__ == "__main__":
    from data_processor import DataProcessor
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        
        analyzer = ResourceAnalyzer(df)
        
        print("✅ Resource analyzer initialized")
        
        # Get utilization summary
        summary = analyzer.get_resource_utilization_summary()
        print(f"\n📊 Resource Utilization Summary:")
        print(summary.to_string(index=False))
        
        # Get overallocation instances
        overloaded = analyzer.detect_overallocation()
        print(f"\n⚠️ Total Over-allocation Instances: {len(overloaded)}")
        
        if not overloaded.empty:
            print(f"\n🔥 Top 5 Worst Cases:")
            top_cases = overloaded.head(5)[['Date', 'Resource', 'Task_Count', 'Severity']]
            print(top_cases.to_string(index=False))
