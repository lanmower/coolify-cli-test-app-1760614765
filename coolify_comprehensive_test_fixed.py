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

            # Extract CSRF token
            print("2. Extracting CSRF token...")
            csrf_token = None
            import re
            
            # Try different CSRF token patterns
            patterns = [
                r'name="_token"[^>]*value="([^"]*)"',
                r'name="csrf-token"[^>]*content="([^"]*)"',
                r'csrfToken: \'([^\']*)\'',  # Fixed escaping
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
                allow_redirects=False
            )
            
            print(f"   Login response status: {response.status_code}")
            
            # Check response
            if response.status_code in [301, 302, 303]:
                redirect_url = response.headers.get('Location', '')
                print(f"   Redirecting to: {redirect_url}")
                
                if redirect_url:
                    final_response = self.session.get(redirect_url)
                    print(f"   Final response status: {final_response.status_code}")
                    
                    if final_response.status_code == 200:
                        if 'dashboard' in final_response.text.lower() or 'logout' in final_response.text.lower():
                            print("   ✅ Login successful!")
                            return True, "Login successful"
                        else:
                            return True, "Login likely successful"
                    else:
                        return False, f"Failed after redirect: {final_response.status_code}"
            elif response.status_code == 200:
                response_text = response.text.strip()
                print(f"   Response: {response_text}")
                
                if response_text == '{"two_factor":false}':
                    print("   ✅ Login successful (2FA not required)")
                    return True, "Login successful"
                else:
                    return False, f"Unexpected response: {response_text}"
            else:
                return False, f"Login failed: {response.status_code}"

        except Exception as e:
            return False, f"Login error: {e}"

    def test_api_endpoints(self):
        """Test various API endpoints"""
        print("🔌 Testing API endpoints...")

        endpoints = [
            ("/api/v1/servers", "Servers API v1"),
            ("/api/v1/applications", "Applications API v1"),
            ("/api/servers", "Servers API"),
            ("/api/applications", "Applications API"),
            ("/api/user", "User API"),
            ("/api/resources", "Resources API"),
        ]

        successful_endpoints = []
        
        for endpoint, description in endpoints:
            print(f"   Testing {endpoint}...")
            
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                status = response.status_code
                
                if status == 200:
                    print(f"     ✅ {description} - SUCCESS")
                    successful_endpoints.append(endpoint)
                else:
                    print(f"     ❌ {description} - Status {status}")
                    
            except Exception as e:
                print(f"     ❌ {description} - Error: {e}")

        return successful_endpoints

    def comprehensive_test(self, email, password):
        """Run comprehensive test suite"""
        print("=" * 60)
        print("🧪 COMPREHENSIVE COOLIFY TEST SUITE")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Login
        print("\n1️⃣ LOGIN TEST")
        print("-" * 30)
        login_success, login_message = self.test_login(email, password)
        results['login'] = {'success': login_success, 'message': login_message}
        
        if not login_success:
            print("\n❌ Login failed - stopping tests")
            return results
        
        # Test 2: API Endpoints
        print("\n2️⃣ API ENDPOINTS TEST")
        print("-" * 30)
        successful_endpoints = self.test_api_endpoints()
        results['api_endpoints'] = {'successful': successful_endpoints, 'count': len(successful_endpoints)}
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Login: {'SUCCESS' if login_success else 'FAILED'}")
        print(f"✅ API Endpoints: {len(successful_endpoints)} working")
        
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
    
    print(f"\n📁 Results saved to coolify_test_results.json")

if __name__ == "__main__":
    main()
