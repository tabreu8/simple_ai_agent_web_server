#!/usr/bin/env python3
"""
Test runner script that starts the FastAPI server and runs tests.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time

import requests


def setup_test_environment():
    """Set up test environment variables."""
    # Create temporary directories for testing
    test_chromadb_path = tempfile.mkdtemp(prefix="test_chromadb_")
    test_agent_memory_path = tempfile.mkdtemp(prefix="test_agent_memory_")

    # Set environment variables
    os.environ["CHROMADB_PATH"] = test_chromadb_path
    os.environ["CHROMADB_COLLECTION"] = "test_collection"
    os.environ["AGENT_MEMORY_PATH"] = test_agent_memory_path

    # Set test OpenAI key if not already set
    if "OPENAI_API_KEY" not in os.environ:
        os.environ["OPENAI_API_KEY"] = "test-key-for-testing"

    return test_chromadb_path, test_agent_memory_path


def cleanup_test_environment(test_chromadb_path, test_agent_memory_path):
    """Clean up test environment."""
    try:
        if os.path.exists(test_chromadb_path):
            shutil.rmtree(test_chromadb_path)
        if os.path.exists(test_agent_memory_path):
            shutil.rmtree(test_agent_memory_path)
    except Exception as e:
        print(f"Warning: Failed to cleanup test directories: {e}")


def wait_for_server(url="http://localhost:8000", timeout=30):
    """Wait for the server to be ready."""
    print(f"Waiting for server at {url} to be ready...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/docs", timeout=5)
            if response.status_code == 200:
                print("Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        time.sleep(1)

    print(f"Server did not start within {timeout} seconds")
    return False


def start_server():
    """Start the FastAPI server."""
    print("Starting FastAPI server...")

    # Change to parent directory to run the server
    original_dir = os.getcwd()
    parent_dir = os.path.dirname(os.getcwd())
    os.chdir(parent_dir)

    # Start the server using uvicorn
    server_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--log-level",
            "info",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Change back to tests directory
    os.chdir(original_dir)

    # Wait for server to be ready
    if wait_for_server():
        return server_process
    else:
        # Kill the server if it didn't start properly
        server_process.terminate()
        server_process.wait()
        return None


def run_tests():
    """Run the pytest test suite."""
    print("Running tests...")

    # Run pytest with coverage (from current directory which should be tests/)
    test_command = [
        sys.executable,
        "-m",
        "pytest",
        ".",  # Current directory (tests/)
        "-v",
        "--tb=short",
        "--color=yes",
    ]

    result = subprocess.run(test_command, capture_output=False)
    return result.returncode


def main():
    """Main test runner function."""
    print("=" * 60)
    print("FastAPI Application Test Runner")
    print("=" * 60)

    # Setup test environment
    test_chromadb_path, test_agent_memory_path = setup_test_environment()

    server_process = None
    exit_code = 1

    try:
        # Start the server
        server_process = start_server()

        if server_process is None:
            print("Failed to start server. Exiting.")
            return 1

        # Run tests
        exit_code = run_tests()

        if exit_code == 0:
            print("\n" + "=" * 60)
            print("✅ All tests passed!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ Some tests failed!")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        exit_code = 130

    finally:
        # Stop the server
        if server_process:
            print("Stopping server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("Server didn't stop gracefully, killing...")
                server_process.kill()
                server_process.wait()

        # Cleanup test environment
        cleanup_test_environment(test_chromadb_path, test_agent_memory_path)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
