import requests
import re
from bs4 import BeautifulSoup

def test_login():
    """Quick test of login functionality"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    base_url = "https://coolify.247420.xyz"
    email = "admin@247420.xyz"
    password = "123,slam123,slam"
    
    try:
        # Get login page
        response = session.get(f"{base_url}/login")
        print(f"Login page status: {response.status_code}")
        
        # Extract CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_meta = soup.find('meta', {'name': 'csrf-token'})
        csrf_token = csrf_meta.get('content') if csrf_meta else None
        
        if csrf_token:
            print(f"CSRF Token: {csrf_token[:20]}...")
        
        # Login data
        login_data = {
            'email': email,
            'password': password
        }
        
        if csrf_token:
            login_data['_token'] = csrf_token
        
        # Perform login
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            print(f"Redirect to: {redirect_url}")
            
            # Follow redirect
            response = session.get(redirect_url)
            print(f"Redirect follow status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for dashboard indicators
                dashboard_words = ['dashboard', 'applications', 'deployments', 'resources', 'logout']
                dashboard_count = sum(1 for word in dashboard_words if word in content)
                
                print(f"Dashboard words found: {dashboard_count}")
                
                if dashboard_count >= 2:
                    print("✅ Login successful - dashboard detected!")
                    
                    # Extract UUIDs
                    project_matches = re.findall(r'/project/([a-z0-9]{32})', response.text)
                    env_matches = re.findall(r'/environment/([a-z0-9]{32})', response.text)
                    
                    print(f"Project UUIDs found: {len(project_matches)}")
                    print(f"Environment UUIDs found: {len(env_matches)}")
                    
                    if project_matches:
                        print(f"First project UUID: {project_matches[0]}")
                    if env_matches:
                        print(f"First environment UUID: {env_matches[0]}")
                    
                    return True, {
                        'project_uuid': project_matches[0] if project_matches else None,
                        'environment_uuid': env_matches[0] if env_matches else None,
                        'session': session
                    }
                else:
                    print("❌ Login failed - no dashboard content")
                    return False, "No dashboard content detected"
            else:
                print(f"❌ Redirect failed: {response.status_code}")
                return False, f"Redirect failed with status {response.status_code}"
        else:
            print(f"❌ No redirect - login likely failed: {response.status_code}")
            return False, f"No redirect received: {response.status_code}"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, f"Exception: {str(e)}"

if __name__ == "__main__":
    success, result = test_login()
    print(f"\nFinal result: {success}")
    if success and isinstance(result, dict):
        print(f"Project UUID: {result.get('project_uuid')}")
        print(f"Environment UUID: {result.get('environment_uuid')}")
    elif isinstance(result, str):
        print(f"Error: {result}")
