#!/usr/bin/env python3
"""
Test script for the unified search API endpoint.

This script tests the new unified search API endpoint with various search
scenarios to ensure it works as expected.

Usage:
    python test_unified_search_api.py

Requirements:
    - Flask app must be running on http://localhost:3000
    - Python 3.8+
    - requests library
"""

import requests
import json
import sys


# Configuration
API_URL = "http://localhost:3000/api/lang/{}/unified_search"
LANGUAGE_CODE = "el"  # Greek

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def run_test(test_name, query):
    """Run a test case and print results."""
    print(f"\n{YELLOW}Testing: {test_name}{RESET}")
    url = API_URL.format(LANGUAGE_CODE)
    
    if query:
        url = f"{url}?q={query}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Pretty-print the JSON response
        data = response.json()
        print(f"{GREEN}Status: {data.get('status', 'unknown')}{RESET}")
        print(f"Response code: {response.status_code}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        return False


def main():
    """Run all test cases."""
    print(f"{YELLOW}Testing Unified Search API{RESET}")
    print(f"API URL: {API_URL.format(LANGUAGE_CODE)}")
    
    # List of test cases (name, query)
    test_cases = [
        ("Empty query", ""),
        ("Greek lemma", "γεια"),         # "hello"
        ("Greek inflected form", "καλά"), # "good" (plural)
        ("Misspelled Greek", "γειαα"),    # Typo of "γεια"
        ("English word", "hello"),
        ("Invalid word", "asdf"),
        # Add more test cases as needed
    ]
    
    # Run all tests
    failed_tests = 0
    for name, query in test_cases:
        if not run_test(name, query):
            failed_tests += 1
    
    # Summary
    total_tests = len(test_cases)
    passed_tests = total_tests - failed_tests
    
    print(f"\n{YELLOW}Test Summary:{RESET}")
    print(f"Passed: {GREEN}{passed_tests}/{total_tests}{RESET}")
    if failed_tests > 0:
        print(f"Failed: {RED}{failed_tests}/{total_tests}{RESET}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())