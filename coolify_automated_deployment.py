import requests
import re
import json
import time
from bs4 import BeautifulSoup

class CoolifyAutomatedDeployment:
    """Complete automated deployment based on visual workflow analysis"""
    
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
        # Real UUIDs from analysis
        self.project_uuid = "ckgkgcwo00sc4ks4okcwgoww"
        self.environment_uuid = "jsso4kwcwgw0oss0co8k4888"
        
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'X-Requested-With': 'XMLHttpRequest'
        })
    
    def login(self, email, password):
        """Authenticate with Coolify"""
        print(f"🔐 Authenticating...")
        
        try:
            # Get login page
            response = self.session.get(f"{self.base_url}/login")
            
            # Extract CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
                self.session.headers['X-CSRF-TOKEN'] = self.csrf_token
            
            # Login
            login_data = {
                'email': email,
                'password': password,
                '_token': self.csrf_token
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data, allow_redirects=False)
            
            if response.status_code == 302:
                # Follow redirect to verify
                response = self.session.get(f"{self.base_url}")
                if 'dashboard' in response.text.lower():
                    print("   ✅ Authentication successful")
                    return True
            
            print("   ❌ Authentication failed")
            return False
            
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    def extract_resource_types(self):
        """Extract available resource types from the selection page"""
        print("🔍 Extracting resource types...")
        
        try:
            # Get resource creation page
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            response = self.session.get(resource_url)
            
            # Extract component information
            component_match = re.search(r'wire:id="([^"]+)"', response.text)
            if component_match:
                component_id = component_match.group(1)
                print(f"   ✅ Found component ID: {component_id}")
            else:
                print("   ❌ Component ID not found")
                return None, None
            
            # Look for application type patterns
            app_patterns = [
                r'"application".*?"id":\s*"([^"]+)"',
                r'application.*?id.*?([a-f0-9-]{36})',
                r'git-based.*?application.*?id["\s:]+["\s]*([a-f0-9-]+)'
            ]
            
            resource_id = None
            for pattern in app_patterns:
                match = re.search(pattern, response.text, re.IGNORECASE)
                if match:
                    resource_id = match.group(1)
                    print(f"   ✅ Found application resource ID: {resource_id}")
                    break
            
            if not resource_id:
                # Try to find any application-related ID
                id_match = re.search(r'"id":\s*"([a-f0-9-]{36})"', response.text)
                if id_match:
                    resource_id = id_match.group(1)
                    print(f"   ✅ Found fallback resource ID: {resource_id}")
            
            return component_id, resource_id
            
        except Exception as e:
            print(f"   ❌ Error extracting resources: {e}")
            return None, None
    
    def select_resource_type(self, component_id, resource_id):
        """Select application resource type using Livewire"""
        print(f"📱 Selecting application resource type...")
        
        try:
            # Prepare Livewire request
            livewire_data = {
                "components": [{
                    "id": component_id,
                    "calls": [{
                        "method": "setType",
                        "params": [resource_id]
                    }]
                }]
            }
            
            # Add required headers
            headers = {
                'X-CSRF-TOKEN': self.csrf_token,
                'X-Livewire': 'true',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.base_url}/livewire/{component_id}",
                json=livewire_data,
                headers=headers
            )
            
            print(f"   📡 Livewire response: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Resource type selected")
                return True, response.text
            else:
                print(f"   ❌ Failed to select resource: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Error selecting resource: {e}")
            return False, None
    
    def configure_application(self, app_name, repo_url, domain_name, livewire_response):
        """Configure application parameters"""
        print(f"⚙️  Configuring application: {app_name}")
        
        try:
            # Parse the Livewire response to find configuration forms
            soup = BeautifulSoup(livewire_response, 'html.parser')
            
            # Look for configuration form or input fields
            forms = soup.find_all('form')
            input_fields = soup.find_all(['input', 'select', 'textarea'])
            
            print(f"   📋 Found {len(forms)} forms and {len(input_fields)} input fields")
            
            # Extract component ID for configuration
            component_match = re.search(r'wire:id="([^"]+)"', livewire_response)
            if not component_match:
                print("   ❌ Configuration component not found")
                return False
            
            config_component_id = component_match.group(1)
            print(f"   ✅ Configuration component ID: {config_component_id}")
            
            # Prepare configuration data
            config_data = {
                "components": [{
                    "id": config_component_id,
                    "data": {
                        "name": app_name,
                        "repository": repo_url,
                        "domain": domain_name,
                        "build_method": "nixpacks"
                    },
                    "calls": [{
                        "method": "submit",
                        "params": []
                    }]
                }]
            }
            
            # Submit configuration
            headers = {
                'X-CSRF-TOKEN': self.csrf_token,
                'X-Livewire': 'true',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f"{self.base_url}/livewire/{config_component_id}",
                json=config_data,
                headers=headers
            )
            
            print(f"   📡 Configuration response: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Application configuration submitted")
                return True, response.text
            else:
                print(f"   ❌ Configuration failed: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            return False, None
    
    def deploy_application(self, app_name, repo_url, domain_name=None):
        """Complete automated deployment workflow"""
        print(f"🚀 Starting automated deployment of {app_name}")
        
        if not domain_name:
            domain_name = f"{app_name}.247420.xyz"
        
        # Step 1: Authentication
        if not self.login("admin@247420.xyz", "123,slam123,slam"):
            return False, "Authentication failed"
        
        # Step 2: Extract resource types
        component_id, resource_id = self.extract_resource_types()
        if not component_id or not resource_id:
            return False, "Could not extract resource information"
        
        # Step 3: Select application type
        success, livewire_response = self.select_resource_type(component_id, resource_id)
        if not success:
            return False, "Failed to select resource type"
        
        # Step 4: Configure application
        success, final_response = self.configure_application(app_name, repo_url, domain_name, livewire_response)
        if not success:
            return False, "Failed to configure application"
        
        print(f"\n✅ Automated deployment initiated successfully!")
        print(f"🌐 Application will be available at: https://{domain_name}")
        print(f"📊 Monitor deployment in Coolify dashboard")
        
        return True, "Deployment initiated successfully"

if __name__ == "__main__":
    # Test the automated deployment
    deployer = CoolifyAutomatedDeployment()
    
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "nixpacks-test.247420.xyz"
    
    success, result = deployer.deploy_application(app_name, repo_url, domain_name)
    
    if success:
        print(f"\n🎉 SUCCESS: {result}")
    else:
        print(f"\n❌ FAILED: {result}")
