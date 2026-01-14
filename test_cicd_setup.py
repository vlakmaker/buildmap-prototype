#!/usr/bin/env python3
"""
Test script to verify CI/CD setup is working correctly.
This script tests that all required files and configurations are in place.
"""

import os
import sys
from pathlib import Path


def test_github_workflows_exist():
    """Test that GitHub Actions workflow files exist."""
    workflow_dir = Path(".github/workflows")

    if not workflow_dir.exists():
        print("❌ GitHub workflows directory does not exist")
        return False

    required_files = ["ci-cd-pipeline.yml", "manual-deploy.yml"]

    for file in required_files:
        file_path = workflow_dir / file
        if not file_path.exists():
            print(f"❌ Missing workflow file: {file}")
            return False
        print(f"✅ Found workflow file: {file}")

    return True


def test_configuration_files_exist():
    """Test that required configuration files exist."""
    required_files = ["pyproject.toml", ".flake8", "setup.py", "requirements.txt"]

    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing configuration file: {file}")
            return False
        print(f"✅ Found configuration file: {file}")

    return True


def test_python_environment():
    """Test that Python environment is properly set up."""
    try:
        import black
        import flake8
        import isort
        import pytest

        print("✅ All required Python packages are available")
        return True
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        return False


def test_workflow_syntax():
    """Test that workflow files have valid YAML syntax."""
    try:
        import yaml
    except ImportError:
        print("⚠️  yaml package not available, skipping YAML syntax check")
        return True

    workflow_dir = Path(".github/workflows")

    for yaml_file in workflow_dir.glob("*.yml"):
        try:
            with open(yaml_file, "r") as f:
                yaml.safe_load(f)
            print(f"✅ Valid YAML syntax: {yaml_file.name}")
        except yaml.YAMLError as e:
            print(f"❌ Invalid YAML syntax in {yaml_file.name}: {e}")
            return False

    return True


def main():
    """Run all CI/CD setup tests."""
    print("🔧 Testing CI/CD Setup")
    print("=" * 50)

    tests = [
        ("GitHub Workflows", test_github_workflows_exist),
        ("Configuration Files", test_configuration_files_exist),
        ("Python Environment", test_python_environment),
        ("Workflow Syntax", test_workflow_syntax),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        result = test_func()
        results.append(result)

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 All {total} tests passed! CI/CD setup is ready.")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
