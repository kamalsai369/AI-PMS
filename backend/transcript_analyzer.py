"""
Meeting Transcript Analyzer (NLP)
Extracts project insights from meeting transcripts
"""

import re
from datetime import datetime
from collections import defaultdict


class TranscriptAnalyzer:
    """Analyzes meeting transcripts to extract project intelligence"""
    
    def __init__(self, transcript_files):
        self.transcript_files = transcript_files
        self.insights = []
        self.task_mentions = []
        self.resource_mentions = []
        self.events = []
        
    def load_transcript(self, filepath):
        """Load a meeting transcript file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return ""
    
    def extract_metadata(self, content):
        """Extract meeting metadata (date, participants)"""
        metadata = {}
        
        # Extract date
        date_match = re.search(r'\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            metadata['date'] = date_match.group(1)
        
        # Extract participants
        participants_match = re.search(r'\*\*Participants\*\*:\s*(.+)', content)
        if participants_match:
            metadata['participants'] = participants_match.group(1)
        
        # Extract meeting type from header
        header_match = re.search(r'#\s+Meeting Transcript:\s+(.+)', content)
        if header_match:
            metadata['meeting_type'] = header_match.group(1).strip()
        
        return metadata
    
    def extract_task_ids(self, content):
        """Extract task ID references from text"""
        # Look for patterns like "Task 1096", "ID 1315", "IDs 1023 through 1032"
        task_ids = []
        
        # Pattern: Task XXXX or ID XXXX
        single_matches = re.findall(r'(?:Task|ID)\s+(\d{4})', content, re.IGNORECASE)
        task_ids.extend([int(tid) for tid in single_matches])
        
        # Pattern: IDs XXXX through XXXX
        range_matches = re.findall(r'(?:IDs|tasks)\s+(\d{4})\s+through\s+(\d{4})', content, re.IGNORECASE)
        for start, end in range_matches:
            task_ids.extend(range(int(start), int(end) + 1))
        
        # Pattern: 1081 through 1085
        range_matches2 = re.findall(r'(\d{4})\s+through\s+(\d{4})', content)
        for start, end in range_matches2:
            task_ids.extend(range(int(start), int(end) + 1))
        
        return list(set(task_ids))
    
    def extract_delay_mentions(self, content):
        """Extract mentions of delays or problems"""
        delay_keywords = [
            'delay', 'delayed', 'behind', 'late', 'postpone', 'postponed',
            'slip', 'slipped', 'overrun', 'waiting', 'stuck', 'blocked',
            'can\'t', 'cannot', 'won\'t let', 'ghost reference'
        ]
        
        delays = []
        lines = content.split('\n')
        
        for line in lines:
            lower_line = line.lower()
            for keyword in delay_keywords:
                if keyword in lower_line:
                    # Extract task IDs from this line
                    task_ids = self.extract_task_ids(line)
                    
                    delays.append({
                        'text': line.strip(),
                        'keyword': keyword,
                        'task_ids': task_ids
                    })
                    break
        
        return delays
    
    def extract_resource_issues(self, content):
        """Extract resource-related issues (overallocation, conflicts)"""
        resource_keywords = [
            'assigned to', 'over-allocation', 'overload', 'spread thin',
            'can\'t be in', 'simultaneously', 'at once', 'parallel',
            'how am i supposed to', 'magician', 'literally can\'t'
        ]
        
        issues = []
        lines = content.split('\n')
        
        for line in lines:
            lower_line = line.lower()
            for keyword in resource_keywords:
                if keyword in lower_line:
                    # Extract task IDs and resources
                    task_ids = self.extract_task_ids(line)
                    
                    issues.append({
                        'text': line.strip(),
                        'keyword': keyword,
                        'task_ids': task_ids,
                        'type': 'Resource Overallocation'
                    })
                    break
        
        return issues
    
    def extract_data_quality_issues(self, content):
        """Extract mentions of data errors (invalid dates, missing refs)"""
        quality_keywords = [
            'typo', 'error', 'wrong', 'incorrect', 'invalid', 'doesn\'t exist',
            'ghost', 'missing', 'can\'t find', 'june 31', 'weird', 'trust'
        ]
        
        issues = {
            'date_errors': [],
            'reference_errors': [],
            'other_errors': []
        }
        
        lines = content.split('\n')
        
        for line in lines:
            lower_line = line.lower()
            
            # Check for date errors
            if 'june 31' in lower_line or 'june only has 30 days' in lower_line:
                task_ids = self.extract_task_ids(line)
                issues['date_errors'].append({
                    'text': line.strip(),
                    'task_ids': task_ids,
                    'issue_type': 'Invalid Date'
                })
            
            # Check for missing references
            elif 'doesn\'t exist' in lower_line or 'ghost' in lower_line or 'can\'t find' in lower_line:
                task_ids = self.extract_task_ids(line)
                issues['reference_errors'].append({
                    'text': line.strip(),
                    'task_ids': task_ids,
                    'issue_type': 'Missing Reference'
                })
            
            # Other quality issues
            else:
                for keyword in quality_keywords:
                    if keyword in lower_line:
                        task_ids = self.extract_task_ids(line)
                        issues['other_errors'].append({
                            'text': line.strip(),
                            'task_ids': task_ids,
                            'issue_type': 'Data Quality Issue'
                        })
                        break
        
        return issues
    
    def extract_status_updates(self, content):
        """Extract task status mentions"""
        status_keywords = {
            'completed': ['completed', 'finished', 'done'],
            'in_progress': ['in progress', 'working on', 'currently'],
            'delayed': ['delayed', 'behind schedule', 'late'],
            'blocked': ['blocked', 'waiting', 'stuck', 'can\'t proceed']
        }
        
        updates = []
        lines = content.split('\n')
        
        for line in lines:
            lower_line = line.lower()
            for status, keywords in status_keywords.items():
                for keyword in keywords:
                    if keyword in lower_line:
                        task_ids = self.extract_task_ids(line)
                        if task_ids:
                            updates.append({
                                'text': line.strip(),
                                'status': status,
                                'task_ids': task_ids
                            })
                        break
        
        return updates
    
    def analyze_transcript(self, filepath):
        """Comprehensive analysis of a single transcript"""
        content = self.load_transcript(filepath)
        if not content:
            return None
        
        metadata = self.extract_metadata(content)
        
        analysis = {
            'file': filepath,
            'metadata': metadata,
            'task_ids_mentioned': self.extract_task_ids(content),
            'delays': self.extract_delay_mentions(content),
            'resource_issues': self.extract_resource_issues(content),
            'data_quality_issues': self.extract_data_quality_issues(content),
            'status_updates': self.extract_status_updates(content)
        }
        
        return analysis
    
    def analyze_all(self):
        """Analyze all transcript files"""
        all_analyses = []
        
        for filepath in self.transcript_files:
            print(f"Analyzing: {filepath}")
            analysis = self.analyze_transcript(filepath)
            if analysis:
                all_analyses.append(analysis)
        
        return all_analyses
    
    def get_consolidated_insights(self, analyses):
        """Consolidate insights from all transcripts"""
        insights = {
            'total_transcripts': len(analyses),
            'unique_tasks_mentioned': set(),
            'delay_mentions': [],
            'resource_conflicts': [],
            'data_errors': {
                'date_errors': [],
                'reference_errors': [],
                'other': []
            },
            'status_updates': []
        }
        
        for analysis in analyses:
            # Collect unique task IDs
            insights['unique_tasks_mentioned'].update(analysis['task_ids_mentioned'])
            
            # Collect delays
            for delay in analysis['delays']:
                insights['delay_mentions'].append({
                    'meeting': analysis['metadata'].get('meeting_type', 'Unknown'),
                    'date': analysis['metadata'].get('date', 'Unknown'),
                    'description': delay['text'],
                    'task_ids': delay['task_ids']
                })
            
            # Collect resource issues
            for issue in analysis['resource_issues']:
                insights['resource_conflicts'].append({
                    'meeting': analysis['metadata'].get('meeting_type', 'Unknown'),
                    'date': analysis['metadata'].get('date', 'Unknown'),
                    'description': issue['text'],
                    'task_ids': issue['task_ids']
                })
            
            # Collect data errors
            dq_issues = analysis['data_quality_issues']
            insights['data_errors']['date_errors'].extend([
                {
                    'meeting': analysis['metadata'].get('meeting_type', 'Unknown'),
                    'description': err['text'],
                    'task_ids': err['task_ids']
                }
                for err in dq_issues['date_errors']
            ])
            
            insights['data_errors']['reference_errors'].extend([
                {
                    'meeting': analysis['metadata'].get('meeting_type', 'Unknown'),
                    'description': err['text'],
                    'task_ids': err['task_ids']
                }
                for err in dq_issues['reference_errors']
            ])
        
        insights['unique_tasks_mentioned'] = list(insights['unique_tasks_mentioned'])
        
        return insights


if __name__ == "__main__":
    transcript_files = [
        "progress_review_meeting_transcript.md",
        "design_coordination_meeting_transcript.md",
        "safety_readiness_briefing_transcript.md"
    ]
    
    analyzer = TranscriptAnalyzer(transcript_files)
    analyses = analyzer.analyze_all()
    
    print("\n✅ Transcript analysis complete")
    
    insights = analyzer.get_consolidated_insights(analyses)
    print(f"\n📊 Consolidated Insights:")
    print(f"  Total Transcripts: {insights['total_transcripts']}")
    print(f"  Unique Tasks Mentioned: {len(insights['unique_tasks_mentioned'])}")
    print(f"  Delay Mentions: {len(insights['delay_mentions'])}")
    print(f"  Resource Conflicts: {len(insights['resource_conflicts'])}")
    print(f"  Data Errors: {len(insights['data_errors']['date_errors']) + len(insights['data_errors']['reference_errors'])}")
    
    if insights['delay_mentions']:
        print(f"\n⚠️ Sample Delay Mentions:")
        for mention in insights['delay_mentions'][:3]:
            print(f"  [{mention['meeting']}] Tasks {mention['task_ids']}: {mention['description'][:80]}...")
