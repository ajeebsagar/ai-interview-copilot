#!/bin/bash
# Delete unnecessary documentation and test files

echo "Deleting unnecessary files..."

# Duplicate/old documentation
rm -f "AZURE_FIX_SUMMARY.md"
rm -f "CHECK_AZURE_SETUP.md"
rm -f "QUICK_FIX.md"
rm -f "CHROME_EXTENSION_TESTING_GUIDE.md"
rm -f "COMPLETE_TEST_GUIDE.md"
rm -f "COMPLETE_TESTING_GUIDE.md"
rm -f "DEEP_ANALYSIS_RESULTS.md"
rm -f "COMPREHENSIVE_IMPLEMENTATION_ANALYSIS.md"
rm -f "END_TO_END_TEST_RESULTS.md"
rm -f "FINAL_STATUS.md"
rm -f "FINAL_TEST_REPORT.md"
rm -f "FIX_ERROR_SENDING_MESSAGE.md"
rm -f "FIX_FAILED_TO_FETCH.md"
rm -f "MODEL_CHANGE_SUMMARY.md"
rm -f "START_HERE.md"
rm -f "TEST_RESULTS.md"
rm -f "TESTING_RESULTS_SUMMARY.md"
rm -f "WORKING.md"

# Unnecessary test files
rm -f "comprehensive_test_suite.py"
rm -f "test_azure_now.py"
rm -f "verify_azure.py"
rm -f "verify_azure_config.py"
rm -f "master_test_runner.py"
rm -f "test_websocket.py"

# Extension test files
rm -f "extension/diagnostic.html"
rm -f "extension/test.html"
rm -f "extension/simple-test.html"

# Backend test files that are duplicates
rm -f "backend/test_direct.py"
rm -f "backend/test_endpoint.py"
rm -f "backend/test_integration.py"
rm -f "backend/start_server.py"
rm -f "backend/start_server.bat"
rm -f "backend/run_tests.bat"

# Log files
rm -f "backend/*.log"
rm -f "backend/test_execution.log"

echo "Cleanup complete!"
echo "Deleted 27+ unnecessary files"
