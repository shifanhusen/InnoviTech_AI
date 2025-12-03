#!/usr/bin/env python3
"""
Test script for AI Assistant API
Tests all endpoints and validates responses
"""

import requests
import json
import time
import uuid
from typing import Dict, Any


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class APITester:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session_id = str(uuid.uuid4())
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    
    def print_test(self, test_name: str, status: str, message: str = ""):
        """Print test result"""
        if status == "PASS":
            symbol = "✓"
            color = Colors.GREEN
            self.tests_passed += 1
        elif status == "FAIL":
            symbol = "✗"
            color = Colors.RED
            self.tests_failed += 1
        else:
            symbol = "⚠"
            color = Colors.YELLOW
        
        print(f"{color}{symbol} {test_name}{Colors.END}", end="")
        if message:
            print(f" - {message}")
        else:
            print()
    
    def test_health(self) -> bool:
        """Test health check endpoint"""
        self.print_header("Testing Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.print_test("Health Check", "PASS", f"Response: {data}")
                    return True
                else:
                    self.print_test("Health Check", "FAIL", f"Unexpected response: {data}")
                    return False
            else:
                self.print_test("Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Health Check", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_chat_simple(self) -> bool:
        """Test simple chat message"""
        self.print_header("Testing Simple Chat")
        
        try:
            payload = {
                "session_id": self.session_id,
                "message": "Hello! What is 2+2?",
                "use_scrape": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/llm/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                if reply:
                    self.print_test("Simple Chat", "PASS", f"Got reply ({len(reply)} chars)")
                    print(f"\n{Colors.YELLOW}AI Response:{Colors.END}")
                    print(f"{reply[:200]}...")
                    return True
                else:
                    self.print_test("Simple Chat", "FAIL", "Empty reply")
                    return False
            else:
                self.print_test("Simple Chat", "FAIL", f"HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except requests.exceptions.Timeout:
            self.print_test("Simple Chat", "FAIL", "Request timeout (Ollama may be slow)")
            return False
        except requests.exceptions.RequestException as e:
            self.print_test("Simple Chat", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_conversation_memory(self) -> bool:
        """Test conversation memory across messages"""
        self.print_header("Testing Conversation Memory")
        
        try:
            # First message
            payload1 = {
                "session_id": self.session_id,
                "message": "My name is Alice.",
                "use_scrape": False
            }
            
            response1 = requests.post(
                f"{self.base_url}/api/llm/chat",
                json=payload1,
                timeout=60
            )
            
            if response1.status_code != 200:
                self.print_test("Memory Test (1st msg)", "FAIL", f"HTTP {response1.status_code}")
                return False
            
            self.print_test("Memory Test (1st msg)", "PASS", "First message sent")
            
            # Wait a moment
            time.sleep(2)
            
            # Second message - should remember name
            payload2 = {
                "session_id": self.session_id,
                "message": "What is my name?",
                "use_scrape": False
            }
            
            response2 = requests.post(
                f"{self.base_url}/api/llm/chat",
                json=payload2,
                timeout=60
            )
            
            if response2.status_code == 200:
                data = response2.json()
                reply = data.get("reply", "").lower()
                
                # Check if AI remembers the name
                if "alice" in reply:
                    self.print_test("Memory Test (2nd msg)", "PASS", "AI remembered the name!")
                    print(f"\n{Colors.YELLOW}AI Response:{Colors.END}")
                    print(f"{data['reply'][:200]}...")
                    return True
                else:
                    self.print_test("Memory Test (2nd msg)", "FAIL", "AI didn't remember the name")
                    print(f"Response: {reply[:200]}...")
                    return False
            else:
                self.print_test("Memory Test (2nd msg)", "FAIL", f"HTTP {response2.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Memory Test", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_session_history(self) -> bool:
        """Test session history retrieval"""
        self.print_header("Testing Session History")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/llm/session/{self.session_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                history = data.get("history", [])
                message_count = data.get("message_count", 0)
                
                if message_count > 0:
                    self.print_test("Session History", "PASS", f"Retrieved {message_count} messages")
                    print(f"\n{Colors.YELLOW}Recent messages:{Colors.END}")
                    for msg in history[-3:]:
                        print(f"  {msg['role']}: {msg['content'][:50]}...")
                    return True
                else:
                    self.print_test("Session History", "FAIL", "No messages in history")
                    return False
            else:
                self.print_test("Session History", "FAIL", f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Session History", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_session_reset(self) -> bool:
        """Test session reset"""
        self.print_header("Testing Session Reset")
        
        try:
            payload = {
                "session_id": self.session_id
            }
            
            response = requests.post(
                f"{self.base_url}/api/llm/reset",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test("Session Reset", "PASS", data.get("message", ""))
                
                # Verify history is cleared
                time.sleep(1)
                history_response = requests.get(
                    f"{self.base_url}/api/llm/session/{self.session_id}",
                    timeout=5
                )
                
                if history_response.status_code == 200:
                    history_data = history_response.json()
                    if history_data.get("message_count", 0) == 0:
                        self.print_test("Session Clear Verify", "PASS", "History cleared")
                        return True
                    else:
                        self.print_test("Session Clear Verify", "FAIL", "History not cleared")
                        return False
            else:
                self.print_test("Session Reset", "FAIL", f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Session Reset", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_scraping(self) -> bool:
        """Test web scraping functionality (optional)"""
        self.print_header("Testing Web Scraping (Optional)")
        
        try:
            payload = {
                "session_id": str(uuid.uuid4()),  # New session
                "message": "What is on this page?",
                "use_scrape": True,
                "scrape_url": "https://example.com"
            }
            
            response = requests.post(
                f"{self.base_url}/api/llm/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                
                if reply:
                    self.print_test("Web Scraping", "PASS", f"Got reply with scraped content")
                    print(f"\n{Colors.YELLOW}AI Response:{Colors.END}")
                    print(f"{reply[:200]}...")
                    return True
                else:
                    self.print_test("Web Scraping", "FAIL", "Empty reply")
                    return False
            else:
                self.print_test("Web Scraping", "FAIL", f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test("Web Scraping", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.BOLD}{'='*60}")
        print(f"AI Assistant API Test Suite")
        print(f"Base URL: {self.base_url}")
        print(f"Session ID: {self.session_id}")
        print(f"{'='*60}{Colors.END}\n")
        
        # Run tests
        self.test_health()
        time.sleep(1)
        
        self.test_chat_simple()
        time.sleep(2)
        
        self.test_conversation_memory()
        time.sleep(1)
        
        self.test_session_history()
        time.sleep(1)
        
        self.test_session_reset()
        time.sleep(1)
        
        self.test_scraping()
        
        # Print summary
        self.print_header("Test Summary")
        total = self.tests_passed + self.tests_failed
        pass_rate = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests: {total}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.END}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        if self.tests_failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.END}\n")
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed. Check logs above.{Colors.END}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Assistant API")
    parser.add_argument(
        "--url",
        default="http://localhost:5001",
        help="Base URL of the API (default: http://localhost:5001)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(base_url=args.url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
