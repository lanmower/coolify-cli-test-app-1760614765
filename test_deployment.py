import sys
sys.path.append('.')

from coolify_api import CoolifyAPI

def test_deployment():
    """Test deployment of our nixpacks test app"""
    print("🚀 Starting deployment test...")
    
    api = CoolifyAPI()
    
    # Step 1: Login
    print("\n1. 🔐 Logging in...")
    success, result = api.login("admin@247420.xyz", "123,slam123,slam")
    if not success:
        print(f"❌ Login failed: {result}")
        return False
    print(f"✅ Login successful")
    
    # Step 2: Get dashboard info
    print("\n2. 📊 Getting dashboard info...")
    success, result = api.get_dashboard_info()
    if not success:
        print(f"❌ Dashboard error: {result}")
        return False
    print(f"✅ Dashboard info retrieved")
    print(f"   Project ID: {api.project_id}")
    print(f"   Environment ID: {api.environment_id}")
    
    # Step 3: Create application
    print("\n3. 🏗️ Creating application...")
    app_name = "nixpacks-test-app"
    repo_url = "https://github.com/AnEntrypoint/nixpacks-test-app.git"
    domain_name = "nixpacks-test.247420.xyz"
    
    success, result = api.create_application(app_name, repo_url, domain_name, "nixpacks")
    if success:
        print(f"✅ Application creation initiated: {result}")
        
        # Step 4: Monitor deployment
        print("\n4. 📊 Monitoring deployment...")
        success, result = api.monitor_deployment(app_name, timeout=180)
        if success:
            print(f"✅ Deployment successful!")
            print(f"🌐 Application should be available at: https://{domain_name}")
            return True
        else:
            print(f"❌ Deployment failed: {result}")
            return False
    else:
        print(f"❌ Application creation failed: {result}")
        return False

if __name__ == "__main__":
    success = test_deployment()
    if success:
        print("\n🎉 Complete deployment test successful!")
    else:
        print("\n❌ Deployment test failed")
        sys.exit(1)
