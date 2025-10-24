import requests
import re
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class CoolifyAPI:
    """Updated Coolify API wrapper with correct component structure"""
    
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
            'Upgrade-Insecure-Requests': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': None,  # Will be set dynamically
            'X-Livewire': 'true',
            'Content-Type': 'application/json'
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
    
    def extract_uuids_from_dashboard(self):
        """Extract project and environment UUIDs from dashboard"""
        print("🔍 Extracting UUIDs from dashboard...")
        
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            if response.status_code != 200:
                return False, f"Dashboard not accessible: {response.status_code}"
            
            # Extract UUIDs from page content
            content = response.text
            
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
            
            # If not found in content, try to find them in specific patterns
            if not self.project_uuid or not self.environment_uuid:
                # Look for resource creation links
                resource_links = re.findall(r'href="([^"]*/project/[^"]*/environment/[^"]*/new[^"]*)"', content)
                if resource_links:
                    link = resource_links[0]
                    project_match = re.search(r'/project/([a-z0-9]{32})', link)
                    env_match = re.search(r'/environment/([a-z0-9]{32})', link)
                    
                    if project_match:
                        self.project_uuid = project_match.group(1)
                        print(f"   ✅ Found project UUID from link: {self.project_uuid}")
                    
                    if env_match:
                        self.environment_uuid = env_match.group(1)
                        print(f"   ✅ Found environment UUID from link: {self.environment_uuid}")
            
            if self.project_uuid and self.environment_uuid:
                return True, "UUIDs extracted successfully"
            else:
                return False, "Could not extract required UUIDs"
                
        except Exception as e:
            return False, f"UUID extraction error: {str(e)}"
    
    def navigate_to_resource_creation(self):
        """Navigate to resource creation page and extract component info"""
        print("🚀 Navigating to resource creation page...")
        
        if not self.project_uuid or not self.environment_uuid:
            return False, "UUIDs not set"
        
        try:
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            print(f"   📡 URL: {resource_url}")
            
            response = self.session.get(resource_url)
            if response.status_code != 200:
                return False, f"Resource page not accessible: {response.status_code}"
            
            print("   ✅ Resource creation page loaded")
            
            # Extract component IDs
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all wire:id attributes
            wire_components = soup.find_all(attrs={'wire:id': True})
            component_ids = [comp.get('wire:id') for comp in wire_components]
            
            print(f"   📋 Found {len(component_ids)} Livewire components:")
            for comp_id in component_ids:
                print(f"      - {comp_id}")
            
            # Look for the resource selection component
            resource_component = None
            for comp in wire_components:
                text = comp.get_text().lower()
                if 'select' in text and ('resource' in text or 'application' in text):
                    resource_component = comp.get('wire:id')
                    break
            
            if resource_component:
                print(f"   ✅ Found resource selection component: {resource_component}")
                return True, resource_component
            else:
                print("   ⚠️  Resource selection component not found, using first component")
                if component_ids:
                    return True, component_ids[0]
                return False, "No components found"
                
        except Exception as e:
            return False, f"Navigation error: {str(e)}"
    
    def select_application_type(self, component_id):
        """Select application type using Livewire"""
        print("📱 Selecting application type...")
        
        try:
            # Livewire request to select application type
            livewire_data = {
                "components": [{
                    "id": component_id,
                    "calls": [{
                        "method": "setType",
                        "params": ["git-based-application"]  # or appropriate type ID
                    }]
                }]
            }
            
            response = self.session.post(
                f"{self.base_url}/livewire/{component_id}",
                json=livewire_data
            )
            
            print(f"   📡 Livewire response: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Application type selected")
                return True, "Application type selected"
            else:
                print(f"   ❌ Failed to select type: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False, f"Failed to select application type: {response.status_code}"
                
        except Exception as e:
            return False, f"Type selection error: {str(e)}"
    
    def create_application_with_form(self, app_name, repo_url, domain_name=None):
        """Create application by submitting the form"""
        print(f"🏗️ Creating application: {app_name}")
        
        try:
            # Navigate to the application creation page again to get the form
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            response = self.session.get(resource_url)
            
            if response.status_code != 200:
                return False, f"Cannot access form page: {response.status_code}"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for application configuration forms
            forms = soup.find_all('form')
            app_form = None
            
            for form in forms:
                form_text = form.get_text().lower()
                if 'application' in form_text and ('repository' in form_text or 'git' in form_text):
                    app_form = form
                    break
            
            if app_form:
                print("   ✅ Found application configuration form")
                
                # Extract form data
                form_data = {}
                
                # Find all input fields
                inputs = app_form.find_all(['input', 'select', 'textarea'])
                for inp in inputs:
                    name = inp.get('name')
                    value = inp.get('value', '')
                    
                    if name == 'name':
                        form_data[name] = app_name
                    elif name == 'repository' or name == 'git_repository':
                        form_data[name] = repo_url
                    elif name == 'domain' or name == 'hostname':
                        form_data[name] = domain_name or f"{app_name}.247420.xyz"
                    elif name == 'build_method' or name == 'build_pack':
                        form_data[name] = 'nixpacks'
                    elif name and name != '_token':  # Don't override CSRF token
                        form_data[name] = value
                
                # Add CSRF token
                if self.csrf_token:
                    form_data['_token'] = self.csrf_token
                
                print(f"   📝 Form data: {list(form_data.keys())}")
                
                # Submit the form
                form_action = app_form.get('action', resource_url)
                if not form_action.startswith('http'):
                    form_action = urljoin(self.base_url, form_action)
                
                response = self.session.post(form_action, data=form_data)
                
                if response.status_code in [200, 302]:
                    print("   ✅ Application form submitted")
                    return True, "Application creation initiated"
                else:
                    print(f"   ❌ Form submission failed: {response.status_code}")
                    return False, f"Form submission failed: {response.status_code}"
            else:
                print("   ❌ Application form not found")
                return False, "Application form not found"
                
        except Exception as e:
            return False, f"Form submission error: {str(e)}"
    
    def full_deployment_workflow(self, app_name, repo_url, domain_name=None):
        """Execute the complete deployment workflow"""
        print(f"🚀 Starting full deployment workflow for {app_name}")
        
        # Step 1: Login
        success, result = self.login("admin@247420.xyz", "123,slam123,slam")
        if not success:
            return False, f"Login failed: {result}"
        
        # Step 2: Extract UUIDs
        success, result = self.extract_uuids_from_dashboard()
        if not success:
            return False, f"UUID extraction failed: {result}"
        
        # Step 3: Navigate to resource creation
        success, result = self.navigate_to_resource_creation()
        if not success:
            return False, f"Navigation failed: {result}"
        
        component_id = result
        
        # Step 4: Try Livewire approach first
        success, result = self.select_application_type(component_id)
        if success:
            # Step 5: Create application with form
            return self.create_application_with_form(app_name, repo_url, domain_name)
        else:
            # Fallback to direct form submission
            return self.create_application_with_form(app_name, repo_url, domain_name)

if __name__ == "__main__":
    # Test the updated API
    api = CoolifyAPI()
    
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "nixpacks-test.247420.xyz"
    
    success, result = api.full_deployment_workflow(app_name, repo_url, domain_name)
    
    if success:
        print(f"✅ Deployment workflow successful: {result}")
        print(f"🌐 Application should be available at: https://{domain_name}")
    else:
        print(f"❌ Deployment workflow failed: {result}")
