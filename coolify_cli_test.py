#!/usr/bin/env python3
"""
Coolify CLI Deployment Test Script
Tests the full deployment workflow using the CLI tooling
"""

import os
import requests
import json
import time
import subprocess
from urllib.parse import urljoin

class CoolifyCLITester:
    def __init__(self):
        self.base_url = "https://coolify.247420.xyz"
        self.username = os.getenv("COOLIFY_USERNAME", "admin@247420.xyz")
        self.password = os.getenv("COOLIFY_PASSWORD", "123,slam123,slam")
        self.session = requests.Session()
        self.session.verify = False  # Ignore SSL warnings
        self.test_results = {}
        
    def log_step(self, step_name, status, details=None):
        """Log test step results"""
        result = {
            'timestamp': time.time(),
            'status': status,
            'details': details
        }
        self.test_results[step_name] = result
        print(f"[{status.upper()}] {step_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_basic_connectivity(self):
        """Test basic connectivity to Coolify"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 302:  # Redirect to login is expected
                self.log_step("basic_connectivity", "success", 
                            f"Redirect to login: {response.headers.get('location')}")
                return True
            else:
                self.log_step("basic_connectivity", "failed", 
                            f"Unexpected status: {response.status_code}")
                return False
        except Exception as e:
            self.log_step("basic_connectivity", "failed", str(e))
            return False
    
    def test_login_workflow(self):
        """Test login to Coolify"""
        try:
            # Get login page
            login_url = urljoin(self.base_url, "/login")
            response = self.session.get(login_url)
            
            if response.status_code != 200:
                self.log_step("login_page_access", "failed", 
                            f"Status: {response.status_code}")
                return False
            
            # Extract CSRF token
            csrf_token = None
            if 'XSRF-TOKEN' in response.cookies:
                csrf_token = response.cookies['XSRF-TOKEN']
            
            # Perform login
            login_data = {
                'email': self.username,
                'password': self.password,
                '_token': csrf_token
            }
            
            response = self.session.post(login_url, data=login_data, allow_redirects=False)
            
            if response.status_code in [302, 303]:
                self.log_step("login_workflow", "success", 
                            f"Redirect after login: {response.headers.get('location')}")
                return True
            else:
                self.log_step("login_workflow", "failed", 
                            f"Login failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_step("login_workflow", "failed", str(e))
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        try:
            # Test servers endpoint
            servers_url = urljoin(self.base_url, "/api/servers")
            response = self.session.get(servers_url)
            
            if response.status_code == 200:
                servers_data = response.json()
                self.log_step("api_servers", "success", 
                            f"Found {len(servers_data)} servers")
            else:
                self.log_step("api_servers", "failed", 
                            f"Status: {response.status_code}")
            
            # Test resources endpoint
            resources_url = urljoin(self.base_url, "/api/resources")
            response = self.session.get(resources_url)
            
            if response.status_code == 200:
                resources_data = response.json()
                self.log_step("api_resources", "success", 
                            f"Found {len(resources_data)} resources")
            else:
                self.log_step("api_resources", "failed", 
                            f"Status: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_step("api_endpoints", "failed", str(e))
            return False
    
    def test_github_repo_access(self):
        """Test access to the GitHub repository"""
        try:
            repo_url = "https://api.github.com/repos/AnEntrypoint/nixpacks-test-app"
            response = requests.get(repo_url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                self.log_step("github_repo_access", "success", 
                            f"Repo: {repo_data['full_name']}, Stars: {repo_data['stargazers_count']}")
                return True
            else:
                self.log_step("github_repo_access", "failed", 
                            f"GitHub API status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_step("github_repo_access", "failed", str(e))
            return False
    
    def test_nixpacks_config(self):
        """Test nixpacks configuration"""
        try:
            config_path = "/mnt/c/dev/setdomain/nixpacks-test-app/nixpacks.toml"
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_content = f.read()
                
                self.log_step("nixpacks_config", "success", 
                            "nixpacks.toml exists and readable")
                return True
            else:
                self.log_step("nixpacks_config", "failed", 
                            "nixpacks.toml not found")
                return False
                
        except Exception as e:
            self.log_step("nixpacks_config", "failed", str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("Starting Coolify CLI Deployment Tests...\n")
        
        tests = [
            self.test_basic_connectivity,
            self.test_login_workflow,
            self.test_api_endpoints,
            self.test_github_repo_access,
            self.test_nixpacks_config
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
            time.sleep(1)  # Brief pause between tests
        
        total = len(tests)
        print(f"\n=== Test Results ===")
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Save detailed results
        with open('coolify_cli_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        return passed == total

if __name__ == "__main__":
    tester = CoolifyCLITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
