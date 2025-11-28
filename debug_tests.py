import subprocess
import sys

print("Running tests...")
try:
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/test_vector_store.py", "tests/integration/test_vector_store_integration.py", "tests/integration/test_vector_store_config_integration.py"], capture_output=True, text=True)
    with open("test_results_debug.txt", "w") as f:
        f.write("STDOUT:\n" + result.stdout + "\n")
        f.write("STDERR:\n" + result.stderr + "\n")
except Exception as e:
    with open("test_results_debug.txt", "w") as f:
        f.write(f"Error: {e}")
