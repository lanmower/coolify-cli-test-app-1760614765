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
            csrf_match = re.search(r'name=["\']_token["\']\s*value=["\']([^"\']+)["\']', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF Token found: {csrf_token[:20]}...")
            else:
                print("   ⚠️  No CSRF token found")
            
            # Step 3: Perform login
            login_data = {
                'email': email,
                'password': password,
                '_token': csrf_token or '',
            }
            
            print("2. Submitting login...")
            login_response = self.session.post(
                f"{self.base_url}/login",
                data=login_data,
                allow_redirects=False
            )
            
            # Step 4: Check authentication
            if 'coolify_session' in [cookie.name for cookie in self.session.cookies]:
                print("   ✅ Session cookie found!")
                
                # Follow redirect to dashboard
                if login_response.status_code in [301, 302, 303]:
                    redirect_url = login_response.headers.get('Location', self.base_url)
                    print(f"   Following redirect to: {redirect_url}")
                    
                    dashboard_response = self.session.get(redirect_url)
                    if dashboard_response.status_code == 200:
                        print("   ✅ Dashboard accessed successfully!")
                        return True, "Authentication successful"
                
                return True, "Authentication successful"
            else:
                print("   ❌ No session cookie found")
                return False, "Authentication failed"
                
        except Exception as e:
            return False, f"Authentication error: {e}"

    def test_livewire_endpoints(self):
        """Test Livewire endpoints with simpler approach"""
        print("🧪 Testing Livewire communication...")
        
        try:
            # Get dashboard page to extract Livewire components
            print("1. Getting dashboard page...")
            response = self.session.get(self.base_url)
            
            if response.status_code != 200:
                return {'success': False, 'message': f"Cannot access dashboard: {response.status_code}"}
            
            print("   ✅ Dashboard accessed")
            
            # Look for Livewire components in the HTML
            livewire_patterns = [
                r'wire:initial-data=["']([^"']*)["']',
                r'wire:id=["']([^"']*)["']',
                r'livewire:[^=]*=["']([^"']*)["']',
            ]
            
            found_components = []
            for pattern in livewire_patterns:
                matches = re.findall(pattern, response.text)
                if matches:
                    found_components.extend(matches)
                    print(f"   Found {len(matches)} components with pattern: {pattern}")
            
            if found_components:
                print(f"   ✅ Found {len(found_components)} Livewire components")
                return {
                    'success': True,
                    'components_found': len(found_components),
                    'components': found_components[:5]  # Show first 5
                }
            else:
                print("   ⚠️  No Livewire components found")
                return {
                    'success': False,
                    'message': "No Livewire components found"
                }
                
        except Exception as e:
            return {'success': False, 'message': f"Error testing Livewire: {e}"}

    def test_application_creation(self):
        """Test accessing application creation page"""
        print("🚀 Testing application creation access...")
        
        try:
            # Access new application page
            response = self.session.get(f"{self.base_url}/new-application")
            
            if response.status_code == 200:
                print("   ✅ Application creation page accessible")
                
                # Check for form elements
                has_repo_input = 'repository' in response.text.lower()
                has_git_options = 'github' in response.text.lower() or 'git' in response.text.lower()
                
                return {
                    'success': True,
                    'has_repo_input': has_repo_input,
                    'has_git_options': has_git_options
                }
            else:
                return {
                    'success': False,
                    'message': f"Cannot access application creation: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"Error testing application creation: {e}"
            }

    def full_test(self, email, password):
        """Run comprehensive test suite"""
        print("=" * 70)
        print("🧪 COOLIFY COMPREHENSIVE TEST")
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
        
        # Step 2: Livewire Test
        print("\n📡 STEP 2: LIVEWIRE COMPONENTS")
        print("-" * 40)
        livewire_results = self.test_livewire_endpoints()
        results['livewire'] = livewire_results
        
        # Step 3: Application Creation Test
        print("\n🚀 STEP 3: APPLICATION CREATION")
        print("-" * 40)
        app_results = self.test_application_creation()
        results['application_creation'] = app_results
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"✅ Authentication: {'SUCCESS' if auth_success else 'FAILED'}")
        print(f"✅ Livewire Components: {'SUCCESS' if livewire_results.get('success') else 'FAILED'}")
        if livewire_results.get('components_found'):
            print(f"    - Found {livewire_results['components_found']} components")
        print(f"✅ Application Creation: {'SUCCESS' if app_results.get('success') else 'FAILED'}")
        
        return results

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 coolify_livewire_fixed.py <email> <password>")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]
    
    deployer = CoolifyLivewireDeployer()
    results = deployer.full_test(email, password)
    
    # Save results
    with open('coolify_livewire_fixed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to coolify_livewire_fixed_results.json")

if __name__ == "__main__":
    main()
