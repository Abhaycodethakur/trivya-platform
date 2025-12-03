"""
Complete System Test Runner
Runs all tests and provides a summary report
"""
import os
import sys
import subprocess
import json
from datetime import datetime

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        return True, result.stdout
    else:
        print(f"❌ {description} - FAILED")
        print(f"Error: {result.stderr}")
        return False, result.stderr

def main():
    """Run all tests and generate a report"""
    print("🚀 Starting Complete System Test Suite")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    test_results = []
    test_outputs = {}
    
    # Run unit tests
    success, output = run_command(
        "python -m pytest tests/test_config.py tests/test_logger.py tests/test_security.py tests/test_pricing_optimizer.py -v --tb=short",
        "Core Functions Unit Tests"
    )
    test_results.append(success)
    test_outputs["core_functions"] = output
    
    success, output = run_command(
        "python -m pytest tests/test_vector_store.py tests/test_rag_pipeline.py tests/test_kb_manager.py -v --tb=short",
        "Knowledge Base Unit Tests"
    )
    test_results.append(success)
    test_outputs["knowledge_base"] = output
    
    # Run integration tests
    success, output = run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    )
    test_results.append(success)
    test_outputs["integration"] = output
    
    # Run custom validation scripts
    success, output = run_command(
        "python validate_kb_system.py",
        "Knowledge Base System Validation"
    )
    test_results.append(success)
    test_outputs["kb_system"] = output
    
    success, output = run_command(
        "python validate_integration.py",
        "Component Integration Validation"
    )
    test_results.append(success)
    test_outputs["component_integration"] = output
    
    # Check if API server is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            success, output = run_command(
                "python validate_api.py",
                "API Endpoint Validation"
            )
            test_results.append(success)
            test_outputs["api"] = output
        else:
            print("\n⚠️ API server not responding, skipping API tests")
            test_results.append(False)
            test_outputs["api"] = "API server not responding"
    except:
        print("\n⚠️ API server not running, skipping API tests")
        test_results.append(False)
        test_outputs["api"] = "API server not running"
    
    # Generate summary report
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY REPORT")
    print(f"{'='*50}")
    print(f"Total Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    # Save report to file
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_test_suites": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": passed/total*100,
        "test_outputs": test_outputs
    }
    
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: test_report.json")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready for the next phase.")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED! Please review and fix the issues before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
