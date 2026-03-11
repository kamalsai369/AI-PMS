"""
Test Suite - Run all modules to verify installation
"""

import sys
import os


def test_module(module_name, test_func):
    """Test a module and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {module_name}")
    print('='*60)
    
    try:
        test_func()
        print(f"✅ {module_name} - PASSED")
        return True
    except Exception as e:
        print(f"❌ {module_name} - FAILED")
        print(f"Error: {str(e)}")
        return False


def test_data_processor():
    """Test data processing module"""
    from data_processor import DataProcessor
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    assert processor.process(), "Failed to process data"
    df = processor.get_data()
    assert len(df) > 0, "No data loaded"
    print(f"  Loaded {len(df)} tasks")
    
    anomalies = processor.detect_date_anomalies()
    print(f"  Found {len(anomalies)} date anomalies")


def test_wbs_hierarchy():
    """Test WBS hierarchy module"""
    from data_processor import DataProcessor
    from wbs_hierarchy import WBSHierarchy
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    processor.process()
    df = processor.get_data()
    
    hierarchy = WBSHierarchy(df)
    hierarchy.parse_wbs_structure()
    hierarchy.build_hierarchy_tree()
    
    levels = hierarchy.get_level_summary()
    print(f"  Hierarchy levels: {len(levels)}")
    
    phases = hierarchy.get_phase_tasks()
    print(f"  Project phases: {len(phases)}")


def test_dependency_analyzer():
    """Test dependency analyzer module"""
    from data_processor import DataProcessor
    from dependency_analyzer import DependencyAnalyzer
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    processor.process()
    df = processor.get_data()
    
    analyzer = DependencyAnalyzer(df)
    analyzer.build_dependency_graph()
    
    results = analyzer.validate_all()
    print(f"  Total issues: {results['total_issues']}")
    print(f"  Missing references: {len(results['missing_references'])}")
    print(f"  Circular dependencies: {len(results['circular_dependencies'])}")
    print(f"  Date violations: {len(results['date_logic_violations'])}")


def test_resource_analyzer():
    """Test resource analyzer module"""
    from data_processor import DataProcessor
    from resource_analyzer import ResourceAnalyzer
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    processor.process()
    df = processor.get_data()
    
    analyzer = ResourceAnalyzer(df)
    utilization = analyzer.get_resource_utilization_summary()
    print(f"  Resources analyzed: {len(utilization)}")
    
    overloaded = analyzer.detect_overallocation()
    print(f"  Over-allocation instances: {len(overloaded)}")


def test_transcript_analyzer():
    """Test transcript analyzer module"""
    from transcript_analyzer import TranscriptAnalyzer
    
    transcript_files = [
        "progress_review_meeting_transcript.md",
        "design_coordination_meeting_transcript.md",
        "safety_readiness_briefing_transcript.md"
    ]
    
    analyzer = TranscriptAnalyzer(transcript_files)
    analyses = analyzer.analyze_all()
    print(f"  Transcripts analyzed: {len(analyses)}")
    
    insights = analyzer.get_consolidated_insights(analyses)
    print(f"  Tasks mentioned: {len(insights['unique_tasks_mentioned'])}")
    print(f"  Delay mentions: {len(insights['delay_mentions'])}")
    print(f"  Resource conflicts: {len(insights['resource_conflicts'])}")


def test_conflict_detector():
    """Test conflict detector module"""
    from data_processor import DataProcessor
    from transcript_analyzer import TranscriptAnalyzer
    from conflict_detector import ConflictDetector
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    processor.process()
    df = processor.get_data()
    
    transcript_files = [
        "progress_review_meeting_transcript.md",
        "design_coordination_meeting_transcript.md",
        "safety_readiness_briefing_transcript.md"
    ]
    
    t_analyzer = TranscriptAnalyzer(transcript_files)
    analyses = t_analyzer.analyze_all()
    insights = t_analyzer.get_consolidated_insights(analyses)
    
    detector = ConflictDetector(df, insights)
    conflicts = detector.detect_all_conflicts()
    
    print(f"  Total conflicts: {conflicts['summary']['total_conflicts']}")
    print(f"  Status conflicts: {conflicts['summary']['status_conflicts_count']}")
    print(f"  Resource conflicts: {conflicts['summary']['resource_conflicts_count']}")
    print(f"  Data errors: {conflicts['summary']['data_errors_count']}")


def test_risk_predictor():
    """Test risk predictor module"""
    from data_processor import DataProcessor
    from dependency_analyzer import DependencyAnalyzer
    from resource_analyzer import ResourceAnalyzer
    from risk_predictor import RiskPredictor
    
    processor = DataProcessor("metro_rail_wbs_data.csv")
    processor.process()
    df = processor.get_data()
    
    dep_analyzer = DependencyAnalyzer(df)
    dep_analyzer.build_dependency_graph()
    
    res_analyzer = ResourceAnalyzer(df)
    
    predictor = RiskPredictor(df, dep_analyzer, res_analyzer)
    predictions = predictor.predict_delays()
    
    print(f"  Tasks analyzed: {len(predictions)}")
    
    high_risk = predictor.get_high_risk_tasks(predictions, min_risk_score=60)
    print(f"  High-risk tasks: {len(high_risk)}")
    
    distribution = predictor.get_risk_distribution(predictions)
    print(f"  Risk distribution: {distribution}")


def main():
    """Run all tests"""
    print("="*60)
    print("AI-PMS Test Suite")
    print("Testing all modules...")
    print("="*60)
    
    tests = [
        ("Data Processor", test_data_processor),
        ("WBS Hierarchy", test_wbs_hierarchy),
        ("Dependency Analyzer", test_dependency_analyzer),
        ("Resource Analyzer", test_resource_analyzer),
        ("Transcript Analyzer", test_transcript_analyzer),
        ("Conflict Detector", test_conflict_detector),
        ("Risk Predictor", test_risk_predictor)
    ]
    
    results = []
    for name, func in tests:
        results.append(test_module(name, func))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - System ready to use!")
        print("\nTo launch dashboard, run:")
        print("  streamlit run dashboard.py")
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        print("Please check the errors above")
    
    print('='*60)


if __name__ == "__main__":
    main()
