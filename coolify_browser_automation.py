#!/usr/bin/env python3
"""
Coolify Browser Automation Tool
Uses web scraping to simulate browser interactions for deployment automation
"""

import requests
import re
import json
import sys
import time
import argparse
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class CoolifyBrowserAutomation:
    def __init__(self, base_url="https://coolify.247420.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.verify = False
        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def login(self, email, password):
        """Perform browser-like login"""
        print(f"🔐 Performing browser login to {self.base_url}...")
        
        try:
            # Step 1: Get login page with all assets
            print("   Loading login page...")
            response = self.session.get(f"{self.base_url}/login")
            response.raise_for_status()
            
            # Parse HTML to extract all necessary tokens and form data
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract CSRF token
            csrf_input = soup.find('input', {'name': '_token'})
            csrf_token = csrf_input['value'] if csrf_input else None
            
            if not csrf_token:
                print("   ❌ Could not find CSRF token")
                return False
            
            print(f"   ✅ CSRF token extracted: {csrf_token[:20]}...")
            
            # Extract any other hidden fields
            form_data = {}
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
            for inp in hidden_inputs:
                if inp.get('name'):
                    form_data[inp['name']] = inp.get('value', '')
            
            # Add login credentials
            form_data.update({
                'email': email,
                'password': password
            })
            
            print("   Submitting login form...")
            
            # Step 2: Submit login form
            login_response = self.session.post(
                f"{self.base_url}/login",
                data=form_data,
                allow_redirects=False
            )
            
            print(f"   Login response status: {login_response.status_code}")
            
            # Step 3: Follow redirects to establish session
            if login_response.status_code == 302:
                redirect_url = login_response.headers.get('Location', '/')
                print(f"   Following redirect to: {redirect_url}")
                
                # Follow the redirect
                dashboard_response = self.session.get(
                    urljoin(self.base_url, redirect_url),
                    allow_redirects=True
                )
                
                if dashboard_response.status_code == 200:
                    print("   ✅ Login successful - session established")
                    return True
                else:
                    print(f"   ❌ Dashboard access failed: {dashboard_response.status_code}")
                    return False
            elif login_response.status_code == 200:
                print("   ✅ Login successful - direct response")
                return True
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False
    
    def get_dashboard_content(self):
        """Get and parse dashboard content"""
        try:
            print("📋 Loading dashboard content...")
            response = self.session.get(f"{self.base_url}/dashboard")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for navigation links and key elements
            nav_links = {}
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                if text and any(keyword in text.lower() for keyword in ['server', 'application', 'resource', 'new', 'create']):
                    nav_links[text] = href
            
            print("   📊 Dashboard navigation found:")
            for text, href in nav_links.items():
                print(f"      - {text}: {href}")
            
            return {
                'html': response.text,
                'soup': soup,
                'navigation': nav_links,
                'size': len(response.text)
            }
            
        except Exception as e:
            print(f"   ❌ Error loading dashboard: {e}")
            return None
    
    def find_applications_page(self, dashboard_content):
        """Find the applications/resources page from dashboard"""
        if not dashboard_content:
            return None
            
        nav = dashboard_content['navigation']
        
        # Look for applications or resources links
        for text, href in nav.items():
            if 'application' in text.lower() or 'resource' in text.lower():
                print(f"📱 Found applications link: {text} -> {href}")
                return href
        
        # Try common patterns
        common_patterns = ['/applications', '/resources', '/apps']
        for pattern in common_patterns:
            print(f"🔍 Testing common pattern: {pattern}")
            response = self.session.get(urljoin(self.base_url, pattern))
            if response.status_code == 200:
                print(f"✅ Found applications page: {pattern}")
                return pattern
        
        return None
    
    def parse_applications_page(self, applications_url):
        """Parse the applications page to find existing apps"""
        try:
            print(f"📱 Loading applications page: {applications_url}")
            response = self.session.get(urljoin(self.base_url, applications_url))
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for application listings
            apps = []
            
            # Try different selectors for application cards/rows
            selectors = [
                '[data-application-id]',
                '.application-card',
                '.app-item',
                'tr[data-id]',
                '[wire\\:key*="application"]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements:
                        app_data = self._extract_app_data(element)
                        if app_data:
                            apps.append(app_data)
                    
                    if apps:
                        break
            
            # Also look for "New Application" buttons
            new_app_buttons = soup.find_all('a', string=re.compile(r'New.*Application|Create.*Application|Add.*Application', re.I))
            if new_app_buttons:
                print(f"   Found {len(new_app_buttons)} 'New Application' buttons")
            
            return {
                'applications': apps,
                'html': response.text,
                'soup': soup,
                'new_app_buttons': [btn.get('href') for btn in new_app_buttons if btn.get('href')]
            }
            
        except Exception as e:
            print(f"   ❌ Error parsing applications page: {e}")
            return None
    
    def _extract_app_data(self, element):
        """Extract application data from HTML element"""
        try:
            app_data = {}
            
            # Try to find app ID
            app_id = element.get('data-application-id') or element.get('data-id')
            if app_id:
                app_data['id'] = app_id
            
            # Try to find app name
            name_elem = element.find(['h1', 'h2', 'h3', 'h4', 'span', 'a'], class_=re.compile(r'name|title', re.I))
            if name_elem:
                app_data['name'] = name_elem.get_text(strip=True)
            
            # Try to find repository URL
            repo_elem = element.find(string=re.compile(r'github\.com|gitlab\.com|bitbucket\.org', re.I))
            if repo_elem:
                app_data['repository'] = repo_elem.strip()
            
            # Try to find status
            status_elem = element.find(class_=re.compile(r'status|state', re.I))
            if status_elem:
                app_data['status'] = status_elem.get_text(strip=True)
            
            # Only return if we found at least an ID or name
            if app_data.get('id') or app_data.get('name'):
                return app_data
            
        except Exception as e:
            print(f"   Warning: Could not extract app data: {e}")
        
        return None
    
    def test_deployment_workflow(self):
        """Test the complete deployment workflow"""
        print("🚀 Testing complete deployment workflow...")
        
        # Step 1: Login
        if not self.login("admin@247420.xyz", "123,slam123,slam"):
            return False
        
        # Step 2: Get dashboard
        dashboard = self.get_dashboard_content()
        if not dashboard:
            return False
        
        print(f"   Dashboard loaded: {dashboard['size']} bytes")
        
        # Step 3: Find applications page
        apps_url = self.find_applications_page(dashboard)
        if not apps_url:
            print("   ❌ Could not find applications page")
            return False
        
        # Step 4: Parse applications
        apps_page = self.parse_applications_page(apps_url)
        if apps_page:
            print(f"   ✅ Found {len(apps_page['applications'])} applications")
            for app in apps_page['applications'][:3]:  # Show first 3
                print(f"      - {app.get('name', 'Unknown')} (ID: {app.get('id', 'Unknown')})")
        
        return True
    
    def create_selenium_alternative_info(self):
        """Provide information for Selenium implementation"""
        print("\n📋 SELENIUM IMPLEMENTATION GUIDE:")
        print("="*50)
        print("""
Since web scraping has limitations with dynamic JavaScript content,
here's how to implement with Selenium:

1. Install requirements:
   pip install selenium webdriver-manager

2. Basic Selenium structure:
   from selenium import webdriver
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   
3. Login workflow:
   driver.get('https://coolify.247420.xyz/login')
   driver.find_element(By.NAME, 'email').send_keys('admin@247420.xyz')
   driver.find_element(By.NAME, 'password').send_keys('123,slam123,slam')
   driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
   
4. Navigate to applications:
   wait = WebDriverWait(driver, 10)
   apps_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Applications')))
   apps_link.click()
   
5. Create application:
   new_app_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'New Application')))
   new_app_btn.click()
   
   # Fill form fields
   name_field = driver.find_element(By.NAME, 'name')
   repo_field = driver.find_element(By.NAME, 'git_repository')
   # etc.
   
6. Deploy application:
   deploy_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Deploy")]')
   deploy_btn.click()
   
7. Monitor deployment:
   # Watch for log updates
   logs_container = driver.find_element(By.CLASS_NAME, 'deployment-logs')
   while 'deploying' in logs_container.text.lower():
       print(logs_container.text)
       time.sleep(2)
""")

def main():
    parser = argparse.ArgumentParser(description='Coolify Browser Automation Tool')
    parser.add_argument('command', choices=['login', 'dashboard', 'apps', 'test', 'selenium-guide'], 
                       help='Command to execute')
    parser.add_argument('--email', default='admin@247420.xyz', help='Email for login')
    parser.add_argument('--password', default='123,slam123,slam', help='Password for login')
    
    args = parser.parse_args()
    
    automation = CoolifyBrowserAutomation()
    
    try:
        if args.command == 'login':
            success = automation.login(args.email, args.password)
            print(f"Login {'successful' if success else 'failed'}")
            
        elif args.command == 'dashboard':
            if automation.login(args.email, args.password):
                dashboard = automation.get_dashboard_content()
                if dashboard:
                    print(f"Dashboard loaded successfully ({dashboard['size']} bytes)")
                    print("Navigation links found:")
                    for text, href in dashboard['navigation'].items():
                        print(f"  - {text}: {href}")
            
        elif args.command == 'apps':
            if automation.login(args.email, args.password):
                dashboard = automation.get_dashboard_content()
                apps_url = automation.find_applications_page(dashboard)
                if apps_url:
                    apps_page = automation.parse_applications_page(apps_url)
                    if apps_page and apps_page['applications']:
                        print("Applications found:")
                        for app in apps_page['applications']:
                            print(f"  - {app}")
                    else:
                        print("No applications found")
            
        elif args.command == 'test':
            automation.test_deployment_workflow()
            
        elif args.command == 'selenium-guide':
            automation.create_selenium_alternative_info()
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
