"""
LLM-Powered Meeting Transcript Processor
Extracts action items, prioritizes tasks, detects conflicts
"""

import os
import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import google.generativeai as genai


class LLMProcessor:
    """
    Intelligent meeting transcript analyzer using Gemini LLM
    """
    
    def __init__(self, provider: str = "gemini"):
        """
        Initialize LLM processor with Gemini
        
        Args:
            provider: LLM provider (only "gemini" is supported)
        """
        self.provider = "gemini"  # Force Gemini only
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.available = True
                print("✅ Gemini API connected successfully")
            except Exception as e:
                self.available = False
                print(f"⚠️  Gemini API error: {e}. Using rule-based fallback.")
        else:
            self.available = False
            print("⚠️  No GEMINI_API_KEY found. Using rule-based fallback.")
    
    
    def get_status(self) -> str:
        """Get LLM availability status"""
        if self.available:
            return f"Connected ({self.provider})"
        return "Fallback Mode (No API Key)"
    
    
    def process_transcript(self, transcript: str, meeting_title: str, meeting_date: str) -> Dict[str, Any]:
        """
        Process meeting transcript and extract intelligence
        
        Args:
            transcript: Raw meeting transcript text
            meeting_title: Title of the meeting
            meeting_date: Date of meeting
            
        Returns:
            Dictionary with action items, conflicts, summary, etc.
        """
        if self.available and self.provider == "gemini":
            return self._process_with_gemini(transcript, meeting_title, meeting_date)
        else:
            return self._process_with_rules(transcript, meeting_title, meeting_date)
    
    
    def _process_with_gemini(self, transcript: str, meeting_title: str, meeting_date: str) -> Dict[str, Any]:
        """Process transcript using Google Gemini"""
        
        prompt = f"""You are an AI project management assistant analyzing a meeting transcript.

Meeting: {meeting_title}
Date: {meeting_date}

Transcript:
{transcript}

Analyze this transcript and provide a structured JSON response with:

1. **action_items**: List of specific tasks mentioned
   - task: Clear description of the action item
   - assignee: Person responsible (extract from context)
   - deadline: Any deadline mentioned (format: YYYY-MM-DD or "Not specified")
   - priority_score: Score 1-10 based on urgency and impact
   - urgency: "Low", "Medium", "High", or "Critical"
   - impact: "Low", "Medium", "High", or "Critical"
   - context: Brief context from the meeting

2. **conflicts**: Any conflicting information detected
   - type: "Date Conflict", "Resource Conflict", "Scope Conflict", etc.
   - description: What's conflicting
   - parties: People involved in the conflict
   - conflicting_info: Dictionary of conflicting details
   - severity: "Low", "Medium", "High", or "Critical"

3. **summary**: 2-3 sentence meeting summary

4. **key_decisions**: List of important decisions made

5. **risks_identified**: List of risks or blockers mentioned

Return ONLY valid JSON, no other text.
"""

        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            data = json.loads(result_text.strip())
            
            # Add metadata
            data['meeting_title'] = meeting_title
            data['meeting_date'] = meeting_date
            data['total_action_items'] = len(data.get('action_items', []))
            data['high_priority_count'] = sum(1 for item in data.get('action_items', []) 
                                              if item.get('priority_score', 0) >= 7)
            
            return data
        
        except Exception as e:
            print(f"⚠️  Gemini processing failed: {e}. Using fallback.")
            return self._process_with_rules(transcript, meeting_title, meeting_date)
    
    
    def _process_with_rules(self, transcript: str, meeting_title: str, meeting_date: str) -> Dict[str, Any]:
        """
        Fallback rule-based processing when LLM is unavailable
        Uses pattern matching and heuristics
        """
        
        action_items = self._extract_action_items_rules(transcript)
        conflicts = self._detect_conflicts_rules(transcript)
        summary = self._generate_summary_rules(transcript)
        key_decisions = self._extract_decisions_rules(transcript)
        risks = self._extract_risks_rules(transcript)
        
        return {
            "meeting_title": meeting_title,
            "meeting_date": meeting_date,
            "action_items": action_items,
            "conflicts": conflicts,
            "summary": summary,
            "key_decisions": key_decisions,
            "risks_identified": risks,
            "total_action_items": len(action_items),
            "high_priority_count": sum(1 for item in action_items if item['priority_score'] >= 7)
        }
    
    
    def _extract_action_items_rules(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items using pattern matching"""
        
        action_items = []
        lines = transcript.split('\n')
        
        # Patterns for action items
        action_patterns = [
            r'(?:need to|should|must|will|going to|action item:?)\s+(.+?)(?:\.|$)',
            r'(?:TODO|Action|Task):\s*(.+?)(?:\.|$)',
            r'(\w+)\s+will\s+(.+?)(?:\.|$)',
            r'(\w+)\s+needs? to\s+(.+?)(?:\.|$)',
        ]
        
        # Person name pattern
        person_pattern = r'\*\*(\w+)\*\*:'
        
        current_speaker = "Unknown"
        
        for line in lines:
            # Track current speaker
            speaker_match = re.search(person_pattern, line)
            if speaker_match:
                current_speaker = speaker_match.group(1)
            
            # Look for action items
            for pattern in action_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    task_text = match.group(1).strip()
                    
                    if len(task_text) > 10:  # Meaningful length
                        # Extract assignee
                        assignee = current_speaker
                        will_match = re.search(r'(\w+)\s+will\s+', task_text)
                        if will_match:
                            assignee = will_match.group(1)
                        
                        # Extract deadline
                        deadline = self._extract_deadline(line)
                        
                        # Calculate priority
                        priority = self._calculate_priority_rules(line, task_text)
                        
                        # Determine urgency and impact
                        urgency, impact = self._determine_urgency_impact(priority)
                        
                        action_items.append({
                            "task": task_text[:200],  # Limit length
                            "assignee": assignee,
                            "deadline": deadline,
                            "priority_score": priority,
                            "urgency": urgency,
                            "impact": impact,
                            "context": line.strip()[:150]
                        })
        
        # Remove duplicates
        unique_items = []
        seen_tasks = set()
        for item in action_items:
            task_key = item['task'].lower()[:50]
            if task_key not in seen_tasks:
                seen_tasks.add(task_key)
                unique_items.append(item)
        
        return unique_items[:20]  # Limit to 20 items
    
    
    def _extract_deadline(self, text: str) -> Optional[str]:
        """Extract deadline from text"""
        
        # Date patterns
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(?:by|before|due)\s+(.+?)(?:\.|,|$)',
            r'deadline[:\s]+(.+?)(?:\.|,|$)',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Not specified"
    
    
    def _calculate_priority_rules(self, context: str, task: str) -> int:
        """Calculate priority score 1-10 based on keywords"""
        
        score = 5  # Default medium
        
        context_lower = (context + " " + task).lower()
        
        # High urgency keywords
        if any(word in context_lower for word in ['critical', 'urgent', 'immediately', 'asap', 'blocker']):
            score += 3
        
        # Medium urgency
        if any(word in context_lower for word in ['important', 'priority', 'soon', 'deadline']):
            score += 2
        
        # High impact keywords
        if any(word in context_lower for word in ['budget', 'safety', 'compliance', 'legal', 'delay']):
            score += 2
        
        # Risk keywords
        if any(word in context_lower for word in ['risk', 'problem', 'issue', 'concern']):
            score += 1
        
        # Lower priority indicators
        if any(word in context_lower for word in ['maybe', 'someday', 'whenever', 'optional']):
            score -= 2
        
        return max(1, min(10, score))
    
    
    def _determine_urgency_impact(self, priority_score: int) -> tuple:
        """Determine urgency and impact from priority score"""
        
        if priority_score >= 9:
            return "Critical", "Critical"
        elif priority_score >= 7:
            return "High", "High"
        elif priority_score >= 5:
            return "Medium", "Medium"
        else:
            return "Low", "Low"
    
    
    def _detect_conflicts_rules(self, transcript: str) -> List[Dict[str, Any]]:
        """Detect conflicting information using pattern matching"""
        
        conflicts = []
        lines = transcript.split('\n')
        
        # Track mentions of dates, numbers, assignments
        date_mentions = {}
        assignment_mentions = {}
        
        person_pattern = r'\*\*(\w+)\*\*:'
        date_pattern = r'\d{4}-\d{2}-\d{2}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'
        task_pattern = r'[Tt]ask\s+(\d+)'
        
        for line in lines:
            speaker_match = re.search(person_pattern, line)
            if not speaker_match:
                continue
            
            speaker = speaker_match.group(1)
            
            # Check for task-date associations
            task_match = re.search(task_pattern, line)
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            
            if task_match and date_match:
                task_id = task_match.group(1)
                date_str = date_match.group(0)
                
                if task_id in date_mentions:
                    if date_mentions[task_id]['date'] != date_str:
                        conflicts.append({
                            "type": "Date Conflict",
                            "description": f"Different dates mentioned for Task {task_id}",
                            "parties": [date_mentions[task_id]['speaker'], speaker],
                            "conflicting_info": {
                                date_mentions[task_id]['speaker']: date_mentions[task_id]['date'],
                                speaker: date_str
                            },
                            "severity": "High"
                        })
                else:
                    date_mentions[task_id] = {"speaker": speaker, "date": date_str}
        
        # Look for explicit conflict keywords
        conflict_keywords = ['conflict', 'disagree', 'different', 'contradict', 'but actually', 'however']
        for line in lines:
            if any(keyword in line.lower() for keyword in conflict_keywords):
                speaker_match = re.search(person_pattern, line)
                speaker = speaker_match.group(1) if speaker_match else "Unknown"
                
                conflicts.append({
                    "type": "Discussion Conflict",
                    "description": "Potential disagreement or conflicting information",
                    "parties": [speaker],
                    "conflicting_info": {"context": line.strip()[:150]},
                    "severity": "Medium"
                })
        
        return conflicts[:10]  # Limit conflicts
    
    
    def _generate_summary_rules(self, transcript: str) -> str:
        """Generate simple summary"""
        
        lines = [l.strip() for l in transcript.split('\n') if l.strip() and not l.startswith('**')]
        
        if len(lines) > 3:
            return f"Meeting discussion covered multiple topics. {lines[0][:100]}... Key focus areas were discussed by the team."
        else:
            return "Meeting transcript analyzed. Action items and decisions extracted."
    
    
    def _extract_decisions_rules(self, transcript: str) -> List[str]:
        """Extract key decisions"""
        
        decisions = []
        decision_keywords = ['decided', 'agreed', 'approved', 'decision', 'finalized', 'will go with']
        
        lines = transcript.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in decision_keywords):
                decisions.append(line.strip()[:200])
        
        return decisions[:5]
    
    
    def _extract_risks_rules(self, transcript: str) -> List[str]:
        """Extract risks and blockers"""
        
        risks = []
        risk_keywords = ['risk', 'blocker', 'blocked', 'problem', 'issue', 'delay', 'concern', 'worry']
        
        lines = transcript.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in risk_keywords):
                risks.append(line.strip()[:200])
        
        return risks[:5]
