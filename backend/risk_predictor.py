"""
Risk Prediction Model
Predicts task delay probability using ML features
"""

import pandas as pd
import numpy as np
from datetime import datetime


class RiskPredictor:
    """Predicts delay risk for project tasks"""
    
    def __init__(self, df, dependency_analyzer, resource_analyzer):
        self.df = df
        self.dependency_analyzer = dependency_analyzer
        self.resource_analyzer = resource_analyzer
        
    def extract_features(self):
        """Extract features for risk prediction"""
        features = []
        
        for idx, row in self.df.iterrows():
            task_id = row['ID']
            
            # Feature 1: Task duration (longer tasks = higher risk)
            duration = row['Duration_Days']
            
            # Feature 2: Number of dependencies
            dep_info = self.dependency_analyzer.analyze_task_dependencies(task_id)
            num_predecessors = dep_info['total_predecessors'] if dep_info else 0
            num_successors = dep_info['total_successors'] if dep_info else 0
            
            # Feature 3: Task complexity (based on WBS level)
            wbs_level = len(str(row['WBS_Code']).split('.'))
            
            # Feature 4: Is on critical path (if computable)
            # (Simplified: assume tasks with many successors are critical)
            is_critical = 1 if num_successors >= 3 else 0
            
            # Feature 5: Has tight deadline
            has_deadline = 1 if pd.notna(row['Deadline']) else 0
            
            # Feature 6: Current status indicates risk
            status = row['Status']
            status_risk = {
                'Completed': 0,
                'In Progress': 0.3,
                'Not Started': 0.5,
                'Delayed': 1.0,
                'On Hold': 0.8
            }.get(status, 0.5)
            
            # Feature 7: Resource type (some resources more overloaded)
            resource = row['Resources']
            
            # Feature 8: Task is milestone
            is_milestone = 1 if row['Milestone'] == 'Yes' else 0
            
            # Feature 9: Time until deadline (if exists)
            days_to_deadline = 0
            if pd.notna(row['Deadline']) and pd.notna(row['Finish_Date']):
                days_to_deadline = (row['Deadline'] - row['Finish_Date']).days
            
            features.append({
                'Task_ID': task_id,
                'Task_Name': row['Task_Name'],
                'Duration': duration,
                'Num_Predecessors': num_predecessors,
                'Num_Successors': num_successors,
                'WBS_Level': wbs_level,
                'Is_Critical': is_critical,
                'Has_Deadline': has_deadline,
                'Status_Risk': status_risk,
                'Resource': resource,
                'Is_Milestone': is_milestone,
                'Days_To_Deadline': days_to_deadline,
                'Current_Status': status
            })
        
        return pd.DataFrame(features)
    
    def calculate_risk_score(self, features_df):
        """Calculate risk score using rule-based approach"""
        
        def compute_score(row):
            score = 0.0
            
            # Duration risk (normalized to 0-20 points)
            duration_risk = min(row['Duration'] / 30, 1.0) * 20
            score += duration_risk
            
            # Dependency complexity (0-15 points)
            dep_risk = min((row['Num_Predecessors'] + row['Num_Successors']) / 5, 1.0) * 15
            score += dep_risk
            
            # Status-based risk (0-25 points)
            score += row['Status_Risk'] * 25
            
            # Critical path bonus (0-10 points)
            score += row['Is_Critical'] * 10
            
            # Milestone importance (0-10 points)
            score += row['Is_Milestone'] * 10
            
            # Deadline pressure (0-20 points)
            if row['Has_Deadline']:
                if row['Days_To_Deadline'] < 0:
                    score += 20  # Already past deadline
                elif row['Days_To_Deadline'] < 30:
                    score += 15  # Very tight
                elif row['Days_To_Deadline'] < 60:
                    score += 10  # Moderately tight
            
            # Normalize to 0-100 scale
            return min(score, 100)
        
        features_df['Risk_Score'] = features_df.apply(compute_score, axis=1)
        
        # Convert to percentage and risk level
        features_df['Risk_Percentage'] = features_df['Risk_Score']
        features_df['Risk_Level'] = features_df['Risk_Score'].apply(self._categorize_risk)
        
        return features_df
    
    def _categorize_risk(self, score):
        """Categorize risk score into levels"""
        if score >= 75:
            return 'Critical'
        elif score >= 60:
            return 'High'
        elif score >= 40:
            return 'Medium'
        elif score >= 20:
            return 'Low'
        else:
            return 'Very Low'
    
    def predict_delays(self):
        """Generate delay risk predictions for all tasks"""
        features = self.extract_features()
        predictions = self.calculate_risk_score(features)
        
        return predictions
    
    def get_high_risk_tasks(self, predictions, min_risk_score=60):
        """Get tasks with high delay risk"""
        high_risk = predictions[predictions['Risk_Score'] >= min_risk_score].copy()
        high_risk = high_risk.sort_values('Risk_Score', ascending=False)
        
        return high_risk[['Task_ID', 'Task_Name', 'Risk_Score', 'Risk_Level', 
                          'Current_Status', 'Duration', 'Num_Predecessors', 
                          'Num_Successors', 'Is_Milestone']]
    
    def get_risk_distribution(self, predictions):
        """Get distribution of risk across tasks"""
        distribution = predictions['Risk_Level'].value_counts().to_dict()
        
        return {
            'Critical': distribution.get('Critical', 0),
            'High': distribution.get('High', 0),
            'Medium': distribution.get('Medium', 0),
            'Low': distribution.get('Low', 0),
            'Very Low': distribution.get('Very Low', 0)
        }
    
    def analyze_risk_by_phase(self, predictions):
        """Analyze risk grouped by project phase (WBS Level 2)"""
        # Add WBS code from original df
        predictions_with_wbs = predictions.merge(
            self.df[['ID', 'WBS_Code']], 
            left_on='Task_ID', 
            right_on='ID',
            how='left'
        )
        
        # Extract phase (first two levels of WBS)
        def get_phase(wbs_code):
            parts = str(wbs_code).split('.')
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
            return wbs_code
        
        predictions_with_wbs['Phase'] = predictions_with_wbs['WBS_Code'].apply(get_phase)
        
        # Aggregate by phase
        phase_risk = predictions_with_wbs.groupby('Phase').agg({
            'Risk_Score': ['mean', 'max', 'count'],
            'Task_ID': 'count'
        }).round(2)
        
        phase_risk.columns = ['Avg_Risk_Score', 'Max_Risk_Score', 'Task_Count', 'Total_Tasks']
        phase_risk = phase_risk.sort_values('Avg_Risk_Score', ascending=False)
        
        return phase_risk
    
    def recommend_actions(self, high_risk_tasks):
        """Generate recommendations for high-risk tasks"""
        recommendations = []
        
        for idx, task in high_risk_tasks.iterrows():
            actions = []
            
            # Based on duration
            if task['Duration'] > 90:
                actions.append("Consider breaking task into smaller subtasks")
            
            # Based on dependencies
            if task['Num_Predecessors'] >= 3:
                actions.append("Review predecessor dependencies for potential parallelization")
            
            if task['Num_Successors'] >= 3:
                actions.append("Critical path task - prioritize resources and monitoring")
            
            # Based on status
            if task['Current_Status'] == 'Not Started' and task['Risk_Score'] >= 70:
                actions.append("URGENT: Task not started but high risk - initiate immediately")
            
            if task['Current_Status'] == 'In Progress' and task['Risk_Score'] >= 75:
                actions.append("Increase monitoring frequency and consider additional resources")
            
            # Based on milestone
            if task['Is_Milestone'] == 1:
                actions.append("Milestone task - ensure executive visibility")
            
            if not actions:
                actions.append("Monitor progress closely")
            
            recommendations.append({
                'Task_ID': task['Task_ID'],
                'Task_Name': task['Task_Name'],
                'Risk_Level': task['Risk_Level'],
                'Priority_Actions': actions
            })
        
        return recommendations


if __name__ == "__main__":
    from data_processor import DataProcessor
    from dependency_analyzer import DependencyAnalyzer
    from resource_analyzer import ResourceAnalyzer
    
    # Load data
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        
        # Initialize analyzers
        dep_analyzer = DependencyAnalyzer(df)
        dep_analyzer.build_dependency_graph()
        
        res_analyzer = ResourceAnalyzer(df)
        
        # Initialize risk predictor
        predictor = RiskPredictor(df, dep_analyzer, res_analyzer)
        
        print("✅ Generating risk predictions...")
        predictions = predictor.predict_delays()
        
        # Get risk distribution
        distribution = predictor.get_risk_distribution(predictions)
        print(f"\n📊 Risk Distribution:")
        for level, count in distribution.items():
            print(f"  {level}: {count} tasks")
        
        # Get high-risk tasks
        high_risk = predictor.get_high_risk_tasks(predictions, min_risk_score=70)
        print(f"\n⚠️ High-Risk Tasks (Score >= 70): {len(high_risk)}")
        
        if not high_risk.empty:
            print("\nTop 5 Highest Risk Tasks:")
            print(high_risk.head(5)[['Task_ID', 'Task_Name', 'Risk_Score', 'Risk_Level']].to_string(index=False))
        
        # Get recommendations
        if not high_risk.empty:
            recommendations = predictor.recommend_actions(high_risk.head(10))
            print(f"\n💡 Sample Recommendations:")
            for rec in recommendations[:3]:
                print(f"\n  Task {rec['Task_ID']}: {rec['Task_Name']}")
                print(f"  Risk Level: {rec['Risk_Level']}")
                for action in rec['Priority_Actions']:
                    print(f"    • {action}")
