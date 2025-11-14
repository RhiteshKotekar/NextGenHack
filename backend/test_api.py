#!/usr/bin/env python3
"""
test_api.py - Test script for Insight-o-pedia Flask Backend
Run this after starting the server to verify all endpoints work correctly.
"""

import requests
import json
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)

BASE_URL = "http://localhost:5000"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.CYAN}{'='*70}\n")

def print_success(text):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"{Fore.RED}✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {text}")

def test_health():
    """Test health check endpoint"""
    print_header("Testing Health Check Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data['status']}")
            print_info(f"Models loaded: {', '.join(data['models_loaded'])}")
            return True
        else:
            print_error(f"Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is the server running?")
        print_info("Start server with: python app.py")
        return False
    except Exception as e:
        print_error(f"Health check error: {e}")
        return False

def test_chat(question):
    """Test chat endpoint with a question"""
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Response received")
            print_info(f"Intent detected: {data['intent']}")
            print_info(f"Parameters: {json.dumps(data['params'], indent=2)}")
            print(f"\n{Fore.WHITE}Insights:")
            
            for i, insight in enumerate(data['insights'], 1):
                print(f"\n{Fore.MAGENTA}--- Insight {i} ({insight['type']}) ---")
                print(f"{Fore.WHITE}{insight['text']}\n")
            
            return True
        else:
            error_data = response.json()
            print_error(f"Chat request failed: {error_data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print_error(f"Chat request error: {e}")
        return False

def main():
    """Run all tests"""
    print(f"{Fore.MAGENTA}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║         Insight-o-pedia Backend API Test Suite                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # Test health
    if not test_health():
        print_error("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Forecasting - Q4 Demand",
            "question": "What will Q4 demand look like based on current trends?"
        },
        {
            "name": "Inventory - 20% Surge",
            "question": "If demand increases by 20%, what stock adjustments are needed?"
        },
        {
            "name": "Shipping - Courier Delays",
            "question": "Which courier partners might cause late deliveries?"
        },
        {
            "name": "Sentiment - Customer Reviews",
            "question": "How are customer reviews trending?"
        },
        {
            "name": "General - Help",
            "question": "What can you help me with?"
        }
    ]
    
    # Run each test
    results = []
    for i, test in enumerate(test_cases, 1):
        print_header(f"Test {i}/{len(test_cases)}: {test['name']}")
        print_info(f"Question: \"{test['question']}\"")
        print()
        
        success = test_chat(test['question'])
        results.append((test['name'], success))
        
        if i < len(test_cases):
            input(f"\n{Fore.CYAN}Press Enter to continue to next test...")
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        if success:
            print_success(f"{name}")
        else:
            print_error(f"{name}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}🎉 All tests passed! Backend is working correctly.")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()
