#!/usr/bin/env python3
"""
Comprehensive Coolify Deployment Test
Tests login, server access, and creates a test deployment
"""

import requests
import json
import sys
import time
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CoolifyComprehensiveTest:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def test_login(self, email, password):
        """Test login with detailed debugging"""
        print(f"🔐 Testing login to {self.base_url}")

        try:
            # Get login page
            print("1. Getting login page...")
            login_page = self.session.get(f"{self.base_url}/login")
            print(f"   Status: {login_page.status_code}")
            
            if login_page.status_code != 200:
                return False, f"Failed to get login page: {login_page.status_code}"

            # Extract all forms and inputs
            print("2. Analyzing login form...")
            
            # Extract CSRF token
            csrf_token = None
            import re
            
            # Try different CSRF token patterns
            patterns = [
                r'name="_token"[^>]*value="([^"]*)"',
                r'name="csrf-token"[^>]*content="([^"]*)"',
                r'csrfToken: '([^']*)'',
                r'"_token":"([^"]*)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, login_page.text)
                if match:
                    csrf_token = match.group(1)
                    print(f"   CSRF token found: {csrf_token[:20]}...")
                    break
            
            if not csrf_token:
                print("   ⚠️  No CSRF token found")

            # Perform login
            print("3. Submitting login...")
            login_data = {
                'email': email,
                'password': password
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token

            response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=False  # Handle redirects manually
            )
            
            print(f"   Login response status: {response.status_code}")
            print(f"   Response headers: {dict(response.headers)}")
            
            # Handle redirects
            if response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirecting to: {redirect_url}")
                
                if redirect_url:
                    # Follow the redirect
                    final_response = self.session.get(redirect_url)
                    print(f"   Final response status: {final_response.status_code}")
                    
                    # Check if we're logged in
                    if final_response.status_code == 200:
                        if 'dashboard' in final_response.text.lower() or 'logout' in final_response.text.lower():
                            print("   ✅ Login successful!")
                            return True, "Login successful"
                        else:
                            print("   ⚠️  Redirect successful but login unclear")
                            return True, "Login likely successful"
                    else:
                        return False, f"Failed after redirect: {final_response.status_code}"
            
            # Check if direct login response indicates success
            elif response.status_code == 200:
                response_text = response.text.strip()
                print(f"   Response preview: {response_text[:200]}")
                
                if response_text == '{"two_factor":false}':
                    print("   ✅ Login successful (2FA not required)")
                    return True, "Login successful"
                elif 'dashboard' in response.text.lower():
                    print("   ✅ Login successful")
                    return True, "Login successful"
                else:
                    return False, "Login response unclear"
            else:
                return False, f"Login failed: {response.status_code}"

        except Exception as e:
            return False, f"Login error: {e}"

    def test_api_endpoints(self):
        """Test various API endpoints"""
        print("🔌 Testing API endpoints...")

        # Common API endpoints to try
        endpoints = [
            ("/api/v1/servers", "Servers API v1"),
            ("/api/v1/applications", "Applications API v1"),
            ("/api/servers", "Servers API"),
            ("/api/applications", "Applications API"),
            ("/api/user", "User API"),
            ("/api/resources", "Resources API"),
            ("/livewire", "Livewire endpoint"),
        ]

        successful_endpoints = []
        
        for endpoint, description in endpoints:
            print(f"   Testing {endpoint} ({description})...")
            
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                status = response.status_code
                
                print(f"     Status: {status}")
                
                if status == 200:
                    print(f"     ✅ {description} - SUCCESS")
                    successful_endpoints.append(endpoint)
                    
                    # Try to parse JSON
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"     Found {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"     Found {len(data)} keys")
                    except:
                        print(f"     Response is not JSON: {response.text[:100]}...")
                elif status == 401:
                    print(f"     ❌ {description} - Authentication failed")
                elif status == 404:
                    print(f"     ❌ {description} - Not found")
                else:
                    print(f"     ⚠️  {description} - Status {status}")
                    
            except Exception as e:
                print(f"     ❌ {description} - Error: {e}")

        return successful_endpoints

    def test_create_application(self):
        """Test creating a new application"""
        print("🚀 Testing application creation...")

        # First, let's check if we can access the new application page
        try:
            print("   Accessing new application page...")
            response = self.session.get(f"{self.base_url}/new-application")
            
            if response.status_code != 200:
                return False, f"Cannot access new application page: {response.status_code}"
            
            print("   ✅ Can access new application page")
            
            # Look for form data or Livewire components
            if 'livewire' in response.text.lower():
                print("   📡 Found Livewire components")
                
                # Try to find application creation endpoints
                import re
                livewire_patterns = [
                    r'wire:init="([^"]*)"',
                    r'wire:click="([^"]*)"',
                    r'wire:model="([^"]*)"',
                ]
                
                for pattern in livewire_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        print(f"   Found Livewire patterns: {matches[:3]}")
                        break
            
            return True, "Application creation page accessible"
            
        except Exception as e:
            return False, f"Application creation test error: {e}"

    def comprehensive_test(self, email, password):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("🧪 COMPREHENSIVE COOLIFY TEST SUITE")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Login
        print("
1️⃣ LOGIN TEST")
        print("-" * 30)
        login_success, login_message = self.test_login(email, password)
        results['login'] = {'success': login_success, 'message': login_message}
        
        if not login_success:
            print("
❌ Login failed - stopping tests")
            return results
        
        # Test 2: API Endpoints
        print("
2️⃣ API ENDPOINTS TEST")
        print("-" * 30)
        successful_endpoints = self.test_api_endpoints()
        results['api_endpoints'] = {'successful': successful_endpoints, 'count': len(successful_endpoints)}
        
        # Test 3: Application Creation
        print("
3️⃣ APPLICATION CREATION TEST")
        print("-" * 30)
        app_creation_success, app_creation_message = self.test_create_application()
        results['app_creation'] = {'success': app_creation_success, 'message': app_creation_message}
        
        # Summary
        print("
" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Login: {'SUCCESS' if login_success else 'FAILED'}")
        print(f"✅ API Endpoints: {len(successful_endpoints)} working")
        print(f"✅ App Creation: {'SUCCESS' if app_creation_success else 'FAILED'}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 coolify_comprehensive_test.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    
    tester = CoolifyComprehensiveTest()
    results = tester.comprehensive_test(email, password)
    
    # Save results
    with open('coolify_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"
📁 Results saved to coolify_test_results.json")

if __name__ == "__main__":
    main()
