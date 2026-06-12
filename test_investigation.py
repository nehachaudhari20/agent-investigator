"""
Quick test script for the LangGraph investigation workflow.
"""

import json
from pathlib import Path
from orchestration.langgraph.workflow import run_investigation, format_results


def test_investigation(scenario: str):
    """Test investigation on a scenario."""
    print(f"\n{'='*60}")
    print(f"Testing scenario: {scenario}")
    print(f"{'='*60}\n")
    
    try:
        # Run investigation
        final_state = run_investigation(scenario)
        report = format_results(final_state)
        
        # Quick output
        print(f"✓ Root Cause: {report['root_cause']}")
        print(f"✓ Confidence: {report['confidence']:.2%}")
        print(f"✓ Suspect Services: {', '.join(report['suspect_services'][:3])}")
        
        # Verify against ground truth
        dataset_path = Path('datasets') / scenario
        incident_path = dataset_path / 'incident.json'
        
        if incident_path.exists():
            with open(incident_path, 'r') as f:
                ground_truth = json.load(f)
            
            match = report['root_cause'] == ground_truth['root_cause']
            status = '✓ PASS' if match else '✗ FAIL'
            print(f"{status} - Expected: {ground_truth['root_cause']}")
        
        print()
        return True
    
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test all scenarios."""
    print("\n" + "="*60)
    print("LANGGRAPH INVESTIGATION WORKFLOW - TEST SUITE")
    print("="*60)
    
    scenarios = ['retry_storm', 'misleading_logs', 'memory_poisoning']
    results = {}
    
    for scenario in scenarios:
        results[scenario] = test_investigation(scenario)
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for scenario, passed_test in results.items():
        status = '✓' if passed_test else '✗'
        print(f"{status} {scenario}")
    
    print(f"\nTotal: {passed}/{total} scenarios passed\n")
    
    return all(results.values())


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
