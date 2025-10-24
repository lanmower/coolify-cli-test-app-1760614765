#!/usr/bin/env python3
"""
Simple Coolify Test Tool
Tests basic functionality without complex regex
"""

import requests
import json
import sys
import time
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SimpleCoolifyTest:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def login(self, email, password):
        """Simple login test"""
        print(f"🔐 Testing login to {self.base_url}")
        
        try:
            # Get login page
            response = self.session.get(f"{self.base_url}/login")
            print(f"   Login page status: {response.status_code}")
            
            if response.status_code != 200:
                return False, f"Cannot access login page: {response.status_code}"
            
            # Simple check for login form
            has_login_form = 'email' in response.text.lower() and 'password' in response.text.lower()
            print(f"   Has login form: {has_login_form}")
            
            if not has_login_form:
                print("   ⚠️  Login form not found - might be already logged in")
                return True, "Already logged in or no form needed"
            
            # Try to login (without complex token extraction)
            login_data = {
                'email': email,
                'password': password,
            }
            
            print("   Submitting login...")
            login_response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=True
            )
            
            print(f"   Login response status: {login_response.status_code}")
            print(f"   Final URL: {login_response.url}")
            
            # Check if we're now logged in
            cookies = list(self.session.cookies.keys())
            print(f"   Session cookies: {cookies}")
            
            if 'coolify_session' in cookies:
                print("   ✅ Session cookie found - likely logged in")
                
                # Verify by checking dashboard content
                if 'dashboard' in login_response.text.lower() or 'logout' in login_response.text.lower():
                    print("   ✅ Dashboard content confirmed")
                    return True, "Login successful"
                else:
                    print("   ⚠️  Session cookie found but dashboard unclear")
                    return True, "Login likely successful"
            else:
                print("   ❌ No session cookie found")
                return False, "Login failed"
                
        except Exception as e:
            return False, f"Login error: {e}"

    def test_dashboard(self):
        """Test dashboard access"""
        print("📊 Testing dashboard access...")
        
        try:
            # Access main dashboard
            response = self.session.get(self.base_url)
            print(f"   Dashboard status: {response.status_code}")
            
            if response.status_code == 200:
                # Look for key dashboard elements
                content_lower = response.text.lower()
                
                has_servers = 'server' in content_lower
                has_applications = 'application' in content_lower
                has_resources = 'resource' in content_lower
                has_livewire = 'livewire' in content_lower
                
                print(f"   Has servers: {has_servers}")
                print(f"   Has applications: {has_applications}")
                print(f"   Has resources: {has_resources}")
                print(f"   Has Livewire: {has_livewire}")
                
                return {
                    'success': True,
                    'has_servers': has_servers,
                    'has_applications': has_applications,
                    'has_resources': has_resources,
                    'has_livewire': has_livewire
                }
            else:
                return {
                    'success': False,
                    'message': f"Dashboard access failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Dashboard test error: {e}"
            }

    def test_application_creation(self):
        """Test application creation page"""
        print("🚀 Testing application creation...")
        
        try:
            # Access new application page
            response = self.session.get(f"{self.base_url}/new-application")
            print(f"   App creation page status: {response.status_code}")
            
            if response.status_code == 200:
                content_lower = response.text.lower()
                
                has_form = 'form' in content_lower
                has_repository = 'repository' in content_lower or 'git' in content_lower
                has_submit = 'submit' in content_lower or 'create' in content_lower
                
                print(f"   Has form: {has_form}")
                print(f"   Has repository field: {has_repository}")
                print(f"   Has submit button: {has_submit}")
                
                return {
                    'success': True,
                    'has_form': has_form,
                    'has_repository': has_repository,
                    'has_submit': has_submit
                }
            else:
                return {
                    'success': False,
                    'message': f"Cannot access app creation: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"App creation test error: {e}"
            }

    def test_endpoints(self):
        """Test common endpoints"""
        print("🔌 Testing common endpoints...")
        
        endpoints = [
            ("/", "Main page"),
            ("/dashboard", "Dashboard"),
            ("/servers", "Servers"),
            ("/applications", "Applications"),
            ("/resources", "Resources"),
            ("/api/v1/servers", "Servers API v1"),
            ("/api/v1/applications", "Applications API v1"),
        ]
        
        results = {}
        
        for endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url)
                
                results[endpoint] = {
                    'status': response.status_code,
                    'success': response.status_code == 200,
                    'description': description
                }
                
                print(f"   {endpoint}: {response.status_code} ({'✅' if response.status_code == 200 else '❌'})")
                
            except Exception as e:
                results[endpoint] = {
                    'status': 'ERROR',
                    'success': False,
                    'description': description,
                    'error': str(e)
                }
                print(f"   {endpoint}: ERROR - {e}")
        
        return results

    def run_full_test(self, email, password):
        """Run complete test suite"""
        print("=" * 70)
        print("🧪 SIMPLE COOLIFY TEST SUITE")
        print("=" * 70)
        
        results = {}
        
        # Step 1: Login
        print("\n🔐 STEP 1: LOGIN TEST")
        print("-" * 40)
        login_success, login_message = self.login(email, password)
        results['login'] = {
            'success': login_success,
            'message': login_message
        }
        
        if not login_success:
            print("\n❌ Login failed - stopping tests")
            return results
        
        # Step 2: Dashboard Test
        print("\n📊 STEP 2: DASHBOARD TEST")
        print("-" * 40)
        dashboard_results = self.test_dashboard()
        results['dashboard'] = dashboard_results
        
        # Step 3: Application Creation Test
        print("\n🚀 STEP 3: APPLICATION CREATION TEST")
        print("-" * 40)
        app_creation_results = self.test_application_creation()
        results['application_creation'] = app_creation_results
        
        # Step 4: Endpoints Test
        print("\n🔌 STEP 4: ENDPOINTS TEST")
        print("-" * 40)
        endpoints_results = self.test_endpoints()
        results['endpoints'] = endpoints_results
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        login_status = "✅ SUCCESS" if login_success else "❌ FAILED"
        print(f"Login: {login_status}")
        
        if dashboard_results.get('success'):
            print("Dashboard: ✅ SUCCESS")
            features = []
            if dashboard_results.get('has_servers'): features.append('servers')
            if dashboard_results.get('has_applications'): features.append('applications')
            if dashboard_results.get('has_resources'): features.append('resources')
            if dashboard_results.get('has_livewire'): features.append('livewire')
            print(f"  Features: {', '.join(features)}")
        else:
            print("Dashboard: ❌ FAILED")
        
        app_status = "✅ SUCCESS" if app_creation_results.get('success') else "❌ FAILED"
        print(f"Application Creation: {app_status}")
        
        working_endpoints = [ep for ep, result in endpoints_results.items() if result.get('success')]
        print(f"Working Endpoints: {len(working_endpoints)}/{len(endpoints_results)}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 simple_coolify_test.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    
    tester = SimpleCoolifyTest()
    results = tester.run_full_test(email, password)
    
    # Save results
    with open('simple_coolify_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to simple_coolify_test_results.json")

if __name__ == "__main__":
    main()
