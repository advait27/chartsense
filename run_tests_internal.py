import pytest
import sys
import os

print("Starting test run...", file=sys.__stdout__)

try:
    with open("/Users/advaitdharmadhikari/Documents/Personal Projects/chartsense/test_results_internal.txt", "w") as f:
        sys.stdout = f
        sys.stderr = f
        print("Running tests...")
        ret = pytest.main(["/Users/advaitdharmadhikari/Documents/Personal Projects/chartsense/tests/"])
        print(f"Done. Return code: {ret}")
except Exception as e:
    with open("/Users/advaitdharmadhikari/Documents/Personal Projects/chartsense/error_log.txt", "w") as f:
        f.write(str(e))
