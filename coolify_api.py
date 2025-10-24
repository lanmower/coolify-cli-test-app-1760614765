import requests
import re
import json
import time
from urllib.parse import urljoin, parse_qs
from bs4 import BeautifulSoup

class CoolifyAPI:
    """Complete Coolify API wrapper based on reverse engineering findings"""
    
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        self.project_id = None
        self.environment_id = None
        
        # Set proper headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': None,  # Will be set dynamically
            'X-Livewire': 'true'   # Required for Livewire requests
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
                self.session.headers['X-CSRF-TOKEN'] = self.csrf_token
            else:
                print("   ⚠️  No CSRF token found")
            
            # Perform login
            login_data = {
                'email': email,
                'password': password,
                '_token': self.csrf_token
            }
            
            response = self.session.post(f"{self.base_url}/login", data=login_data)
            
            if response.status_code == 302 or (response.status_code == 200 and 'dashboard' in response.text.lower()):
                print("   ✅ Login successful!")
                return True, "Authentication successful"
            else:
                return False, f"Login failed: {response.status_code}"
                
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def get_dashboard_info(self):
        """Get dashboard information and extract project/environment IDs"""
        print("📊 Getting dashboard information...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code != 200:
                return False, f"Dashboard not accessible: {response.status_code}"
            
            # Extract project and environment IDs from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for project links or forms
            project_links = soup.find_all('a', href=re.compile(r'/project/'))
            if project_links:
                # Extract project ID from first project link
                href = project_links[0].get('href', '')
                project_match = re.search(r'/project/(\d+)', href)
                if project_match:
                    self.project_id = project_match.group(1)
                    print(f"   ✅ Found project ID: {self.project_id}")
            
            # Look for environment links
            env_links = soup.find_all('a', href=re.compile(r'/environment/'))
            if env_links:
                href = env_links[0].get('href', '')
                env_match = re.search(r'/environment/(\d+)', href)
                if env_match:
                    self.environment_id = env_match.group(1)
                    print(f"   ✅ Found environment ID: {self.environment_id}")
            
            if not self.project_id:
                # Try to find default project
                self.project_id = "1"  # Default assumption
                print("   ⚠️  Using default project ID: 1")
            
            if not self.environment_id:
                # Try to find default environment
                self.environment_id = "1"  # Default assumption
                print("   ⚠️  Using default environment ID: 1")
            
            return True, "Dashboard info extracted"
            
        except Exception as e:
            return False, f"Dashboard error: {str(e)}"
    
    def create_application(self, app_name, repo_url, domain_name=None, build_method="nixpacks"):
        """Create a new application using Livewire"""
        print(f"🚀 Creating application: {app_name}")
        
        if not self.project_id or not self.environment_id:
            return False, "Project or environment ID not set"
        
        try:
            # Navigate to resource creation page
            resource_url = f"{self.base_url}/project/{self.project_id}/environment/{self.environment_id}/new"
            response = self.session.get(resource_url)
            
            if response.status_code != 200:
                return False, f"Resource page not accessible: {response.status_code}"
            
            # Extract Livewire component ID for resource selection
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for application selection component
            app_components = soup.find_all('div', {'wire:id': True})
            component_id = None
            
            for component in app_components:
                if 'application' in component.get_text().lower():
                    component_id = component.get('wire:id')
                    break
            
            if not component_id:
                # Try to extract from wire:click attributes
                wire_clicks = soup.find_all(attrs={'wire:click': True})
                for element in wire_clicks:
                    if 'application' in element.get_text().lower():
                        # Extract component ID from parent
                        parent = element.find_parent(attrs={'wire:id': True})
                        if parent:
                            component_id = parent.get('wire:id')
                            break
            
            if not component_id:
                return False, "Could not find Livewire component for application creation"
            
            print(f"   ✅ Found component ID: {component_id}")
            
            # First, select application type
            select_data = {
                'components': [{
                    'id': component_id,
                    'calls': [
                        {'method': 'selectResourceType', 'params': ['application']}
                    ]
                }]
            }
            
            livewire_response = self.session.post(
                f"{self.base_url}/livewire/{component_id}",
                json=select_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"   📡 Resource selection: {livewire_response.status_code}")
            
            # Now configure the application
            config_data = {
                'components': [{
                    'id': component_id,
                    'data': {
                        'name': app_name,
                        'repository': repo_url,
                        'build_method': build_method,
                        'domain': domain_name or f"{app_name}.247420.xyz"
                    },
                    'calls': [
                        {'method': 'submit', 'params': []}
                    ]
                }]
            }
            
            livewire_response = self.session.post(
                f"{self.base_url}/livewire/{component_id}",
                json=config_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if livewire_response.status_code == 200:
                print(f"   ✅ Application creation initiated")
                return True, "Application created successfully"
            else:
                return False, f"Application creation failed: {livewire_response.status_code}"
                
        except Exception as e:
            return False, f"Application creation error: {str(e)}"
    
    def monitor_deployment(self, app_name, timeout=300):
        """Monitor deployment progress"""
        print(f"📊 Monitoring deployment for {app_name}...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check deployment status
                response = self.session.get(f"{self.base_url}/dashboard")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Look for deployment status
                    status_elements = soup.find_all(text=re.compile(r'deploy|running|success|error', re.I))
                    
                    for element in status_elements:
                        if app_name.lower() in element.lower():
                            print(f"   📈 Status: {element.strip()}")
                            
                            if 'success' in element.lower() or 'deployed' in element.lower():
                                print(f"   ✅ Deployment completed successfully!")
                                return True, "Deployment successful"
                            elif 'error' in element.lower():
                                print(f"   ❌ Deployment failed")
                                return False, "Deployment failed"
                
                print(f"   ⏳ Checking again in 10 seconds...")
                time.sleep(10)
                
            except Exception as e:
                print(f"   ⚠️  Error checking status: {e}")
                time.sleep(5)
        
        return False, "Deployment timeout"

if __name__ == "__main__":
    # Test the API
    api = CoolifyAPI()
    
    # Login
    success, result = api.login("admin@247420.xyz", "123,slam123,slam")
    if not success:
        print(f"❌ Login failed: {result}")
        exit(1)
    
    # Get dashboard info
    success, result = api.get_dashboard_info()
    if not success:
        print(f"❌ Dashboard error: {result}")
        exit(1)
    
    # Create test application
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "test-app.247420.xyz"
    
    success, result = api.create_application(app_name, repo_url, domain_name)
    if success:
        print(f"✅ Application creation initiated: {result}")
        
        # Monitor deployment
        success, result = api.monitor_deployment(app_name)
        if success:
            print(f"✅ Deployment successful: {result}")
            print(f"🌐 Application should be available at: https://{domain_name}")
        else:
            print(f"❌ Deployment failed: {result}")
    else:
        print(f"❌ Application creation failed: {result}")
