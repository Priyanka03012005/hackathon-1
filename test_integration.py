import requests
import json
import time
import sys
from bs4 import BeautifulSoup

def test_integration():
    print("Testing full Ollama integration flow with detailed debugging...")

    # Define base URL
    base_url = "http://localhost:5000"
    session = requests.Session()

    # 0. Create test user account
    print("\n0. Creating test user account...")
    response = session.post(f"{base_url}/signup", data={
        "email": "test_user@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    
    # Check if user already exists (will redirect to login)
    if "login" in response.url:
        print("   ℹ️ User already exists, proceeding to login")
    else:
        print("   ✓ User created successfully")

    # 1. Login
    print("\n1. Logging in...")
    response = session.post(f"{base_url}/login", data={
        "email": "test_user@example.com",
        "password": "password123"
    })
    
    # Check if login was successful
    if "dashboard" in response.url:
        print("   ✓ Login successful (redirected to dashboard)")
    else:
        print("   ✗ Login failed")
        soup = BeautifulSoup(response.text, 'html.parser')
        flash_messages = soup.select('.alert')
        if flash_messages:
            for msg in flash_messages:
                print(f"   Error: {msg.text.strip()}")
        return False

    # Store cookies for debug
    print(f"   Debug - Session cookies: {session.cookies}")

    # 2. Access settings page
    print("\n2. Accessing settings page...")
    response = session.get(f"{base_url}/settings")
    
    if response.status_code == 200:
        print("   ✓ Settings page loaded")
        
        # Parse the HTML to extract current Ollama settings
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for radio buttons
        default_model = soup.find('input', {'id': 'defaultModel'})
        ollama_model = soup.find('input', {'id': 'ollamaModel'})
        
        if default_model and ollama_model:
            print(f"   Debug - Default model checked: {default_model.get('checked') == ''}")
            print(f"   Debug - Ollama model checked: {ollama_model.get('checked') == ''}")
        else:
            print("   ✗ Couldn't find model selection radio buttons")
            
        # Look for Ollama URL input
        ollama_url_input = soup.find('input', {'name': 'ollama_url'})
        if ollama_url_input:
            print(f"   Debug - Current Ollama URL value: {ollama_url_input.get('value', 'Not set')}")
        else:
            print("   ✗ Couldn't find Ollama URL input field")
            
        # Check for Ollama status
        ollama_status = soup.find(id='ollama-status')
        if ollama_status:
            print(f"   Debug - Ollama status display: {ollama_status.text.strip()[:100]}...")
        else:
            print("   ✗ Couldn't find Ollama status element")
    else:
        print(f"   ✗ Failed to load settings page (status code: {response.status_code})")
        return False

    # 3. Enable Ollama in settings
    print("\n3. Enabling Ollama in settings...")
    response = session.post(f"{base_url}/settings", data={
        "ai_model": "ollama",
        "ollama_url": "http://localhost:11434",
        "use_context": "on"
    })
    
    if response.status_code == 200 or response.status_code == 302:
        print("   ✓ Settings updated")
        
        # Check for flash messages
        soup = BeautifulSoup(response.text, 'html.parser')
        flash_messages = soup.select('.alert')
        if flash_messages:
            for msg in flash_messages:
                print(f"   Message: {msg.text.strip()}")
    else:
        print(f"   ✗ Failed to update settings (status code: {response.status_code})")

    # Check settings again to verify
    print("\n3.1 Verifying settings update...")
    response = session.get(f"{base_url}/settings")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ollama_model = soup.find('input', {'id': 'ollamaModel'})
        
        if ollama_model and ollama_model.get('checked') == '':
            print("   ✓ Ollama model is selected")
        else:
            print("   ✗ Ollama model is not selected")
    else:
        print(f"   ✗ Failed to load settings page (status code: {response.status_code})")

    # 4. Check Ollama directly
    print("\n4. Verifying Ollama is working directly...")
    try:
        from app.ollama_integration import OllamaCodeLlama
        ollama = OllamaCodeLlama(base_url="http://localhost:11434")
        is_available = ollama.check_availability()
        if is_available:
            print("   ✓ Ollama is available directly through Python")
        else:
            print("   ✗ Ollama is not available directly")
            return False
    except Exception as e:
        print(f"   ✗ Error checking Ollama directly: {str(e)}")
        return False

    # 5. Call check_ollama endpoint directly
    print("\n4.1 Testing check_ollama endpoint...")
    response = session.get(f"{base_url}/check_ollama")
    
    try:
        result = response.json()
        print(f"   Debug - check_ollama response: {result}")
        if result.get('available', False):
            print("   ✓ check_ollama endpoint confirms Ollama is available")
        else:
            print(f"   ✗ check_ollama endpoint says Ollama is not available: {result.get('message', 'No message')}")
    except Exception as e:
        print(f"   ✗ Error parsing check_ollama response: {str(e)}")
        print(f"   Raw response: {response.text[:100]}...")

    # 6. Upload code for analysis
    print("\n5. Uploading code for analysis...")
    test_code = """
def calculate_total(items):
    total = 0
    for item in items:
        # Bug: This will raise an exception if item is not a dictionary
        total += item['price']
    return total
"""
    
    response = session.post(f"{base_url}/upload", data={
        "code_content": test_code,
        "language": "python"
    }, allow_redirects=True)
    
    # Check if redirected to report page
    if "/report/" in response.url:
        print(f"   ✓ Code uploaded and redirected to: {response.url}")
        
        # Extract scan_id from URL
        scan_id = response.url.split('/')[-1]
        print(f"   ✓ Extracted scan_id: {scan_id}")
        
        # Parse report page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check which model was used
        model_badge = soup.select('.model-badge')
        if model_badge:
            model_text = model_badge[0].text.strip()
            print(f"   Debug - Model info badge: {model_text}")
            if "Ollama" in model_text:
                print("   ✓ Ollama was used for analysis")
            else:
                print(f"   ✗ Ollama was not used for analysis. Model used: {model_text}")
        else:
            print("   ✗ No model badge found in report")
        
        # Check for badges (indicating analysis results)
        badges = soup.select('.badge')
        if badges:
            badges_text = [b.text.strip() for b in badges]
            print(f"   ✓ Found badges: {badges_text}")
            
            # Check if "Ollama" appears in any badge
            if any("Ollama" in badge for badge in badges_text):
                print("   ✓ Ollama was used for analysis")
            else:
                print(f"   ✗ Ollama was not used for analysis. Found badges:")
                for badge in badges_text:
                    print(f"     - {badge}")
        else:
            print("   ✗ No badges found in report")
        
        # Check if analysis results are present
        results_section = soup.select('.analysis-results')
        if results_section:
            print("   ✓ Found analysis results in the report")
            
            # Count issues found
            bugs_count = len(soup.select('.bug-item'))
            security_count = len(soup.select('.security-item'))
            optimization_count = len(soup.select('.optimization-item'))
            
            print(f"   ✓ Analysis found: {bugs_count} bugs, {security_count} security issues, {optimization_count} optimizations")
        else:
            print("   ✗ No analysis results found in report")
    else:
        print(f"   ✗ Upload failed or did not redirect to report page. Redirected to: {response.url}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1) 