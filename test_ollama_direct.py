#!/usr/bin/env python
import json
import sys
from app.ollama_integration import OllamaCodeLlama

def test_direct_ollama_integration():
    print("\n=== Testing direct Ollama integration ===")
    
    # Initialize the Ollama integration
    ollama_url = "http://localhost:11434"
    ollama = OllamaCodeLlama(base_url=ollama_url)
    
    # Check availability
    print(f"\n1. Checking Ollama availability at {ollama_url}")
    is_available = ollama.check_availability()
    print(f"   Result: {'Available' if is_available else 'Not available'}")
    
    if not is_available:
        print("   ❌ Ollama is not available. Exiting test.")
        return False
    
    # Test generating a response
    print("\n2. Testing code analysis with Ollama")
    test_code = """
def add_numbers(a, b):
    return a + b + 1  # Bug: adding 1 unnecessarily
"""
    
    try:
        # Print API URL
        print(f"   API URL: {ollama.api_url}")
        
        # Construct the actual request payload
        request_payload = {
            "model": ollama.model_name,
            "prompt": ollama._generate_prompt(test_code, "python"),
            "stream": False
        }
        print(f"   Request Payload preview:\n   {json.dumps({**request_payload, 'prompt': request_payload['prompt'][:100] + '...'})}") 
        
        # Call analyze_code
        print("   Calling analyze_code...")
        analysis_result = ollama.analyze_code(test_code, "python")
        
        # Print the result
        print(f"   Result: {json.dumps(analysis_result, indent=2)}")
        
        # Check for expected components
        if 'bugs' in analysis_result:
            print(f"   ✅ Found {len(analysis_result['bugs'])} bugs")
        else:
            print("   ❌ No bugs section in response")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_ollama_integration()
    sys.exit(0 if success else 1) 