"""
WBS Hierarchy Engine
Builds and analyzes project hierarchy structure
"""

import pandas as pd
import networkx as nx
from collections import defaultdict


class WBSHierarchy:
    """Manages WBS hierarchical structure"""
    
    def __init__(self, df):
        self.df = df
        self.hierarchy_tree = defaultdict(list)
        self.level_map = {}
        
    def parse_wbs_structure(self):
        """Parse WBS codes into hierarchical levels"""
        for idx, row in self.df.iterrows():
            wbs_code = str(row['WBS_Code'])
            task_id = row['ID']
            task_name = row['Task_Name']
            
            # Determine hierarchy level based on WBS code depth
            level = len(wbs_code.split('.'))
            
            self.level_map[task_id] = {
                'wbs_code': wbs_code,
                'level': level,
                'name': task_name,
                'parent': self._get_parent_wbs(wbs_code)
            }
        
        return True
    
    def _get_parent_wbs(self, wbs_code):
        """Get parent WBS code"""
        parts = wbs_code.split('.')
        if len(parts) <= 1:
            return None
        parent_code = '.'.join(parts[:-1])
        return parent_code
    
    def build_hierarchy_tree(self):
        """Build parent-child relationships"""
        for task_id, info in self.level_map.items():
            parent_wbs = info['parent']
            if parent_wbs:
                # Find parent task ID
                parent_id = self._find_task_by_wbs(parent_wbs)
                if parent_id:
                    self.hierarchy_tree[parent_id].append(task_id)
        
        return True
    
    def _find_task_by_wbs(self, wbs_code):
        """Find task ID by WBS code"""
        for task_id, info in self.level_map.items():
            if info['wbs_code'] == wbs_code:
                return task_id
        return None
    
    def get_children(self, task_id):
        """Get all child tasks of a given task"""
        return self.hierarchy_tree.get(task_id, [])
    
    def get_descendants(self, task_id):
        """Get all descendants (recursive)"""
        descendants = []
        children = self.get_children(task_id)
        descendants.extend(children)
        for child in children:
            descendants.extend(self.get_descendants(child))
        return descendants
    
    def get_level_summary(self):
        """Get summary by hierarchy level"""
        level_stats = defaultdict(lambda: {'count': 0, 'tasks': []})
        
        for task_id, info in self.level_map.items():
            level = info['level']
            level_stats[level]['count'] += 1
            level_stats[level]['tasks'].append({
                'id': task_id,
                'name': info['name'],
                'wbs': info['wbs_code']
            })
        
        return dict(level_stats)
    
    def get_phase_tasks(self):
        """Get top-level phases (Level 2 in hierarchy)"""
        phases = {}
        for task_id, info in self.level_map.items():
            if info['level'] == 2:  # Phase level
                phases[task_id] = {
                    'name': info['name'],
                    'wbs': info['wbs_code'],
                    'children': self.get_descendants(task_id)
                }
        return phases
    
    def propagate_delay_impact(self, delayed_task_id):
        """Analyze impact of delay on parent tasks"""
        impact_chain = []
        
        current_id = delayed_task_id
        while current_id in self.level_map:
            info = self.level_map[current_id]
            impact_chain.append({
                'id': current_id,
                'name': info['name'],
                'level': info['level'],
                'wbs': info['wbs_code']
            })
            
            parent_wbs = info['parent']
            if parent_wbs:
                current_id = self._find_task_by_wbs(parent_wbs)
            else:
                break
        
        return impact_chain
    
    def get_hierarchy_graph(self):
        """Build NetworkX graph for visualization"""
        G = nx.DiGraph()
        
        for task_id, info in self.level_map.items():
            G.add_node(task_id, 
                      name=info['name'], 
                      wbs=info['wbs_code'],
                      level=info['level'])
        
        for parent_id, children in self.hierarchy_tree.items():
            for child_id in children:
                G.add_edge(parent_id, child_id)
        
        return G


if __name__ == "__main__":
    from data_processor import DataProcessor
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        
        hierarchy = WBSHierarchy(df)
        hierarchy.parse_wbs_structure()
        hierarchy.build_hierarchy_tree()
        
        print("✅ WBS Hierarchy built successfully")
        
        # Show level summary
        levels = hierarchy.get_level_summary()
        print(f"\n📊 Hierarchy Levels:")
        for level in sorted(levels.keys()):
            print(f"  Level {level}: {levels[level]['count']} tasks")
        
        # Show phases
        phases = hierarchy.get_phase_tasks()
        print(f"\n📋 Project Phases ({len(phases)} total):")
        for phase_id, phase_info in list(phases.items())[:5]:
            print(f"  {phase_info['wbs']}: {phase_info['name']} ({len(phase_info['children'])} subtasks)")
