import requests
import json

def test_upload():
    print("Testing code upload with Ollama integration...")
    
    # Simple Python code to analyze
    code = """
def factorial(n):
    if n < 0:
        return None
    if n == 0:
        return 1
    return n * factorial(n-1)

# Test with a large number (can cause stack overflow)
print(factorial(100))
"""
    
    # Data for the upload
    data = {
        'code_content': code,
        'filename': 'test.py'
    }
    
    # First, try to login (we need a session)
    session = requests.Session()
    
    try:
        # Login first
        print("Logging in...")
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        login_response = session.post('http://localhost:5000/login', data=login_data)
        
        if login_response.status_code == 200:
            print("Login successful (or at least returned 200)")
        else:
            print(f"Login returned: {login_response.status_code}")
        
        # Now submit the code
        print("Uploading code...")
        upload_response = session.post('http://localhost:5000/upload', data=data)
        
        if upload_response.status_code == 200:
            print("Upload successful")
            if 'Ollama' in upload_response.text:
                print("Found Ollama reference in response")
            else:
                print("No Ollama reference found in response")
        else:
            print(f"Upload returned: {upload_response.status_code}")
            print(upload_response.text[:200])
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_upload() 