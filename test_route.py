from app import create_app
import requests
import json

app = create_app()

# Extract the URL map
print("Registered routes:")
routes = sorted([str(rule) for rule in app.url_map.iter_rules()])
for route in routes:
    print(f"  {route}")

# Check if check_ollama route exists
if '/check_ollama' in routes:
    print("\ncheck_ollama route is registered.")
else:
    print("\ncheck_ollama route is NOT registered!")

# Test the route with requests
try:
    print("\nTesting route with Flask test client:")
    with app.test_client() as client:
        response = client.get('/check_ollama')
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response data: {response.data.decode('utf-8')}")
        else:
            print(f"Error: {response.data.decode('utf-8')}")
except Exception as e:
    print(f"Error testing with test client: {str(e)}")

# Also try with direct requests if the server is running
try:
    print("\nTesting route with direct HTTP request:")
    response = requests.get('http://localhost:5000/check_ollama')
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        print(f"Response data: {response.text[:100]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error making HTTP request: {str(e)}") 