import requests
import re
from urllib.parse import urljoin

class SimpleCoolifyDeployer:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
    
    def test_deployment(self):
        """Test basic deployment functionality"""
        print("🧪 Testing deployment functionality...")
        
        try:
            # Check dashboard
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code == 200:
                print("   ✅ Dashboard accessible")
            else:
                print(f"   ❌ Dashboard not accessible: {response.status_code}")
            
            return True
        except Exception as e:
            print(f"   ❌ Deployment test failed: {e}")
            return False

if __name__ == "__main__":
    deployer = SimpleCoolifyDeployer()
    success, result = deployer.authenticate("admin@247420.xyz", "123,slam123,slam")
    if success:
        print("✅ Authentication successful!")
        deployer.test_deployment()
    else:
        print(f"❌ Authentication failed: {result}")
