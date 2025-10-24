import requests
import re
import time
import json
from urllib.parse import urljoin

class CoolifyDeploymentTester:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def authenticate(self, email, password):
        """Authenticate with Coolify"""
        print(f"🔐 Authenticating with Coolify at {self.base_url}")
        
        try:
            # Get login page
            print("1. Getting login page...")
            response = self.session.get(f"{self.base_url}/login")
            
            if response.status_code != 200:
                return False, f"Failed to get login page: {response.status_code}"

            # Extract CSRF token
            csrf_token = None
            csrf_match = re.search(r'name=["\']_token["\'] content=["\']([^"\']+)["\']', response.text)
            if not csrf_match:
                csrf_match = re.search(r'name=["\']_token["\'] value=["\']([^"\']+)["\']', response.text)
            
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF Token found: {csrf_token[:20]}...")
            else:
                print("   ⚠️  No CSRF token found")

            # Prepare login data
            login_data = {
                'email': email,
                'password': password
            }
            
            if csrf_token:
                login_data['_token'] = csrf_token

            # Perform login
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 200:
                # Check if login was successful
                if 'dashboard' in response.text.lower() or 'applications' in response.text.lower():
                    print("   ✅ Login successful!")
                    return True, "Authentication successful"
                else:
                    print("   ❌ Login failed - checking for error messages")
                    if 'invalid' in response.text.lower() or 'error' in response.text.lower():
                        return False, "Invalid credentials"
                    return False, "Login failed - unknown reason"
            else:
                return False, f"Login failed with status {response.status_code}"
                
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def explore_dashboard(self):
        """Explore the dashboard to understand the UI structure"""
        print("🔍 Exploring dashboard structure...")
        
        try:
            # Get dashboard
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code != 200:
                print(f"❌ Dashboard not accessible: {response.status_code}")
                return False
            
            print("✅ Dashboard accessible")
            
            # Look for key elements
            content = response.text
            
            # Check for application creation
            if 'new application' in content.lower() or 'create application' in content.lower():
                print("✅ Application creation option found")
            
            # Check for servers
            if 'server' in content.lower():
                print("✅ Server management found")
            
            # Check for deployment-related content
            if 'deploy' in content.lower():
                print("✅ Deployment options found")
            
            # Look for Livewire components
            if 'wire:' in content or 'livewire' in content.lower():
                print("✅ Livewire components detected")
            
            # Look for API endpoints or forms
            forms = re.findall(r'<form[^>]*action="([^"]*)"[^>]*>', content)
            if forms:
                print(f"✅ Found {len(forms)} forms")
                for form in forms[:3]:  # Show first 3
                    print(f"   Form action: {form}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error exploring dashboard: {e}")
            return False
    
    def test_network_endpoints(self):
        """Test various API endpoints to understand the API structure"""
        print("🌐 Testing API endpoints...")
        
        endpoints = [
            '/api/v1/user',
            '/api/v1/servers', 
            '/api/v1/applications',
            '/api/v1/deployments',
            '/api/servers',
            '/api/applications',
            '/api/user'
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                results[endpoint] = {
                    'status': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_preview': response.text[:100] if response.status_code == 200 else None
                }
                print(f"   {endpoint}: {response.status_code}")
            except Exception as e:
                results[endpoint] = {'error': str(e)}
                print(f"   {endpoint}: Error - {e}")
        
        return results

if __name__ == "__main__":
    deployer = CoolifyDeploymentTester()
    
    # Authenticate
    success, result = deployer.authenticate("admin@247420.xyz", "123,slam123,slam")
    if success:
        print("✅ Authentication successful!")
        
        # Explore dashboard
        deployer.explore_dashboard()
        
        # Test endpoints
        endpoint_results = deployer.test_network_endpoints()
        print("\n=== API ENDPOINT RESULTS ===")
        for endpoint, result in endpoint_results.items():
            print(f"{endpoint}: {result}")
            
    else:
        print(f"❌ Authentication failed: {result}")
