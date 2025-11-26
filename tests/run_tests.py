import subprocess
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """Run all tests using pytest"""
    print("Trivya Platform Test Runner")
    print("=" * 50)
    print("Including unit tests and integration tests...")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Run pytest
    print("Running tests with pytest...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/"],
        cwd=project_root,
        capture_output=False  # Let pytest output directly to stdout
    )
    
    print("\n" + "=" * 50)
    if result.returncode == 0:
        print("[PASS] All tests passed!")
    else:
        print("[FAIL] Some tests failed.")
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()