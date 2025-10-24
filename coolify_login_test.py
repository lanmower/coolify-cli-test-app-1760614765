import requests
import re
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class CoolifyAPI:
    """Fixed Coolify API wrapper with better login detection"""
    
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.project_uuid = None
        self.environment_uuid = None
        
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def login(self, email, password):
        """Authenticate with Coolify"""
        print(f"🔐 Logging into {self.base_url}")
        
        try:
            # Get login page and extract CSRF token
            response = self.session.get(f"{self.base_url}/login")
            if response.status_code != 200:
                return False, f"Failed to access login page: {response.status_code}"
            
            # Extract CSRF token from meta tags
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
            else:
                # Try alternative method
                csrf_match = re.search(r'name=["\']_token["\'] content=["\']([^"\']+)["\']', response.text)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
            
            if self.csrf_token:
                print(f"   ✅ CSRF Token: {self.csrf_token[:20]}...")
            else:
                print("   ⚠️  No CSRF token found")
            
            # Prepare login data
            login_data = {
                'email': email,
                'password': password
            }
            
            if self.csrf_token:
                login_data['_token'] = self.csrf_token
            
            # Perform login
            response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
            
            print(f"   📡 Login response status: {response.status_code}")
            
            # Check for redirect (302) which indicates successful login
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"   🔄 Redirect to: {redirect_url}")
                
                if 'dashboard' in redirect_url or redirect_url == '/' or redirect_url.endswith('/dashboard'):
                    print("   ✅ Login successful (redirect to dashboard)!")
                    return True, "Authentication successful"
            
            # If no redirect, check if we're still on login page or moved to dashboard
            elif response.status_code == 200:
                response_text = response.text.lower()
                
                # Check if we're logged in by looking for dashboard indicators
                dashboard_indicators = ['dashboard', 'applications', 'deployments', 'resources', 'logout']
                login_indicators = ['login', 'password', 'sign in', 'forgot password']
                
                dashboard_score = sum(1 for indicator in dashboard_indicators if indicator in response_text)
                login_score = sum(1 for indicator in login_indicators if indicator in response_text)
                
                print(f"   📊 Dashboard indicators: {dashboard_score}")
                print(f"   📊 Login indicators: {login_score}")
                
                if dashboard_score > login_score:
                    print("   ✅ Login successful (dashboard content detected)!")
                    return True, "Authentication successful"
                else:
                    print("   ❌ Still on login page - credentials may be invalid")
                    return False, "Invalid credentials"
            else:
                return False, f"Login failed with status {response.status_code}"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def test_dashboard_access(self):
        """Test if we can access the dashboard"""
        print("🧪 Testing dashboard access...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            
            print(f"   📡 Dashboard response: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Look for dashboard-specific content
                if 'dashboard' in content and ('application' in content or 'deployment' in content):
                    print("   ✅ Dashboard accessible with content!")
                    
                    # Now extract UUIDs
                    return self.extract_uuids_from_content(content)
                else:
                    print("   ❌ Dashboard page but no dashboard content")
                    return False, "Dashboard accessible but missing content"
            else:
                print(f"   ❌ Dashboard not accessible: {response.status_code}")
                return False, f"Dashboard not accessible: {response.status_code}"
                
        except Exception as e:
            return False, f"Dashboard test error: {str(e)}"
    
    def extract_uuids_from_content(self, content):
        """Extract UUIDs from page content"""
        print("🔍 Extracting UUIDs from content...")
        
        # Look for project UUID patterns
        project_matches = re.findall(r'/project/([a-z0-9]{32})', content)
        if project_matches:
            self.project_uuid = project_matches[0]
            print(f"   ✅ Found project UUID: {self.project_uuid}")
        
        # Look for environment UUID patterns  
        env_matches = re.findall(r'/environment/([a-z0-9]{32})', content)
        if env_matches:
            self.environment_uuid = env_matches[0]
            print(f"   ✅ Found environment UUID: {self.environment_uuid}")
        
        if self.project_uuid and self.environment_uuid:
            return True, "UUIDs extracted successfully"
        else:
            return False, "Could not extract required UUIDs"

if __name__ == "__main__":
    # Test the fixed login
    api = CoolifyAPI()
    
    print("=== TESTING LOGIN AND DASHBOARD ACCESS ===")
    
    # Test login
    success, result = api.login("admin@247420.xyz", "123,slam123,slam")
    print(f"Login result: {success} - {result}")
    
    if success:
        # Test dashboard access
        success, result = api.test_dashboard_access()
        print(f"Dashboard result: {success} - {result}")
        
        if success:
            print(f"✅ Ready for deployment!")
            print(f"   Project UUID: {api.project_uuid}")
            print(f"   Environment UUID: {api.environment_uuid}")
        else:
            print(f"❌ Dashboard access failed: {result}")
    else:
        print(f"❌ Login failed: {result}")
