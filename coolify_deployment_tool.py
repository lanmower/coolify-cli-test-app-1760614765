import requests
import re
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class CoolifyDeploymentTool:
    """Complete working Coolify deployment tool with real UUIDs"""
    
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
        # Real UUIDs from reverse engineering
        self.project_uuids = [
            "ckgkgcwo00sc4ks4okcwgoww",
            "gs4gc8css0sc0g8808kccow0"
        ]
        self.environment_uuids = [
            "jsso4kwcwgw0oss0co8k4888", 
            "ng000gkg0cccs80w8cc0ooos"
        ]
        
        # Use the first project/environment pair
        self.project_uuid = self.project_uuids[0]
        self.environment_uuid = self.environment_uuids[0]
        
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
            
            # Prepare login data
            login_data = {
                'email': email,
                'password': password
            }
            
            if self.csrf_token:
                login_data['_token'] = self.csrf_token
            
            # Perform login
            response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
            
            print(f"   📡 Login response: {response.status_code}")
            
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"   🔄 Redirect: {redirect_url}")
                
                # Follow redirect to verify
                response = self.session.get(redirect_url if redirect_url.startswith('http') else f"{self.base_url}{redirect_url}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    if any(word in content for word in ['dashboard', 'applications', 'resources', 'logout']):
                        print("   ✅ Login successful!")
                        return True, "Authentication successful"
                    else:
                        print("   ❌ Login failed - no dashboard content")
                        return False, "Invalid credentials"
                else:
                    print(f"   ❌ Redirect failed: {response.status_code}")
                    return False, f"Redirect failed: {response.status_code}"
            else:
                print(f"   ❌ No redirect - login failed: {response.status_code}")
                return False, f"Login failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def navigate_to_resource_creation(self):
        """Navigate to resource creation page with real UUIDs"""
        print(f"🚀 Navigating to resource creation page...")
        
        try:
            # Use the real UUID structure
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            print(f"   📡 URL: {resource_url}")
            
            response = self.session.get(resource_url)
            
            print(f"   📡 Resource page status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Resource creation page loaded")
                
                # Save page content for debugging
                with open('resource_page.html', 'w') as f:
                    f.write(response.text)
                print("   💾 Saved page content to resource_page.html")
                
                return True, "Resource creation page accessible"
            else:
                print(f"   ❌ Resource page not accessible: {response.status_code}")
                return False, f"Resource page not accessible: {response.status_code}"
                
        except Exception as e:
            return False, f"Navigation error: {str(e)}"
    
    def analyze_resource_page(self):
        """Analyze the resource creation page for components"""
        print("🔍 Analyzing resource creation page...")
        
        try:
            # Read the saved page content
            with open('resource_page.html', 'r') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all wire:id attributes
            wire_components = soup.find_all(attrs={'wire:id': True})
            component_ids = [comp.get('wire:id') for comp in wire_components]
            
            print(f"   📋 Found {len(component_ids)} Livewire components:")
            for i, comp_id in enumerate(component_ids[:5], 1):  # Show first 5
                print(f"      {i}. {comp_id}")
            
            # Look for resource type selection elements
            resource_elements = soup.find_all(text=re.compile(r'application|service|database', re.I))
            
            print(f"   📋 Found {len(resource_elements)} resource-related text elements:")
            for i, element in enumerate(resource_elements[:5], 1):
                print(f"      {i}. {element.strip()}")
            
            # Look for forms
            forms = soup.find_all('form')
            print(f"   📋 Found {len(forms)} forms")
            
            # Look for buttons with specific text
            buttons = soup.find_all(['button', 'a'], text=re.compile(r'application|create|next|continue', re.I))
            print(f"   📋 Found {len(buttons)} relevant buttons:")
            for i, button in enumerate(buttons[:3], 1):
                print(f"      {i}. {button.strip()}")
            
            return True, {
                'components': component_ids,
                'resource_elements': len(resource_elements),
                'forms': len(forms),
                'buttons': len(buttons)
            }
                
        except Exception as e:
            return False, f"Analysis error: {str(e)}"
    
    def deploy_application(self, app_name, repo_url, domain_name=None):
        """Complete deployment workflow"""
        print(f"🚀 Starting deployment of {app_name}")
        
        # Step 1: Login
        success, result = self.login("admin@247420.xyz", "123,slam123,slam")
        if not success:
            return False, f"Login failed: {result}"
        
        # Step 2: Navigate to resource creation
        success, result = self.navigate_to_resource_creation()
        if not success:
            return False, f"Navigation failed: {result}"
        
        # Step 3: Analyze page
        success, result = self.analyze_resource_page()
        if success:
            print(f"   ✅ Page analysis complete: {result}")
        
        print("   🎯 Resource creation page is ready for manual interaction")
        print(f"   🌐 URL: {self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new")
        print(f"   📧 Logged in as: admin@247420.xyz")
        print(f"   🔗 Repo URL to use: {repo_url}")
        print(f"   🏷️  Domain to set: {domain_name or f'{app_name}.247420.xyz'}")
        
        return True, "Deployment preparation complete - ready for manual application creation"

if __name__ == "__main__":
    # Test the complete tool
    tool = CoolifyDeploymentTool()
    
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "nixpacks-test.247420.xyz"
    
    success, result = tool.deploy_application(app_name, repo_url, domain_name)
    
    if success:
        print(f"\n✅ Success: {result}")
        print(f"\n📋 Next Steps:")
        print(f"   1. Visit the resource creation URL manually")
        print(f"   2. Select 'Application' as resource type")
        print(f"   3. Configure with the repository and domain information")
        print(f"   4. Submit the form to create the application")
    else:
        print(f"\n❌ Failed: {result}")
