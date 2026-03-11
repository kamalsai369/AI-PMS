"""
Dependency Graph Analyzer
Validates task dependencies and detects scheduling conflicts
"""

import pandas as pd
import networkx as nx
from datetime import datetime, timedelta


class DependencyAnalyzer:
    """Analyzes and validates task dependencies"""
    
    def __init__(self, df):
        self.df = df
        self.dependency_graph = nx.DiGraph()
        self.errors = []
        self.warnings = []
        
    def build_dependency_graph(self):
        """Build directed graph of task dependencies"""
        # Add all tasks as nodes
        for idx, row in self.df.iterrows():
            task_id = row['ID']
            self.dependency_graph.add_node(
                task_id,
                name=row['Task_Name'],
                start=row['Start_Date'],
                finish=row['Finish_Date'],
                duration=row['Duration_Days'],
                status=row['Status']
            )
        
        # Add dependency edges
        for idx, row in self.df.iterrows():
            task_id = row['ID']
            predecessors = row['Predecessor_List']
            
            for pred_id in predecessors:
                # Only add edge if predecessor exists as a node
                if pred_id in self.dependency_graph:
                    self.dependency_graph.add_edge(pred_id, task_id)
        
        return True
    
    def validate_missing_references(self):
        """Detect dependencies pointing to non-existent tasks"""
        missing_refs = []
        all_task_ids = set(self.df['ID'].values)
        
        for idx, row in self.df.iterrows():
            task_id = row['ID']
            task_name = row['Task_Name']
            predecessors = row['Predecessor_List']
            
            for pred_id in predecessors:
                if pred_id not in all_task_ids:
                    missing_refs.append({
                        'Task_ID': task_id,
                        'Task_Name': task_name,
                        'Issue': 'Missing Predecessor',
                        'Description': f'Depends on non-existent task {pred_id}',
                        'Severity': 'Critical'
                    })
        
        return missing_refs
    
    def detect_circular_dependencies(self):
        """Detect circular dependency loops using cycle detection"""
        circular_deps = []
        
        try:
            # Find all cycles in the graph
            cycles = list(nx.simple_cycles(self.dependency_graph))
            
            for cycle in cycles:
                # Get task names for the cycle
                cycle_tasks = []
                for task_id in cycle:
                    task_data = self.dependency_graph.nodes[task_id]
                    cycle_tasks.append(f"{task_id} ({task_data['name']})")
                
                circular_deps.append({
                    'Cycle': ' → '.join(map(str, cycle)) + f' → {cycle[0]}',
                    'Tasks_Involved': len(cycle),
                    'Task_Names': cycle_tasks,
                    'Severity': 'Critical',
                    'Description': 'Circular dependency creates infinite scheduling loop'
                })
        
        except Exception as e:
            print(f"Error detecting cycles: {e}")
        
        return circular_deps
    
    def validate_date_logic(self):
        """Validate that predecessor finish dates come before successor start dates"""
        date_violations = []
        
        for edge in self.dependency_graph.edges():
            pred_id, succ_id = edge
            
            pred_data = self.dependency_graph.nodes[pred_id]
            succ_data = self.dependency_graph.nodes[succ_id]
            
            pred_finish = pred_data['finish']
            succ_start = succ_data['start']
            
            # Check if dates are valid
            if pd.notna(pred_finish) and pd.notna(succ_start):
                if pred_finish > succ_start:
                    date_violations.append({
                        'Predecessor_ID': pred_id,
                        'Predecessor_Name': pred_data['name'],
                        'Predecessor_Finish': pred_finish.strftime('%Y-%m-%d'),
                        'Successor_ID': succ_id,
                        'Successor_Name': succ_data['name'],
                        'Successor_Start': succ_start.strftime('%Y-%m-%d'),
                        'Gap_Days': (pred_finish - succ_start).days,
                        'Severity': 'High',
                        'Description': 'Predecessor finishes AFTER successor starts'
                    })
        
        return date_violations
    
    def get_critical_path(self):
        """Identify critical path through the project (longest path)"""
        try:
            # For scheduling, we need to find the longest path
            # This requires a DAG (no cycles)
            if not nx.is_directed_acyclic_graph(self.dependency_graph):
                return None, "Cannot compute critical path: graph contains cycles"
            
            # Find longest path (critical path)
            longest_path = nx.dag_longest_path(self.dependency_graph)
            
            critical_tasks = []
            for task_id in longest_path:
                task_data = self.dependency_graph.nodes[task_id]
                critical_tasks.append({
                    'ID': task_id,
                    'Name': task_data['name'],
                    'Duration': task_data['duration'],
                    'Status': task_data['status']
                })
            
            return critical_tasks, None
        
        except Exception as e:
            return None, f"Error computing critical path: {str(e)}"
    
    def analyze_task_dependencies(self, task_id):
        """Get detailed dependency information for a specific task"""
        if task_id not in self.dependency_graph:
            return None
        
        # Get predecessors (tasks that must complete before this one)
        predecessors = list(self.dependency_graph.predecessors(task_id))
        
        # Get successors (tasks that depend on this one)
        successors = list(self.dependency_graph.successors(task_id))
        
        task_data = self.dependency_graph.nodes[task_id]
        
        return {
            'task_id': task_id,
            'task_name': task_data['name'],
            'predecessors': [
                {
                    'id': pred_id,
                    'name': self.dependency_graph.nodes[pred_id]['name'],
                    'status': self.dependency_graph.nodes[pred_id]['status']
                }
                for pred_id in predecessors
            ],
            'successors': [
                {
                    'id': succ_id,
                    'name': self.dependency_graph.nodes[succ_id]['name'],
                    'status': self.dependency_graph.nodes[succ_id]['status']
                }
                for succ_id in successors
            ],
            'total_predecessors': len(predecessors),
            'total_successors': len(successors)
        }
    
    def validate_all(self):
        """Run all validation checks"""
        results = {
            'missing_references': self.validate_missing_references(),
            'circular_dependencies': self.detect_circular_dependencies(),
            'date_logic_violations': self.validate_date_logic()
        }
        
        # Calculate total issues
        total_issues = sum(len(v) for v in results.values())
        results['total_issues'] = total_issues
        results['has_errors'] = total_issues > 0
        
        return results
    
    def get_dependency_stats(self):
        """Get statistical summary of dependencies"""
        stats = {
            'total_tasks': self.dependency_graph.number_of_nodes(),
            'total_dependencies': self.dependency_graph.number_of_edges(),
            'tasks_with_no_predecessors': sum(
                1 for node in self.dependency_graph.nodes() 
                if self.dependency_graph.in_degree(node) == 0
            ),
            'tasks_with_no_successors': sum(
                1 for node in self.dependency_graph.nodes() 
                if self.dependency_graph.out_degree(node) == 0
            ),
            'max_predecessors': max(
                self.dependency_graph.in_degree(node) 
                for node in self.dependency_graph.nodes()
            ) if self.dependency_graph.nodes() else 0,
            'max_successors': max(
                self.dependency_graph.out_degree(node) 
                for node in self.dependency_graph.nodes()
            ) if self.dependency_graph.nodes() else 0,
            'is_dag': nx.is_directed_acyclic_graph(self.dependency_graph)
        }
        
        return stats


if __name__ == "__main__":
    from data_processor import DataProcessor
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    if processor.process():
        df = processor.get_data()
        
        analyzer = DependencyAnalyzer(df)
        analyzer.build_dependency_graph()
        
        print("✅ Dependency graph built successfully")
        
        # Run validations
        results = analyzer.validate_all()
        
        print(f"\n🔍 Dependency Validation Results:")
        print(f"  Total Issues Found: {results['total_issues']}")
        print(f"  - Missing References: {len(results['missing_references'])}")
        print(f"  - Circular Dependencies: {len(results['circular_dependencies'])}")
        print(f"  - Date Logic Violations: {len(results['date_logic_violations'])}")
        
        # Show some issues
        if results['missing_references']:
            print(f"\n⚠️ Sample Missing References:")
            for issue in results['missing_references'][:3]:
                print(f"  Task {issue['Task_ID']}: {issue['Description']}")
        
        # Get stats
        stats = analyzer.get_dependency_stats()
        print(f"\n📊 Dependency Statistics:")
        print(f"  Total Tasks: {stats['total_tasks']}")
        print(f"  Total Dependencies: {stats['total_dependencies']}")
        print(f"  Is DAG (no cycles): {stats['is_dag']}")
