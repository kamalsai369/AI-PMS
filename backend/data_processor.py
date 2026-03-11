"""
Data Processing Module for AI-PMS
Handles CSV loading, date parsing, and data cleaning
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re


class DataProcessor:
    """Processes and cleans project WBS data"""
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        self.errors = []
        
    def load_data(self):
        """Load CSV file into pandas DataFrame"""
        try:
            self.df = pd.read_csv(self.csv_path)
            return True
        except Exception as e:
            self.errors.append(f"Failed to load CSV: {str(e)}")
            return False
    
    def parse_dates(self):
        """Parse and validate date columns"""
        date_columns = ['Start_Date', 'Finish_Date', 'Deadline']
        
        for col in date_columns:
            if col in self.df.columns:
                # Parse dates with error checking
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce', format='%Y-%m-%d')
        
        return True
    
    def split_predecessors(self):
        """Split predecessor lists into arrays"""
        def parse_predecessor(value):
            if pd.isna(value) or value == '':
                return []
            # Handle multiple predecessors separated by comma
            predecessors = str(value).split(',')
            result = []
            for p in predecessors:
                p = p.strip()
                if p:
                    try:
                        # Handle both int and float strings (e.g., "1315.0")
                        result.append(int(float(p)))
                    except ValueError:
                        pass
            return result
        
        self.df['Predecessor_List'] = self.df['Predecessors'].apply(parse_predecessor)
        return True
    
    def normalize_resources(self):
        """Normalize and clean resource names"""
        if 'Resources' in self.df.columns:
            # Strip whitespace and standardize
            self.df['Resources'] = self.df['Resources'].str.strip()
        return True
    
    def validate_data(self):
        """Check for missing or invalid values"""
        issues = []
        
        # Check required columns
        required_cols = ['ID', 'WBS_Code', 'Task_Name', 'Start_Date', 'Finish_Date']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            issues.append(f"Missing columns: {missing_cols}")
        
        # Check for null IDs
        if self.df['ID'].isna().any():
            issues.append(f"Found {self.df['ID'].isna().sum()} null IDs")
        
        # Check for duplicate IDs
        duplicates = self.df[self.df.duplicated('ID', keep=False)]
        if not duplicates.empty:
            issues.append(f"Found {len(duplicates)} duplicate IDs")
        
        self.errors.extend(issues)
        return len(issues) == 0
    
    def detect_date_anomalies(self):
        """Detect invalid dates and date logic errors"""
        anomalies = []
        
        for idx, row in self.df.iterrows():
            task_id = row['ID']
            task_name = row['Task_Name']
            start = row['Start_Date']
            finish = row['Finish_Date']
            duration = row['Duration_Days']
            deadline = row['Deadline']
            
            # Check 1: Null dates for non-zero duration tasks
            if duration > 0 and (pd.isna(start) or pd.isna(finish)):
                anomalies.append({
                    'ID': task_id,
                    'Task': task_name,
                    'Type': 'Missing Date',
                    'Description': 'Task has duration but missing start/finish date'
                })
            
            # Check 2: Start date after finish date
            if pd.notna(start) and pd.notna(finish) and start > finish:
                anomalies.append({
                    'ID': task_id,
                    'Task': task_name,
                    'Type': 'Date Logic Error',
                    'Description': f'Start date ({start.date()}) is after finish date ({finish.date()})'
                })
            
            # Check 3: Duration mismatch
            if pd.notna(start) and pd.notna(finish) and duration > 0:
                calculated_duration = (finish - start).days
                if abs(calculated_duration - duration) > 1:  # Allow 1 day tolerance
                    anomalies.append({
                        'ID': task_id,
                        'Task': task_name,
                        'Type': 'Duration Mismatch',
                        'Description': f'Recorded duration: {duration} days, Calculated: {calculated_duration} days'
                    })
            
            # Check 4: Invalid deadline dates (like June 31st)
            if pd.notna(deadline):
                # Deadline might have been parsed as NaT if invalid
                pass
            else:
                # Check raw deadline value
                raw_deadline = str(row.get('Deadline', ''))
                if raw_deadline and raw_deadline != 'nan':
                    # Check for impossible dates like June 31, Feb 30, etc.
                    if re.match(r'\d{4}-06-31', raw_deadline):
                        anomalies.append({
                            'ID': task_id,
                            'Task': task_name,
                            'Type': 'Invalid Date',
                            'Description': f'Impossible date: {raw_deadline} (June only has 30 days)'
                        })
        
        return pd.DataFrame(anomalies) if anomalies else pd.DataFrame()
    
    def process(self):
        """Execute full processing pipeline"""
        steps = [
            ('Loading data', self.load_data),
            ('Parsing dates', self.parse_dates),
            ('Splitting predecessors', self.split_predecessors),
            ('Normalizing resources', self.normalize_resources),
            ('Validating data', self.validate_data)
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                print(f"❌ Failed at: {step_name}")
                return False
        
        return True
    
    def get_data(self):
        """Return processed DataFrame"""
        return self.df
    
    def get_errors(self):
        """Return list of errors encountered"""
        return self.errors


if __name__ == "__main__":
    # Test the processor
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        print("✅ Data processing successful")
        print(f"Loaded {len(processor.get_data())} tasks")
        
        # Check for date anomalies
        anomalies = processor.detect_date_anomalies()
        if not anomalies.empty:
            print(f"\n⚠️ Found {len(anomalies)} date anomalies:")
            print(anomalies)
    else:
        print("❌ Data processing failed")
        for error in processor.get_errors():
            print(f"  - {error}")
