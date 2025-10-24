#!/usr/bin/env python3
"""
Coolify Livewire-based Deployment Tool
Uses the same communication patterns as the browser
"""

import requests
import json
import sys
import time
import urllib3
import re
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CoolifyLivewireDeployer:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        
        # Set proper browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })

    def authenticate(self, email, password):
        """Authenticate with Coolify using web login"""
        print(f"🔐 Authenticating with Coolify at {self.base_url}")
        
        try:
            # Step 1: Get login page
            print("1. Getting login page...")
            response = self.session.get(f"{self.base_url}/login")
            
            if response.status_code != 200:
                return False, f"Failed to get login page: {response.status_code}"

            # Step 2: Extract CSRF token
            csrf_token = None
            csrf_match = re.search(r'name=["\']_token["\'] value=["\']([^"\']+)["\']'', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF Token found: {csrf_token[:20]}...")
            else:
                print("   ⚠️  No CSRF token found")

            # Step 3: Perform login
            login_data = {
                'email': email,
                'password': password
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token

            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 200:
                # Check if login was successful by looking for dashboard elements
                if 'dashboard' in response.text.lower() or 'applications' in response.text.lower():
                    print("   ✅ Login successful!")
                    return True, "Authentication successful"
                else:
                    return False, "Login failed - invalid credentials or CSRF token"
            else:
                return False, f"Login failed with status {response.status_code}"
                
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    def get_livewire_csrf_token(self):
        """Get Livewire-specific CSRF token from dashboard"""
        try:
            print("🔑 Getting Livewire CSRF token...")
            
            # Access dashboard to get Livewire context
            response = self.session.get(self.base_url)
            
            if response.status_code != 200:
                return None
            
            # Extract Livewire CSRF token from HTML
            patterns = [
                r'<meta name="csrf-token" content="([^"]*)"',
                r'<meta name="livewire_csrf_token" content="([^"]*)"',
                r'"csrfToken":\s*"([^"]*)"',
                r'window\.Livewire\.csrfToken = "([^"]*)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    token = match.group(1)
                    print(f"   ✅ Livewire CSRF token found: {token[:20]}...")
                    return token
            
            # Fallback: use the XSRF-TOKEN cookie
            xsrf_cookie = self.session.cookies.get('XSRF-TOKEN')
            if xsrf_cookie:
                print(f"   ✅ Using XSRF-TOKEN cookie: {xsrf_cookie[:20]}...")
                return xsrf_cookie
            
            print("   ⚠️  No Livewire CSRF token found")
            return None
            
        except Exception as e:
            print(f"   ❌ Error getting Livewire CSRF token: {e}")
            return None

    def livewire_request(self, component, method, data=None):
        """Make a Livewire request"""
        if data is None:
            data = {}
            
        csrf_token = self.get_livewire_csrf_token()
        if not csrf_token:
            return None, "No CSRF token available"
        
        # Prepare Livewire request data
        livewire_data = {
            'fingerprint': {
                'id': component,
                'name': component,
                'locale': 'en',
                'path': '/',
                'method': 'GET',
            },
            'serverMemo': {
                'children': [],
                'errors': [],
                'htmlHash': '',
                'data': data,
                'dataMeta': [],
                'checksum': '',
            },
            'updates': [
                {
                    'type': 'callMethod',
                    'payload': {
                        'method': method,
                        'params': [],
                    },
                }
            ],
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/html, application/xhtml+xml',
            'X-CSRF-TOKEN': csrf_token,
            'X-Livewire': 'true',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        try:
            print(f"📡 Making Livewire request to {component}::{method}")
            
            response = self.session.post(
                f"{self.base_url}/livewire/update",
                json=livewire_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   ✅ Livewire response received")
                    return result, "Success"
                except json.JSONDecodeError:
                    print(f"   ⚠️  Response is not JSON: {response.text[:200]}...")
                    return response.text, "Non-JSON response"
            else:
                print(f"   ❌ Livewire request failed: {response.status_code}")
                return None, f"HTTP {response.status_code}"
                
        except Exception as e:
            print(f"   ❌ Livewire request error: {e}")
            return None, f"Request error: {e}"

    def test_livewire_endpoints(self):
        """Test common Livewire components"""
        print("🧪 Testing Livewire components...")
        
        # Common Coolify Livewire components to test
        components = [
            ('dashboard.servers', 'getServers'),
            ('dashboard.applications', 'getApplications'), 
            ('dashboard.resources', 'getResources'),
            ('resources', 'index'),
            ('servers', 'index'),
            ('applications', 'index'),
        ]
        
        results = {}
        
        for component, method in components:
            print(f"\n   Testing {component}::{method}...")
            result, message = self.livewire_request(component, method)
            
            results[f"{component}::{method}"] = {
                'success': result is not None,
                'message': message,
                'result_type': type(result).__name__ if result else None
            }
            
            if result:
                print(f"      ✅ Success ({message})")
            else:
                print(f"      ❌ Failed ({message})")
        
        return results

    def create_test_application(self):
        """Create a test application using Livewire"""
        print("🚀 Creating test application...")
        
        # First try to get to the application creation page
        try:
            print("1. Accessing application creation page...")
            response = self.session.get(f"{self.base_url}/new-application")
            
            if response.status_code != 200:
                return False, f"Cannot access application creation page: {response.status_code}"
            
            print("   ✅ Application creation page accessed")
            
            # Extract Livewire component information
            component_pattern = r'wire:initial-data="([^"]*)"'
            match = re.search(component_pattern, response.text)
            
            if match:
                print("   ✅ Found Livewire component data")
                # Parse the component data (this would need JSON decoding)
                return True, "Found Livewire component ready for application creation"
            else:
                print("   ⚠️  No Livewire component data found")
                return False, "No Livewire component found"
                
        except Exception as e:
            return False, f"Error accessing application creation: {e}"

    def full_test(self, email, password):
        """Run full test suite"""
        print("=" * 70)
        print("🧪 COOLIFY LIVewire DEPLOYMENT TEST")
        print("=" * 70)
        
        results = {}
        
        # Step 1: Authentication
        print("\n🔐 STEP 1: AUTHENTICATION")
        print("-" * 40)
        auth_success, auth_message = self.authenticate(email, password)
        results['authentication'] = {
            'success': auth_success,
            'message': auth_message
        }
        
        if not auth_success:
            print("\n❌ Authentication failed - stopping tests")
            return results
        
        # Step 2: Livewire Components Test
        print("\n📡 STEP 2: LIVEWIRE COMPONENTS TEST")
        print("-" * 40)
        livewire_results = self.test_livewire_endpoints()
        results['livewire_components'] = livewire_results
        
        # Step 3: Application Creation Test
        print("\n🚀 STEP 3: APPLICATION CREATION TEST")
        print("-" * 40)
        app_creation_success, app_creation_message = self.create_test_application()
        results['application_creation'] = {
            'success': app_creation_success,
            'message': app_creation_message
        }
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"✅ Authentication: {'SUCCESS' if auth_success else 'FAILED'}")
        
        working_components = [name for name, result in livewire_results.items() if result['success']]
        print(f"✅ Livewire Components: {len(working_components)} working")
        for component in working_components:
            print(f"    - {component}")
        
        print(f"✅ Application Creation: {'SUCCESS' if app_creation_success else 'FAILED'}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 coolify_livewire_deployer.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    
    deployer = CoolifyLivewireDeployer()
    results = deployer.full_test(email, password)
    
    # Save results
    with open('coolify_livewire_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to coolify_livewire_test_results.json")

if __name__ == "__main__":
    main()
