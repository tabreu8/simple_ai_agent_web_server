#!/usr/bin/env python3
"""
Quick validation script to test the test setup.
"""
import os
import sys
import tempfile

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import pytest
        import fastapi
        import requests
        import httpx
        from fastapi.testclient import TestClient
        print("✅ All required test modules can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_test_structure():
    """Test that test files exist and are structured correctly."""
    test_files = [
        "__init__.py",
        "conftest.py", 
        "test_docs_api.py",
        "test_agent_api.py",
        "test_knowledge_base.py"
    ]
    
    missing_files = []
    for file in test_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    else:
        print("✅ All test files exist")
        return True

def test_pytest_config():
    """Test that pytest configuration is valid."""
    if os.path.exists("pytest.ini"):
        print("✅ pytest.ini configuration file exists")
        return True
    else:
        print("❌ pytest.ini configuration file missing")
        return False

def test_environment_setup():
    """Test that test environment can be set up."""
    try:
        # Create temporary test directories
        test_dir1 = tempfile.mkdtemp(prefix="validation_test_")
        test_dir2 = tempfile.mkdtemp(prefix="validation_test_")
        
        # Set test environment variables
        os.environ["CHROMADB_PATH"] = test_dir1
        os.environ["CHROMADB_COLLECTION"] = "validation_test"
        os.environ["AGENT_MEMORY_PATH"] = test_dir2
        
        print("✅ Test environment can be set up")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir1)
        shutil.rmtree(test_dir2)
        
        return True
    except Exception as e:
        print(f"❌ Environment setup error: {e}")
        return False

def main():
    """Run validation tests."""
    print("=" * 50)
    print("Test Setup Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Test Structure", test_test_structure), 
        ("Pytest Config", test_pytest_config),
        ("Environment Setup", test_environment_setup)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All validation tests passed!")
        print("You can now run the test suite with:")
        print("  python run_tests.py")
        print("  or")
        print("  make test")
    else:
        print("❌ Some validation tests failed!")
        print("Please fix the issues before running the test suite.")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
