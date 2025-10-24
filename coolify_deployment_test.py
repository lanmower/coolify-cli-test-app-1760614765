#!/usr/bin/env python3
"""
Coolify Deployment Testing Script
Tests deployment of AnEntrypoint/nixpacks-test-app to coolify.247420.xyz
Captures all network communications and Livewire interactions
"""

import requests
import json
import time
from urllib.parse import urljoin

class CoolifyDeploymentTester:
    def __init__(self):
        self.base_url = "https://coolify.247420.xyz"
        self.session = requests.Session()
        self.username = "admin@247420.xyz"
        self.password = "123,slam123,slam"
        self.network_log = []
        
    def log_request(self, method, url, data=None, response=None):
        """Log all network requests"""
        log_entry = {
            'timestamp': time.time(),
            'method': method,
            'url': url,
            'data': data,
            'response_status': response.status_code if response else None,
            'response_headers': dict(response.headers) if response else None,
            'response_data': response.text[:1000] if response and hasattr(response, 'text') else None
        }
        self.network_log.append(log_entry)
        print(f"📡 {method} {url} -> {response.status_code if response else 'N/A'}")
        
    def get_login_page(self):
        """Get login page and extract CSRF token"""
        print("🔍 Getting login page...")
        response = self.session.get(f"{self.base_url}/login")
        self.log_request('GET', f"{self.base_url}/login", response=response)
        
        # Extract CSRF token from page
        csrf_token = None
        if 'csrf-token' in response.text:
            import re
            csrf_match = re.search(r'name="csrf-token" content="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
        
        print(f"🔑 CSRF Token: {csrf_token}")
        return csrf_token
        
    def login(self, csrf_token):
        """Perform login"""
        print("🚪 Attempting login...")
        login_data = {
            'email': self.username,
            'password': self.password,
            '_token': csrf_token
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        self.log_request('POST', f"{self.base_url}/login", login_data, response)
        
        if response.status_code == 302:
            print("✅ Login successful - redirected")
            return True
        else:
            print(f"❌ Login failed - status: {response.status_code}")
            return False
            
    def get_applications_page(self):
        """Get applications page to find deployment options"""
        print("📱 Getting applications page...")
        response = self.session.get(f"{self.base_url}/applications")
        self.log_request('GET', f"{self.base_url}/applications", response=response)
        
        return response
        
    def test_livewire_endpoint(self):
        """Test Livewire endpoint with typical data"""
        print("⚡ Testing Livewire endpoint...")
        
        # Typical Livewire data structure
        livewire_data = {
            'fingerprint': {
                'id': 'test-component',
                'name': 'deployment.test',
                'locale': 'en',
                'path': '/',
                'method': 'GET'
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': {},
                'dataMeta': [],
                'checksum': 'test'
            },
            'updates': [],
            'meta': {
                'components': {
                    'test-component': {
                        'id': 'test-component',
                        'name': 'deployment.test'
                    }
                }
            }
        }
        
        headers = {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': self.session.cookies.get('XSRF-TOKEN', ''),
            'X-Livewire': 'true'
        }
        
        response = self.session.post(
            f"{self.base_url}/livewire/update",
            json=livewire_data,
            headers=headers
        )
        self.log_request('POST', f"{self.base_url}/livewire/update", livewire_data, response)
        
        return response
        
    def simulate_deployment_request(self):
        """Simulate a deployment request structure"""
        print("🚀 Simulating deployment request structure...")
        
        deployment_data = {
            'repository': 'https://github.com/AnEntrypoint/nixpacks-test-app',
            'branch': 'main',
            'build_pack': 'nixpacks',
            'destination': {
                'domain': 'test-app.247420.xyz'
            },
            'environment_variables': {
                'NODE_ENV': 'production',
                'PORT': '3000'
            },
            'nixpacks_config': {
                'phases': {
                    'setup': {'nixPkgs': ['nodejs_18', 'npm']},
                    'build': {'cmds': ['npm install']},
                    'install': {'onlyIncludes': ['package.json', 'package-lock.json']}
                },
                'start': {'cmd': 'npm start'},
                'variables': {
                    'NODE_ENV': 'production',
                    'PORT': '3000'
                }
            }
        }
        
        print("📋 Deployment request structure:")
        print(json.dumps(deployment_data, indent=2))
        
        return deployment_data
        
    def run_test(self):
        """Run complete test sequence"""
        print("🎯 Starting Coolify Deployment Test")
        print("=" * 50)
        
        # Step 1: Get login page
        csrf_token = self.get_login_page()
        if not csrf_token:
            print("❌ Could not get CSRF token")
            return False
            
        # Step 2: Login
        if not self.login(csrf_token):
            print("❌ Login failed")
            return False
            
        # Step 3: Get applications page
        apps_response = self.get_applications_page()
        
        # Step 4: Test Livewire endpoint
        livewire_response = self.test_livewire_endpoint()
        
        # Step 5: Simulate deployment request
        deployment_structure = self.simulate_deployment_request()
        
        # Step 6: Save network log
        self.save_network_log()
        
        print("✅ Test completed successfully!")
        return True
        
    def save_network_log(self):
        """Save network log to file"""
        log_file = "/mnt/c/dev/setdomain/network_log.json"
        with open(log_file, 'w') as f:
            json.dump(self.network_log, f, indent=2)
        print(f"💾 Network log saved to {log_file}")
        
if __name__ == "__main__":
    tester = CoolifyDeploymentTester()
    tester.run_test()
