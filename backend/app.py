"""
AI-PMS Backend API
FastAPI server with LLM-powered transcript analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import json
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import existing analyzers
import sys
sys.path.append(os.path.dirname(__file__))

from llm_processor import LLMProcessor
from data_processor import DataProcessor

app = FastAPI(title="AI-PMS API", version="2.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM processor
llm_processor = LLMProcessor()


# Request/Response Models
class TranscriptRequest(BaseModel):
    transcript: str
    meeting_title: Optional[str] = "Untitled Meeting"
    meeting_date: Optional[str] = None


class ActionItem(BaseModel):
    task: str
    assignee: str
    deadline: Optional[str]
    priority_score: int
    urgency: str
    impact: str
    context: str


class Conflict(BaseModel):
    type: str
    description: str
    parties: List[str]
    conflicting_info: Dict[str, Any]
    severity: str


class TranscriptResponse(BaseModel):
    meeting_title: str
    meeting_date: str
    action_items: List[ActionItem]
    conflicts: List[Conflict]
    summary: str
    key_decisions: List[str]
    risks_identified: List[str]
    total_action_items: int
    high_priority_count: int


class ProjectStatusResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    overallocated_resources: int
    critical_issues: int
    schedule_health: str


# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "running",
        "service": "AI-PMS Backend",
        "version": "2.0",
        "llm_status": llm_processor.get_status()
    }


@app.post("/api/analyze-transcript", response_model=TranscriptResponse)
async def analyze_transcript(request: TranscriptRequest):
    """
    Process meeting transcript with LLM
    Extracts action items, detects conflicts, prioritizes tasks
    """
    try:
        # Process with LLM
        result = llm_processor.process_transcript(
            transcript=request.transcript,
            meeting_title=request.meeting_title,
            meeting_date=request.meeting_date or datetime.now().strftime("%Y-%m-%d")
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.get("/api/project-status", response_model=ProjectStatusResponse)
async def get_project_status():
    """
    Get overall project health status
    """
    try:
        # Load WBS data
        csv_path = os.path.join(os.path.dirname(__file__), "../datasets/metro_rail_wbs_data.csv")
        processor = DataProcessor(csv_path)
        
        if not processor.process():
            raise HTTPException(status_code=500, detail="Failed to load project data")
        
        df = processor.get_data()
        
        # Calculate metrics dynamically
        total_tasks = len(df)
        completed = len(df[df['Status'] == 'Completed'])
        in_progress = len(df[df['Status'] == 'In Progress'])
        
        # Calculate actual resource conflicts
        from resource_analyzer import ResourceAnalyzer
        res_analyzer = ResourceAnalyzer(df)
        overload = res_analyzer.detect_overallocation()
        overallocated_count = len(overload)
        
        # Calculate actual critical issues
        from dependency_analyzer import DependencyAnalyzer
        dep_analyzer = DependencyAnalyzer(df)
        dep_analyzer.build_dependency_graph()
        validation = dep_analyzer.validate_all()
        critical_issues_count = validation['total_issues']
        
        # Determine health
        completion_rate = (completed / total_tasks) * 100 if total_tasks > 0 else 0
        if completion_rate >= 90:
            health = "Excellent"
        elif completion_rate >= 70:
            health = "Good"
        elif completion_rate >= 50:
            health = "At Risk"
        else:
            health = "Critical"
        
        return ProjectStatusResponse(
            total_tasks=total_tasks,
            completed_tasks=completed,
            in_progress_tasks=in_progress,
            overallocated_resources=overallocated_count,
            critical_issues=critical_issues_count,
            schedule_health=health
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/high-priority-tasks")
async def get_high_priority_tasks():
    """
    Get tasks with high priority/risk
    """
    try:
        from risk_predictor import RiskPredictor
        from dependency_analyzer import DependencyAnalyzer
        from resource_analyzer import ResourceAnalyzer
        
        csv_path = os.path.join(os.path.dirname(__file__), "../datasets/metro_rail_wbs_data.csv")
        processor = DataProcessor(csv_path)
        
        if not processor.process():
            raise HTTPException(status_code=500, detail="Failed to load data")
        
        df = processor.get_data()
        
        # Initialize analyzers for risk prediction
        dep_analyzer = DependencyAnalyzer(df)
        dep_analyzer.build_dependency_graph()
        res_analyzer = ResourceAnalyzer(df)
        risk_predictor = RiskPredictor(df, dep_analyzer, res_analyzer)
        
        # Calculate risk scores for all tasks
        features_df = risk_predictor.extract_features()
        scores_df = risk_predictor.calculate_risk_score(features_df)
        
        # Filter critical tasks and merge with risk scores
        critical_tasks = df[df['Status'].isin(['Not Started', 'In Progress', 'Delayed'])].copy()
        critical_tasks = critical_tasks.merge(scores_df[['Task_ID', 'Risk_Score']], left_on='ID', right_on='Task_ID', how='left')
        critical_tasks = critical_tasks.sort_values('Risk_Score', ascending=False).head(20)
        
        tasks = []
        for _, row in critical_tasks.iterrows():
            tasks.append({
                "id": int(row['ID']),
                "name": row['Task_Name'],
                "status": row['Status'],
                "assignee": row['Resources'],
                "start_date": str(row['Start_Date']) if pd.notna(row['Start_Date']) else None,
                "end_date": str(row['Finish_Date']) if pd.notna(row['Finish_Date']) else None,
                "duration": int(row['Duration_Days']) if pd.notna(row['Duration_Days']) else 0,
                "priority_score": round(float(row['Risk_Score']), 1) if pd.notna(row.get('Risk_Score')) else 5.0
            })
        
        # Get all tasks for dependency graph (limit to 50 for performance)
        all_tasks = []
        for _, row in df.head(50).iterrows():
            all_tasks.append({
                "task_id": int(row['ID']),
                "task_name": row['Task_Name'],
                "status": row['Status'],
                "wbs_code": row['WBS_Code'],
                "predecessors": row['Predecessors'] if pd.notna(row['Predecessors']) else None,
                "start_date": str(row['Start_Date']) if pd.notna(row['Start_Date']) else None,
                "end_date": str(row['Finish_Date']) if pd.notna(row['Finish_Date']) else None
            })
        
        return {
            "tasks": tasks, 
            "count": len(tasks),
            "all_tasks": all_tasks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/resource-conflicts")
async def get_resource_conflicts():
    """
    Get resource over-allocation issues and aggregated resource allocation
    """
    try:
        from resource_analyzer import ResourceAnalyzer
        
        csv_path = os.path.join(os.path.dirname(__file__), "../datasets/metro_rail_wbs_data.csv")
        processor = DataProcessor(csv_path)
        
        if not processor.process():
            raise HTTPException(status_code=500, detail="Failed to load data")
        
        df = processor.get_data()
        analyzer = ResourceAnalyzer(df)
        
        overload = analyzer.detect_overallocation()
        
        # Get diverse conflicts - sample from different resources to avoid showing same resource repeatedly
        conflicts = []
        seen_resources = set()
        max_per_resource = 4  # Max conflicts to show per resource
        resource_counts = {}
        
        # Add diversity by limiting repeats of same resource
        for _, row in overload.iterrows():
            resource = row['Resource']
            
            # Skip if we already have max conflicts from this resource
            if resource_counts.get(resource, 0) >= max_per_resource:
                continue
            
            task_names = [t['name'] for t in row['Tasks']]
            
            # Add context to resource name if it's repeated
            display_resource = resource
            if resource_counts.get(resource, 0) > 0:
                # Add context based on task types
                task_keywords = ' '.join(task_names).lower()
                if 'station' in task_keywords:
                    display_resource = f"{resource} (Station Works)"
                elif 'tunnel' in task_keywords or 'underground' in task_keywords:
                    display_resource = f"{resource} (Tunnel Construction)"
                elif 'piling' in task_keywords or 'foundation' in task_keywords:
                    display_resource = f"{resource} (Foundation Works)"
                elif 'track' in task_keywords or 'alignment' in task_keywords:
                    display_resource = f"{resource} (Track Installation)"
                else:
                    display_resource = f"{resource} (Team {resource_counts.get(resource, 0) + 1})"
            
            conflicts.append({
                "date": row['Date'],
                "resource": display_resource,
                "task_count": int(row['Task_Count']),
                "severity": row['Severity'],
                "overload_percentage": round(((row['Task_Count'] / 4) - 1) * 100, 1),
                "tasks": task_names
            })
            
            resource_counts[resource] = resource_counts.get(resource, 0) + 1
            seen_resources.add(resource)
            
            # Stop after collecting enough diverse conflicts
            if len(conflicts) >= 20:
                break
        
        # Aggregate resource allocation (for heatmap) - average tasks per resource
        workload_df = analyzer.calculate_daily_workload()
        resource_avg = workload_df.groupby('Resource')['Task_Count'].mean().reset_index()
        resource_avg.columns = ['resource', 'avg_task_count']
        resource_avg = resource_avg.sort_values('avg_task_count', ascending=False)
        
        resource_allocation = []
        for _, row in resource_avg.iterrows():
            resource_allocation.append({
                "resource": row['resource'],
                "taskCount": round(float(row['avg_task_count']), 1)
            })
        
        return {
            "conflicts": conflicts, 
            "total_count": len(overload),
            "resource_allocation": resource_allocation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meeting-insights")
async def get_meeting_insights():
    """
    Get insights from previously analyzed meeting transcripts
    """
    try:
        from transcript_analyzer import TranscriptAnalyzer
        
        datasets_path = os.path.join(os.path.dirname(__file__), "../datasets")
        transcript_files = [
            os.path.join(datasets_path, "progress_review_meeting_transcript.md"),
            os.path.join(datasets_path, "design_coordination_meeting_transcript.md"),
            os.path.join(datasets_path, "safety_readiness_briefing_transcript.md")
        ]
        
        analyzer = TranscriptAnalyzer(transcript_files)
        analyses = analyzer.analyze_all()
        insights = analyzer.get_consolidated_insights(analyses)
        
        return {
            "total_meetings": insights['total_transcripts'],
            "tasks_mentioned": list(insights['unique_tasks_mentioned']),
            "delay_mentions": insights['delay_mentions'][:5],
            "resource_conflicts": insights['resource_conflicts'][:5],
            "data_errors": {
                "date_errors": insights['data_errors']['date_errors'],
                "reference_errors": insights['data_errors']['reference_errors']
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sample-transcripts")
async def get_sample_transcripts():
    """
    Get list of available sample transcripts from datasets folder
    """
    try:
        datasets_path = os.path.join(os.path.dirname(__file__), "../datasets")
        transcript_files = [
            "progress_review_meeting_transcript.md",
            "design_coordination_meeting_transcript.md",
            "safety_readiness_briefing_transcript.md"
        ]
        
        samples = []
        for filename in transcript_files:
            filepath = os.path.join(datasets_path, filename)
            if os.path.exists(filepath):
                # Extract title from filename
                title = filename.replace("_", " ").replace(".md", "").title()
                samples.append({
                    "filename": filename,
                    "title": title
                })
        
        return {"transcripts": samples}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sample-transcripts/{filename}")
async def get_sample_transcript(filename: str):
    """
    Load content of a specific sample transcript
    """
    try:
        datasets_path = os.path.join(os.path.dirname(__file__), "../datasets")
        filepath = os.path.join(datasets_path, filename)
        
        # Security: only allow specific transcript files
        allowed_files = [
            "progress_review_meeting_transcript.md",
            "design_coordination_meeting_transcript.md",
            "safety_readiness_briefing_transcript.md"
        ]
        
        if filename not in allowed_files:
            raise HTTPException(status_code=403, detail="Access to this file is not allowed")
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Transcript file not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title = filename.replace("_", " ").replace(".md", "").title()
        
        return {
            "filename": filename,
            "title": title,
            "content": content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
