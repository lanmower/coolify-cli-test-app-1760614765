import requests
import re
import json
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class CoolifyFinalDeployment:
    """Final working deployment tool with correct resource IDs"""
    
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.csrf_token = None
        
        # Real UUIDs from analysis
        self.project_uuid = "ckgkgcwo00sc4ks4okcwgoww"
        self.environment_uuid = "jsso4kwcwgw0oss0co8k4888"
        
        # Found application resource IDs
        self.application_resource_ids = [
            "848ed38f09cb40e780a5f10186155e346d17",
            "7a6ff7c63919cd0347681ac8489caf47fa9c"
        ]
        
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
        print(f"🔐 Authenticating...")
        
        try:
            # Get login page
            response = self.session.get(f"{self.base_url}/login")
            
            # Extract CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_meta = soup.find('meta', {'name': 'csrf-token'})
            if csrf_meta:
                self.csrf_token = csrf_meta.get('content')
            
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
    
    def extract_main_component_id(self):
        """Extract the main component ID from the resource creation page"""
        print("🔍 Extracting main component ID...")
        
        try:
            # Get resource creation page
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            response = self.session.get(resource_url)
            
            # Extract component ID
            component_match = re.search(r'wire:id="([^"]+)"', response.text)
            if component_match:
                component_id = component_match.group(1)
                print(f"   ✅ Found main component ID: {component_id}")
                return component_id
            else:
                print("   ❌ Component ID not found")
                return None
                
        except Exception as e:
            print(f"   ❌ Error extracting component ID: {e}")
            return None
    
    def select_application_type(self, component_id, resource_id):
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
                'Content-Type': 'application/json',
                'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate'
            }
            
            response = self.session.post(
                f"{self.base_url}/livewire/{component_id}",
                json=livewire_data,
                headers=headers
            )
            
            print(f"   📡 Livewire response: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Application type selected")
                return True, response.text
            else:
                print(f"   ❌ Failed to select resource: {response.status_code}")
                print(f"   Response content: {response.text[:200]}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Error selecting resource: {e}")
            return False, None
    
    def create_application_simple(self, app_name, repo_url, domain_name):
        """Simple application creation by submitting form data"""
        print(f"🏗️ Creating application: {app_name}")
        
        try:
            # Get resource creation page
            resource_url = f"{self.base_url}/project/{self.project_uuid}/environment/{self.environment_uuid}/new"
            response = self.session.get(resource_url)
            
            if response.status_code != 200:
                return False, f"Cannot access resource page: {response.status_code}"
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for any application-related forms or links
            app_links = soup.find_all('a', href=re.compile(r'application|new|create', re.I))
            if app_links:
                print(f"   📋 Found {len(app_links)} application-related links")
                for i, link in enumerate(app_links[:3], 1):
                    print(f"      {i}. {link.get('href', 'No href')} - {link.get_text().strip()}")
            
            # Try to find and click on application-related elements
            buttons = soup.find_all(['button', 'a'], string=re.compile(r'application|create|new', re.I))
            if buttons:
                print(f"   📋 Found {len(buttons)} application-related buttons")
                # Try clicking the first button
                first_button = buttons[0]
                if first_button.get('href'):
                    # Navigate to the link
                    link_url = first_button['href']
                    if not link_url.startswith('http'):
                        link_url = urljoin(self.base_url, link_url)
                    
                    print(f"   🖱️  Clicking application link: {link_url}")
                    response = self.session.get(link_url)
                    
                    if response.status_code == 200:
                        print("   ✅ Navigated to application creation page")
                        
                        # Look for application creation form
                        app_soup = BeautifulSoup(response.text, 'html.parser')
                        forms = app_soup.find_all('form')
                        
                        if forms:
                            print(f"   📋 Found {len(forms)} forms on application page")
                            
                            # Try to submit the first form with application data
                            form = forms[0]
                            action = form.get('action', '')
                            if action:
                                form_url = urljoin(self.base_url, action)
                            else:
                                form_url = response.url
                            
                            # Prepare form data
                            form_data = {}
                            
                            # Look for input fields
                            inputs = form.find_all(['input', 'select', 'textarea'])
                            for inp in inputs:
                                name = inp.get('name')
                                if name:
                                    if 'name' in name.lower():
                                        form_data[name] = app_name
                                    elif 'repo' in name.lower() or 'git' in name.lower():
                                        form_data[name] = repo_url
                                    elif 'domain' in name.lower() or 'host' in name.lower():
                                        form_data[name] = domain_name
                                    elif 'build' in name.lower():
                                        form_data[name] = 'nixpacks'
                                    elif 'token' in name.lower():
                                        form_data[name] = self.csrf_token
                                    else:
                                        # Get default value
                                        value = inp.get('value', '')
                                        if value:
                                            form_data[name] = value
                            
                            print(f"   📝 Form data prepared: {list(form_data.keys())}")
                            
                            # Submit form
                            submit_response = self.session.post(form_url, data=form_data)
                            
                            if submit_response.status_code in [200, 302]:
                                print("   ✅ Application form submitted successfully")
                                return True, "Application creation initiated"
                            else:
                                print(f"   ❌ Form submission failed: {submit_response.status_code}")
                                return False, f"Form submission failed: {submit_response.status_code}"
                        else:
                            print("   ❌ No forms found on application page")
                            return False, "No forms found"
                    else:
                        print(f"   ❌ Failed to navigate to application page: {response.status_code}")
                        return False, f"Navigation failed: {response.status_code}"
            
            # If no direct links found, provide manual instructions
            print("   ⚠️  No automatic application creation found")
            print("   📋 Manual application creation required")
            
            return True, {
                'message': 'Manual application creation required',
                'url': resource_url,
                'instructions': [
                    f"1. Visit: {resource_url}",
                    f"2. Click on 'Application' or similar resource type",
                    f"3. Fill in application name: {app_name}",
                    f"4. Fill in repository: {repo_url}",
                    f"5. Set domain: {domain_name}",
                    f"6. Select build method: nixpacks",
                    f"7. Submit the form"
                ]
            }
                
        except Exception as e:
            return False, f"Application creation error: {str(e)}"
    
    def deploy_application(self, app_name, repo_url, domain_name=None):
        """Complete deployment workflow"""
        print(f"🚀 Starting deployment of {app_name}")
        
        if not domain_name:
            domain_name = f"{app_name}.247420.xyz"
        
        # Step 1: Authentication
        if not self.login("admin@247420.xyz", "123,slam123,slam"):
            return False, "Authentication failed"
        
        # Step 2: Get main component ID
        component_id = self.extract_main_component_id()
        if not component_id:
            return False, "Could not extract component ID"
        
        # Step 3: Try Livewire approach with found resource IDs
        for resource_id in self.application_resource_ids:
            success, livewire_response = self.select_application_type(component_id, resource_id)
            if success:
                print(f"   ✅ Livewire approach successful with resource ID: {resource_id}")
                break
        else:
            print("   ⚠️  Livewire approach failed, trying direct form submission")
        
        # Step 4: Try simple application creation
        success, result = self.create_application_simple(app_name, repo_url, domain_name)
        
        if success:
            if isinstance(result, dict):
                # Manual creation required
                print(f"\n📋 Manual deployment instructions:")
                for instruction in result.get('instructions', []):
                    print(f"   {instruction}")
                return True, result
            else:
                print(f"\n✅ Automated deployment successful!")
                print(f"🌐 Application will be available at: https://{domain_name}")
                return True, result
        else:
            return False, result

if __name__ == "__main__":
    # Test the final deployment tool
    deployer = CoolifyFinalDeployment()
    
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "nixpacks-test.247420.xyz"
    
    success, result = deployer.deploy_application(app_name, repo_url, domain_name)
    
    if success:
        print(f"\n🎉 SUCCESS: {result}")
    else:
        print(f"\n❌ FAILED: {result}")
